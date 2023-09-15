import importlib
import logging
import multiprocessing
import pickle
import threading
from enum import Enum
from pathlib import Path

import sys
import time
import zmq
from PyQt5.QtCore import QObject, QLockFile
from PyQt5.QtCore import QThread
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import QApplication, QScrollArea, QAction, QWidget, QSizePolicy, QMessageBox
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QVBoxLayout
from prometheus_client import start_http_server

from egse.confman import ConfigurationManagerProxy
from egse.confman import is_configuration_manager_active
from egse.control import is_control_server_active, Response, Failure
from egse.device import DeviceInterface
from egse.gui import show_info_message
from egse.gui.buttons import ToggleButton, TouchButton
from egse.gui.led import Indic
from egse.gui.led import LED
from egse.obsid import ObservationIdentifier
from egse.process import ProcessStatus
from egse.process import SubProcess
from egse.procman import ProcessManagerProxy
from egse.resource import get_resource
from egse.settings import Settings
from egse.setup import Setup
from egse.system import do_every
from egse.system import find_class
from egse.zmq_ser import connect_address
from egse.zmq_ser import set_address_port

logging.basicConfig(level=logging.INFO, format=Settings.LOG_FORMAT_FULL)

GUI_SETTINGS = Settings.load("PM GUI")
LOGGER = logging.getLogger(__name__)
SITE = Settings.load("SITE")

class FILE_GENERATION_PROCESS_NAMES(str, Enum):

    FITSGEN = "FITS generation"
    FOV_HK = "FOV HK"
    N_FEE_HK = "N-FEE HK"


class ConfigurationMonitoringWorker(QObject):

    # The thread will send a signal with the monitoring information:
    #   - The obsid;
    #   - The setup that has been loaded by the configuration manager.

    setup_changed_signal = pyqtSignal(dict)
    obsid_changed_signal = pyqtSignal(object)   # This allows ObservationIdentifier or None to be returned

    def __init__(self):

        """ Initialisation of a monitoring thread.

        This monitoring thread will listen on the monitoring port of the
        Control Server.  At this point the socket (that will connect to the
        monitoring port) is not created yet.
        """

        super(ConfigurationMonitoringWorker, self).__init__()

        self.setup = None   # Previous setup
        self.obsid = None   # Previous obsid
        self.active = False

        self.connect_socket()

    def connect_socket(self):
        """ Create a socket and connect to the monitoring port.

        Args:
            - proxy_type: Proxy type (needed to read the connection details).
        """

        # Start listening to the monitoring port

        self.socket = zmq.Context().socket(zmq.SUB)

        cm = ConfigurationManagerProxy()
        endpoint = cm.get_endpoint()
        monitoring_port = cm.get_monitoring_port()
        address = set_address_port(endpoint, monitoring_port)

        self.socket.connect(address)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")

    def start_process(self):
        """ Start listening on the monitoring port.
        """

        self.run()

    @pyqtSlot()
    def run(self):
        """ Keep on listening on the monitoring port.

        If monitoring information is received before the timeout, it is
        checked whether the obsid and/or current setup have changed.  If so, a
        signal with the monitoring information is emitted.
        """

        self.active = True

        while self.active:

            pickle_string = self.socket.recv()
            monitoring_info = pickle.loads(pickle_string)

            new_setup = monitoring_info["setup"]  # New setup

            # The setup has changed

            if new_setup != self.setup:

                self.setup = new_setup

                # Emit the setup ID

                self.setup_changed_signal.emit(self.setup)

            new_obsid = monitoring_info["obsid"]    # New obsid

            if new_obsid != self.obsid:

                self.obsid = new_obsid

                # Emit the obsid

                self.obsid_changed_signal.emit(self.obsid)

    def has_setup(self):
        """ Check whether a setup has been loaded.

        Returns: True if a setup has been loaded; False otherwise.
        """

        return self.setup is not None


class MonitoringWorker(QObject):
    """ Worker for monitoring the status of an EGSE process."""

    # The worker will send a signal with the following information:
    #   - process name
    #   - colour of the led (in the process widget)
    #   - in case of a running device process: whether or not it is running in simulator mode

    process_status_signal = pyqtSignal(dict)

    def __init__(self, process_name, process_info):
        """ Initialisation of a monitoring worker.

        This monitoring worker will listen on the monitoring port of the Control Server.

        Args:
            - process_name: Name of the process.
            - proxy_type: Proxy type (needed to read the connection details).
        """

        super(MonitoringWorker, self).__init__()

        self.active = False
        self.start_stop_cs_button_clicked = False

        self.process_name = process_name
        self.proxy_type = process_info[0]
        self.proxy_type_as_type = find_class(self.proxy_type[7:])
        self.device_args = process_info[1]

        self.monitoring_socket = None
        self.monitoring_timeout = 0.5  # [s]
        self.is_socket_connected = False

        self.commanding_address = None
        self.connect_socket()

        self.previous_state = -1

    def connect_socket(self):
        """ Create a socket and connect to the monitoring port."""

        try:

            module_name = self.proxy_type[7:].rsplit(".", 1)[0]
            module = importlib.import_module(module_name)

            # Ctrl settings:
            #   - transport protocol
            #   - hostname
            #   - commanding port (to check whether the CS is active)
            #   - monitoring port (to ask for process information)

            ctrl_settings = module.CTRL_SETTINGS

            transport = ctrl_settings.PROTOCOL
            hostname = ctrl_settings.HOSTNAME

            if module_name == "egse.aeu.aeu" or "egse.tempcontrol.agilent.agilent3497" in module_name:

                name = self.process_name.split(" ")[1].upper()

                commanding_port = ctrl_settings[name]["COMMANDING_PORT"]
                monitoring_port = ctrl_settings[name]["MONITORING_PORT"]

            elif module_name == "egse.powermeter.ni.cdaq9184":
                commanding_port = ctrl_settings.CDAQ9184["COMMANDING_PORT"]
                monitoring_port = ctrl_settings.CDAQ9184["MONITORING_PORT"]

            elif module_name == "egse.tempcontrol.lakeshore.lsci":
                name = "LS_" + self.process_name.split(" ")[2].upper()
                commanding_port = ctrl_settings[name]["COMMANDING_PORT"]
                monitoring_port = ctrl_settings[name]["MONITORING_PORT"]

            else:
                commanding_port = ctrl_settings.COMMANDING_PORT
                monitoring_port = ctrl_settings.MONITORING_PORT

            # Create a socket and connect to the monitoring port

            monitoring_address = connect_address(transport, hostname, monitoring_port)
            self.monitoring_socket = zmq.Context().socket(zmq.SUB)
            self.monitoring_socket.connect(monitoring_address)
            self.monitoring_socket.setsockopt_string(zmq.SUBSCRIBE, "")

            # Address of the commanding port
            # This is needed when checking whether or not the CS is active

            self.commanding_address = connect_address(transport, hostname, commanding_port)

            self.is_socket_connected = True

        except AttributeError:

            self.is_socket_connected = False

    def stop(self):

        """ Stop the monitoring worker.

        The monitoring socket is disconnected from the monitoring port and is then closed immediately.
        """

        self.is_socket_connected = False
        self.monitoring_socket.close()

        # self.monitoring_socket.disconnect(self.monitoring_address)
        # self.monitoring_socket.close(linger=0)

    def start_process(self):
        """ Start listening on the monitoring port.

        If the Control Server is not active when the thread starts listening on the monitoring port, a signal is emitted
        to notify the GUI.
        """

        if not is_control_server_active(self.commanding_address, 0.5):

            # Emit a signal, indicating the CS is not running

            process_status = {"Name": self.process_name, "Color": Indic.RED}
            self.previous_state = Indic.RED

            self.process_status_signal.emit(process_status)

        self.run()

    @pyqtSlot()
    def run(self):
        """ Keep on listening on the monitoring port.

        If monitoring information is received before the timeout, a signal with the monitoring information is emitted.
        Otherwise, it is checked whether or not the Control Server is active.  If not, a signal is emitted with the
        process name.  Otherwise, the timeout for monitoring was too strict (and it will therefore be increased by
        0.5s).
        """

        self.active = True

        while self.is_socket_connected and self.active:

            process_status = {"Name": self.process_name}

            try:

                socket_list, _, _ = zmq.select([self.monitoring_socket], [], [], timeout=self.monitoring_timeout)

                # Monitoring information was received (before timeout)

                if self.monitoring_socket in socket_list:

                    pickle_string = self.monitoring_socket.recv()
                    monitoring_info = pickle.loads(pickle_string)

                    # Update the timeout, to be more in line with the monitoring
                    # frequency of the CS (i.e. the delay).  Take 0.5s extra to be
                    # on the safe side.

                    self.monitoring_timeout = monitoring_info["delay"] / 1000.0 + 0.5    # [s]

                    # Running core CS

                    if self.process_name in ["Logger", "Storage", "Configuration Manager", "Process Manager",
                                             "Synoptics Manager"]:
                        process_status["Color"] = Indic.GREEN

                    # Running device CS

                    else:
                        process_status["Color"], process_status["Simulator"] = self.get_device_process_status()

                        if not issubclass(self.proxy_type_as_type, DeviceInterface):
                            process_status.pop("Simulator")

                    if self.previous_state != process_status["Color"]:

                        self.process_status_signal.emit(process_status)
                        self.previous_state = process_status["Color"]

            except zmq.ZMQError:
                pass

            # Timeout occurred

            else:

                # The CS is not active

                if not is_control_server_active(endpoint=self.commanding_address, timeout=10):

                    process_status["Color"] = Indic.RED

                    if self.previous_state != process_status["Color"]:

                        self.process_status_signal.emit(process_status)
                        self.previous_state = process_status["Color"]

                    elif self.start_stop_cs_button_clicked:

                        self.process_status_signal.emit(process_status)
                        self.previous_state = process_status["Color"]
                        self.start_stop_cs_button_clicked = False

                # The CS is active, but the timeout was too strict

                else:
                    self.monitoring_timeout += 0.5

    def get_device_process_status(self):
        """ Determine the status of the device Control Server.

        Returns:
            - color: Colour of the led light (to use in the process widget).
            - is_simulator: Whether or not the Control Server is running in simulator mode.
        """

        color = Indic.BLACK
        is_simulator = False

        # Core process -> green

        try:

            with find_class(self.proxy_type)(*self.device_args) as process_proxy:

                # CS that are supposed to connect to a H/W unit (controller)

                if isinstance(process_proxy, DeviceInterface):

                    try:

                        # CS connected to Controller -> green

                        if process_proxy.is_connected():
                            color = Indic.GREEN

                        # CS not connected to Controller -> orange

                        else:
                            color = Indic.ORANGE

                    except AttributeError:
                        color = Indic.GREEN

                    is_simulator = process_proxy.is_simulator()

                # CS that do not control any device (e.g. FDIR, alert manager, etc.)

                else:
                    color = Indic.GREEN
                    is_simulator = False

        except ConnectionError:
            pass

        return color, is_simulator


class ProcessMonitoringWorker(QObject):
    """ Worker for monitoring the status of a process."""

    is_running_signal = pyqtSignal(bool)

    def __init__(self, module):
        """ Worker for monitoring the status of a process.

        Args:
            - module
        """

        super(ProcessMonitoringWorker, self).__init__()

        self.active = False
        self.start_stop_cs_button_clicked = False

        self.was_running_before = None

        self.module = importlib.import_module(module)

    def start_process(self):
        """ Start listening on the monitoring port.

        If the Control Server is not active when the thread starts listening on the monitoring port, a signal is emitted
        to notify the GUI.
        """

        self.run()

    @pyqtSlot()
    def run(self):
        """ Keep on asking for the status of the status of the process.

        Every 5s, ask for the status of the process.  If this changes w.r.t. of they way it was before, a signal is
        emitted with the current status.
        """

        self.active = True
        last_time = time.time()

        while self.active:

            if time.time() - last_time >= 5:

                is_running = self.module.send_request("status").get("status") == "ACK"

                if is_running != self.was_running_before:
                    self.was_running_before = is_running
                    self.is_running_signal.emit(is_running)

                elif self.start_stop_cs_button_clicked:

                    for index in range(15):

                        # Check (max 15x) to see whether pressing the button had an effect

                        is_running = self.module.send_request("status").get("status") == "ACK"
                        if self.was_running_before != is_running:
                            break
                        time.sleep(2)

                        self.was_running_before = is_running
                        self.start_stop_cs_button_clicked = False
                        self.is_running_signal.emit(is_running)

                last_time = time.time()

            else:
                time.sleep(0.1)


class ProcessWidget(QGroupBox):

    def __init__(self, process_name, process_info, parent, include_start_stop_button=True):
        """ Initialisation of a process widget.

        For a Control Server with the given process name and Proxy type, a process widget is created.  This widget will
        comprise the following components:

            - status LED;
            - process name;
            - button to start the GUI for the Control Server (if this has been
              configured in the YAML file with the "UserInterface" entry);
            - button to start / shut down the Control Server (for devices only).

        Args:
            - process_name: Name of the process (to display on the widget).
            - proxy_type: Type of Proxy (to check the status of the process).
        """

        super().__init__()

        self.process_name = process_name
        self.proxy_type = process_info[0]
        self.proxy_type_as_type = find_class(self.proxy_type[7:])
        self.device_args = process_info[1]
        self.is_simulator_mode = False
        self.is_device = True

        self.parent = parent

        layout = QGridLayout()

        index = 0

        # Status LED

        self.status_led = LED(parent=self)
        layout.addWidget(self.status_led, 0, index)
        index += 1

        # Process name

        self.process_name_label = QLabel(process_name)
        layout.addWidget(self.process_name_label, 0, index)
        layout.setColumnStretch(index, 1)   # Push LED and name to the left and buttons to the right
        index += 1

        # Fire up (default) GUI

        self.show_gui_button = TouchButton(name=f"Open the GUI for the {self.process_name}.",
                                           status_tip=f"Open the GUI for the {self.process_name}.",
                                           selected=get_resource(":/icons/user-interface.svg")
                                           )
        self.show_gui_button.setFixedSize(30, 30)
        self.show_gui_button.clicked.connect(self.start_gui)

        module_name = self.proxy_type[7:].rsplit(".", 1)[0]
        module = importlib.import_module(module_name)

        if not process_name.startswith("AEU") or process_name == "AEU cRIO":

            if hasattr(module, "DEVICE_SETTINGS") and hasattr(module.DEVICE_SETTINGS, "UserInterface"):
                layout.addWidget(self.show_gui_button, 0, index)
            elif hasattr(module, "COMMAND_SETTINGS") and hasattr(module.COMMAND_SETTINGS, "UserInterface"):
                layout.addWidget(self.show_gui_button, 0, index)

        index += 1

        # Shut down / re-start

        if include_start_stop_button:

            self.start_stop_button = ToggleButton(name=f"Start / shut down the {self.process_name} control server.",
                                                  status_tip=f"Start / shut down the {self.process_name} control server.",
                                                  selected=get_resource(":/images/play-button.svg"),
                                                  not_selected=get_resource(":/images/stop-button.svg"),
                                                  disabled=[get_resource(":/icons/busy.svg"),
                                                            get_resource(":/icons/busy.svg")]
                                                  )
            self.start_stop_button.clicked.connect(self.start_stop_cs)

            layout.addWidget(self.start_stop_button, 0, index)
            index += 1

            if issubclass(self.proxy_type_as_type, DeviceInterface):
                self.sim_option_button = ToggleButton(name=f"Operational vs. simulator mode",
                                                      status_tip=f"Indicate whether you want to start the "
                                                                 f"{self.process_name} Control Server in operational or in "
                                                                 f"simulator mode.",
                                                      selected=get_resource(":/icons/sim-mode.svg"),
                                                      not_selected=get_resource(":/icons/ops-mode.svg"),
                                                      disabled=[get_resource(":/icons/sim-mode.svg"),
                                                                get_resource(":/icons/ops-mode.svg")]
                                                      )
                self.sim_option_button.set_selected(False)  # Default: operational mode
            else:
                self.sim_option_button = ToggleButton(name=f"Operational vs. simulator mode",
                                                      status_tip=f"The {self.process_name} Control Server can only be "
                                                                 f"started in operational mode.",
                                                      selected=get_resource(":/icons/ops-mode.svg"),
                                                      not_selected=get_resource(":/icons/ops-mode.svg"),
                                                      disabled=[get_resource(":/icons/ops-mode.svg"),
                                                                get_resource(":/icons/ops-mode.svg")]
                                                      )
                self.is_device = False
            self.sim_option_button.clicked.connect(self.set_cs_start_mode)

            if self.process_name == "DAQ":

                self.start_stop_button.setToolTip(f"Start / shut down the {self.process_name} control server and its "
                                                  f"data acquisition.")
                self.sim_option_button.setEnabled(False)    # Only in operational mode
                self.sim_option_button.setStatusTip(f"The {self.process_name} and its data acquisition can only be"
                                                    f"started in operational mode.")

            layout.addWidget(self.sim_option_button, 0, index)
            index += 1

        self.setLayout(layout)

    def start_gui(self):
        """ Starting the default GUI for the process."""

        LOGGER.debug(f"Starting GUI for {self.process_name}")

        module_name = self.proxy_type[7:].rsplit(".", 1)[0]
        module = importlib.import_module(module_name)

        if hasattr(module, "DEVICE_SETTINGS") and hasattr(module.DEVICE_SETTINGS, "UserInterface"):
            gui_type = module.DEVICE_SETTINGS.UserInterface     # Device CS
        elif hasattr(module, "COMMAND_SETTINGS") and hasattr(module.COMMAND_SETTINGS, "UserInterface"):
            gui_type = module.COMMAND_SETTINGS.UserInterface    # Core CS
        else:   # No GUI defined in the YAML file of the CS
            LOGGER.debug(f"No GUI available for {self.process_name}")
            return
        if module_name == "egse.tempcontrol.lakeshore.lsci":
            index = self.process_name.split(" ")[2]
            gui_process = SubProcess("MyApp", [sys.executable, "-m", gui_type, "--index", index])
            gui_process.execute(detach_from_parent=True)
        else:
            gui_process = SubProcess("MyApp", [sys.executable, "-m", gui_type])
            gui_process.execute(detach_from_parent=True)

    def set_cs_start_mode(self):
        """ Change the start mode for the Control Server.

        Change the start mode for the Control Server from simulator mode to operational mode, or vice versa.
        """
        self.is_simulator_mode = not self.is_simulator_mode

    def start_stop_cs(self):
        """ Start or shut down the Control Server.

        Depending on the current state of the Control Server, it will either be started or shut down.
        """

        self.sim_option_button.setEnabled(False)
        self.start_stop_button.setDisabled(True)

        if self.start_stop_button.is_selected():

            LOGGER.info(f"Shut down the {self.process_name} Control Server")
            thread = threading.Thread(target=self.stop_cs)

        else:

            LOGGER.info(f"Start the {self.process_name} Control Server")
            thread = threading.Thread(target=self.start_cs)

        thread.daemon = True
        thread.start()

        # Let the main UI window know that the start/stop button has been clicked
        self.parent.on_start_stop_cs_button_clicked(self.process_name)

    def start_cs(self):

        try:

            with ProcessManagerProxy() as pm:

                response: Response = pm.start_cs(self.process_name, self.is_simulator_mode)
                if response.successful:
                    self.sim_option_button.setDisabled(True)
                else:
                    self.sim_option_button.setEnabled(True)

                    gui_process = SubProcess("MyApp", [sys.executable, "-m", "egse.procman.cannot_start_process_popup",
                                                       "--process_name", f"{self.process_name} Control Server",
                                                       "--message", response.message])
                    gui_process.execute(detach_from_parent=True)

                return response

        #
        #         try:
        #             pm.start_cs(self.process_name, self.is_simulator_mode)
        #             self.sim_option_button.setDisabled(True)
        #
        #         except ConnectionError:
        #             LOGGER.info(f"Could not start Control Server for {self.process_name}")
        #             self.sim_option_button.setEnabled(True)
        #
        except ConnectionError as exc:

            message = f"Lost connection to Process Manager"
            LOGGER.critical(message, exc_info=True)

            self.sim_option_button.setEnabled(True)
            self.start_stop_button.setEnabled(True)
            self.start_stop_button.set_selected(True)

            return Failure(message, cause=exc)

    def stop_cs(self):

        try:
            with ProcessManagerProxy() as pm:
                LOGGER.info(f"PM: shut down {self.process_name}")
                pm.shut_down_cs(self.process_name)
                self.sim_option_button.setDisabled(False)

        except ConnectionError:

            LOGGER.critical(f"Lost connection to Process Manager")
            self.sim_option_button.setEnabled(True)

    def set_led_color(self, color: int):
        """ Set the colour of the LED, representing the status of the process.

        The meaning of the colours is the following:

                - green:
                    - core process with running Control Server;
                    - device process in simulator mode with running Control Server;
                    - device process in operational mode with running Control Server and connection to the Controller;
                - orange: device process in operational mode with Control Server running but without connection to the
                  Controller;
                - red: no Control Server running.

        Args:
            - color: Integer representing the colour to indicate the process status.  Should only be Indic.GREEN,
                     Indic.ORANGE, or Indic.RED.
        """

        self.status_led.set_color(color)

        try:
            self.start_stop_button.setDisabled(False)
        except AttributeError:
            # Core processes don't have this button
            pass

        if color != Indic.RED:
            try:
                self.sim_option_button.setEnabled(False)
                self.start_stop_button.set_selected(False)
            except AttributeError:
                # Core processes don't have this button
                pass

        else:
            try:
                self.sim_option_button.setEnabled(True)
                self.start_stop_button.set_selected(True)
            except AttributeError:
                # Core processes don't have this button
                pass

    def is_simulator_mode(self):
        """ Check whether the simulator mode checkbox was checked.

        Returns: True of the simulator mode checkbox was checked; False otherwise.
        """

        return self.sim_option_button.is_selected()


class NonCSProcessWidget(QGroupBox):

    def __init__(self, process_name, parent, include_gui_button=True, include_start_stop_button=True):
        """ Initialisation of a process widget.

        For a Control Server with the given process name and Proxy type, a process widget is created.  This widget will
        comprise the following components:

            - status LED;
            - process name;
            - button to start the GUI for the process;
            - button to start / shut down the process.

        Args:
            - process_name: Name of the process (to display on the widget).
        """

        super().__init__()

        self.process_name = process_name
        self.parent = parent

        layout = QGridLayout()

        index = 0

        # Status LED

        self.status_led = LED(parent=self)
        layout.addWidget(self.status_led, 0, index)
        index += 1

        # Process name

        self.process_name_label = QLabel(process_name)
        layout.addWidget(self.process_name_label, 0, index)
        layout.setColumnStretch(index, 1)  # Push LED and name to the left and buttons to the right
        index += 1

        # Fire up (default) GUI

        if include_gui_button:

            self.show_gui_button = TouchButton(name=f"Open the GUI for the {self.process_name}.",
                                               status_tip=f"Open the GUI for the {self.process_name}.",
                                               selected=get_resource(":/icons/user-interface.svg")
                                               )
            self.show_gui_button.setFixedSize(30, 30)
            layout.addWidget(self.show_gui_button, 0, index)
            self.show_gui_button.clicked.connect(self.start_gui)

            index += 1

        # Shut down / re-start

        if include_start_stop_button:

            self.start_stop_button = ToggleButton(name=f"Start / shut down the {self.process_name}.",
                                                  status_tip=f"Start / shut down the {self.process_name}.",
                                                  selected=get_resource(":/images/play-button.svg"),
                                                  not_selected=get_resource(":/images/stop-button.svg"),
                                                  disabled=[get_resource(":/icons/busy.svg"),
                                                            get_resource(":/icons/busy.svg")]
                                                  )
            self.start_stop_button.clicked.connect(self.start_stop_service)
            layout.addWidget(self.start_stop_button, 0, index)
            index += 1

        self.setLayout(layout)

    def start_stop_service(self):

        self.start_stop_button.setDisabled(True)

        if self.start_stop_button.is_selected():

            print(f"Stopping {self.process_name}")
            LOGGER.info(f"Shut down the {self.process_name}")
            thread = threading.Thread(target=self.stop_service)

        else:

            print(f"Starting {self.process_name}")
            LOGGER.info(f"Start the {self.process_name}")
            thread = threading.Thread(target=self.start_service)

        thread.daemon = True
        thread.start()

        self.parent.on_start_stop_non_cs_process_button_clicked(self.process_name)

    # def start_gui(self):
    #     """ Starting the default GUI for the process."""
    #
    #     LOGGER.debug(f"Starting GUI for {self.process_name}")
    #     print("Starting GUI")

    def set_led_color(self, color: int):
        """ Set the colour of the LED, representing the status of the process.

        The meaning of the colours is the following:

            - green: process running;
            - red: process not running.

        Args:
            - color: Integer representing the colour to indicate the process status.  Should only be Indic.GREEN,
                     or Indic.RED.
        """

        self.status_led.set_color(color)

        try:
            self.start_stop_button.setDisabled(False)
            self.start_stop_button.set_selected(color == Indic.RED)
        except AttributeError:
            # The logger doesn't have a start/stop button
            pass


class LogWidget(NonCSProcessWidget):

    def __init__(self, parent):

        super().__init__("Logger", parent, include_gui_button=True, include_start_stop_button=False)

    def start_gui(self):

        gui_process = SubProcess("MyApp", [sys.executable, "-m", "cutelog"])
        gui_process.execute(detach_from_parent=True)


class FitsgenWidget(NonCSProcessWidget):

    def __init__(self, parent):

        super(FitsgenWidget, self).__init__(FILE_GENERATION_PROCESS_NAMES.FITSGEN, parent, include_gui_button=True,
                                            include_start_stop_button=True)

    def start_gui(self):

        gui_process = SubProcess("MyApp", [sys.executable, "-m", "egse.dpu.fitsgen_ui"])
        gui_process.execute(detach_from_parent=True)

    def start_service(self):

        response: Response = start_fitsgen()

        if not response.successful:
            gui_process = SubProcess("MyApp", [sys.executable, "-m", "egse.procman.cannot_start_process_popup",
                                               "--process_name", "FITS generation", "--message", response.message])
            gui_process.execute(detach_from_parent=True)

    def stop_service(self):

        stop_fitsgen()


class FovHkWidget(NonCSProcessWidget):

    def __init__(self, parent):

        super(FovHkWidget, self).__init__(FILE_GENERATION_PROCESS_NAMES.FOV_HK, parent, include_gui_button=False,
                                          include_start_stop_button=True)

    def start_service(self):

        response: Response = start_fov_hk()

        if not response.successful:
            gui_process = SubProcess("MyApp", [sys.executable, "-m", "egse.procman.cannot_start_process_popup",
                                               "--process_name", "FOV HK generation", "--message", response.message])
            gui_process.execute(detach_from_parent=True)

    def stop_service(self):

        stop_fov_hk()


class NFeeHkWidget(NonCSProcessWidget):

    def __init__(self, parent):

        super(NFeeHkWidget, self).__init__(FILE_GENERATION_PROCESS_NAMES.N_FEE_HK, parent, include_gui_button=False,
                                           include_start_stop_button=True)

    def start_service(self):

        response: Response = start_n_fee_hk()

        if not response.successful:
            gui_process = SubProcess("MyApp", [sys.executable, "-m", "egse.procman.cannot_start_process_popup",
                                               "--process_name", "N-FEE HK generation", "--message", response.message])
            gui_process.execute(detach_from_parent=True)

    def stop_service(self):

        stop_n_fee_hk()


def start_fitsgen():
    """ Start the FITS generation."""

    with ProcessManagerProxy() as pm:
        return pm.start_fitsgen()


def stop_fitsgen():
    """ Stop the FITS generation."""

    with ProcessManagerProxy() as pm:
        pm.stop_fitsgen()


def start_fov_hk():
    """ Start the generation of FOV HK."""

    with ProcessManagerProxy() as pm:
        return pm.start_fov_hk()


def stop_fov_hk():
    """ Stop the generation of FOV HK"""

    with ProcessManagerProxy() as pm:
        pm.stop_fov_hk()


def start_n_fee_hk():
    """ Start the generation of N-FEE HK."""

    with ProcessManagerProxy() as pm:
        return pm.start_n_fee_hk()


def stop_n_fee_hk():
    """ Stop the generation of N-FEE HK."""

    with ProcessManagerProxy() as pm:
        pm.stop_n_fee_hk()


def start_egse():
    """ Start all device Control Servers in one go."""

    with ProcessManagerProxy() as pm:
        pm.start_egse()


def stop_egse():
    """ Stop all device Control Servers in one go."""

    with ProcessManagerProxy() as pm:
        pm.shut_down_egse()

def open_th_ui():
    """ Open the TH Operator UI."""

    sitehash = {
        "CSL": get_csl_ui_process,
        "CSL1": get_csl_ui_process,
        "CSL2": get_csl_ui_process,
        "IAS": get_ias_ui_process,
        "INTA": get_inta_ui_process,
        "SRON": get_sron_ui_process,
    }

    gui_process = sitehash[SITE.ID]()
    gui_process.execute(detach_from_parent=True)


def get_csl_ui_process():
    return SubProcess("MyApp", ["csl_ui"])


def get_sron_ui_process():
    return SubProcess("MyApp", ["sron_ui"])


def get_ias_ui_process():
    return SubProcess("MyApp", ["ias_ui"])


def get_inta_ui_process():
    return SubProcess("MyApp", ["inta_ui"])


def open_fov_ui():
    """ Open the FOV UI."""

    gui_process = SubProcess("MyApp", ["fov_ui"])
    gui_process.execute(detach_from_parent=True)


def open_visited_positions_ui():
    """ Open the visited-positions UI."""

    gui_process = SubProcess("MyApp", ["visited_positions_ui"])
    gui_process.execute(detach_from_parent=True)


class ProcessManagerUIView(QMainWindow):

    def __init__(self):
        """ Initialisation of the Process Manager GUI.

        The components are placed in the window and threads are created for all processes, to be able to check for
        updates in the process status (in the background) and display these in the GUI.
        """

        super().__init__()

        self.setGeometry(300, 300, 1000, 1000)
        self.setWindowTitle("Process Manager")

        self.processes = {}
        self.devices = {}

        try:

            with ProcessManagerProxy() as process_manager_proxy:

                self.core = process_manager_proxy.get_core()        # Core

        except ConnectionError:

            self.core = {}

        self.monitoring_threads = {}
        self.monitoring_workers = {}

        self.process_widgets = {}

        self.process_widgets_core = {}

        self.setup_monitoring_thread = QThread(self)
        self.setup_monitoring_worker = ConfigurationMonitoringWorker()
        self.setup_monitoring_worker.moveToThread(self.setup_monitoring_thread)

        # What to do when information has been received on the monitoring
        # port before timeout?

        self.setup_monitoring_worker.setup_changed_signal.connect(self.on_setup_changed_signal)
        self.setup_monitoring_worker.obsid_changed_signal.connect(self.on_obsid_changed_signal)
        self.setup_monitoring_thread.started.connect(self.setup_monitoring_worker.start_process)
        self.setup_monitoring_thread.start()

        # Build up the GUI

        self.init_ui()

        # Keep an eye on the logger

        self.logger_monitoring_thread = QThread(self)
        self.logger_monitoring_worker = ProcessMonitoringWorker("egse.logger.log_cs")
        self.logger_monitoring_worker.moveToThread(self.logger_monitoring_thread)
        self.logger_monitoring_worker.is_running_signal.connect(self.on_logger_is_running_signal)
        self.logger_monitoring_thread.started.connect(self.logger_monitoring_worker.start_process)
        self.logger_monitoring_thread.start()

        # Keep an eye on the FITS generation

        self.fitsgen_monitoring_thread = QThread(self)
        self.fitsgen_monitoring_worker = ProcessMonitoringWorker("egse.dpu.fitsgen")
        self.fitsgen_monitoring_worker.moveToThread(self.fitsgen_monitoring_thread)
        self.fitsgen_monitoring_worker.is_running_signal.connect(self.on_fitsgen_is_running_signal)
        self.fitsgen_monitoring_thread.started.connect(self.fitsgen_monitoring_worker.start_process)
        self.fitsgen_monitoring_thread.start()

        # Keep an eye on the generation of FOV HK

        self.fov_hk_monitoring_thread = QThread(self)
        self.fov_hk_monitoring_worker = ProcessMonitoringWorker("egse.fov.fov_hk")
        self.fov_hk_monitoring_worker.moveToThread(self.fov_hk_monitoring_thread)
        self.fov_hk_monitoring_worker.is_running_signal.connect(self.on_fov_hk_is_running_signal)
        self.fov_hk_monitoring_thread.started.connect(self.fov_hk_monitoring_worker.start_process)
        self.fov_hk_monitoring_thread.start()

        # Keep an eye on the generation of N-FEE HK

        self.n_fee_hk_monitoring_thread = QThread(self)
        self.n_fee_hk_monitoring_worker = ProcessMonitoringWorker("egse.fee.n_fee_hk")
        self.n_fee_hk_monitoring_worker.moveToThread(self.n_fee_hk_monitoring_thread)
        self.n_fee_hk_monitoring_worker.is_running_signal.connect(self.on_n_fee_hk_is_running_signal)
        self.n_fee_hk_monitoring_thread.started.connect(self.n_fee_hk_monitoring_worker.start_process)
        self.n_fee_hk_monitoring_thread.start()

        self.file_generation_monitoring_workers = {
            FILE_GENERATION_PROCESS_NAMES.FITSGEN: self.fitsgen_monitoring_worker,
            FILE_GENERATION_PROCESS_NAMES.FOV_HK: self.fov_hk_monitoring_worker,
            FILE_GENERATION_PROCESS_NAMES.N_FEE_HK: self.n_fee_hk_monitoring_worker
        }

    def init_ui(self):
        """ Put the components in the GUI window.

        The GUI comprises the following components:

            - the toolbar;
            - on the left-hand side: one process widget per process;
            - on the right-hand side: one tab per process.
        """

        # Creating the content

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        self.create_toolbar()
        self.create_statusbar()

        scroll = QScrollArea()
        # widget_frame = QFrame()

        hbox = QHBoxLayout()
        vbox_left = QVBoxLayout()
        vbox_right = QVBoxLayout()
        hbox.addLayout(vbox_left)
        hbox.addLayout(vbox_right)

        vbox_right.addStretch()

        app_frame.setLayout(hbox)

        # Obsid

        info_gridbox = QGridLayout()

        self.obsid = QLabel("No observation is running")
        self.setStyleSheet('QMainWindow{border: 3px solid green;}')
        info_gridbox.addWidget(QLabel("Obsid:"), 0, 0)
        info_gridbox.addWidget(self.obsid, 0, 1)


        self.setup_id = QLabel("No setup loaded")
        info_gridbox.addWidget(QLabel("Setup ID:"), 1, 0)
        info_gridbox.addWidget(self.setup_id, 1, 1)

        self.camera_id = QLabel("Camera ID unknown")
        info_gridbox.addWidget(QLabel("Camera ID:"), 2, 0)
        info_gridbox.addWidget(self.camera_id, 2, 1)

        self.csl_hexapod_id = QLabel("Hexapod ID unknown")
        if "CSL" in SITE.ID:
            info_gridbox.addWidget(QLabel("Hexapod ID:"), 3, 0)
            info_gridbox.addWidget(self.csl_hexapod_id, 3, 1)

        vbox_left.addLayout(info_gridbox)
        vbox_left.addWidget(QLabel())

        self.overview_widget_device_cs_layout = QVBoxLayout()
        self.overview_widget_device_cs_layout.addStretch()
        self.overview_widget_device_cs = QGroupBox("Device Control Servers", self)
        self.overview_widget_device_cs.setLayout(self.overview_widget_device_cs_layout)
        self.overview_widget_device_cs.setToolTip(
            "EGSE device control servers:\n" +
            "can be started in this GUI or on the command line.")

        self.overview_widget_non_device_cs_layout = QVBoxLayout()
        self.overview_widget_non_device_cs_layout.addStretch()
        self.overview_widget_non_device_cs = QGroupBox("Non-Device Control Servers", self)
        self.overview_widget_non_device_cs.setLayout(self.overview_widget_non_device_cs_layout)
        self.overview_widget_non_device_cs.setToolTip(
            "EGSE non-device control servers:\n" +
            "can be started in this GUI or on the command line (operational mode only).")

        self.create_overview_widget_core()
        vbox_left.addWidget(self.overview_widget_core)

        self.create_overview_widget_file_services()
        vbox_left.addWidget(self.overview_widget_file_services)

        vbox_right.addWidget(self.overview_widget_device_cs)
        vbox_left.addWidget(self.overview_widget_non_device_cs)

        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)

        scroll.setWidget(app_frame)
        self.setCentralWidget(scroll)

    def start_monitoring(self) -> object:
        """ Start listening on the monitoring port.

        Create and start a thread that listens on the monitoring port in the background.  If information is received
        before timeout, the Control Server is running: the light in the process tab should be set to green or orange,
        and the process information should be updated in the process tab.
        """

        for process_name, process_info in self.processes.items():

            self.monitoring_threads[process_name] = QThread()

            self.monitoring_workers[process_name] = MonitoringWorker(process_name, process_info)
            self.monitoring_workers[process_name].moveToThread(self.monitoring_threads[process_name])

            # What to do when information has been sent back from the process thread?

            self.monitoring_workers[process_name].process_status_signal.connect(self.on_process_status_signal)

            self.monitoring_threads[process_name].started.connect(
                self.monitoring_workers[process_name].start_process)

            self.monitoring_threads[process_name].start()

    def on_setup_changed_signal(self, setup: Setup):
        """ Re-build the GUI after a change in setup.

        Args:
            - setup: New setup.
        """

        # self.all_aeu_cs_button.disable()
        # self.start_aeu_button.setDisabled(True)
        # self.stop_aeu_button.setDisabled(True)

        # Stop all workers and threads

        for process_name in self.processes.keys():

            self.monitoring_workers[process_name].process_status_signal.disconnect()

            self.monitoring_workers[process_name].stop()
            self.monitoring_threads[process_name].quit()

        for process_name in self.processes.keys():
            self.monitoring_threads[process_name].wait()

        self.monitoring_workers.clear()
        self.monitoring_threads.clear()

        # Make process list

        self.processes.clear()
        self.core.clear()
        self.devices.clear()

        self.start_aeu_button.setVisible(False)
        self.stop_aeu_button.setVisible(False)

        # Remove the widgets from the layouts

        while self.overview_widget_device_cs_layout.count():

            widget = self.overview_widget_device_cs_layout.takeAt(0).widget()

            if widget is not None:
                widget.deleteLater()

        while self.overview_widget_non_device_cs_layout.count():

            widget = self.overview_widget_non_device_cs_layout.takeAt(0).widget()

            if widget is not None:
                widget.deleteLater()

        self.process_widgets.clear()

        # Re-build the process list

        try:

            with ProcessManagerProxy() as process_manager_proxy:

                self.core = process_manager_proxy.get_core()
                self.devices = process_manager_proxy.get_devices()

                self.processes.update(self.core)
                self.processes.update(self.devices)

        except ConnectionError:

            self.core = {}
            self.devices = {}

        # Make new process widgets

        for process_name in self.devices.keys():

            process_widget = ProcessWidget(process_name, self.devices[process_name], self)

            self.process_widgets[process_name] = process_widget

            if process_widget.is_device:
                self.overview_widget_device_cs_layout.addWidget(process_widget)
            else:
                self.overview_widget_non_device_cs_layout.addWidget(process_widget)

        self.process_widgets.update(self.process_widgets_core)

        # Make sure the boxes stay nicely together when vertically resizing

        self.overview_widget_device_cs_layout.addStretch()
        self.overview_widget_non_device_cs_layout.addStretch()

        # Start monitoring the process status

        self.start_monitoring()

        if "AEU cRIO" in self.devices.keys():

            # self.all_aeu_cs_button.set_selected(False)
            # self.all_aeu_cs_button.enable()
            self.start_aeu_button.setEnabled(True)
            self.stop_aeu_button.setEnabled(True)

        else:

            # self.all_aeu_cs_button.set_selected(False)
            # self.all_aeu_cs_button.disable()
            self.start_aeu_button.setEnabled(False)
            self.stop_aeu_button.setEnabled(False)

        self.setup_id.setText(f"{setup.get_id()}")

        try:
            cam_id = setup.camera.ID
            if cam_id != "EM":
                self.camera_id.setToolTip("Ah, beer!  The cause of and the solution to all of life's problems!")
            self.camera_id.setText(cam_id)
        except AttributeError:
            self.camera_id.setText("Camera ID unknown")

        try:
            self.csl_hexapod_id.setText(str(setup.gse.hexapod.ID))
        except AttributeError:
            self.csl_hexapod_id.setText("Hexapod ID unknown")

    def on_obsid_changed_signal(self, obsid: ObservationIdentifier):
        """ Update the GUI for the new obsid.

        Args:
            - obsid: The new obsid.
        """

        if obsid is None:

            self.obsid.setText("No observation is running")
            self.setStyleSheet('QMainWindow{border: 3px solid green;}')

        else:

            self.obsid.setText(str(obsid))
            self.setStyleSheet('QMainWindow{border: 3px solid red;}')

    def on_process_status_signal(self, process_info):
        """ Update the GUI for the process with the given name.

        This method is called to update the GUI for the process with the given name in case the Control Server is
        running:

            - the colour of the light in the process widget is set to green or orange;
            - the process information is updated in the tab.

        The meaning of the colours is the following:

            - green:
                - core process with running Control Server;
                - device process in simulator mode with running Control Server;
                - device process in operational mode with running Control Server and connection to the Controller;
            - orange: device process in operational mode with Control Server running but without connection to the
              Controller.


        Args:
            process_info: Information for one process, to be updated in the
                          Process Manager GUI.
        """

        process_name = process_info["Name"]
        color = process_info["Color"]

        widget = self.process_widgets[process_name]

        # Update the process widget

        if "Simulator" in process_info:

            if process_name != "DPU":

                try:
                    widget.sim_option_button.set_selected(process_info["Simulator"])
                except TypeError:
                    # See #1419
                    widget.sim_option_button.set_selected(False)
                    LOGGER.debug(f"Unchecking the simulator checkbox in PM UI for {process_name}")

                widget.sim_option_button.button_disabled = widget.sim_option_button.button_selected \
                    if widget.sim_option_button.is_selected() \
                    else widget.sim_option_button.button_disabled
                widget.sim_option_button.setDisabled(True)

        widget.set_led_color(color)

        if process_name == "Configuration Manager" and color == Indic.RED:

            self.obsid.setText("Obsid unknown")
            self.setStyleSheet('QMainWindow{border: 3px solid orange;}')

    def on_start_stop_cs_button_clicked(self, process_name):

        self.monitoring_workers[process_name].start_stop_cs_button_clicked = True

    def on_start_stop_non_cs_process_button_clicked(self, process_name):

        self.file_generation_monitoring_workers[process_name].start_stop_cs_button_clicked = True

    def on_logger_is_running_signal(self, logger_is_running: bool):

        if logger_is_running:
            self.logger_widget.set_led_color(Indic.GREEN)
        else:
            self.logger_widget.set_led_color(Indic.RED)

    def on_fitsgen_is_running_signal(self, fitsgen_is_running: bool):
        """ Update the icon of the toolbar button for FITS generation.

        Args:
            - fitsgen_is_running: Indicates whether or not the FITS generation is running.
        """

        if fitsgen_is_running:
            self.fitsgen_widget.set_led_color(Indic.GREEN)
        else:
            self.fitsgen_widget.set_led_color(Indic.RED)

        self.fitsgen_widget.start_stop_button.set_selected(not fitsgen_is_running)

    def on_fov_hk_is_running_signal(self, fov_hk_is_running: bool):
        """ Update the icon of the toolbar button for the generation of FOV HK.

        Args:
            - fov_hk_is_running: Indicates whether or not the generation of FOV HK is running.
        """

        if fov_hk_is_running:
            self.fov_hk_widget.set_led_color(Indic.GREEN)
        else:
            self.fov_hk_widget.set_led_color(Indic.RED)

        self.fov_hk_widget.start_stop_button.set_selected(not fov_hk_is_running)

    def on_n_fee_hk_is_running_signal(self, n_fee_hk_is_running: bool):
        """ Update the icon of the toolbar button for the generation of N-FEE HK.

        Args:
            - n_fee_hk_is_running: Indicates whether or not the generation of N-FEE HK is running.
        """

        if n_fee_hk_is_running:
            self.n_fee_hk_widget.set_led_color(Indic.GREEN)
        else:
            self.n_fee_hk_widget.set_led_color(Indic.RED)

        self.n_fee_hk_widget.start_stop_button.set_selected(not n_fee_hk_is_running)

    def set_process_list(self):
        """ Make dictionary with all processes (core + devices).

        The Configuration Manager is asked which processes (core + devices) are included in the setup.
        """

        self.processes = {}

        # Ask the CM which CS are included in the setup

        try:

            with ProcessManagerProxy() as process_manager_proxy:

                self.core = process_manager_proxy.get_core()        # Core
                self.devices = process_manager_proxy.get_devices()  # Devices

                self.processes.update(self.core)
                self.processes.update(self.devices)

        except ConnectionError:

            self.devices = {}
            self.core = {}

    def create_toolbar(self):
        """ Create the toolbar.

        Buttons with the following functionality are foreseen:
            - Start/stop all EGSE device Control Servers in one go;
            - Start/stop all AEU Control Servers in one go:
            - Start/stop the FITS generation;
            - Start/stop the generation of FOV HK;
            - Start/stop the generation of N-FEE HK.
        """

        self.start_egse_button = ToggleButton(name="Start all device control servers in one go.",
                                              status_tip="Start all device control servers in one go.",
                                              selected=get_resource(":/icons/play-green.svg"),
                                              not_selected=get_resource(":/icons/play-green.svg")
                                              )
        self.start_egse_button.clicked.connect(self.start_egse)
        self.stop_egse_button = ToggleButton(name="Start all device control servers in one go.",
                                             status_tip="Stop all device control servers in one go.",
                                             selected=get_resource(":/icons/stop-red.svg"),
                                             not_selected=get_resource(":/icons/stop-red.svg")
                                             )
        self.stop_egse_button.clicked.connect(self.stop_egse)

        self.start_aeu_button = ToggleButton(name="Start all AEU control servers in one go.",
                                             status_tip="Start all AEU control servers in one go.",
                                             selected=get_resource(":/icons/aeu-cs-start.svg"),
                                             not_selected=get_resource(":/icons/aeu-cs-start.svg"),
                                             disabled=[get_resource(":/icons/aeu-cs.svg"),
                                                       get_resource(":/icons/aeu-cs.svg")]
                                             )
        self.start_aeu_button.clicked.connect(self.start_all_aeu_cs)

        self.stop_aeu_button = ToggleButton(name="Stop all AEU control servers in one go.",
                                            status_tip="Stop all AEU control servers in one go.",
                                            selected=get_resource(":/icons/aeu-cs-stop.svg"),
                                            not_selected=get_resource(":/icons/aeu-cs-stop.svg"),
                                            disabled=get_resource(":/icons/aeu-cs.svg")
                                            )
        self.stop_aeu_button.clicked.connect(self.stop_all_aeu_cs)

        th_ui_icon = QIcon(str(get_resource(":/icons/th_ui_logo.svg")))
        th_ui_action = QAction(th_ui_icon, f"Open the {SITE.ID} Operator UI", self)
        th_ui_action.setToolTip(f"Open the {SITE.ID} Operator UI")
        th_ui_action.setCheckable(False)
        th_ui_action.triggered.connect(open_th_ui)

        fov_ui_icon = QIcon(str(get_resource(":/icons/location-marker.svg")))  # TODO
        fov_ui_action = QAction(fov_ui_icon, "Open the FOV UI", self)
        fov_ui_action.setToolTip("Open the FOV UI")
        fov_ui_action.setCheckable(False)
        fov_ui_action.triggered.connect(open_fov_ui)

        visited_positions_ui_icon = QIcon(str(get_resource(":/icons/radar.svg")))    #TODO
        visited_positions_ui_action = QAction(visited_positions_ui_icon, "Open the visited-positions UI", self)
        visited_positions_ui_action.setToolTip("Open the visited-positions UI")
        visited_positions_ui_action.setCheckable(False)
        visited_positions_ui_action.triggered.connect(open_visited_positions_ui)

        self.toolbar = self.addToolBar("MainToolbar")
        self.toolbar.addWidget(self.start_egse_button)
        self.toolbar.addWidget(self.stop_egse_button)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.start_aeu_button)
        self.toolbar.addWidget(self.stop_aeu_button)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)

        if "CSL" in SITE.ID:
            self.toolbar.addAction(fov_ui_action)

        self.toolbar.addAction(th_ui_action)
        self.toolbar.addSeparator()

        self.toolbar.addAction(visited_positions_ui_action)

        return self.toolbar

    def create_statusbar(self):
        """ Create the status bar."""

        self.statusBar().setStyleSheet("border: 0; background-color: #FFF8DC;")
        self.statusBar().setStyleSheet("QStatusBar::item {border: none;}")
        # self.statusBar().addPermanentWidget(VLine())

    def start_egse(self):
        """ Start all EGSE device Control Servers in one go.

        We only try to start the control servers that are currently down.  For those, the following steps are taken:
            - The start/stop button of each of these control servers should show the stop icon;
            - The simulator option button is disabled;
            - The control server is started, in the mode indicated by the simulator option button.

        For the control servers that could be started, the start/stop button keeps showing the stop icon and the
        simulator mode button stays disabled.  For control servers that could not be started, the start/stop button
        show the start icon again and the simulator mode button is enabled again.
        """

        LOGGER.info(f"Starting all device Control Servers")
        thread = threading.Thread(target=self._start_egse)

        thread.daemon = True
        thread.start()

    def _start_egse(self):

        # First make sure that the start/stop buttons in the process widgets show the hourglass icon (denoting is going
        # on with that CD) and that the simulator option button is disabled (so you cannot switch between simulator and
        # operational mode while starting the CS)

        for process_name in self.devices.keys():

            process_widget: ProcessWidget = self.process_widgets[process_name]

            if process_widget.status_led.color == Indic.RED:

                process_widget.start_stop_button.setDisabled(True)
                process_widget.sim_option_button.setEnabled(False)

        # In order not to overload the Process Manager, we loop through the list of devices again and start the CS
        # one-by-one

        with ProcessManagerProxy() as pm:

            for process_name in self.devices.keys():

                if process_widget.status_led.color == Indic.RED:

                    self.monitoring_workers[process_name].start_stop_cs_button_clicked = True

                    sim_mode = self.process_widgets[process_name].is_simulator_mode
                    response: Response = pm.start_cs(process_name, sim_mode)

                    if not response.successful:
                        gui_process = SubProcess("MyApp", [sys.executable, "-m",
                                                           "egse.procman.cannot_start_process_popup", "--process_name",
                                                           process_name, "--message", response.message])
                        gui_process.execute(detach_from_parent=True)

    def stop_egse(self):
        """ Shut down all EGSE device Control Servers in one go.

        We only try to start the control servers that are currently running.  For those, the following steps are taken:
            - The start/stop button of each of these control servers should show the start icon;
            - The simulator option button is disabled;
            - The control server is stopped.

        For the control servers that could be stopped, the start/stop button keeps showing the start icon and the
        simulator mode button is enabled.  For control servers that could not be stopped, the start/stop button
        show the stop icon again and the simulator mode button is disabled again.
        """

        LOGGER.info(f"Shutting down all device Control Servers")
        thread = threading.Thread(target=self._stop_egse)

        thread.daemon = True
        thread.start()

    def _stop_egse(self):

        # First make sure that the start/stop buttons in the process widgets show the hourglass icon (denoting is going
        # on with that CD) and that the simulator option button is disabled (so you cannot switch between simulator and
        # operational mode while starting the CS)

        for process_name in self.devices.keys():

            process_widget: ProcessWidget = self.process_widgets[process_name]

            if process_widget.status_led.color != Indic.RED:

                process_widget.start_stop_button.setDisabled(True)

        # In order not to overload the Process Manager, we loop through the list of devices again and start the CS
        # one-by-one

        with ProcessManagerProxy() as pm:

            for process_name in reversed(self.devices.keys()):

                if process_widget.status_led.color != Indic.RED:

                    self.monitoring_workers[process_name].start_stop_cs_button_clicked = True
                    pm.shut_down_cs(process_name)

    def start_all_aeu_cs(self):
        """ Start the AEU Control Servers in one go."""

        thread = threading.Thread(target=self._start_all_aeu_cs)

        thread.daemon = True
        thread.start()

    def _start_all_aeu_cs(self):

        # First make sure that the start/stop buttons in the process widgets show the hourglass icon (denoting is going
        # on with that CD) and that the simulator option button is disabled (so you cannot switch between simulator and
        # operational mode while starting the CS)

        for process_name in self.devices.keys():

            if str.startswith(process_name, "AEU"):

                process_widget: ProcessWidget = self.process_widgets[process_name]

                if process_widget.status_led.color == Indic.RED:

                    process_widget.start_stop_button.setDisabled(True)
                    process_widget.sim_option_button.setEnabled(False)

        # In order not to overload the Process Manager, we loop through the list of devices again and start the CS
        # one-by-one

        with ProcessManagerProxy() as pm:

            for process_name in self.devices.keys():

                if str.startswith(process_name, "AEU"):

                    process_widget: ProcessWidget = self.process_widgets[process_name]

                    if process_widget.status_led.color == Indic.RED:

                        self.monitoring_workers[process_name].start_stop_cs_button_clicked = True

                        sim_mode = self.process_widgets[process_name].is_simulator_mode
                        response: Response = pm.start_cs(process_name, sim_mode)

                        if not response.successful:
                            gui_process = SubProcess("MyApp", [sys.executable, "-m",
                                                               "egse.procman.cannot_start_process_popup",
                                                               "--process_name", process_name,
                                                               "--message", response.message])
                            gui_process.execute(detach_from_parent=True)

    def stop_all_aeu_cs(self):
        """ Shut down the AEU Control Servers in one go."""

        thread = threading.Thread(target=self._stop_all_aeu_cs)

        thread.daemon = True
        thread.start()

    def _stop_all_aeu_cs(self):

        # First make sure that the start/stop buttons in the process widgets show the hourglass icon (denoting is going
        # on with that CD) and that the simulator option button is disabled (so you cannot switch between simulator and
        # operational mode while starting the CS)

        for process_name in self.devices.keys():

            if str.startswith(process_name, "AEU"):

                process_widget: ProcessWidget = self.process_widgets[process_name]

                if process_widget.status_led.color != Indic.RED:
                    process_widget.start_stop_button.setDisabled(True)

        # In order not to overload the Process Manager, we loop through the list of devices again and start the CS
        # one-by-one

        with ProcessManagerProxy() as pm:

            for process_name in reversed(self.devices.keys()):

                if str.startswith(process_name, "AEU"):

                    process_widget: ProcessWidget = self.process_widgets[process_name]

                    if process_widget.status_led.color != Indic.RED:

                        self.monitoring_workers[process_name].start_stop_cs_button_clicked = True
                        pm.shut_down_cs(process_name)


    # def start_stop_fitsgen(self):
    #     """ Start/stop the FITS generation.
    #
    #     Depending on the selection state of the FITS generation button, the FITS generation will be started or stopped
    #     (this is done in a separate thread).
    #     """
    #
    #     if self.fitsgen_button.is_selected():
    #         thread = threading.Thread(target=stop_fitsgen)
    #     else:
    #         thread = threading.Thread(target=start_fitsgen)
    #
    #     thread.daemon = True
    #     thread.start()
    #
    # def start_stop_fov_hk(self):
    #     """ Start/stop the generation of FOV HK.
    #
    #     Depending on the selection state of the FOV HK generation button, the FOV HK generation will be started or
    #     stopped (this is done in a separate thread).
    #     """
    #
    #     if self.fov_hk_button.is_selected():
    #         thread = threading.Thread(target=stop_fov_hk)
    #     else:
    #         thread = threading.Thread(target=start_fov_hk)
    #
    #     thread.daemon = True
    #     thread.start()
    #
    # def start_stop_n_fee_hk(self):
    #     """ Start/stop the generation of N-FEE HK.
    #
    #     Depending on the selection state of the N-FEE HK generation button, the N-FEE HK generation will be started or
    #     stopped (this is done in a separate thread).
    #     """
    #
    #     if self.n_fee_hk_button.is_selected():
    #         thread = threading.Thread(target=stop_n_fee_hk)
    #     else:
    #         thread = threading.Thread(target=start_n_fee_hk)
    #
    #     thread.daemon = True
    #     thread.start()

    def create_overview_widget_core(self):
        """ Create a frame with one process widget per core process."""

        # Core processes

        self.overview_widget_core_layout = QVBoxLayout()

        for process_name in self.core.keys():

            process_widget = ProcessWidget(
                process_name, self.core[process_name], self,
                include_start_stop_button=False)
            self.process_widgets[process_name] = process_widget
            self.process_widgets_core[process_name] = process_widget

            self.overview_widget_core_layout.addWidget(process_widget)

        self.logger_widget = LogWidget(self)
        self.overview_widget_core_layout.addWidget(self.logger_widget)

        self.overview_widget_core = QGroupBox("Services/Core", self)
        self.overview_widget_core.setLayout(self.overview_widget_core_layout)
        self.overview_widget_core.setToolTip(
            "EGSE core processes: must be running at all times.")

    def create_overview_widget_file_services(self):

        # File generation processes

        self.overview_widget_file_services_layout = QVBoxLayout()

        self.fitsgen_widget = FitsgenWidget(self)
        self.overview_widget_file_services_layout.addWidget(self.fitsgen_widget)

        self.fov_hk_widget = FovHkWidget(self)
        self.overview_widget_file_services_layout.addWidget(self.fov_hk_widget)

        self.n_fee_hk_widget = NFeeHkWidget(self)
        self.overview_widget_file_services_layout.addWidget(self.n_fee_hk_widget)

        self.overview_widget_file_services = QGroupBox("File Generation Processes", self)
        self.overview_widget_file_services.setLayout(self.overview_widget_file_services_layout)
        # self.overview_widget_file_services.setToolTip(
        #     "EGSE core processes: must be running at all times.")

    def closeEvent(self, close_event: QCloseEvent) -> None:
        """ Make sure that all threads are stopped when the GUI is closed.

        Args:
            - close_event: Close event received when the GUI is closed.
        """
        for monitoring_worker in self.monitoring_workers.values():
            monitoring_worker.active = False

        for monitoring_thread in self.monitoring_threads.values():
            monitoring_thread.quit()

        self.setup_monitoring_worker.active = False
        self.setup_monitoring_thread.quit()

        self.logger_monitoring_worker.active = False
        self.logger_monitoring_thread.quit()

        self.fitsgen_monitoring_worker.active = False
        self.fitsgen_monitoring_thread.quit()

        self.fov_hk_monitoring_worker.active = False
        self.fov_hk_monitoring_thread.quit()

        self.n_fee_hk_monitoring_worker.active = False
        self.n_fee_hk_monitoring_thread.quit()

        # Group the waiting
        for monitoring_thread in self.monitoring_threads.values():
            monitoring_thread.wait()

        self.setup_monitoring_thread.wait()
        self.logger_monitoring_thread.wait()
        self.fitsgen_monitoring_thread.wait()
        self.fov_hk_monitoring_thread.wait()
        self.n_fee_hk_monitoring_thread.wait()

class ProcessManagerUIModel:

    def __init__(self):
        """ Initialisation of the Process Manager UI model."""

        try:

            self.process_manager = ProcessManagerProxy()

        except ConnectionError:

            self.process_manager = None

    def is_connected(self):
        """ Checks whether the Process Manager Control Server is active.

        Checks whether a connection to the Process Manager Control Server has been established.

        Returns:
            - True if a connection to the Process Manager Control Server has been established; False otherwise.
        """

        return self.process_manager.ping() and self.process_manager.is_cs_connected()


class ProcessManagerUIController:

    def __init__(self, model: ProcessManagerUIModel, view: ProcessManagerUIView):
        """ Initialisation of the Controller for the Process Manager GUI.

        Args:
            - model: Process Manager UI model.
            - view: Process Manager UI view.
        """

        self.model = model
        self.view = view


def main():
    """ Main method to launch the Process Manager GUI."""
    lock_file = QLockFile(str(Path("~/pm_ui.app.lock").expanduser()))

    multiprocessing.current_process().name = "pm_ui"
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(get_resource(":/icons/pm_ui.svg"))))

    if lock_file.tryLock(100):
        process_status = ProcessStatus()

        timer_thread = threading.Thread(target=do_every, args=(10, process_status.update))
        timer_thread.daemon = True
        timer_thread.start()

        start_http_server(GUI_SETTINGS.METRICS_PORT)


        # Check whether the Process Manager CS is running
        # (show a warning in a pop-up window if it's not)

        try:

            with ProcessManagerProxy():

                if not is_configuration_manager_active():

                    description = "Could not connect to Configuration Manager"
                    into_text = (
                        "The GUI will start, but without listed processes. "
                        "Please, check if the Configuration Manager is running and start the server if needed."
                        # "Otherwise, check if the correct HOSTNAME for the Configuration Manager is set in the "
                        # "Settings.yaml "
                        # "configuration file."
                        "The Process Manager GUI will have to be re-started after that."
                    )

                    show_info_message(description, into_text)

        except ConnectionError:

            description = "Could not connect to Process Manager Control Server"

            into_text = (
                "The GUI will start, but the connection button will show a disconnected state. "
                "Please, check if the Control Server is running and start the server if needed. "
                "Otherwise, check if the correct HOSTNAME for the control server is set in the "
                "Settings.yaml "
                "configuration file."
            )

            show_info_message(description, into_text)

        # proxy = ProcessManagerProxy()

        # if not proxy.ping():
        #         description = "Could not connect to Process Manager Control Server"
        #         into_text = (
        #             "The GUI will start, but the connection button will show a disconnected state. "
        #             "Please check if the Control Server is running and start the server if needed. "
        #             "Otherwise, check if the correct HOSTNAME for the control server is set in the "
        #             "Settings.yaml "
        #             "configuration file."
        #         )

        #         show_info_message(description, into_text)

        # proxy.disconnect_cs()

        # Create the Process Manager GUI, following the MVC-model

        view = ProcessManagerUIView()
        model = ProcessManagerUIModel()
        ProcessManagerUIController(model, view)

        view.show()

        return app.exec_()
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The Process Manager (PM) GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()


if __name__ == '__main__':

    sys.exit(main())
