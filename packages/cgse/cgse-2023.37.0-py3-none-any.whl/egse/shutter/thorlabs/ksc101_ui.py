import argparse
import logging
import sys
from pathlib import Path
import pyqtgraph as pg
import numpy as np

from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QFrame,
                             QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QSpinBox, QToolButton, QRadioButton,
                             QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QLockFile
from PyQt5.QtGui import QIcon, QPixmap, QPalette, QFont
from QLed import QLed

from egse.resource import get_resource
from egse.settings import Settings
from egse.observer import Observer
from egse.observer import Observable
from egse.state import UnknownStateError
from egse.config import find_file, set_logger_levels

from egse.shutter.thorlabs.ksc101 import ShutterKSC101Proxy, ShutterKSC101Controller, ShutterKSC101Simulator
from egse.gui import show_warning_message

from egse.process import ProcessStatus
from egse.system import do_every

from prometheus_client import Gauge, Summary
from prometheus_client import start_http_server

import threading

MODULE_LOGGER = logging.getLogger(__name__)
SETTINGS = Settings.load("Shutter KSC101 Controller")
GUI_SETTINGS = Settings.load("KSC101 GUI")
FONT = QFont("Helvetica", 18)

logger_levels = [
    ("egse.protocol", logging.INFO),
    ("egse.command", logging.INFO),
    ("egse.settings", logging.INFO),
    ("egse.config", logging.INFO),
    ("git.cmd", logging.INFO),
]

set_logger_levels(logger_levels)

class ShutterUIView(QMainWindow, Observable):
    # TODO: on reconnect new values need to be updated
    # TODO: get enable states for interlock and alarm (see ATPServer Help File)
    # TODO: update values enable value when after a "single" or an "automatic" operation

    def __init__(self):
        super().__init__()

        # Define those variables that we will need/use in different methods

        self.state = None
        self.clear_action = None
        self.reconnect_action = None
        self.toolbar = None

        self.setGeometry(0, 0, 300, 500)
        self.setWindowTitle('Thorlabs Shutter KSC101 Controller')

        self.init_gui()

    def createToolbar(self):
        image_location = Path(__file__).resolve().parent.parent.parent / "images"

        # The Reconnect action is used to reconnect the device or control server

        connected_pix = QPixmap(str(image_location / "connected-100.png"))
        disconnected_pix = QPixmap(str(image_location / "disconnected-100.png"))
        reconnect_icon = QIcon()
        reconnect_icon.addPixmap(connected_pix, QIcon.Normal, QIcon.On)
        reconnect_icon.addPixmap(disconnected_pix, QIcon.Normal, QIcon.Off)

        self.reconnect_action = QAction(reconnect_icon, 'Reconnect', self)
        self.reconnect_action.setToolTip("Reconnect")
        self.reconnect_action.setCheckable(True)
        self.reconnect_action.triggered.connect(self.onClick)

        self.enable = QToolButton()
        self.enable.setArrowType(Qt.RightArrow)
        self.enable.clicked.connect(self.set_enable)
        self.enable.setToolTip("Enable Solenoid")

        self.toolbar = self.addToolBar('MainToolbar')
        self.toolbar.addAction(self.reconnect_action)
        self.toolbar.addWidget(self.enable)

        return self.toolbar

    def createStatesWidget(self):

        self.states = [
            [QLabel("Shutter alarm"), QLed(self, offColour = QLed.Green, onColour = QLed.Red), QLed.setBaseSize(self, 1, 1)],
            [QLabel("Interlock alarm"), QLed(self, offColour = QLed.Green, onColour = QLed.Red)],
            [QLabel("Enable"), QLed(self, offColour = QLed.Red, onColour = QLed.Green)],
            ]

        vbox = QVBoxLayout()

        for state in self.states:
            hbox = QHBoxLayout()
            hbox.addWidget(state[1])
            hbox.addWidget(state[0])
            state[1].setFixedSize(20, 20)
            hbox.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            hbox.setSpacing(5)
            vbox.addLayout(hbox)

        vbox.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        vbox.setSpacing(0)

        group_box = QGroupBox("Shutter State",self)

        group_box.setLayout(vbox)

        return group_box

    def createOperationWidget(self):

        hbox = QHBoxLayout()

        group_mode = QGroupBox("Control Mode", self)
        vbox = QVBoxLayout()

        self.operation_modes = [[QRadioButton("Manual")],
                                [QRadioButton("Single")],
                                [QRadioButton("Auto")],
                                [QRadioButton("Trigger")]
                                ]

        for mode in self.operation_modes:
            mode[0].clicked.connect(self.set_mode)
            vbox.addWidget(mode[0])

        vbox.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        vbox.setSpacing(10)

        group_mode.setLayout(vbox)

        group_cycle = QGroupBox("Cycling Settings", self)
        vbox_cycle = QVBoxLayout()

        self.cycle = [
                [QLabel("ON duration (ms):"), QSpinBox(), "ON", 100, 100000],
                [QLabel("OFF duration (ms):"), QSpinBox(), "OFF", 100, 100000],
                [QLabel("Number of cycles:"), QSpinBox(), "Number", 0, 100000]
                ]

        for options in self.cycle:
            hbox_cycle = QHBoxLayout()
            hbox_cycle.addWidget(options[0])
            #hbox_cycle.addStretch(2) --> Not needed if fixed width is set
            hbox_cycle.addWidget(options[1])
            options[1].setObjectName(options[2])
            options[1].setMinimum(options[3])
            options[1].setMaximum(options[4])
            options[1].valueChanged.connect(self.set_cycle)
            options[1].setFixedWidth(100)
            options[0].setFixedWidth(120)
            hbox_cycle.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            vbox_cycle.addLayout(hbox_cycle)
            vbox_cycle.setSpacing(10)

        vbox_cycle.addStretch()
        group_cycle.setLayout(vbox_cycle)

        hbox.addWidget(group_mode)
        hbox.addWidget(group_cycle)

        group_operation = QGroupBox("Shutter operations", self)
        group_operation.setLayout(hbox)

        return group_operation

    def init_gui(self):

        ## Switch to using white background and black foreground for pyqtgraph stripcharts

        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        # The main frame in which all the other frames are located, the outer Application frame

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        create_state = self.createStatesWidget()
        create_operation = self.createOperationWidget()

        hbox = QHBoxLayout()
        toolbar_widget = self.createToolbar()
        hbox.addWidget(create_state)
        hbox.addWidget(create_operation)

        app_frame.setLayout(hbox)

        self.setCentralWidget(app_frame)

    def set_style(self):
        """
        Set the style for the Shutter Widget when it is connected to a real
        Shutter Controller (hardware).
        This will override the styles that were defined in the styles.qss style file
        that was loaded for the Application.
        """
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.Light)
        self.setStyleSheet("""
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
        """)

    def set_style_simulator(self):
        """
        Set the style for the Shutter UI Widget when it is connected to a
        Shutter Simulator.
        This will override the styles that were defined in the styles.qss style file
        that was loaded for the Application.
        """
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.Dark)
        self.setStyleSheet("""
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
        """)

    def initialize_values(self, configuration):
        "gets the parameter values on shutter start up"
        _cycle = configuration["cycle"]
        _cycle = list(_cycle.values())

        for parameter in range(len(self.cycle)):
            self.cycle[parameter][1].blockSignals(True)                 #avoids to trigger an event on init
            self.cycle[parameter][1].setValue(_cycle[parameter])
            self.cycle[parameter][1].blockSignals(False)

        _mode = configuration["mode"] - 1
        self.operation_modes[_mode][0].blockSignals(True)
        self.operation_modes[_mode][0].setChecked(True)
        self.operation_modes[_mode][0].blockSignals(False)

        _state = [False, False, configuration["state"]]

        for state in range(len(self.states)):
            self.states[state][1].blockSignals(True)
            self.states[state][1].setValue(_state[state])
            self.states[state][1].blockSignals(False)

    def onClick(self):

        sender = self.sender()

        MODULE_LOGGER.debug(f"sender.text() = {sender.text()}")
        MODULE_LOGGER.debug(f"sender.isChecked() = {sender.isChecked()}")

        self.notifyObservers(sender)

    def set_cycle(self):
        cycle =[]
        for parameter in range(len(self.cycle)):
            cycle.append(self.cycle[parameter][1].value())
        self.actionObservers({'set_cycle': cycle})

    def set_mode(self):
        _mode=[]
        op_modes = ["manual", "single", "auto", "trigger"]
        for mode in range(len(self.operation_modes)):
            _mode.append(self.operation_modes[mode][0].isChecked())
        self.actionObservers({'set_mode': op_modes[int(np.where(_mode)[0])]})

    def set_enable(self):
        self.actionObservers({'set_enable': not self.states[2][1].value})

    def set_connection_state(self, state):

        if state == 'connected':
            self.reconnect_action.setChecked(True)
        elif state == 'disconnected':
            self.reconnect_action.setChecked(False)
        else:
            raise UnknownStateError(
                f"Unknown State ({state}), expected 'connected' or 'disconnected'.")

class ShutterUIModel:
    def __init__(self, type_):
        self.type = type_

        if self.type == "proxy":
            self.sht = ShutterKSC101Proxy()
        elif self.type == "direct":
            self.sht = ShutterKSC101Controller()
            self.sht.connect()
        elif self.type == "simulator":
            self.sht = ShutterKSC101Simulator()
        else:
            raise Exception(f"Unknown type of Shutter implementation passed into the model: {type}")

        if self.sht is not None:
            MODULE_LOGGER.debug(f"ShutterKSC101Controller initialized as {self.sht.__class__.__name__}")

    def has_commands(self):
        if self.type == "proxy":
            return self.sht.has_commands()
        return True

    def load_commands(self):
        if self.type == "proxy":
            self.sht.load_commands()

    def is_simulator(self):
        return self.sht.is_simulator()

    def is_connected(self):
        if self.type == "proxy":
            return self.sht.is_cs_connected()
        else:
            return self.sht.is_connected()

    def reconnect(self):
        if self.type == "proxy":
            self.sht.reconnect_cs()
            return self.sht.is_cs_connected()
        else:
            self.sht.reconnect()
            return self.sht.is_connected()
        return False

    def disconnect(self):
        if self.type == "proxy":
            self.sht.disconnect_cs()
        else:
            self.sht.disconnect()

    def set_mode(self, mode):
        self.sht.set_mode(mode = mode)

    def set_cycle(self, on, off, number):
        self.sht.set_cycle(on, off, number)

    def set_enable(self, status):
        self.sht.set_enable(status)

    def get_configuration(self):
        cycle = self.sht.get_cycle()
        mode = self.sht.get_mode()
        state = self.sht.get_enable()
        configuration = {"cycle": cycle, "mode": mode, "state": state}
        return configuration

class ShutterUIController(Observer):
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.addObserver(self)

        self.create_timer()

        if self.model.is_connected():
            self.initialize_values()

            if self.model.is_simulator():
                self.view.set_style_simulator()
            else:
                self.view.set_style()

            self.view.set_connection_state('connected')
            self.start_timer()
        else:
            self.stop_timer()
            self.view.set_connection_state('disconnected')

    def create_timer(self):
        """Create a Timer that will update the States every second."""

        self.states_capture_timer = QTimer()
        # This is only needed when the Timer needs to run in another Thread
        # self.states_capture_timer.moveToThread(self)
        self.states_capture_timer.setInterval(200)
        self.states_capture_timer.timeout.connect(self.initialize_values)

        self.stripchart_timer = QTimer()
#        self.stripchart_timer.timeout.connect(self.update_stripchart)
        self.stripchart_timer.setInterval(200)

    def start_timer(self):
        self.states_capture_timer.start()
        self.stripchart_timer.start()

    def stop_timer(self):
        self.states_capture_timer.stop()
        self.stripchart_timer.stop()

    def initialize_values(self):
        configuration = self.model.get_configuration()
        self.view.initialize_values(configuration)

    def update(self, changed_object):

        text = changed_object.text()

        if text == "Reconnect":
            if changed_object.isChecked():
                MODULE_LOGGER.debug("Reconnecting the Shutter KSC101 model.")
                if self.model.reconnect():
                    self.view.set_connection_state('connected')
                    if not self.model.has_commands():
                        self.model.load_commands()
                    self.start_timer()
                else:
                    self.view.reconnect_action.setChecked(False)
            else:
                MODULE_LOGGER.debug("Disconnecting the Shutter KSC101 model.")
                self.stop_timer()
                self.model.disconnect()
                self.view.set_connection_state('disconnected')

            return

        if text == "ClearErrors":
            self.model.clearError()

        if text == "Reset":
            pass

    def do(self, actions):

        for action, value in actions.items():
            MODULE_LOGGER.debug(f"do {action} with {value}")
            if action == "set_mode":
                mode = value
                MODULE_LOGGER.debug(f"do: set_mode({mode}:{type(mode)})")
                self.model.set_mode(mode)
                self.initialize_values()

            if action == "set_cycle":
                on, off, number = value
                MODULE_LOGGER.debug(f"do: set_mode({on}:{type(on)}, {off}:{type(off)}, {number}:{type(number)})")
                self.model.set_cycle(on, off, number)
                self.initialize_values()

            if action == "set_enable":
                status = value
                MODULE_LOGGER.debug(f"do: set_enable({status}:{type(status)})")
                self.model.set_enable(status)
                self.initialize_values()

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
    lock_file = QLockFile(str(Path("~/ksc101_ui.app.lock").expanduser()))

    STYLES_LOCATION = find_file("styles.qss", in_dir="egse/gui")

    args = list(sys.argv)
    args[1:1] = ["-stylesheet", str(STYLES_LOCATION)]
    app = QApplication(args)
    app.setWindowIcon(QIcon(str(get_resource(":/icons/shutter.svg"))))

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
            proxy = ShutterKSC101Proxy()
            if not proxy.ping():
                description = "Could not connect to Shutter Control Server"
                info_text = (
                        "The GUI will start, but the connection button will show a disconnected state. "
                        "Please check if the Control Server is running and start the server if needed. "
                        "Otherwise, check if the correct HOSTNAME for the control server is set in the "
                        "Settings.yaml "
                        "configuration file."
                    )

                show_warning_message(description, info_text)

        view = ShutterUIView()
        model = ShutterUIModel(args.type)
        controller = ShutterUIController(model, view)

        view.show()
        return app.exec_()
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The KSC101 GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()


if __name__ == "__main__":
    sys.exit(main())
