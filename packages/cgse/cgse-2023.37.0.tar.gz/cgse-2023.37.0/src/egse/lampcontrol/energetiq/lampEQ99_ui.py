import argparse
import logging
from pathlib import Path

import sys

from egse.resource import get_resource

"""
Qt imports for the LampView class
"""

from PyQt5.QtWidgets import QApplication, QMessageBox
import pyqtgraph as pg
from PyQt5.QtGui import (QFont, QIcon, QPalette, QPixmap)
from PyQt5.QtWidgets import (QAction, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QMainWindow, QVBoxLayout)
from PyQt5.QtCore import QTimer, QLockFile
from QLed import QLed

from egse.settings import Settings
from egse.observer import Observable
from egse.observer import Observer
from egse.state import UnknownStateError
from egse.config import find_file, set_logger_levels

from egse.lampcontrol.energetiq.lampEQ99 import LampEQ99Controller, LampEQ99Proxy, LampEQ99Simulator

from egse.gui import show_warning_message

from prometheus_client import start_http_server
from egse.process import ProcessStatus
import threading
from egse.system import do_every

MODULE_LOGGER = logging.getLogger(__name__)

# Note that, in production, the logging level for the different loggers can be changed with a
# service command `set_logging_level(logger_name, level)`.

logger_levels = [
    ("egse.protocol", logging.INFO),
    ("egse.command", logging.INFO),
    ("egse.settings", logging.INFO),
    ("egse.config", logging.INFO),
    ("git.cmd", logging.INFO),
]

set_logger_levels((logger_levels))

SETTINGS = Settings.load("Lamp EQ99 Controller")
FONT = QFont("Helvetica", 18)

GUI_SETTINGS = Settings.load("LAMP EQ99 GUI")

class LampUIView(QMainWindow, Observable):
    def __init__(self):
        super().__init__()

        # Define those variables that we will need/use in different methods

        self.measure = None
        self.clear_action = None
        self.reconnect_action = None
        self.toolbar = None

        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle("Energetiq Lamp EQ99 Controller")

        self.init_gui()

    def createToolbar(self):
        image_location = Path(__file__).resolve().parent.parent.parent / "images"

        # The Reconnect action is used to reconnect the device or control server

        connected_pix = QPixmap(str(image_location / "connected-100.png"))
        disconnected_pix = QPixmap(str(image_location / "disconnected-100.png"))
        reconnect_icon = QIcon()
        reconnect_icon.addPixmap(connected_pix, QIcon.Normal, QIcon.On)
        reconnect_icon.addPixmap(disconnected_pix, QIcon.Normal, QIcon.Off)

        self.reconnect_action = QAction(reconnect_icon, "Reconnect", self)
        self.reconnect_action.setToolTip("Reconnect")
        self.reconnect_action.setCheckable(True)
        self.reconnect_action.triggered.connect(self.onClick)

        switch_on_pix = QPixmap(str(find_file("switch-on.svg", in_dir="images")))
        switch_off_pix = QPixmap(str(find_file("switch-off.svg", in_dir="images")))
        switch_icon = QIcon()
        switch_icon.addPixmap(switch_on_pix, QIcon.Normal, QIcon.On)
        switch_icon.addPixmap(switch_off_pix, QIcon.Normal, QIcon.Off)
        self.switch_action = QAction(switch_icon, "Control", self)
        self.switch_action.setToolTip("Lamp ON/OFF")
        self.switch_action.setCheckable(True)
        self.switch_action.triggered.connect(self.set_lamp)

        self.toolbar = self.addToolBar("MainToolbar")
        self.toolbar.addAction(self.reconnect_action)
        self.toolbar.addAction(self.switch_action)

        return self.toolbar

    def set_lamp(self):
        self.actionObservers({"set_lamp" : self.switch_action.isChecked()})

    def create_channel_group(self):

        group_box = QGroupBox("Lamp control")
        grid_show = QGridLayout()
        vbox = QVBoxLayout()

        self.led = QLed(self, onColour=QLed.Yellow, shape=QLed.Circle)
        self.led.setFixedSize(20, 20)
        self.led_error = QLed(self, onColour=QLed.Red, shape=QLed.Circle)
        self.led_error.setFixedSize(20, 20)
        self.label_lamp_error = QLabel("")

        grid_show.addWidget(QLabel("Lamp state"), 0, 0)
        grid_show.addWidget(self.led,1, 0)
        grid_show.addWidget(QLabel("Lamp error"), 2, 0)
        grid_show.addWidget(self.led_error, 3, 0)
        grid_show.addWidget(self.label_lamp_error, 3, 1)

        grid_show.setColumnStretch(1, 10)

        vbox.addLayout(grid_show)
        vbox.addStretch(1)

        group_box.setLayout(vbox)

        return group_box

    def init_gui(self):

        # Switch to using white background and black foreground for pyqtgraph stripcharts

        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")

        # The main frame in which all the other frames are located, the outer Application frame

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        hbox = QHBoxLayout()
        self.createToolbar()
        hbox.addWidget(self.create_channel_group())

        app_frame.setLayout(hbox)

        self.setCentralWidget(app_frame)

    def set_style(self):
        """
        Set the style for the LakeShoreUI Widget when it is connected to a real
        Lamp Controller (hardware).
        This will override the styles that were defined in the styles.qss style file
        that was loaded for the Application.
        """
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.Light)
        self.setStyleSheet(
            """
            QGroupBox {
                border: 1px solid lightGray;
                border-radius: 0px;
                margin-top: 0px;
                padding-top: 10px;
            }
            QGroupBox::title {
                background-color: transparent;
                padding-top: 0px;
                padding-left: 0px;
            }
        """
        )

    def set_style_simulator(self):
        """
        Set the style for the LakeShoreUI Widget when it is connected to a
        LakeSHore Simulator.
        This will override the styles that were defined in the styles.qss style file
        that was loaded for the Application.
        """
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.Dark)
        self.setStyleSheet(
            """
            QGroupBox {
                border: 1px solid lightGray;
                border-radius: 0px;
                margin-top: 0px;
                padding-top: 10px;
            }
            QGroupBox::title {
                background-color: transparent;
                padding-top: 0px;
                padding-left: 0px;
            }
        """
        )

    def onClick(self):

        sender = self.sender()

        MODULE_LOGGER.debug(f"sender.text() = {sender.text()}")
        MODULE_LOGGER.debug(f"sender.isChecked() = {sender.isChecked()}")

        self.notifyObservers(sender)

    def set_connection_state(self, state):

        if state == "connected":
            self.reconnect_action.setChecked(True)
        elif state == "disconnected":
            self.reconnect_action.setChecked(False)
        else:
            raise UnknownStateError(
                f"Unknown State ({state}), expected 'connected' or 'disconnected'."
            )

class LampUIModel:
    def __init__(self, type_):
        self.type = type_

        if self.type == "proxy":
            self.lamp = LampEQ99Proxy()
        elif self.type == "direct":
            self.lamp = LampEQ99Controller()
            self.lamp.connect()
        elif self.type == "simulator":
            self.lamp = LampEQ99Simulator()
        else:
            raise Exception(
                f"Unknown type of Lamp implementation passed into the model: {type}"
            )

        if self.lamp is not None:
            MODULE_LOGGER.debug(
                f"LampEQ99Controller initialized as {self.lamp.__class__.__name__}"
            )

    def has_commands(self):
        if self.type == "proxy":
            return self.lamp.has_commands()
        return True

    def load_commands(self):
        if self.type == "proxy":
            self.lamp.load_commands()

    def is_simulator(self):
        return self.lamp.is_simulator()

    def is_connected(self):
        if self.type == "proxy":
            return self.lamp.is_cs_connected()
        else:
            return self.lamp.is_connected()

    def reconnect(self):
        if self.type == "proxy":
            self.lamp.reconnect_cs()
            return self.lamp.is_cs_connected()
        else:
            self.lamp.reconnect()
            return self.lamp.is_connected()
        return False

    def disconnect(self):
        if self.type == "proxy":
            self.lamp.disconnect_cs()
        else:
            self.lamp.disconnect()

class LampUIController(Observer):
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.addObserver(self)

        self.create_timer()

        if self.model.is_connected():
            self.update_values()

            if self.model.is_simulator():
                self.view.set_style_simulator()
            else:
                self.view.set_style()

            self.view.set_connection_state("connected")
            self.start_timer()
        else:
            self.stop_timer()
            self.view.set_connection_state("disconnected")

    def create_timer(self):
        """Create a Timer that will update the States every second."""

        self.states_capture_timer = QTimer()

        self.states_capture_timer.setInterval(200) # 200 ms

        self.states_capture_timer.timeout.connect(self.update_values) # The update_values function is called at the end of the timer (200 ms)

        self.stripchart_timer = QTimer()
        self.stripchart_timer.setInterval(200)

    def start_timer(self):
        self.states_capture_timer.start()
        self.stripchart_timer.start()

    def stop_timer(self):
        self.states_capture_timer.stop()
        self.stripchart_timer.stop()

    def update_values(self):
        error_message = self.model.lamp.lamp_errors() # error_message is a string
        lamp_errors = error_message != "Error Message: 0" # lamp_errors is Boolean : True means errors
        #PROBLÈME : l'erreur est vidée dès qu'elle est lue donc elle ne persiste pas et selon l'erreur (dans le cas d'absence de controler notamment) elle ne reste pas affichée car une fois qu'elle est lue c'est comme s'il n'y avait plu d'erreur (dans le cas où elle n'est plu détectable (absence controler notamment) si le switch est sur off (lampe éteinte) et erreur n'existe plus puisqu'on actualise et appelle la fonction lamp_errors toutes les 200 ms
        lamp_state = self.model.lamp.get_lamp()

        self.view.label_lamp_error.setText(error_message)
        self.view.label_lamp_error.setVisible(lamp_errors)
        self.view.led_error.setValue(lamp_errors)
        self.view.led.setValue(lamp_state)
        self.view.switch_action.setChecked(lamp_state)

    def update(self, changed_object):

        text = changed_object.text()

        if text == "Reconnect":

            if changed_object.isChecked():
                MODULE_LOGGER.debug("Reconnecting the Lamp model.")
                if self.model.reconnect():
                    self.view.set_connection_state("connected")
                    if not self.model.has_commands():
                        self.model.load_commands()
                    self.start_timer()
                else:
                    self.view.reconnect_action.setChecked(False)
            else:
                MODULE_LOGGER.debug("Disconnecting the Lamp model.")
                self.stop_timer()
                self.model.disconnect()
                self.view.set_connection_state("disconnected")

            return

        if text == "ClearErrors":
            self.model.clearError()

        if text == "Reset":
            pass

    def do(self, actions):

        for action, value in actions.items():
            MODULE_LOGGER.debug(f"do {action} with {value}")
            if action == "set_wavelength":
                wavelength = value
                print(wavelength)
                MODULE_LOGGER.debug(f"do: set_wavelength({wavelength}:{type(wavelength)})")
                self.model.set_wavelength(wavelength)

            if action == "set_range":
                _range, auto = value
                MODULE_LOGGER.debug(f"do: set_range({_range}:{type(_range)}, {auto}:{type(auto)})")
                self.model.set_range(_range, auto)

            if action == "get_configuration":
                configuration = self.model.get_configuration()
                print(configuration)
                self.view.update_configuration_value(configuration)

            if action == "set_lamp":
                enable = value # value is Boolean : True if switch button is ON (according to the function set_lamp defined in LampUIView class)
                self.model.lamp.set_lamp(enable)
                self.update_values()

def parse_arguments():
    """
    Prepare the arguments that are specific for this application.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type",
        dest="type",
        action="store",
        choices={"proxy", "simulator", "direct"},
        help="Specify the implementation you want to connect to.",
        default="proxy",
    )
    parser.add_argument(
        "--profile",
        default=False,
        action="store_true",
        help="Enable info logging messages with method profile information.",
    )
    args = parser.parse_args()
    return args


def main():
    lock_file = QLockFile(str(Path("~/lampEQ99_ui.app.lock").expanduser()))

    logging.basicConfig(level=logging.DEBUG)

    styles_location = find_file("styles.qss", in_dir="egse/gui")

    args = list(sys.argv)
    args[1:1] = ["-stylesheet", str(styles_location)]
    app = QApplication(args)
    app.setWindowIcon(QIcon(str(get_resource(":/icons/logo-ogse.svg"))))

    if lock_file.tryLock(100):

        process_status = ProcessStatus()

        timer_thread = threading.Thread(target=do_every, args=(10, process_status.update))
        timer_thread.daemon = True
        timer_thread.start()

        start_http_server(GUI_SETTINGS.METRICS_PORT)

        args = parse_arguments()

        if args.profile:
            Settings.set_profiling(True)

        if args.type == "proxy":
            proxy = LampEQ99Proxy()
            if not proxy.ping():
                description = "Could not connect to Lamp Control Server"
                info_text = (
                    "The GUI will start, but the connection button will show a disconnected state. "
                    "Please check if the Control Server is running and start the server if needed. "
                    "Otherwise, check if the correct HOSTNAME for the control server is set in the "
                    "Settings.yaml "
                    "configuration file."
                )

                show_warning_message(description, info_text)

        view = LampUIView()
        model = LampUIModel(args.type)
        controller = LampUIController(model, view)

        view.show()
        return app.exec_()
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The Lamp EQ99 GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()

if __name__ == "__main__":
    sys.exit(main())
