"""
A Graphical User Interface for monitoring and commanding the HUBER Stages.

Start the GUI from your terminal as follows:

    smc9300_ui [--type proxy|direct|simulator]

The application is completely written in Python/Qt5 and can therefore run on any
platform that supports Python and Qt5.

"""
import argparse
import logging
import multiprocessing
from pathlib import Path

import sys
import textwrap
import threading
from typing import Callable
from typing import Optional

from egse.stages.huber.smc9300 import HuberSMC9300Interface

multiprocessing.current_process().name = "smc9300_ui"

import pyqtgraph as pg
from PyQt5.QtCore import QSize, QLockFile
from PyQt5.QtCore import QTime
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QAction, QMessageBox
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from prometheus_client import Summary
from prometheus_client import start_http_server

from egse.decorators import deprecate
from egse.gui import VLine
from egse.gui import show_warning_message
from egse.gui.buttons import ToggleButton
from egse.gui.buttons import TouchButton
from egse.gui.limitswitch import Indic
from egse.gui.limitswitch import LimitSwitch
from egse.gui.stripchart import StripChart
from egse.help.help_ui import HELP_TOPICS
from egse.help.help_ui import HelpWindow
from egse.observer import Observable
from egse.observer import Observer
from egse.process import ProcessStatus
from egse.resource import get_resource
from egse.settings import Settings
from egse.stages.huber.smc9300 import HuberSMC9300Controller
from egse.stages.huber.smc9300 import HuberSMC9300Proxy
from egse.stages.huber.smc9300 import HuberSMC9300Simulator
from egse.state import UnknownStateError
from egse.system import do_every

MODULE_LOGGER = logging.getLogger(__name__)

SETTINGS = Settings.load("Huber Controller")
GUI_SETTINGS = Settings.load("SMC9300 GUI")

AXIS_NAMES = {
    SETTINGS.BIG_ROTATION_STAGE: "Big Rotation Stage",
    SETTINGS.SMALL_ROTATION_STAGE: "Small Rotation Stage",
    SETTINGS.TRANSLATION_STAGE: "Translation Stage",
}

AXIS_LABELS = {
    SETTINGS.BIG_ROTATION_STAGE: "ROT 01",
    SETTINGS.SMALL_ROTATION_STAGE: "ROT 02",
    SETTINGS.TRANSLATION_STAGE: "TRANS 03",
}


class Stage(QFrame, Observable):
    """
    Generic GUI Frame for one of the HUBER stages.

    Args:
        title: The full name of the stage
        label: A short label to identify the stage
        stage_nr: the integer ID for the stage
    """

    def __init__(self, title: str, label: str, stage_nr: int, unit: str, unit_long: str):

        super().__init__()

        self._title = title
        self._label = label
        self._stage_nr = stage_nr
        self._unit = unit
        self._unit_long = unit_long

        self._encoder_type = True

        self.current_position = None
        self.current_position_edit = None
        self.current_encoder_position = None

        self.movement_type = None
        self.move_button = None

        self.stripchart = None

        self.slew_speed_label: QLabel = QLabel()

        self.limit_switch_state: LimitSwitch = LimitSwitch(size=QSize(15, 15))

    def create_gui(self):

        toolbar = StageToolBar(connect=self.axis_settings)

        group_box = QGroupBox(self._title)

        # Create the label fields that display the current position and encoder values -------------

        grid_show = QGridLayout()
        grid_show.setSpacing(0)

        grid_show.addWidget(QLabel(self._label), 0, 0)

        self.current_position = QLabel(self)
        self.current_position.setAlignment(Qt.AlignRight)
        self.current_position.setText("0.0000")

        grid_show.addWidget(self.current_position, 0, 1)

        self.current_encoder_position = QLabel(self)
        self.current_encoder_position.setAlignment(Qt.AlignRight)
        self.current_encoder_position.setText("0.0000")
        self.current_encoder_position.setStyleSheet("font: 9pt;")
        self.current_encoder_position.mouseReleaseEvent = self.set_encoder_type

        grid_show.addWidget(self.current_encoder_position, 1, 1)

        grid_show.addWidget(QLabel(f" {self._unit}"), 0, 2)

        grid_show.setColumnStretch(1, 10)

        # Create the edit text field for setting the position --------------------------------------

        hbox_edit = QHBoxLayout()
        hbox_edit.setContentsMargins(0, 0, 0, 0)

        self.current_position_edit = QLineEdit(self)
        self.current_position_edit.setAlignment(Qt.AlignRight)
        self.current_position_edit.setText("0.0000")

        self.movement_type = QComboBox()

        self.movement_type.addItems(["Absolute", "Relative"])
        self.movement_type.setMinimumContentsLength(8)
        self.movement_type.adjustSize()

        self.move_button = QPushButton("Move To")
        self.move_button.setToolTip(
            "Perform a relative or absolute movement according to selection in the combobox."
            "<ul>"
            "<li><strong>Relative</strong> moves the stage relative to the current position"
            "<li><strong>Absolute</strong> moves the stage to the given absolute position"
            "</ul>"
        )
        self.move_button.clicked.connect(self.goto_position)

        hbox_edit.addWidget(QLabel("Set position: "))
        hbox_edit.addWidget(self.current_position_edit)
        hbox_edit.addWidget(QLabel(self._unit))
        hbox_edit.addWidget(self.movement_type)
        hbox_edit.addWidget(self.move_button)

        vbox = QVBoxLayout()
        vbox.setSpacing(4)
        vbox.addLayout(grid_show)
        vbox.addStretch(1)
        vbox.addLayout(hbox_edit)

        # Add a StripChart for this stage ----------------------------------------------------------

        self.stripchart = StripChart(
            labels={"left": ("Position", f"{self._unit_long}"), "bottom": ("Time", "hh:mm:ss")}
        )
        vbox.addWidget(self.stripchart)

        group_box.setLayout(vbox)

        # The settings box contains the view on the speed and other settings -----------------------

        settings_box = QHBoxLayout()

        settings_box.addWidget(self.limit_switch_state)
        settings_box.addWidget(QLabel("Speed:"))
        settings_box.addWidget(self.slew_speed_label)
        settings_box.addStretch()

        vbox = QVBoxLayout()
        vbox.setSpacing(4)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(toolbar)
        vbox.addWidget(group_box)
        vbox.addLayout(settings_box)
        self.setLayout(vbox)

    def axis_settings(self):
        MODULE_LOGGER.info(f"Handle settings for axis {self._stage_nr}.")
        settings = SettingsDialog(self._stage_nr, self.slew_speed_label.text(), parent=self)
        if rc := settings.exec():
            slew_speed = int(settings.speed_box.text())
            MODULE_LOGGER.debug(f"{rc=}, {slew_speed=}")
            self.actionObservers({"set_speed": (self._stage_nr, slew_speed)})

    def goto_position(self):
        new_position = float(self.current_position_edit.text())
        movement_type = self.movement_type.currentText()

        cmd = "move_absolute" if movement_type == "Absolute" else "move_relative"

        self.actionObservers({cmd: [self._stage_nr, new_position]})

    def set_encoder_type(self, event):
        self._encoder_type = not self._encoder_type

    def update_encoder_position(self, position, counter):
        if self._encoder_type:
            self.current_encoder_position.setText(f"{position:.6f}")
        else:
            self.current_encoder_position.setText(f"{counter:.0f}")

    def update_current_position(self, position):
        self.current_position.setText(f"{position:.4f}")

    def update_speed(self, speed):
        self.slew_speed_label.setText(f"{speed}")

    def update_limit_switch_state(self, state: int):
        self.limit_switch_state.set_state(Indic.from_state(state))

    def update_stripchart(self, time, position):
        self.stripchart.update(time, position)


class BigRotationStage(Stage):
    def __init__(self):
        super().__init__(
            AXIS_NAMES[SETTINGS.BIG_ROTATION_STAGE],
            AXIS_LABELS[SETTINGS.BIG_ROTATION_STAGE],
            SETTINGS.BIG_ROTATION_STAGE,
            unit="deg", unit_long="degrees",
        )
        self.create_gui()


class SmallRotationStage(Stage):
    def __init__(self):
        super().__init__(
            AXIS_NAMES[SETTINGS.SMALL_ROTATION_STAGE],
            AXIS_LABELS[SETTINGS.SMALL_ROTATION_STAGE],
            SETTINGS.SMALL_ROTATION_STAGE,
            unit="deg", unit_long="degrees",
        )
        self.create_gui()


class TranslationStage(Stage):
    def __init__(self):
        super().__init__(
            AXIS_NAMES[SETTINGS.TRANSLATION_STAGE],
            AXIS_LABELS[SETTINGS.TRANSLATION_STAGE],
            SETTINGS.TRANSLATION_STAGE,
            unit="mm", unit_long="millimeter",
        )
        self.create_gui()


class StageToolBar(QFrame):
    def __init__(self, connect: Callable = None, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        toolbar_hbox = QHBoxLayout()
        toolbar_hbox.setContentsMargins(0, 0, 0, 0)
        toolbar_hbox.addWidget(spacer)
        toolbar_hbox.setAlignment(Qt.AlignVCenter)

        br_settings = TouchButton(
            width=25, height=25, selected=get_resource(":/icons/settings.svg"),
            parent=self
        )
        br_settings.clicked.connect(connect)

        br_time_window = QComboBox(parent=self)
        br_time_window.addItems(["5s", "10m", "1h", "12h"])
        br_time_window.setCurrentIndex(1)

        toolbar_hbox.addWidget(br_time_window)
        toolbar_hbox.addWidget(br_settings)

        self.setLayout(toolbar_hbox)
        self.setContentsMargins(0, 0, 0, 0)


class HuberUIView(QMainWindow, Observable):
    def __init__(self):
        super().__init__()

        # Define those variables that we will need/use in different methods

        self.homing_action = None
        self.clear_action = None
        self.reconnect_action = None
        self.toolbar = None

        self.homing = None
        self.clear_errors = None
        self.cs_connection = None
        self.device_connection = None
        self.stop_action = None
        self.help_action = None

        # Switch to using white background and black foreground for pyqtgraph stripcharts
        # This must be done before the pyqtgraphs are created.

        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")

        self.big_rotation_stage = BigRotationStage()
        self.small_rotation_stage = SmallRotationStage()
        self.translation_stage = TranslationStage()

        self.setGeometry(300, 300, 1500, 500)
        self.setWindowTitle("Huber Controller")

        # The mode_label describes the current mode in which the controller is running.
        # The mode can be Proxy, Simulator, Direct

        self.mode_label = QLabel("")

        self.axes = {
            SETTINGS.BIG_ROTATION_STAGE: self.big_rotation_stage,
            SETTINGS.SMALL_ROTATION_STAGE: self.small_rotation_stage,
            SETTINGS.TRANSLATION_STAGE: self.translation_stage,
        }

        # The main frame in which all the other frames are located, the outer Application frame

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        hbox = QHBoxLayout()

        self.create_toolbar()
        self.create_status_bar()

        hbox.addWidget(self.big_rotation_stage)
        hbox.addWidget(self.small_rotation_stage)
        hbox.addWidget(self.translation_stage)

        app_frame.setLayout(hbox)

        self.setCentralWidget(app_frame)

    def addObserver(self, observer):
        super().addObserver(observer)
        self.big_rotation_stage.addObserver(observer)
        self.small_rotation_stage.addObserver(observer)
        self.translation_stage.addObserver(observer)

    def is_cs_action_enabled(self):
        return self.cs_connection.isEnabled()

    def disable_cs_action(self):
        self.cs_connection.disable()

    def enable_cs_action(self):
        self.cs_connection.enable()

    def check_cs_action(self):
        self.cs_connection.set_selected()

    def uncheck_cs_action(self):
        self.cs_connection.set_selected(False)

    def check_device_action(self):
        self.device_connection.set_selected()

    def uncheck_device_action(self):
        self.device_connection.set_selected(False)

    def set_connection_state(self, state):
        # enable or disable all actions that involve a device or cs connection
        # don't change the action buttons for the device nor the cs, that is handled
        # in the caller because it might be a device connection loss that causes this state
        # or a control server, or both...

        MODULE_LOGGER.debug(f"{state=}")

        if state == "connected":
            self.homing.enable()
            self.clear_errors.enable()
        elif state == "disconnected":
            self.homing.disable()
            self.clear_errors.disable()
        else:
            raise UnknownStateError(
                f"Unknown State ({state}), expected 'connected' or 'disconnected'."
            )

    def create_status_bar(self):

        self.statusBar().setStyleSheet("border: 0; background-color: #FFF8DC;")
        self.statusBar().setStyleSheet("QStatusBar::item {border: none;}")
        self.statusBar().addPermanentWidget(VLine())
        self.statusBar().addPermanentWidget(self.mode_label)

    def create_toolbar(self):

        # The Home action is used to command the Homing to the Hexapod.

        self.homing = TouchButton(
            name="HOMING",
            status_tip="perform a homing operation (ON ALL THE STAGES)",
            selected=get_resource(":/icons/home.svg"),
            disabled=get_resource(":/icons/home-disabled.svg"),
        )
        self.homing.clicked.connect(self.on_click)

        # The Clear action is used to command the ClearErrors to the Hexapod.

        self.clear_errors = TouchButton(
            name="CLEAR-ERRORS",
            status_tip="clear the error list on the controller (FOR ALL STAGES)",
            selected=get_resource(":/icons/erase.svg"),
            disabled=get_resource(":/icons/erase-disabled.svg"),
        )
        self.clear_errors.clicked.connect(self.on_click)

        # The Reconnect action is used to reconnect to the control server

        self.cs_connection = ToggleButton(
            name="CS-CONNECT",
            status_tip="connect-disconnect huber stages control server.",
            selected=get_resource(":/icons/cs-connected.svg"),
            not_selected=get_resource(":/icons/cs-not-connected.svg"),
            disabled=get_resource(":/icons/cs-connected-disabled.svg")
        )
        self.cs_connection.clicked.connect(self.on_click)

        # The Reconnect action is used to reconnect the device

        self.device_connection = ToggleButton(
            name="DEVICE-CONNECT",
            status_tip="connect-disconnect the huber stages controller",
            selected=get_resource(":/icons/plugged.svg"),
            not_selected=get_resource(":/icons/unplugged.svg"),
            disabled=get_resource(":/icons/plugged-disabled.svg")
        )
        self.device_connection.clicked.connect(self.on_click)

        # The STOP button is used to immediately stop the current motion

        stop_button = QIcon(str(get_resource(":/icons/stop.svg")))

        self.stop_action = QAction(stop_button, "STOP", self)
        self.stop_action.setToolTip("STOP Movement")
        self.stop_action.triggered.connect(self.on_click)

        # The HELP button is used to show the on-line help in a browser window

        help_button = QIcon(str(get_resource(":/icons/info.svg")))

        self.help_action = QAction(help_button, "INFO", self)
        self.help_action.setToolTip("Browse the on-line documentation")
        self.help_action.triggered.connect(self.on_click)

        # spacer widget to help with aligning STOP button to the right

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.toolbar = self.addToolBar("MainToolbar")
        self.toolbar.addWidget(self.homing)
        self.toolbar.addWidget(self.clear_errors)
        self.toolbar.addWidget(self.device_connection)
        self.toolbar.addWidget(self.cs_connection)
        self.toolbar.addWidget(spacer)
        self.toolbar.addAction(self.stop_action)
        self.toolbar.addAction(self.help_action)

        return self.toolbar

    def update_stripchart(self, axis, time, pos):
        self.axes[axis].stripchart.update(time, pos)

    def update_status_bar(self, message=None, mode=None, timeout=2000):
        if message:
            self.statusBar().showMessage(message, msecs=timeout)
        if mode:
            self.mode_label.setStyleSheet(
                f"border: 0; " f"color: {'red' if 'Simulator' in mode else 'black'};"
            )
            self.mode_label.setText(f"mode: {mode}")
        self.statusBar().repaint()

    def update_position(self, axis, position):
        self.axes[axis].update_current_position(position)

    def update_speed(self, axis, speed):
        self.axes[axis].update_speed(speed)

    def update_encoder_position(self, axis, position, counter):
        self.axes[axis].update_encoder_position(position, counter)

    def on_click(self):

        sender = self.sender()

        # MODULE_LOGGER.debug(f"sender.text() = {sender.text()}")
        # MODULE_LOGGER.debug(f"sender.isChecked() = {sender.isChecked()}")

        self.notifyObservers(sender)


class SettingsDialog(QDialog):

    def __init__(self, axis: int, speed: int,  parent=None):  # <1>
        super().__init__(parent)

        self.axis = axis
        self.speed = speed

        self.setWindowTitle(f"Settings for {AXIS_NAMES[axis]}")

        self.buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(self.buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        hbox = QHBoxLayout()
        message = QLabel("Slew speed:")
        self.speed_box = QLineEdit(f"{self.speed}")
        self.speed_box.setValidator(QIntValidator())
        hbox.addWidget(message)
        hbox.addWidget(self.speed_box)
        self.layout.addLayout(hbox)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class CustomErrorDialog(QDialog):
    def __init__(self, exc: Exception, parent=None):
        super().__init__(parent)

        self.exc = exc

        self.title = f"{exc.__class__.__name__}"
        self.setWindowTitle(self.title)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        message = QLabel(
            textwrap.dedent(
                f"""\
            We caught a {self.exc.__class__.__name__}: 

               {self.exc.args[0]}

            """
            ))
        self.layout.addWidget(message)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)


class HuberUIController(Observer):
    def __init__(self, model, view):
        self.model = model
        self.view: HuberUIView = view
        self.view.addObserver(self)

        self.help_window = HelpWindow(topic_url=HELP_TOPICS["smc9300_ui"])

        self._metrics = {
            "execution_time": Summary('ui_update_execution_time_seconds',
                                      'Time spent updating the values in the GUI', ["type"]),
        }

        self.states_capture_timer = None
        self.states_capture_timer_interval = GUI_SETTINGS.STATES_TIMER_INTERVAL
        self.stripchart_timer = None
        self.stripchart_timer_interval = GUI_SETTINGS.STRIPCHART_TIMER_INTERVAL
        self.create_timer()

        try:
            if self.model.is_device_connected():
                mode = self.model.connection_type.capitalize()
                if self.model.is_simulator():
                    mode = f"{mode} [Simulator]"
                self.view.update_status_bar(mode=mode)
                self.view.check_device_action()
            else:
                self.view.uncheck_device_action()

            if self.model.is_cs_connected():
                self.view.check_cs_action()
            else:
                self.view.uncheck_cs_action()

            MODULE_LOGGER.debug(f"{self.model.is_device_connected()=}, {self.model.is_cs_connected()=}")

            if model.connection_type in ["direct", "simulator"]:
                view.disable_cs_action()

            if self.has_connection():
                self.view.set_connection_state("connected")
                self.start_timer()
            else:
                self.view.set_connection_state("disconnected")
                self.stop_timer()
        except NotImplementedError:
            MODULE_LOGGER.warning(
                "There was no connection to the control server during startup, "
                "GUI starts in disconnected mode."
            )
            self.view.uncheck_cs_action()
            self.view.uncheck_device_action()
            self.view.set_connection_state("disconnected")

    def has_connection(self):
        """
        Returns True if the controller has a connection to the device. This takes into account
        that the control server might be disabled when the controller is directly connected to
        the device or to a simulator.
        """
        if self.view.is_cs_action_enabled():
            return bool(self.model.is_device_connected() and self.model.is_cs_connected())
        else:
            return bool(self.model.is_device_connected())

    def create_timer(self):
        """Create a Timer that will update the States every second."""

        self.states_capture_timer = QTimer()
        self.states_capture_timer.timeout.connect(self.update_values)
        self.states_capture_timer.setInterval(self.states_capture_timer_interval)

        self.stripchart_timer = QTimer()
        self.stripchart_timer.timeout.connect(self.update_stripcharts)
        self.stripchart_timer.setInterval(self.stripchart_timer_interval)

    def start_timer(self):
        self.states_capture_timer.start()
        self.stripchart_timer.start()

    def stop_timer(self):
        self.states_capture_timer.stop()
        self.stripchart_timer.stop()

    def update_values(self):

        with self._metrics["execution_time"].labels(type="values").time():
            # This method should not be called when not connected, by design!

            for axis in (
                SETTINGS.BIG_ROTATION_STAGE,
                SETTINGS.SMALL_ROTATION_STAGE,
                SETTINGS.TRANSLATION_STAGE,
            ):
                # If there is a communication problem with the server, resulting in a None being
                # returned, we skip also the other updates.
                if (pos := self.model.get_current_position(axis)) is None:
                    continue
                self.view.update_position(axis, pos)

                speed = self.model.get_speed(axis)
                self.view.axes[axis].update_speed(speed)

                pos = self.model.get_current_encoder_position(axis)
                cnt = self.model.get_current_encoder_counter_value(axis)
                self.view.update_encoder_position(axis, pos, cnt)

                state = self.model.get_state(axis)
                self.view.axes[axis].update_limit_switch_state(state)

    def update_stripcharts(self):

        with self._metrics["execution_time"].labels(type="stripcharts").time():
            for axis in (
                SETTINGS.BIG_ROTATION_STAGE,
                SETTINGS.SMALL_ROTATION_STAGE,
                SETTINGS.TRANSLATION_STAGE,
            ):
                if (pos := self.model.get_current_position(axis)) is None:
                    continue
                self.view.update_stripchart(axis, QTime.currentTime().msecsSinceStartOfDay(), pos)

    def update(self, changed_object):
        # This method is part of the Observer protocol and will be called when there is a
        # notification of a change in the Observable.

        text = changed_object.text()

        if text == "STOP":
            self.model.stop()

        if text == "INFO":
            self.help_window.show()

        if text == "CS-CONNECT":
            if changed_object.is_selected():
                MODULE_LOGGER.debug("Reconnecting the HUBER Stages Control Server.")
                self.model.reconnect_cs()
                if not self.model.has_commands():
                    self.model.load_commands()
                self.start_timer()
                if self.model.is_device_connected() and self.model.is_cs_connected():
                    self.view.set_connection_state("connected")
                    self.view.device_connection.enable()
            else:
                MODULE_LOGGER.debug("Disconnecting the HUBER Stages Control Server.")
                self.stop_timer()
                self.model.disconnect_cs()
                self.view.device_connection.disable()
                self.view.set_connection_state("disconnected")
            return

        if text == "DEVICE-CONNECT":
            print(f"Pressed {text}")

            if changed_object.is_selected():
                MODULE_LOGGER.debug("Reconnecting the HUBER Stages controller.")
                if self.model.reconnect_device():
                    self.view.set_connection_state("connected")
                    if not self.model.has_commands():
                        self.model.load_commands()
                    self.start_timer()
                else:
                    self.view.device_connection.set_selected(False)
            else:
                MODULE_LOGGER.debug("Disconnecting the HUBER Stages Controller.")
                self.stop_timer()
                self.model.disconnect()
                self.view.set_connection_state("disconnected")
            return

        if text == "HOMING":
            self.model.homing()
            return

        if text == "CLEAR-ERRORS":
            self.model.clear_error()
            return

    def do(self, actions):
        # This method is part of the Observer protocol and will be called when there is a
        # action requested by the Observable.

        for action, value in actions.items():
            MODULE_LOGGER.debug(f"do {action} with {value}")
            if action == "move_absolute":
                axis, position = value
                # MODULE_LOGGER.info(f"do: goto({axis}, {position})")
                try:
                    self.model.goto(axis, position)
                except ValueError as exc:
                    dialog = CustomErrorDialog(exc, parent=self.view)
                    dialog.exec_()
            elif action == "move_relative":
                axis, distance = value
                # MODULE_LOGGER.info(f"do: move({axis}, {distance})")
                self.model.move(axis, distance)
            elif action == "set_speed":
                axis, speed = value
                # MODULE_LOGGER.info(f"do: set_speed({axis=}, {speed=})")
                self.model.set_speed(axis, speed)


class HuberUIModel:
    def __init__(self, type_):
        self.connection_type = type_

        self.huber: HuberSMC9300Interface

        if self.connection_type == "proxy":
            self.huber = HuberSMC9300Proxy()
        elif self.connection_type == "direct":
            self.huber = HuberSMC9300Controller()
            self.huber.connect()
        elif self.connection_type == "simulator":
            self.huber = HuberSMC9300Simulator()
        else:
            raise ValueError(f"Unknown type of Huber implementation passed into the model: {type}")

        if self.huber is not None:
            MODULE_LOGGER.debug(f"HUBER Controller initialized as {self.huber.__class__.__name__}")

    def has_commands(self):
        if self.connection_type == "proxy":
            return True  # with the new dynamic_command decorator there are always commands
        return True

    def load_commands(self):
        if self.connection_type == "proxy":
            return  # no need anymore to load commands

    def is_simulator(self):
        return self.huber.is_simulator()

    def is_cs_connected(self):
        return self.huber.is_cs_connected() if self.connection_type == "proxy" else False

    def is_device_connected(self):
        return self.huber.is_connected()

    def goto(self, axis, position):
        self.huber.goto(axis=axis, position=position, wait=False)

    def move(self, axis, value):
        self.huber.move(axis=axis, distance=value, wait=False)

    def homing(self):
        MODULE_LOGGER.warning("Homing done for all HUBER stages.")
        self.huber.goto(axis=SETTINGS.BIG_ROTATION_STAGE, position=0.0, wait=False)
        self.huber.goto(axis=SETTINGS.SMALL_ROTATION_STAGE, position=0.0, wait=False)
        self.huber.goto(axis=SETTINGS.TRANSLATION_STAGE, position=0.0, wait=False)

    def clear_error(self):
        MODULE_LOGGER.warning("Clearing errors is done for all HUBER stages.")
        self.huber.clear_error(SETTINGS.BIG_ROTATION_STAGE)
        self.huber.clear_error(SETTINGS.SMALL_ROTATION_STAGE)
        self.huber.clear_error(SETTINGS.TRANSLATION_STAGE)

    def stop(self):
        MODULE_LOGGER.warning("STOP immediately terminates all HUBER stages.")
        self.huber.quit()

    @deprecate(alternative="reconnect_device")
    def reconnect(self):
        self.reconnect_device()

    def reconnect_device(self):
        self.huber.reconnect()
        return self.huber.is_connected()

    def reconnect_cs(self):
        self.huber.reconnect_cs()
        return self.huber.is_cs_connected()

    def disconnect(self):
        self.huber.disconnect()

    def disconnect_cs(self):
        self.huber.disconnect_cs()

    def get_speed(self, axis):
        return self.huber.get_slew_speed(axis)

    def set_speed(self, axis, speed):
        return self.huber.set_slew_speed(axis, speed)

    def get_current_position(self, axis):
        return self.huber.get_current_position(axis)

    def get_current_encoder_position(self, axis):
        return self.huber.get_current_encoder_position(axis)

    def get_current_encoder_counter_value(self, axis):
        return self.huber.get_current_encoder_counter_value(axis)

    def get_state(self, axis) -> int:
        return self.huber.get_state(axis)


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
        help="Specify Huber implementation you want to connect to.",
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
    lock_file = QLockFile(str(Path("~/scm9300_ui.app.lock").expanduser()))
    styles_location = get_resource(":/styles/default.qss")
    app_logo = get_resource(":/icons/logo-huber.svg")

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
            proxy = HuberSMC9300Proxy()
            if not proxy.ping():
                description = "Could not connect to Stages Control Server"
                info_text = (
                    "The GUI will start, but the connection button will show a disconnected state. "
                    "Please check if the Control Server is running and start the server if needed. "
                    "Otherwise, check if the correct HOSTNAME for the control server is set in the "
                    "Settings.yaml "
                    "configuration file."
                )

                show_warning_message(description, info_text)

        view = HuberUIView()
        model = HuberUIModel(args.type)
        HuberUIController(model, view)

        view.show()
        sys.exit(app.exec_())
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The SCM9300 GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()


if __name__ == "__main__":
    main()
