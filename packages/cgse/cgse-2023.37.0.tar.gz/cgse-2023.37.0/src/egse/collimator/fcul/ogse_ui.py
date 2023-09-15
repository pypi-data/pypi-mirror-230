import logging
import multiprocessing
import os
from pathlib import Path

import sys
import threading
from typing import Optional
from typing import Tuple
from typing import Union

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QLockFile
from PyQt5.QtCore import QRunnable
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QSlider
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from prometheus_client import start_http_server
from zmq import ZMQError

from egse.collimator.fcul.ogse import OGSEProxy
from egse.decorators import timer
from egse.gui import VLine
from egse.gui.buttons import BUTTON_SELECTED
from egse.gui.buttons import ToggleButton
from egse.gui.buttons import TouchButton
from egse.gui.led import Indic
from egse.gui.led import ShapeEnum
from egse.gui.states import States
from egse.help.help_ui import HELP_TOPICS
from egse.help.help_ui import HelpWindow
from egse.observer import Observable
from egse.observer import Observer
from egse.settings import Settings
from egse.state import UnknownStateError

multiprocessing.current_process().name = "ogse_ui"

from egse.process import ProcessStatus
from egse.resource import get_resource
from egse.system import do_every


MODULE_LOGGER = logging.getLogger("egse.collimator.fcul.ogse_ui")

GUI_SETTINGS = Settings.load("OGSE GUI")

TITLE_FONT_SIZE = 18


class ConfirmationBox(QMessageBox):
    def __init__(self, text: str, title=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(text)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)


class OGSETUIView:
    ...


STATES = [
    ["Interlock", Indic.BLACK],
    ["Power", Indic.BLACK],
    ["Laser", Indic.BLACK],
    ["Lamp", Indic.BLACK],
    ["PSU", Indic.BLACK],
    ["LDLS", Indic.GREEN],
    ["FW moving", Indic.BLACK],
]

FAULTS = [
    ["Lamp Fault", Indic.GREEN],
    ["Controller Fault", Indic.GREEN],
]


class StatusWidget(QWidget):
    def __init__(self):
        super().__init__()

        vbox = QVBoxLayout()

        self.title = QLabel("Status")
        font = self.title.font()
        font.setPointSize(TITLE_FONT_SIZE)
        font.setBold(True)
        self.title.setFont(font)

        self.states = States(STATES, shape=ShapeEnum.SQUARE, title=None)

        vbox.addWidget(self.title, alignment=QtCore.Qt.AlignHCenter)
        vbox.addWidget(self.states)

        self.setLayout(vbox)


class FaultsWidget(QWidget):
    def __init__(self):
        super().__init__()

        vbox = QVBoxLayout()

        self.title = QLabel("Fault Detection")
        font = self.title.font()
        font.setPointSize(TITLE_FONT_SIZE)
        font.setBold(True)
        self.title.setFont(font)

        self.states = States(FAULTS, shape=ShapeEnum.SQUARE, title=None)

        vbox.addWidget(self.title, alignment=QtCore.Qt.AlignHCenter)
        vbox.addWidget(self.states)

        self.setLayout(vbox)


class AttenuationWidget(QWidget):
    def __init__(self):
        super().__init__()

        vbox = QVBoxLayout()

        self.title = QLabel("Attenuation Values")
        font = self.title.font()
        font.setPointSize(TITLE_FONT_SIZE)
        font.setBold(True)
        self.title.setFont(font)

        vbox.addWidget(self.title, alignment=QtCore.Qt.AlignHCenter)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 20, 0, 0)

        labels_vbox = QVBoxLayout()
        labels_vbox.addWidget(QLabel("Index:"))
        labels_vbox.addWidget(QLabel("Factor:"))
        hbox.addLayout(labels_vbox)

        self.index = QLabel()
        self.factor = QLabel()

        values_vbox = QVBoxLayout()
        values_vbox.addWidget(self.index, alignment=QtCore.Qt.AlignRight)
        values_vbox.addWidget(self.factor, alignment=QtCore.Qt.AlignRight)
        hbox.addLayout(values_vbox)

        vbox.addLayout(hbox)

        self.setLayout(vbox)


class PowerMeterWidget(QWidget):
    def __init__(self):
        super().__init__()

        vbox = QVBoxLayout()

        self.title = QLabel("Power Meter")
        font = self.title.font()
        font.setPointSize(TITLE_FONT_SIZE)
        font.setBold(True)
        self.title.setFont(font)

        vbox.addWidget(self.title, alignment=QtCore.Qt.AlignHCenter)

        vbox_labels = QVBoxLayout()
        vbox_values_1 = QVBoxLayout()
        vbox_units_1 = QVBoxLayout()
        vbox_values_2 = QVBoxLayout()
        vbox_units_2 = QVBoxLayout()

        hbox = QHBoxLayout()

        self.power_meter_info = [
            [QLabel("PM1"), QLabel(), QLabel("Watt"), QLabel(), QLabel("ºC")],
            [QLabel("PM2"), QLabel(), QLabel("Watt"), QLabel(), QLabel("ºC")],
        ]

        for pw in self.power_meter_info:
            vbox_labels.addWidget(pw[0])

            vbox_values_1.addWidget(pw[1])
            pw[1].setStyleSheet("QLabel { background-color : White; }")
            pw[1].setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            pw[1].setMinimumWidth(80)

            vbox_units_1.addWidget(pw[2])

            vbox_values_2.addWidget(pw[3])
            pw[3].setStyleSheet("QLabel { background-color : White; }")
            pw[3].setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            pw[3].setMinimumWidth(80)

            vbox_units_2.addWidget(pw[4])

        # Make sure the labels stay nicely together when vertically resizing the Frame.
        for w in vbox_labels, vbox_values_1, vbox_units_1, vbox_values_2, vbox_units_2:
            w.addStretch(1)

        hbox.addLayout(vbox_labels)
        hbox.addLayout(vbox_values_1)
        hbox.addLayout(vbox_units_1)
        hbox.addLayout(vbox_values_2)
        hbox.addLayout(vbox_units_2)

        # Make sure the leds and labels stay nicely together when horizontally resizing the Frame.
        hbox.addStretch(1)

        gbox = QGroupBox(self)
        gbox.setLayout(hbox)

        vbox.addWidget(gbox)
        self.setLayout(vbox)

    @property
    def power_1(self) -> str:
        return self.power_meter_info[0][1].text()

    @power_1.setter
    def power_1(self, value: str):
        self.power_meter_info[0][1].setText(value)

    @property
    def power_2(self) -> str:
        return self.power_meter_info[1][1].text()

    @power_2.setter
    def power_2(self, value: str):
        self.power_meter_info[1][1].setText(value)

    @property
    def temp_1(self) -> str:
        return self.power_meter_info[0][3].text()

    @temp_1.setter
    def temp_1(self, value: str):
        self.power_meter_info[0][3].setText(value)

    @property
    def temp_2(self) -> str:
        return self.power_meter_info[1][3].text()

    @temp_2.setter
    def temp_2(self, value: str):
        self.power_meter_info[1][3].setText(value)


class CommandWidget(QWidget):
    def __init__(self, *, observable):
        super().__init__()
        self.observable = observable

        power_label = QLabel("Power")
        operate_label = QLabel("Operate")
        att_label = QLabel("Attenuation")

        self.cmd_power = ToggleButton(
            name="POWER-ON-OFF",
            width=50, height=25,
            status_tip="Power ON or OFF",
            selected=get_resource(":/icons/switch-on-square.svg"),
            not_selected=get_resource(":/icons/switch-off-square.svg"),
            disabled=get_resource(":/icons/switch-disabled-square.svg"),
        )
        # To avoid repainting the on-off button, we monkey patch the mouseReleaseEvent to a function
        # that does nothing, not even calling its super() method.
        self.cmd_power.mouseReleaseEvent = lambda x: None
        # We want to use the pressed signal here instead of the clicked to avoid repainting the
        # button before the confirmation is asked (see self.on_press)
        self.cmd_power.pressed.connect(self.on_press)

        self.cmd_operate = ToggleButton(
            name="OPERATE-ON-OFF",
            width=50, height=25,
            status_tip="Operate ON or OFF",
            selected=get_resource(":/icons/switch-on-square.svg"),
            not_selected=get_resource(":/icons/switch-off-square.svg"),
            disabled=get_resource(":/icons/switch-disabled-square.svg"),
        )
        self.cmd_operate.clicked.connect(self.on_click)

        self.att_go_button = TouchButton(
            name="ATTENUATION-GO",
            width=25, height=25,
            status_tip="Set the selected attenuation index",
            selected=get_resource(":/icons/small-buttons-go.svg")
        )
        self.att_go_button.clicked.connect(self.on_click)

        self.att_plus_button = TouchButton(
            name="ATTENUATION-PLUS",
            width=15, height=15,
            status_tip="Increase the selected attenuation index",
            selected=get_resource(":/icons/small-buttons-plus.svg")
        )
        self.att_plus_button.clicked.connect(self.on_click)

        self.att_minus_button = TouchButton(
            name="ATTENUATION-MINUS",
            width=15, height=15,
            status_tip="Decrease the selected attenuation index",
            selected=get_resource(":/icons/small-buttons-minus.svg")
        )
        self.att_minus_button.clicked.connect(self.on_click)

        self.att_index_slider = QSlider(QtCore.Qt.Horizontal)
        self.att_index_slider.setMinimum(0)
        self.att_index_slider.setMaximum(46)
        self.att_index_slider.setSingleStep(1)
        self.att_index_slider.setMinimumWidth(47*2)

        # sliderMoved is needed for updating the label
        self.att_index_slider.valueChanged.connect(self.slider_value_changed)
        # sliderReleased is used for
        self.att_index_slider.sliderReleased.connect(self.slider_released)

        self.att_index_slider_position = QLabel()
        self.att_index_slider_position.setMinimumWidth(20)

        layout = QVBoxLayout()

        self.title = QLabel("Commanding")
        font = self.title.font()
        font.setPointSize(TITLE_FONT_SIZE)
        font.setBold(True)
        self.title.setFont(font)

        layout.addWidget(self.title, alignment=QtCore.Qt.AlignHCenter)

        hbox = QHBoxLayout()
        hbox.addWidget(power_label)
        hbox.addWidget(self.cmd_power)
        layout.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(operate_label)
        hbox.addWidget(self.cmd_operate)
        layout.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(att_label)
        hbox.addWidget(self.att_minus_button)
        hbox.addWidget(self.att_index_slider)
        hbox.addWidget(self.att_plus_button)
        hbox.addWidget(self.att_index_slider_position)
        hbox.addWidget(self.att_go_button)
        hbox.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(hbox)

        layout.addStretch()

        hbox = QHBoxLayout()
        hbox.addLayout(layout)
        hbox.addStretch()

        self.setLayout(hbox)

    def disable_commanding(self):
        self.cmd_operate.disable()

    def enable_commanding(self):
        self.cmd_operate.enable()

    def on_click(self, icon: Union[QIcon, bool]):
        # MODULE_LOGGER.info(f"in {self.__class__.__name__}.on_click()")

        sender = self.sender()

        # MODULE_LOGGER.info(f"in {self.__class__.__name__} {sender=!s}")

        # MODULE_LOGGER.info(f"type(sender) = {type(sender)}")
        # MODULE_LOGGER.info(f"sender.text() = {sender.text()}")
        # MODULE_LOGGER.info(f"sender.isCheckable() = {sender.isCheckable()}")
        # MODULE_LOGGER.info(f"sender.isChecked() = {sender.isChecked()}")
        # MODULE_LOGGER.info(f"{type(icon) = }, {icon = }")

        # This will trigger the update() method on all the observers

        self.observable.notifyObservers(sender)

    def slider_moved(self, pos):
        self.att_index_slider_position.setText(str(pos))
        # MODULE_LOGGER.info(f"slider_moved: {pos = }")

    def slider_pressed(self):
        pos = self.att_index_slider_position.text()
        # MODULE_LOGGER.info(f"slider_pressed: {pos = }")

    def slider_released(self):
        pos = self.att_index_slider_position.text()
        # MODULE_LOGGER.info(f"slider_released: {pos = }")

    def slider_value_changed(self, pos):
        self.att_index_slider_position.setText(str(pos))
        # MODULE_LOGGER.info(f"slider_value_changed: {pos = }")

    def on_press(self):
        # MODULE_LOGGER.info(f"in {self.__class__.__name__}.on_press()")

        sender = self.sender()

        # MODULE_LOGGER.info(f"in {self.__class__.__name__} {sender=!s}")

        if sender.is_selected():
            response = QMessageBox.question(
                self,
                "Confirmation Required",
                "Are you sure to power OFF the OGSE?",
            )
            if response == QMessageBox.Yes:
                self.cmd_power.set_selected(False)
                self.observable.notifyObservers(sender)
        else:
            self.cmd_power.set_selected(True)
            self.observable.notifyObservers(sender)


class OGSEGUIView(QMainWindow, Observable):
    def __init__(self):
        super().__init__()

        self.status_puller = None
        self.threadpool = QThreadPool()

        self.cs_connection: ToggleButton = ...
        self.device_connection: ToggleButton = ...
        self.help_action: QAction = ...
        self.toolbar: QToolBar = ...
        self.on_off_button: ToggleButton = ...

        self.setWindowTitle("OGSE Controller GUI")
        self.setGeometry(300, 300, 600, 300)

        # The mode_label describes the current mode in which the controller is running.
        # The mode can be Proxy, Simulator, Direct

        self.mode_label = QLabel("")

        self.create_toolbar()
        self.create_status_bar()

        self.status = StatusWidget()
        self.power_meter = PowerMeterWidget()
        self.faults = FaultsWidget()
        self.commanding = CommandWidget(observable=self)
        self.attenuation = AttenuationWidget()

        layout = QHBoxLayout()
        #
        # vbox_layout = QVBoxLayout()
        # vbox_layout.addWidget(self.power_meter)
        # vbox_layout.addWidget(self.commanding)
        # vbox_layout.addStretch()
        #
        layout.addWidget(self.status, alignment=QtCore.Qt.AlignTop)
        # layout.addLayout(vbox_layout)
        # layout.addWidget(self.faults, alignment=QtCore.Qt.AlignTop)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)

        grid_layout.addWidget(self.power_meter, 0, 0, alignment=QtCore.Qt.AlignTop)
        grid_layout.addWidget(self.attenuation, 0, 1, alignment=QtCore.Qt.AlignTop)
        grid_layout.addWidget(self.faults, 1, 0, alignment=QtCore.Qt.AlignTop)
        grid_layout.addWidget(self.commanding, 1, 1, alignment=QtCore.Qt.AlignTop)

        layout.addLayout(grid_layout)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def closeEvent(self, event):
        MODULE_LOGGER.info("Window closed, quiting....")
        self.status_puller.quit()
        event.accept()

        all_threads_finished = self.threadpool.waitForDone(msecs=2000)
        if not all_threads_finished:
            MODULE_LOGGER.warning("Not all threads were finished before the OGSE GUI terminated.")

    def start_pulling_status(self):
        self.status_puller = worker = StatusPuller(OGSEUIModel())
        self.threadpool.start(worker)
        worker.signals.states.connect(self.worker_states)
        worker.signals.faults.connect(self.worker_faults)
        worker.signals.att.connect(self.worker_att)
        worker.signals.dev.connect(self.worker_dev)
        worker.signals.pm.connect(self.worker_pm)

    @pyqtSlot(list)
    def worker_states(self, states):
        self.status.states.set_states(states)

    @pyqtSlot(list)
    def worker_faults(self, faults):
        self.faults.states.set_states(faults)

    @pyqtSlot(list)
    def worker_att(self, att):
        self.attenuation.index.setText( str(att[0]))
        self.attenuation.factor.setText(str(att[1]))

    @pyqtSlot(bool)
    def worker_dev(self, dev):
        self.device_connection.set_selected(dev)

    @pyqtSlot(dict)
    def worker_pm(self, pm):
        self.power_meter.power_1 = f"{pm['power1']:.4e}"
        self.power_meter.power_2 = f"{pm['power2']:.4e}"
        self.power_meter.temp_1 = f"{pm['temp1']:5.2f}"
        self.power_meter.temp_2 = f"{pm['temp2']:5.2f}"

    def on_click(self, icon: Union[QIcon, bool]):
        # MODULE_LOGGER.info(f"in {self.__class__.__name__}.on_click()")

        sender = self.sender()

        # MODULE_LOGGER.info(f"in {self.__class__.__name__} {sender=!s}")

        # MODULE_LOGGER.info(f"type(sender) = {type(sender)}")
        # MODULE_LOGGER.info(f"sender.text() = {sender.text()}")
        # MODULE_LOGGER.info(f"sender.isCheckable() = {sender.isCheckable()}")
        # MODULE_LOGGER.info(f"sender.isChecked() = {sender.isChecked()}")
        # MODULE_LOGGER.info(f"type(icon) = {type(icon)}")

        # This will trigger the update() method on all the observers

        self.notifyObservers(sender)

    def on_press(self):
        # MODULE_LOGGER.info(f"in {self.__class__.__name__}.on_press()")

        sender: ToggleButton = self.sender()

        # MODULE_LOGGER.info(f"in {self.__class__.__name__} {sender=!s}")

        if sender.is_selected():
            response = QMessageBox.question(
                self,
                "Confirmation Required",
                "Are you sure to switch OFF the OGSE?",
            )
            if response == QMessageBox.Yes:
                self.on_off_button.set_selected(False)
                self.notifyObservers(sender)
        else:
            self.on_off_button.set_selected(True)
            self.notifyObservers(sender)

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

    def create_status_bar(self):

        self.statusBar().setStyleSheet("border: 0; background-color: #FFF8DC;")
        self.statusBar().setStyleSheet("QStatusBar::item {border: none;}")
        self.statusBar().addPermanentWidget(VLine())
        self.statusBar().addPermanentWidget(self.mode_label)

    def create_toolbar(self):

        # The Reconnect action is used to reconnect to the control server

        self.cs_connection = ToggleButton(
            name="CS-CONNECT",
            status_tip="connect-disconnect the OGSE control server",
            selected=get_resource(":/icons/cs-connected.svg"),
            not_selected=get_resource(":/icons/cs-not-connected.svg"),
            disabled=get_resource(":/icons/cs-connected-disabled.svg")
        )
        self.cs_connection.clicked.connect(self.on_click)

        # The Reconnect action is used to reconnect the device

        self.device_connection = ToggleButton(
            name="DEVICE-CONNECT",
            status_tip="connect-disconnect the OGSE device controller",
            selected=get_resource(":/icons/plugged.svg"),
            not_selected=get_resource(":/icons/unplugged.svg"),
            disabled=get_resource(":/icons/plugged-disabled.svg")
        )
        self.device_connection.clicked.connect(self.on_click)

        # The HELP button is used to show the on-line help in a browser window

        help_button = QIcon(str(get_resource(":/icons/info.svg")))

        self.help_action = QAction(help_button, "INFO", self)
        self.help_action.setToolTip("Browse the on-line documentation")
        self.help_action.triggered.connect(self.on_click)

        # spacer widget to help with aligning STOP button to the right

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.toolbar = self.addToolBar("MainToolbar")
        self.toolbar.addWidget(self.device_connection)
        self.toolbar.addWidget(self.cs_connection)
        self.toolbar.addWidget(spacer)
        self.toolbar.addAction(self.help_action)

        return self.toolbar

    def set_connection_state(self, state):
        # enable or disable all actions that involve a device or cs connection
        # don't change the action buttons for the device nor the cs, that is handled
        # in the caller because it might be a device connection loss that causes this state
        # or a control server, or both...

        # MODULE_LOGGER.info(f"{state=}")

        if state == "connected":
            self.commanding.enable_commanding()
        elif state == "disconnected":
            self.commanding.disable_commanding()
        else:
            raise UnknownStateError(
                f"Unknown State ({state}), expected 'connected' or 'disconnected'."
            )

    def update_status_bar(self, message=None, mode=None, timeout=2000):
        if message:
            self.statusBar().showMessage(message, msecs=timeout)
        if mode:
            self.mode_label.setStyleSheet(
                f"border: 0; " f"color: {'red' if 'Simulator' in mode else 'black'};"
            )
            self.mode_label.setText(f"mode: {mode}")
        self.statusBar().repaint()



class OGSEUIModel:
    def __init__(self):

        self.device = OGSEProxy()

    def reconnect_device(self):
        self.device.reconnect()
        return self.device.is_connected()

    def reconnect_cs(self):
        self.device.reconnect_cs()
        return self.device.is_cs_connected()

    def disconnect(self):
        self.device.disconnect()

    def disconnect_cs(self):
        try:
            self.device.disconnect_cs()
        except ZMQError as exc:
            MODULE_LOGGER.error(f"{exc=}")

    def is_cs_connected(self):
        # MODULE_LOGGER.info(f"in {self.__class__.__name__}.is_cs_connected()")
        return self.device.is_cs_connected()

    def is_device_connected(self):
        # MODULE_LOGGER.info(f"in {self.__class__.__name__}.is_device_connected()")
        response = self.device.is_connected()
        # MODULE_LOGGER.info(f"{self.__class__.__name__}.device.is_connected() = {response}")
        return response if response is not None else False

    def is_simulator(self):
        return "sim" in self.device.version()

    def power_on(self):
        MODULE_LOGGER.debug(f"in {self.__class__.__name__}.power_on()")
        self.device.power_on()

    def power_off(self):
        MODULE_LOGGER.debug(f"in {self.__class__.__name__}.power_off()")
        self.device.power_off()

    def operate_on(self):
        MODULE_LOGGER.debug(f"in {self.__class__.__name__}.operate_on()")
        self.device.operate_on()

    def operate_off(self):
        MODULE_LOGGER.debug(f"in {self.__class__.__name__}.operate_off()")
        self.device.operate_off()

    def set_att_level(
            self,
            index: Optional[int] = None,
            factor: Optional[float] = None,
            position: Optional[Tuple[int, int]] = None,
    ):
        MODULE_LOGGER.debug(f"in {self.__class__.__name__}.set_att_level({index=}, "
                           f"{factor=}, {position=})")
        if index and factor and position:
            raise ValueError(f"Only one of the keyword arguments can be provided, {index=}, "
                             f"{factor=}, {position=}")
        if index:
            self.device.att_set_level_index(index)
        if factor:
            self.device.att_set_level_factor(factor)
        if position:
            self.device.att_set_level_factor(factor)

    def get_interlock(self) -> bool:
        interlock = self.device.get_interlock()
        return "ON" in interlock

    def get_power(self) -> bool:
        power = self.device.get_power()
        return "ON" in power

    def get_operate(self) -> bool:
        operate = self.device.get_operate()
        return "ON" in operate

    def get_laser(self) -> bool:
        laser = self.device.get_laser()
        return "ON" in laser

    def get_ldls_status(self):
        ldls = self.device.ldls_status()
        return "OK" in ldls

    def status(self) -> dict:
        """
        Returns a dictionary with the following keys:

            'power', 'lamp', 'interlock', 'psu', 'att_moving', 'att_factor',
            'att_index', 'power1', 'temp1', 'power2', 'temp2'
        """
        return self.device.status()

    def pm_power_1(self) -> float:
        status = self.device.status()
        return status["power1"]

    def pm_power_2(self) -> float:
        status = self.device.status()
        return status["power2"]

    def pm_temperature_1(self) -> float:
        status = self.device.status()
        return status["temp1"]

    def pm_temperature_2(self) -> float:
        status = self.device.status()
        return status["temp2"]

    def get_lamp_fault(self):
        fault = self.device.get_lamp_fault()

        # get_lamp_fault response contains 'NO-ERROR' if all good, and 'ERROR' if there
        # was an error. The model will return True if there is a fault detected!

        return "NO-ERROR" not in fault

    def get_controller_fault(self):
        fault = self.device.get_controller_fault()

        # get_controller_fault response contains 'NO-ERROR' if all good, and 'ERROR' if there
        # was an error. The model will return True if there is a fault detected!

        return "NO-ERROR" not in fault

    def set_attenuation_index(self, index):
        # MODULE_LOGGER.info(f"set_attenuation_index to {index} ({type(index)=})")
        self.device.att_set_level_index(int(index))


class StatusSignals(QObject):
    states = pyqtSignal(list)
    faults = pyqtSignal(list)
    att = pyqtSignal(list)
    dev = pyqtSignal(bool)
    pm = pyqtSignal(dict)


class StatusPuller(QRunnable):
    def __init__(self, model: OGSEUIModel):
        super().__init__()
        self.signals = StatusSignals()
        self.model = model
        self.quit_request = False

    @pyqtSlot()
    def run(self):
        while not self.quit_request:

            self.signals.dev.emit(self.model.is_device_connected())

            # Set all the status LEDs

            status = self.model.status()
            states = [
                Indic.GREEN if 'ON' in status["interlock"] else Indic.BLACK,
                Indic.GREEN if 'ON' in status["power"] else Indic.BLACK,
                Indic.GREEN if self.model.get_laser() else Indic.BLACK,
                Indic.GREEN if 'ON' in status["lamp"] else Indic.BLACK,
                Indic.GREEN if 'ON' in status["psu"] else Indic.BLACK,
                Indic.GREEN if self.model.get_ldls_status() else Indic.BLACK,
                Indic.ORANGE if status["att_moving"] else Indic.BLACK,
            ]
            self.signals.states.emit(states)

            self.signals.pm.emit(
                {
                    "power1": status['power1'],
                    "power2": status['power2'],
                    "temp1": status['temp1'],
                    "temp2": status['temp2'],
                })

            # Set the fault detection on the lamp and controller

            faults = [
                Indic.RED if self.model.get_lamp_fault() else Indic.GREEN,
                Indic.RED if self.model.get_controller_fault() else Indic.GREEN,
            ]
            self.signals.faults.emit(faults)

            self.signals.att.emit([status["att_index"], status["att_factor"]])

    def quit(self):
        self.quit_request = True


class OGSEUIController(Observer):
    def __init__(self, model: OGSEUIModel, view: Union[OGSEGUIView, OGSETUIView]):
        super().__init__()

        self.model = model
        self.view = view

        self.view.addObserver(self)

        self.help_window = HelpWindow(topic_url=HELP_TOPICS["ogse_ui"])

        self.states_capture_timer_interval = 1000  # [ms]
        self.create_timer()

        if self.model.is_cs_connected():
            mode = f"Proxy{' [Simulator]' if self.model.is_simulator() else ''}"
            self.view.update_status_bar(mode=mode)
            self.view.check_cs_action()
        else:
            self.view.uncheck_cs_action()
            # if the control server is not connected, we should not check for the other connection
            # status but just uncheck actions and return
            self.view.uncheck_device_action()
            self.view.set_connection_state("disconnected")
            self.stop_timer()
            return

        if self.model.is_device_connected():
            self.view.check_device_action()
        else:
            self.view.uncheck_device_action()

        if self.has_connection():
            self.view.set_connection_state("connected")
            self.start_timer()
        else:
            self.view.set_connection_state("disconnected")
            self.stop_timer()

        self.view.start_pulling_status()

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
        self.states_capture_timer.timeout.connect(self.update_state)
        self.states_capture_timer.setInterval(self.states_capture_timer_interval)

    def start_timer(self):
        self.states_capture_timer.start()

    def stop_timer(self):
        self.states_capture_timer.stop()

    def do(self, actions):
        # This method is part of the Observer protocol and will be called when there is an
        # action requested by the Observable.

        for action, value in actions.items():
            ...

    def update(self, changed_object):
        # This method is part of the Observer protocol and will be called when there is a
        # notification of a change in the Observable.

        text = changed_object.text()
        # MODULE_LOGGER.debug(f"in {self.__class__.__name__}.update({type(changed_object)}), text=\"{text}\"")

        if text == "INFO":
            self.help_window.show()

        if text == "POWER-ON-OFF":
            obj: ToggleButton = changed_object
            if obj.state == BUTTON_SELECTED:
                self.model.power_on()
                # Should we also execute `operate_on()` or leave that to the user by pressing
                # the button in the GUI?
                self.view.commanding.cmd_operate.enable()
            else:
                self.model.operate_off()
                self.model.power_off()
                self.view.commanding.cmd_operate.disable()

        if text == "OPERATE-ON-OFF":
            if changed_object.is_selected():
                self.model.operate_on()
            else:
                self.model.operate_off()

        if text == "ATTENUATION-GO":
            position = self.view.commanding.att_index_slider_position.text()
            self.model.set_attenuation_index(position)

        if text == "ATTENUATION-PLUS":
            position = min(self.view.commanding.att_index_slider.value() + 1, 46)
            self.view.commanding.att_index_slider_position.setText(str(position))
            self.view.commanding.att_index_slider.setSliderPosition(position)

        if text == "ATTENUATION-MINUS":
            position = max(self.view.commanding.att_index_slider.value() - 1, 0)
            self.view.commanding.att_index_slider_position.setText(str(position))
            self.view.commanding.att_index_slider.setSliderPosition(position)

        if text == "CS-CONNECT":
            if changed_object.is_selected():
                MODULE_LOGGER.debug("Reconnecting the OGSE Control Server.")
                self.model.reconnect_cs()
                # if not self.model.has_commands():
                #     self.model.load_commands()
                self.start_timer()
                if self.model.is_device_connected() and self.model.is_cs_connected():
                    self.view.set_connection_state("connected")
                    self.view.device_connection.enable()
            else:
                MODULE_LOGGER.debug("Disconnecting the OGSE Control Server.")
                self.stop_timer()
                self.model.disconnect_cs()
                self.view.device_connection.disable()
                self.view.set_connection_state("disconnected")
            return

        if text == "DEVICE-CONNECT":
            if changed_object.is_selected():
                MODULE_LOGGER.debug("Reconnecting the OGSE device controller.")
                if self.model.reconnect_device():
                    self.view.set_connection_state("connected")
                    # if not self.model.has_commands():
                    #     self.model.load_commands()
                    self.start_timer()
                else:
                    self.view.device_connection.set_selected(False)
            else:
                MODULE_LOGGER.debug("Disconnecting the OGSE device Controller.")
                self.stop_timer()
                self.model.disconnect()
                self.view.set_connection_state("disconnected")
            return

    def update_state(self):
        # MODULE_LOGGER.info(f"in {self.__class__.__name__}.update_state()")
        # MODULE_LOGGER.info("Disabled update_state() from OGSEUIController")
        # return

        self.view.device_connection.set_selected(self.model.is_device_connected())

        m = self.model

        # Set all the status LEDs

        status = m.status()
        states = [
            Indic.GREEN if 'ON' in status["interlock"] else Indic.BLACK,
            Indic.GREEN if 'ON' in status["power"] else Indic.BLACK,
            Indic.GREEN if m.get_laser() else Indic.BLACK,
            Indic.GREEN if 'ON' in status["lamp"] else Indic.BLACK,
            Indic.GREEN if 'ON' in status["psu"] else Indic.BLACK,
            Indic.GREEN if m.get_ldls_status() else Indic.BLACK,
            Indic.ORANGE if status["att_moving"] else Indic.BLACK,
        ]
        self.view.status.states.set_states(states)

        # Set the value of the power meter

        self.view.power_meter.power_1 = f"{status['power1']:.4e}"
        self.view.power_meter.power_2 = f"{status['power2']:.4e}"
        self.view.power_meter.temp_1 = f"{status['temp1']:5.2f}"
        self.view.power_meter.temp_2 = f"{status['temp2']:5.2f}"

        # Set the fault detection on the lamp and controller

        states = [
            Indic.RED if m.get_lamp_fault() else Indic.GREEN,
            Indic.RED if m.get_controller_fault() else Indic.GREEN,
        ]
        self.view.faults.states.set_states(states)

        if m.get_operate():
            self.view.commanding.cmd_operate.set_selected(True)
        else:
            self.view.commanding.cmd_operate.set_selected(False)

        if 'ON' in status["power"]:
            self.view.commanding.cmd_power.set_selected(True)
            self.view.commanding.enable_commanding()
        else:
            self.view.commanding.cmd_power.set_selected(False)
            self.view.commanding.disable_commanding()

        self.view.attenuation.index.setText( str(status["att_index"]))
        self.view.attenuation.factor.setText(str(status["att_factor"]))


def main():
    lock_file = QLockFile(str(Path("~/ogse_ui.app.lock").expanduser()))

    app_logo = get_resource(":/icons/logo-ogse.svg")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(app_logo)))

    if lock_file.tryLock(100):

        process_status = ProcessStatus()

        timer_thread = threading.Thread(target=do_every, args=(10, process_status.update))
        timer_thread.daemon = True
        timer_thread.start()

        start_http_server(GUI_SETTINGS.METRICS_PORT)

        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

        view = OGSEGUIView()
        model = OGSEUIModel()
        OGSEUIController(model, view)

        view.show()

        return app.exec_()
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The OGSE GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()


if __name__ == '__main__':

    sys.exit(main())
