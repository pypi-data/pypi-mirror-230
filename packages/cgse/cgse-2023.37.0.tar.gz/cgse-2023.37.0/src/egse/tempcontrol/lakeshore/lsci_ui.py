"""
A Graphical User Interface for monitoring the LakeShore Temperature Controller.

.. todo:: put code in the __main__ section into a main() function, so this GUI
          can be called from another Python process/script.
"""
import argparse
import logging
from pathlib import Path

import sys

import pyqtgraph as pg
from PyQt5 import QtGui
from PyQt5.QtCore import QDateTime, QLockFile
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QVBoxLayout

from egse.config import find_file
from egse.gui import show_warning_message
from egse.gui.stripchart import StripChart
from egse.observer import Observable
from egse.observer import Observer
from egse.resource import get_resource
from egse.settings import Settings
from egse.state import UnknownStateError
from egse.tempcontrol.lakeshore.lsci import LakeShoreController
from egse.tempcontrol.lakeshore.lsci import LakeShoreProxy
from egse.tempcontrol.lakeshore.lsci import LakeShoreSimulator

logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)
logger = MODULE_LOGGER = logging.getLogger("LSCI- CS")


class LakeShoreUIView(QMainWindow, Observable):
    def __init__(self,index_):
        super().__init__()

        # Define those variables that we will need/use in different methods

        self.temperature_a = None
        self.clear_action = None
        self.reconnect_action = None
        self.toolbar = None
        self.index = index_
        self.stripchart = None

        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle(f"LakeShore {self.index} Controller")

        self.init_gui()

    def create_channel_group(self):

        group_box = QGroupBox("LakeShore Channel A")

        # Create the label fields that display the current temperature

        grid_show = QGridLayout()

        grid_show.addWidget(QLabel("Channel A "), 0, 0)

        self.temperature_a = QLabel(self)
        self.temperature_a.setAlignment(Qt.AlignRight)
        self.temperature_a.setText("0.000")

        self.temperature_a.setFont(QtGui.QFont(self.temperature_a.font().family(), 24))

        grid_show.addWidget(self.temperature_a, 0, 1)

        grid_show.addWidget(QLabel(" ºC"), 0, 2)

        grid_show.setColumnStretch(1, 10)

        # Create the edit text field for setting the position

        self.stripchart = StripChart(
            labels={"left": ("Temperature", "ºC"), "bottom": ("Time", "d hh:mm:ss")}
        )
        self.stripchart.setInterval(60 * 60 * 12)  # 12h of data
        self.stripchart.set_yrange(20, 40)

        vbox = QVBoxLayout()

        vbox.addLayout(grid_show)
        vbox.addStretch(1)
        vbox.addWidget(self.stripchart)

        group_box.setLayout(vbox)

        return group_box

    def update_stripchart(self, time, temperature):
        self.stripchart.update(time, temperature)

    def update_temperature_field(self, temperature):
        self.temperature_a.setText(f"{temperature:.3f}")

    def init_gui(self):

        # Switch to using white background and black foreground for pyqtgraph stripcharts

        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")

        # The main frame in which all the other frames are located, the outer Application frame

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        hbox = QHBoxLayout()

        hbox.addWidget(self.create_channel_group())

        app_frame.setLayout(hbox)

        self.setCentralWidget(app_frame)

    def set_style(self):
        """
        Set the style for the LakeShoreUI Widget when it is connected to a real
        LakeShore Controller (hardware).

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

    def set_connection_state(self, state):

        if state == "connected":
            pass
        elif state == "disconnected":
            pass
        else:
            raise UnknownStateError(
                f"Unknown State ({state}), expected 'connected' or 'disconnected'."
            )


class LakeShoreUIModel:
    def __init__(self, type_, index_):
        self.type = type_
        self.index = index_
        if self.type == "proxy":
            self.ls = LakeShoreProxy(self.index)
        elif self.type == "direct":
            self.ls = LakeShoreController()
        elif self.type == "simulator":
            self.ls = LakeShoreSimulator()
        else:
            raise ValueError(
                f"Unknown type of LakeShore implementation passed into the model: {type}"
            )

        if self.ls is not None:
            logger.debug(f"LakeShoreController {self.index} initialized as {self.ls.__class__.__name__}")

    def is_simulator(self):
        return self.ls.is_simulator()

    def is_connected(self):
        if self.type == "proxy":
            return_code = self.ls.ping() and self.ls.is_connected()
        else:
            return_code = self.ls.is_connected()

        return return_code

    def get_temperature(self):
        """Returns the temperature of channel A.

        Returns:
            the current temperature as a float or nan if no temperature available.
        """
        temperature = self.ls.get_temperature()
        if temperature is None:
            return float("nan")
        else:
            temperature = float(temperature)
            logger.debug(f"Temperature = {temperature:.3f}")
            return temperature


class LakeShoreUIController(Observer):
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.addObserver(self)

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
        # This is only needed when the Timer needs to run in another Thread
        # self.states_capture_timer.moveToThread(self)
        self.states_capture_timer.timeout.connect(self.update_values)
        self.states_capture_timer.setInterval(300)

    def start_timer(self):
        self.states_capture_timer.start()

    def stop_timer(self):
        self.states_capture_timer.stop()

    def update_values(self):

        # This method should not be called when not connected, by design!

        temperature = self.model.get_temperature()
        self.view.update_temperature_field(temperature)
        self.view.update_stripchart(QDateTime.currentMSecsSinceEpoch(), temperature)

    def update(self, changed_object):

        text = changed_object.text()

        if text == "Reconnect":

            if changed_object.isChecked():
                MODULE_LOGGER.debug("Reconnecting the Huber model.")
                if self.model.reconnect():
                    self.view.set_connection_state("connected")
                    if not self.model.has_commands():
                        self.model.load_commands()
                    self.start_timer()
                else:
                    self.view.reconnect_action.setChecked(False)
            else:
                MODULE_LOGGER.debug("Disconnecting the Huber model.")
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
            if action == "goto":
                axis, position = value
                MODULE_LOGGER.debug(f"do: goto({axis}:{type(axis)}, {position}:{type(position)})")
                self.model.goto(axis, position)


def parse_arguments():
    """
    Prepare the arguments that are specific for this application.
    """
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--index",
        action="store",
        help="Select LakeShore index to connected",
        default="1",
    )

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
    #lock_file = QLockFile(str(Path("~/lsci_ui.app.lock").expanduser()))
    STYLES_LOCATION = find_file("styles.qss", in_dir="egse/gui")

    args = list(sys.argv)
    args[1:1] = ["-stylesheet", str(STYLES_LOCATION)]

    app = QApplication(args)
    app.setWindowIcon(QIcon(str(get_resource(":/icons/temperature-control.svg"))))


    args = parse_arguments()

    if args.profile:
        Settings.set_profiling(True)

    if args.type == "proxy":
        proxy = LakeShoreProxy(args.index)
        if not proxy.ping():
            description = "Could not connect to Temperature Control Control Server"
            info_text = (
                "The GUI will start, but the connection button will show a disconnected state. "
                "Please check if the Control Server is running and start the server if needed. "
                "Otherwise, check if the correct HOSTNAME for the control server is set in the "
                "Settings.yaml "
                "configuration file."
            )

            show_warning_message(description, info_text)
    view = LakeShoreUIView(args.index)
    model = LakeShoreUIModel(args.type,args.index)
    controller = LakeShoreUIController(model, view)

    view.show()
    sys.exit(app.exec_())

if __name__ == "__main__":

    main()
