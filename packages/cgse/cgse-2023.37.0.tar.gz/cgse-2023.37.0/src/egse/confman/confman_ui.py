import pickle
from pathlib import Path

import sys

import zmq
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QObject, QLockFile
from PyQt5.QtGui import QPixmap, QIcon, QCloseEvent
from PyQt5.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel, QMainWindow, QTextBrowser, QVBoxLayout, QAction,
                             QMessageBox)
from rich.console import Console

from egse.config import find_file
from egse.confman import (ConfigurationManagerProxy, is_configuration_manager_active)
from egse.confman.setup_ui import SetupUIView
from egse.resource import get_resource
from egse.settings import Settings
from egse.zmq_ser import set_address_port

CTRL_SETTINGS = Settings.load("Configuration Manager Control Server")


class ConfigurationManagerUIView(QMainWindow):

    def __init__(self):

        """ Initialisation of the Configuration Manager GUI.

        The components are placed in the window and a thread is created to
        listen to the monitoring port of the configuration manager.  When the
        obsid and/or setup change, this information is updated in the GUI.
        """

        super().__init__()

        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle("Configuration Manager")

        self.setup_ui = SetupUIView()

        # Build GUI

        self.toolbar = self.addToolBar("MainToolbar")

        self.init_gui()

        # Listen to the monitoring port of the CM in the background (i.e. in a
        # separate thread) and update the content of the GUI if needed

        self.start_monitoring()

    def start_monitoring(self):
        """ Start listening to the monitoring port.

        Create and start a thread that listens on the monitoring port in the
        background.  If the obsid and/or setup have changed, the information
        in the GUI is updated.
        """

        self.monitoring_thread = QThread(self)
        self.monitoring_worker = MonitoringWorker()
        self.monitoring_worker.moveToThread(self.monitoring_thread)

        self.monitoring_worker.monitoring_signal.connect(self.update_values)
        self.monitoring_thread.started.connect(self.monitoring_worker.start_process)

    def closeEvent(self, close_event: QCloseEvent) -> None:
        """ Make sure that the thread is stopped when the GUI is closed.

        Args:
            - close_event: Close event received when the GUI is closed.
        """

        self.monitoring_worker.active = False
        self.monitoring_thread.quit()
        self.monitoring_thread.wait()

    def update_values(self, monitoring_info):
        """ Update the obsid and setup in the GUI.

        If the obsid and/or the setup have changed, this information needs to
        be updated in the GUI.

        Args:
            - monitoring_info: Information received from the monitoring port
                               of the Configuration Manager.  This contains
                               the obsid and setup.
        """

        # Update the obsid in the GUI

        self.update_obsid(monitoring_info["obsid"])

        # Update the setup in the GUI

        self.update_setup(monitoring_info["setup"])

    def update_obsid(self, obsid):
        """ Update the obsid in the GUI.

        If the give obsid is None, no observation is running (which will be
        shown in the GUI).  The frame around the GUI will turn green, to
        indicate that it is safe to shut down the EGSE Control Servers.
        Otherwise, an observation (with the given identifier is running):
        the obsid will be shown in the GUI and the frame around the GUI will
        turn red, indicating that it is not safe to shut down the EGSE Control
        Servers.

        Args:
            - obsid: New obsid to show in the GUI.  None if no observation is
                     running.
        """

        # No observation is running

        if obsid is None:

            self.setStyleSheet('QMainWindow{border: 3px solid green;}')

            self.obsid.setText("No observation is running")

        # Observation is running

        else:

            self.setStyleSheet('QMainWindow{border: 3px solid red;}')

            self.obsid.setText(str(obsid))

    def update_setup(self, setup):
        """ Update the setup in the GUI.

        Args:
            - setup: New setup to show in the GUI.
        """

        self.setup.setText(setup.pretty_str())

        console = Console(width=120, force_terminal=False, force_jupyter=False)
        with console.capture() as capture:
            console.print(setup)
        text = capture.get()

        self.setup.setText(text)

    def init_gui(self):
        """ Put the components in the GUI window.

        The GUI comprises the following components:
            - text field with the obsid;
            - scrollable area with the current setup (loaded by the
              Configuration Manager).
        """

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        self.add_toolbar()

        box = QVBoxLayout()

        # Obsid

        hbox = QHBoxLayout()

        hbox.addWidget(QLabel("Obsid"))

        self.obsid = QLabel("No observation is running")
        hbox.addWidget(self.obsid)

        box.addLayout(hbox)

        # Setup

        self.setup = QTextBrowser(self)
        self.setup.setText("No setup loaded")

        self.setup.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setup.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        box.addWidget(QLabel("Setup"))
        box.addWidget(self.setup)

        app_frame.setLayout(box)

        self.setCentralWidget(app_frame)

    def add_toolbar(self):

        search_pix = QPixmap(str(find_file("search.png", in_dir="images")))
        search_icon = QIcon()
        search_icon.addPixmap(search_pix, QIcon.Normal, QIcon.On)

        inspect_setup_action = QAction(search_icon, "Inspect available setups", self)
        inspect_setup_action.setToolTip(
            "Open separate window to inspect all available setups.")
        inspect_setup_action.setCheckable(False)
        inspect_setup_action.triggered.connect(self.open_setup_ui)

        self.toolbar.addAction(inspect_setup_action)

        return self.toolbar

    def open_setup_ui(self):
        """ Open separate window to inspect the available setups.
        """

        self.setup_ui.show()


class ConfigurationManagerUIModel:

    def __init__(self):

        """ Initialisation of the Configuration Manager UI model.
        """

        try:

            self.cm = ConfigurationManagerProxy()

        except ConnectionError:

            self.cm = None

    def is_connected(self):
        """ Checks whether the Configuration Manager is active.

        Returns:
            - True if the Configuration Manager is active; False otherwise.
        """

        return is_configuration_manager_active()

    def update(self, changed_object):
        pass

    def do(self):
        pass


class MonitoringWorker(QObject):

    # The thread will send a signal with the monitoring information:
    #   - The obsid;
    #   - The setup that has been loaded by the configuration manager.

    monitoring_signal = pyqtSignal(dict)

    def __init__(self):

        """ Initialisation of a monitoring thread.

        This monitoring thread will listen on the monitoring port of the
        Control Server.  At this point the socket (that will connect to the
        monitoring port) is not created yet.
        """

        super(MonitoringWorker, self).__init__()

        self.obsid = None   # Previous obsid
        self.setup = None   # Previous setup

        self.active = False

    def connect_socket(self, proxy):
        """ Create a socket and connect to the monitoring port.

        Args:
            - proxy_type: Proxy type (needed to read the connection details).
        """

        # Start listening to the monitoring port

        self.socket = zmq.Context().socket(zmq.SUB)

        endpoint = proxy.get_endpoint()
        monitoring_port = proxy.get_monitoring_port()
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

            socket_list, _, _ = zmq.select([self.socket], [], [], timeout=1)

            # Monitoring information was received (before timeout)

            if self.socket in socket_list:

                pickle_string = self.socket.recv()
                monitoring_info = pickle.loads(pickle_string)

                new_obsid = monitoring_info["obsid"]  # New obsid
                new_setup = monitoring_info["setup"]  # New setup

                # The obsid and/or setup have changed

                if (new_obsid != self.obsid) or (new_setup != self.setup):

                    self.obsid = new_obsid
                    self.setup = new_setup

                    # Emit the monitoring info

                    self.monitoring_signal.emit(monitoring_info)

        self.socket.close(linger=0)


class ConfigurationManagerUIController:

    def __init__(self, model: ConfigurationManagerUIModel,
                 view: ConfigurationManagerUIView):

        """ Initialisation of the Controller for the Process Manager GUI.

        Args:
            - model: Configuration Manager UI model.
            - view: Configuration Manager UI view.
        """

        self.model = model
        self.view = view

        self.view.monitoring_worker.connect_socket(self.model.cm)
        self.view.monitoring_thread.start()

    def update(self, changed_object):
        pass

    def do(self):
        pass


def main():
    """ Main method to launch the Configuration Manager GUI.
    """

    lock_file = QLockFile(str(Path("~/cm_ui.app.lock").expanduser()))

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(get_resource(":/icons/settings.svg"))))

    if lock_file.tryLock(100):
        view = ConfigurationManagerUIView()
        model = ConfigurationManagerUIModel()
        ConfigurationManagerUIController(model, view)

        view.show()
        sys.exit(app.exec_())
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The Configuration Manager (CM) GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()


if __name__ == "__main__":
    main()
