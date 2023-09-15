"""
A Graphical User Interface for monitoring and commanding the Symétrie Gimbal.

Start the GUI from your terminal as follows:

    gimbal_ui [--type proxy|direct|simulator]

This GUI is based on the SYM_positioning application from Symétrie. The intent
is to provide operators a user interface which is platform independent, but
familiar.

The application is completely written in Python/Qt5 and can therefore run on any
platform that supports Python and Qt5.

"""
import argparse
import logging
import multiprocessing
import threading
from pathlib import Path

import sys
from PyQt5.QtCore import QLockFile

multiprocessing.current_process().name = "gimbal_ui"

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from prometheus_client import start_http_server

from egse.gui import show_warning_message
from egse.gui.led import Indic
from egse.gui.states import States
from egse.gimbal.symetrie.generic_gimbal_ui import ActuatorStates
from egse.gimbal.symetrie.generic_gimbal_ui import GimbalUIController
from egse.gimbal.symetrie.generic_gimbal_ui import GimbalUIModel
from egse.gimbal.symetrie.generic_gimbal_ui import GimbalUIView
from egse.gimbal.symetrie.gimbal import GimbalController
from egse.gimbal.symetrie.gimbal import GimbalProxy
from egse.gimbal.symetrie.gimbal import GimbalSimulator
from egse.process import ProcessStatus
from egse.resource import get_resource
from egse.settings import Settings
from egse.system import do_every

MODULE_LOGGER = logging.getLogger(__name__)

# Status LEDs define the number of status leds (length of the list), the description and the
# default color when the LED is on.

STATUS_LEDS = [
    ["Error", Indic.RED],  # bit 0
    ["System Initialized", Indic.GREEN],  # bit 1
    ["In position", Indic.GREEN],  # bit 2
    ["Amplifier enabled", Indic.GREEN],  # bit 3
    ["Homing done", Indic.GREEN],  # bit 4
    ["Brake on", Indic.GREEN],  # bit 5
    ["Emergency stop", Indic.ORANGE],  # bit 6
    ["Warning FE", Indic.ORANGE],  # bit 7
    ["Fatal FE", Indic.RED],  # bit 8
    ["Actuator Limit Error", Indic.RED],  # bit 9
    ["Amplifier Error", Indic.RED],  # bit 10
    ["Encoder error", Indic.RED],  # bit 11
    ["Phasing error", Indic.RED],  # bit 12
    ["Homing error", Indic.RED],  # bit 13
    ["Kinematic error", Indic.RED],  # bit 14
    ["Abort input error", Indic.RED],  # bit 15
    ["R/W memory error", Indic.RED],  # bit 16
    ["Temperature error", Indic.RED],  # bit 17
    ["Homing done (virtual)", Indic.ORANGE],  # bit 18
    ["Encoders power off", Indic.ORANGE],  # bit 19
    ["Limit switches power off", Indic.ORANGE],  # bit 20
    ["Reserved", Indic.BLACK],  # bit 21
    ["Reserved", Indic.BLACK],  # bit 22
    ["Reserved", Indic.BLACK],  # bit 23
]

# The index of the Control LED

CONTROL_ONOFF = 3

ACTUATOR_STATE_LABELS = [
    "In position",
    "Control loop on servo motors active",
    "Homing done",
    "Input “Home switch”",
    "Input “Positive limit switch”",
    "Input “Negative limit switch”",
    "Brake control output",
    "Following error (warning)",
    "Following error",
    "Actuator out of bounds error",
    "Amplifier error",
    "Encoder error",
    "Phasing error (brushless engine only)",
]

GUI_SETTINGS = Settings.load("GIMBAL GUI")

class GimbalUIView(GimbalUIView):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gimbal Controller")

        self.actuator_states = ActuatorStates(labels=ACTUATOR_STATE_LABELS)

        self.init_gui()

    def init_gui(self):

        # The main frame in which all the other frames are located, the outer Application frame

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        # The left part which shows the states and positions

        status_frame = QFrame()
        status_frame.setObjectName("StatusFrame")

        # The right part which has tabs that allow settings, movements, maintenance etc.

        tabs_frame = QFrame()
        tabs_frame.setObjectName("TabsFrame")

        # The states of the Gimbal (contains all the leds)

        states_frame = QFrame()
        states_frame.setObjectName("StatesFrame")

        # The user, machine positions and actuator lengths

        positions_frame = QFrame()
        positions_frame.setObjectName("PositionsFrame")

        hbox = QHBoxLayout()
        vbox_left = QVBoxLayout()
        vbox_right = QVBoxLayout()

        self.createToolbar()
        self.createStatusBar()

        self.states = States(STATUS_LEDS)

        user_positions_widget  = self.createUserPositionWidget()
        mach_positions_widget  = self.createMachinePositionWidget()
        actuator_length_widget = self.createActuatorLengthWidget()
        motor_temp_widget      = self.createMotorTemperatureWidget()

        vbox_right.addWidget(user_positions_widget)
        vbox_right.addWidget(mach_positions_widget)
        vbox_right.addWidget(actuator_length_widget)
        vbox_right.addWidget(motor_temp_widget)

        positions_frame.setLayout(vbox_right)

        vbox_left.addWidget(self.states)

        states_frame.setLayout(vbox_left)

        hbox.addWidget(states_frame)
        hbox.addWidget(positions_frame)

        status_frame.setLayout(hbox)

        tabbed_widget = self.create_tabbed_widget()

        hbox = QHBoxLayout()
        hbox.addWidget(tabbed_widget)
        tabs_frame.setLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(status_frame)
        hbox.addWidget(tabs_frame)

        app_frame.setLayout(hbox)

        self.setCentralWidget(app_frame)

    def update_status_bar(self, message=None, mode=None, timeout=2000):
        if message:
            self.statusBar().showMessage(message, msecs=timeout)
        if mode:
            self.mode_label.setStyleSheet(
                f"border: 0; " f"color: {'red' if mode == 'Simulator' else 'black'};"
            )
            self.mode_label.setText(f"mode: {mode}")
        self.statusBar().repaint()

    def updatePositions(self, userPositions, machinePositions, actuatorLengths):

        if userPositions is None:
            MODULE_LOGGER.warning("no userPositions passed into updatePositions(), returning.")
            return

        for upos in range(len(self.user_positions)):
            try:
                self.user_positions[upos][1].setText(f"{userPositions[upos]:10.4f}")
            except IndexError:
                MODULE_LOGGER.error(f"IndexError in user_positions, upos = {upos}")

        if machinePositions is None:
            MODULE_LOGGER.warning("no machinePositions passed into updatePositions(), returning.")
            return

        for mpos in range(len(self.mach_positions)):
            self.mach_positions[mpos][1].setText(f"{machinePositions[mpos]:10.4f}")

        if actuatorLengths is None:
            MODULE_LOGGER.warning("no actuatorLengths passed into updatePositions(), returning.")
            return

        for idx, alen in enumerate(self.actuator_lengths):
            alen[1].setText(f"{actuatorLengths[idx]:10.4f}")

    def updateTemperatures(self, temps):
        if temps is None or len(temps) != 2:
            for idx, mtemp in enumerate(self.motors):
                mtemp[1].setText(fr'N/A')
        else:
            for idx, mtemp in enumerate(self.motors):
                mtemp[1].setText(fr'{temps[idx]:.2f}')

    def updateStates(self, states):

        if states is None:
            return

        self.updateControlButton(states[CONTROL_ONOFF])
        self.states.set_states(states)

    def updateControlButton(self, flag):

        self.control.set_selected(on=flag)


class GimbalUIModel(GimbalUIModel):
    def __init__(self, connection_type):

        if connection_type == "proxy":
            device = GimbalProxy()
        elif connection_type == "direct":
            device = GimbalController()
            device.connect()
        elif connection_type == "simulator":
            device = GimbalSimulator()
        else:
            raise ValueError(
                f"Unknown type of Gimbal implementation passed into the model: {connection_type}"
            )

        super().__init__(connection_type, device)

        if device is not None:
            MODULE_LOGGER.debug(f"Gimbal initialized as {device.__class__.__name__}")

    def get_speed(self):
        sr, sr_min, sr_max = self.device.get_speed()
        return sr, sr_min, sr_max

class GimbalUIController(GimbalUIController):
    def __init__(self, model: GimbalUIModel, view: GimbalUIView):
        super().__init__(model, view)
        self.set_help_topic_home("gimbal_ui")

    def update_values(self):

        super().update_values()

        # Add here any updates to GIMBAL specific widgets


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
        help="Specify Gimbal implementation you want to connect to.",
        default="proxy",
    )
    parser.add_argument(
        "--profile",
        default=False,
        action="store_true",
        help="Enable info logging messages with method profile information.",
    )
    return parser.parse_args()


def main():
    lock_file = QLockFile(str(Path("~/gimbal_ui.app.lock").expanduser()))

    styles_location = get_resource(":/styles/default.qss")
    app_logo = get_resource(":/icons/logo-gimbal.svg")

    args = list(sys.argv)
    args[1:1] = ["-stylesheet", str(styles_location)]

    app = QApplication(args)
    app.setWindowIcon(QIcon(str(app_logo)))

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
            proxy = GimbalProxy()
            if not proxy.ping():
                description = "Could not connect to Gimbal Control Server"
                info_text = (
                    "The GUI will start, but the connection button will show a disconnected state. "
                    "Please check if the Control Server is running and start the server if needed. "
                    "Otherwise, check if the correct HOSTNAME for the control server is set in the "
                    "Settings.yaml "
                    "configuration file."
                )

                show_warning_message(description, info_text)

        view = GimbalUIView()
        model = GimbalUIModel(args.type)
        GimbalUIController(model, view)

        view.show()

        return app.exec_()
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The Gimbal GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)

    sys.exit(main())
