import argparse
import logging
from pathlib import Path

import sys

from egse.resource import get_resource

"""
Qt imports for the View class
"""

from PyQt5.QtWidgets import QApplication, QMessageBox
import pyqtgraph as pg
from PyQt5.QtGui import (QFont, QIcon, QPalette, QPixmap)
from PyQt5.QtWidgets import (QAction, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QMainWindow, QVBoxLayout)
from PyQt5.QtCore import QTimer, QLockFile

from egse.settings import Settings
from egse.observer import Observable, Observer
from egse.state import UnknownStateError
from egse.config import find_file, set_logger_levels
from egse.process import ProcessStatus
from egse.system import do_every
import threading
import datetime

from egse.powermeter.ni.cdaq9184 import cdaq9184Controller, cdaq9184Proxy, cdaq9184Simulator
from egse.gui import show_warning_message
from egse.gui.stripchart import StripChartWidget

from prometheus_client import Summary
from prometheus_client import start_http_server

MODULE_LOGGER = logging.getLogger(__name__)

SETTINGS = Settings.load("NI Controller")
FONT = QFont("Helvetica", 18)

EXECUTION_TIME = Summary(
    'ui_update_execution_time_seconds', 'Time spent updating the values in the GUI',
    ["type"]
)

GUI_SETTINGS = Settings.load("CDAQ 9184 GUI")


class cdaq9184UIView(QMainWindow, Observable):
    def __init__(self):
        super().__init__()

        # Define those variables that we will need/use in different methods

        self.measure = None
        self.clear_action = None
        self.reconnect_action = None
        self.toolbar = None

        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle("CDAQ9184 Controller GUI")

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

        self.toolbar = self.addToolBar("MainToolbar")
        self.toolbar.addAction(self.reconnect_action)

        return self.toolbar

    def create_channel_group(self):

        group_box = QGroupBox("CDAQ9184")

        # Create the label fields that display the current measure

        grid_show = QGridLayout()

        grid_show.addWidget(QLabel("State"), 0, 0)

        grid_show.setColumnStretch(1, 10)

        # Create the edit text field for setting the position

        vbox = QVBoxLayout()

        vbox.addLayout(grid_show)
        vbox.addStretch(1)

        group_box.setLayout(vbox)

        return group_box

    def create_ph1_widget(self):
        main = QFrame()
        main.setContentsMargins(0, 0, 0, 0)

        groupBox = QGroupBox("Photodiode 1")
        groupBox.setContentsMargins(0, 0, 0, 0)

        vbox = QVBoxLayout()

        #stripchart

        self.ph1_stripchart = StripChartWidget("Rotation angle", "degrees")
        vbox.addWidget(self.ph1_stripchart)

        groupBox.setLayout(vbox)

        vbox = QVBoxLayout()
        vbox.setSpacing(4)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(groupBox)
        main.setLayout(vbox)
        return main

    def create_ph2_widget(self):
        main = QFrame()
        main.setContentsMargins(0, 0, 0, 0)

        groupBox = QGroupBox("Photodiode 2")
        groupBox.setContentsMargins(0, 0, 0, 0)

        vbox = QVBoxLayout()

        #stripchart

        self.ph2_stripchart = StripChartWidget("Rotation angle", "degrees")
        vbox.addWidget(self.ph2_stripchart)

        groupBox.setLayout(vbox)

        vbox = QVBoxLayout()
        vbox.setSpacing(4)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(groupBox)
        main.setLayout(vbox)
        return main

    def create_ph3_widget(self):
        main = QFrame()
        main.setContentsMargins(0, 0, 0, 0)

        groupBox = QGroupBox("Photodiode 3")
        groupBox.setContentsMargins(0, 0, 0, 0)

        vbox = QVBoxLayout()

        #stripchart

        self.ph3_stripchart = StripChartWidget("Rotation angle", "degrees")
        vbox.addWidget(self.ph3_stripchart)

        groupBox.setLayout(vbox)

        vbox = QVBoxLayout()
        vbox.setSpacing(4)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(groupBox)
        main.setLayout(vbox)
        return main

    def create_temperature_widget(self):
        main = QFrame()
        main.setContentsMargins(0, 0, 0, 0)

        groupBox = QGroupBox("Temperature")
        groupBox.setContentsMargins(0, 0, 0, 0)

        vbox = QVBoxLayout()

        #stripchart

        self.t_stripchart = StripChartWidget("Rotation angle", "degrees")
        vbox.addWidget(self.t_stripchart)

        groupBox.setLayout(vbox)

        vbox = QVBoxLayout()
        vbox.setSpacing(4)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(groupBox)
        main.setLayout(vbox)
        return main


    def update_stripcharts(self, time, value):
        self.ph1_stripchart.update(time, value[0])
        self.ph2_stripchart.update(time, value[2])
        self.ph3_stripchart.update(time, value[4])
        self.t_stripchart.update(time, value[6])

    def init_gui(self):

        # Switch to using white background and black foreground for pyqtgraph stripcharts

        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")

        # The main frame in which all the other frames are located, the outer Application frame

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        hbox = QHBoxLayout()
        self.createToolbar()
        #hbox.addWidget(self.create_channel_group())
        hbox.addWidget(self.create_ph1_widget())
        hbox.addWidget(self.create_ph2_widget())
        hbox.addWidget(self.create_ph3_widget())
        hbox.addWidget(self.create_temperature_widget())




        app_frame.setLayout(hbox)

        self.setCentralWidget(app_frame)

    def set_style(self):
        """
        Set the style for the LakeShoreUI Widget when it is connected to a real
        Temperature Contorlelr Controller (hardware).
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


class cdaq9184UIModel:
    def __init__(self, type_):
        self.type = type_

        if self.type == "proxy":
            self.cdaq = cdaq9184Proxy()
        elif self.type == "direct":
            self.cdaq = cdaq9184Controller()
            self.cdaq.connect()
        elif self.type == "simulator":
            self.cdaq = cdaq9184Simulator()
        else:
            raise Exception(
                f"Unknown type of Temperature Controller implementation passed into the model: {type}"
            )

        if self.cdaq is not None:
            MODULE_LOGGER.debug(
                f"SRS cdaq9184Controller initialized as {self.cdaq.__class__.__name__}"
            )

    def has_commands(self):
        if self.type == "proxy":
            return self.cdaq.has_commands()
        return True

    def load_commands(self):
        if self.type == "proxy":
            self.cdaq.load_commands()

    def is_simulator(self):
        return self.cdaq.is_simulator()

    def is_connected(self):
        if self.type == "proxy":
            return self.cdaq.is_cs_connected()
        else:
            return self.cdaq.is_connected()

    def reconnect(self):
        if self.type == "proxy":
            self.cdaq.reconnect_cs()
            return self.cdaq.is_cs_connected()
        else:
            self.cdaq.reconnect()
            return self.cdaq.is_connected()
        return False

    def disconnect(self):
        if self.type == "proxy":
            self.cdaq.disconnect_cs()
        else:
            self.cdaq.disconnect()

    def read_values(self):
        return self.cdaq.read_values()


class cdaq9184UIController(Observer):
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.addObserver(self)
        self.timer_interval = 500


        self.create_timer()

        if self.model.is_connected():

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

        self.states_capture_timer.timeout.connect(self.update_values)
        self.states_capture_timer.setInterval(self.timer_interval)


        self.stripchart_timer = QTimer()

        self.stripchart_timer.setInterval(50)

    def start_timer(self):
        self.states_capture_timer.start()
        self.stripchart_timer.start()

    def stop_timer(self):
        self.states_capture_timer.stop()
        self.stripchart_timer.stop()

    def update_values(self):
        with EXECUTION_TIME.labels(type="stripcharts").time():
            value = self.model.read_values()
            MODULE_LOGGER.info(f"requested values from cdaq: {value}")
            ctime = datetime.datetime.strptime(value[1], '%H:%M:%S.%f')
            dtime = ctime - datetime.datetime(1900, 1, 1)
            ttime = dtime.total_seconds()
            self.view.update_stripcharts(ttime, value[2:])

    def update(self, changed_object):

        text = changed_object.text()

        if text == "Reconnect":

            if changed_object.isChecked():
                MODULE_LOGGER.debug("Reconnecting the cdaq9184 model.")
                if self.model.reconnect():
                    self.view.set_connection_state("connected")
                    if not self.model.has_commands():
                        self.model.load_commands()
                    self.start_timer()
                else:
                    self.view.reconnect_action.setChecked(False)
            else:
                MODULE_LOGGER.debug("Disconnecting the cdaq9184 model.")
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
    lock_file = QLockFile(str(Path("~/cdaq98184_ui.app.lock").expanduser()))

    styles_location = find_file("styles.qss", in_dir="egse/gui")

    args = list(sys.argv)
    args[1:1] = ["-stylesheet", str(styles_location)]
    app = QApplication(args)
    app.setWindowIcon(QIcon(str(get_resource(":/icons/meter.svg"))))

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
            proxy = cdaq9184Proxy()
            if not proxy.ping():
                description = "Could not connect to CDAQ9184 Control Server"
                info_text = (
                    "The GUI will start, but the connection button will show a disconnected state. "
                    "Please check if the Control Server is running and start the server if needed. "
                    "Otherwise, check if the correct HOSTNAME for the control server is set in the "
                    "Settings.yaml "
                    "configuration file."
                )

                show_warning_message(description, info_text)

        view = cdaq9184UIView()
        model = cdaq9184UIModel(args.type)
        controller = cdaq9184UIController(model, view)

        view.show()

        return app.exec_()
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The CDAQ9184 GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()


if __name__ == "__main__":
    sys.exit(main())
