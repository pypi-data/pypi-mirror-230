import argparse
import logging
import sys
from pathlib import Path
from typing import List
import numpy as np
from QLed import QLed


"""
Qt imports for the View class
"""

from PyQt5.QtWidgets import QApplication, QMessageBox
import pyqtgraph as pg
from PyQt5.QtGui import (QFont, QIcon, QPalette, QPixmap)
from PyQt5.QtWidgets import (QAction, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QMainWindow, QVBoxLayout,
                             QWidget, QRadioButton, QPushButton, QSpinBox, QDoubleSpinBox, QSizePolicy)
from PyQt5.QtCore import QTimer, Qt, QSize, QLockFile

from egse.settings import Settings
from egse.observer import Observable, Observer
from egse.state import UnknownStateError
from egse.config import find_file, set_logger_levels
from egse.process import ProcessStatus
from egse.system import do_every
from egse.resource import get_resource
from egse.gui.stripchart import StripChart
from egse.gui.buttons import ToggleButton
from egse.gui.buttons import TouchButton


import threading

from egse.tempcontrol.srs.ptc10 import ptc10Controller, ptc10Proxy, ptc10Simulator

from egse.gui import show_warning_message
from egse.gui.led import Indic


logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)
MODULE_LOGGER = logging.getLogger("Temperature controller PTC10 GUI")

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

SETTINGS = Settings.load("SRS PTC10 Controller")
FONT = QFont("Helvetica", 18)

# Variables


SYSTEM_MODES = ["Survival", "Regulation", "Manual", "Custom"]


class ConfigureModes(QWidget):
    def __init__(self):
        super().__init__()
        self.vbox = QVBoxLayout()
        self.mode_label = QLabel("System configuration")
        self.vbox.addWidget(self.mode_label)
        self.vbox.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.operation_modes = list()

        for mode in SYSTEM_MODES:
            _item = QRadioButton(mode)
            self.operation_modes.append(_item)
            self.vbox.addWidget(_item)
            self.vbox.setObjectName(mode)


class PIDSettings(QWidget):
    def __init__(self):
        super().__init__()
        vbox_labels = QVBoxLayout()
        vbox_values = QVBoxLayout()
        hbox = QHBoxLayout()

        copy_right_icon = QIcon(str(get_resource(":/icons/double-right-arrow.svg")))
        self.copy_right_button = QPushButton()
        self.copy_right_button.setIcon(copy_right_icon)
        self.copy_right_button.setToolTip("Set the PID parameters")
        self.copy_right_button.setMinimumWidth(95)
        self.copy_right_button.setMinimumHeight(75)

        self.pid_parameters = [[QLabel("P :"), QLabel()],
                               [QLabel("I :"), QLabel()],
                               [QLabel("D :"), QLabel()]]

        for items in self.pid_parameters:
            vbox_labels.addWidget(items[0])
            vbox_values.addWidget(items[1])
            items[1].setStyleSheet("QLabel { background-color : White; }")
            items[1].setText("0.0")
            items[1].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            items[1].setMinimumWidth(40)

        vbox_labels.addStretch(1)
        vbox_values.addStretch(1)

        hbox.addLayout(vbox_labels)
        hbox.addLayout(vbox_values)
        hbox.addStretch(1)
        hbox.addWidget(self.copy_right_button)
        # Make sure the leds and labels stay nicely together when horizontally resizing the Frame.
        hbox.addStretch(1)

        vbox = QVBoxLayout()

        vbox.addLayout(self.setpoint_setting())

        vbox.addLayout(hbox)
        vbox.addStretch(1)

        self.auto_pid = QPushButton("Autotune PID")
        self.auto_pid.setToolTip("Set the autotune")
        self.auto_pid.setMaximumSize(180, 300)

        vbox.addWidget(self.auto_pid)
        vbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        vbox.addStretch(1)

        self.pidWidget = QGroupBox("PID settings :", self)
        self.pidWidget.setLayout(vbox)
        self.pidWidget.setToolTip("PID SETTINGS")
        self.pidWidget.setMaximumHeight(180)
        self.pidWidget.setMaximumWidth(200)

    def setpoint_setting(self):
        hbox = QHBoxLayout()
        self.setpoint_label = QLabel("Setpoint (°C):")
        self.setpoint_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.setpoint_value = QDoubleSpinBox()
        self.setpoint_value.setMinimum(-125)
        self.setpoint_value.setMinimumWidth(50)
        self.setpoint_value.setMinimumHeight(30)
        self.setpoint_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)


        hbox.addWidget(self.setpoint_label)
        hbox.addWidget(self.setpoint_value)
        hbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        return hbox


class manualSetting(QWidget):
    def __init__(self):
        super().__init__()

        hbox = QHBoxLayout()
        self.power_label = QLabel("Power (W):")
        self.power_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.power_value = QSpinBox()

        self.power_value.setMinimumWidth(50)
        self.power_value.setMinimumHeight(30)
        self.power_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        hbox.addWidget(self.power_label)
        hbox.addWidget(self.power_value)

        hbox.addStretch(1)

        self.manualWidget = QGroupBox("Manual settings :", self)
        self.manualWidget.setLayout(hbox)
        self.manualWidget.setToolTip("Set output power in Watts")

        self.manualWidget.setMaximumHeight(70)


class SystemStatusWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.status_leds = [
            [QLabel("Heaters active"), QLed(self, offColour=QLed.Grey, onColour=QLed.Green, shape=QLed.Square)],
            [QLabel("System Error"), QLed(self, offColour=QLed.Green, onColour=QLed.Red, shape=QLed.Square)]]

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        vbox.addLayout(self.create_states())
        self.StatusWidget = QGroupBox()
        self.StatusWidget.setLayout(vbox)

    def create_states(self):
        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(""))

        for element in self.status_leds:
            hflags = QHBoxLayout()
            hflags.setSpacing(3)
            element[1].setFixedSize(15, 15)
            hflags.addWidget(element[1])
            hflags.addWidget(element[0])

            vbox.addLayout(hflags)
        return vbox


class OutputWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.output_widget_label = QLabel()

        self.output_widget = QVBoxLayout()
        output_power_label = QLabel("Output power(W):")
        self.output_power = QLabel()
        self.output_power.setStyleSheet("QLabel { background-color : White; }")
        self.output_power.setMinimumWidth(70)
        hbox_power = QHBoxLayout()
        hbox_power.addWidget(output_power_label)
        hbox_power.addWidget(self.output_power)

        measured_temperature_label = QLabel("Measured T(°C):")
        self.measured_temperature = QLabel()
        self.measured_temperature.setMaximumWidth(70)
        self.measured_temperature.setStyleSheet("QLabel { background-color : White; }")
        hbox_temp = QHBoxLayout()
        hbox_temp.addWidget(measured_temperature_label)
        hbox_temp.addWidget(self.measured_temperature)

        self.output_widget.addWidget(self.output_widget_label)
        self.output_widget.addLayout(hbox_temp)
        self.output_widget.addLayout(hbox_power)
        self.output_widget.addStretch(1)


class createTRPWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.trp_config = ConfigureModes()
        self.trp_config.vbox.removeItem(self.trp_config.vbox.itemAt(4)) # removes the "custom" mode as not needed here

        self.pid_config = PIDSettings()
        self.manual_config = manualSetting()
        self.stripchart = StripChart(
            labels={"left": ("measure T", "C"), "right":("output Power","W"), "bottom": ("Time", "d hh:mm:ss")}
        )
        self.stripchart.setInterval(60 * 60 * 12)  # 12h of data
        self.stripchart.set_yrange(0, 40)

        hbox = QHBoxLayout()
        vbox_stripchart = QVBoxLayout()
        vbox_stripchart.addWidget(self.stripchart)
        hbox_settings = QHBoxLayout()

        vbox_settings = QVBoxLayout()

        stop_icon = QIcon(str(get_resource(":/icons/stop.svg")))

        self.stop_trp = QPushButton()
        self.stop_trp.setIcon(stop_icon)
        self.stop_trp.setIconSize(QSize(50,50))
        self.stop_trp.setMinimumHeight(100)
        self.stop_trp.setToolTip("STOP TRP Heater")

        vbox_config = QVBoxLayout()
        hbox_settings.addStretch(1)
        vbox_config.addLayout(self.trp_config.vbox)
        vbox_config.addStretch(1)

        vbox_config.addWidget(self.stop_trp)
        hbox_settings.addLayout(vbox_config)
        hbox_settings.addWidget(self.pid_config.pidWidget)
        hbox_settings.addStretch(1)
        vbox_settings.addLayout(hbox_settings)
        vbox_settings.addWidget(self.manual_config.manualWidget)

        hbox.addLayout(vbox_stripchart)
        hbox.addLayout(vbox_settings)
        self.TRPWidget = QGroupBox("TRPWidget", self)
        self.TRPWidget.setLayout(hbox)


class ptc10UIView(QMainWindow, Observable):
    def __init__(self):
        super().__init__()

        # Define those variables that we will need/use in different methods

        self.measure = None
        self.clear_action = None
        self.reconnect_action = None
        self.toolbar = None

        self.setGeometry(200, 200, 1000, 500)
        self.setWindowTitle("SRS PTC10 Temperature Controller")

        #self.pid_parameters = None

        self.system_config = self.SystemConfigure()
        self.system_settings = self.SystemSettings()
        self.system_status = self.SystemStatus()
        self.system_status.setTitle("System Status")

        self.TRPWidget = self.create_channel_group()

        self.system_op = self.system_config.findChildren(QRadioButton)
        #self.trp2_op = self.TRPWidget.widget_trp2()

        self.init_gui()

    ### Widgets definition

    def SystemConfigure(self):
        """This Widget allows to view the configuration mode of the system."""

        vbox = ConfigureModes()

        modes_layout = QGroupBox()
        modes_layout.setLayout(vbox.vbox)

        return modes_layout

    def SystemStatus(self):
        """This Widget reports the sytem status."""
        ## Errors, OOL, active regulation
        self.systemstatus = SystemStatusWidget()

        self.trp2_status = OutputWidget()
        self.trp2_status.output_widget_label.setText(">------- TRP2 Outputs -------<")

        self.trp3_status = OutputWidget()
        self.trp3_status.output_widget_label.setText(">------- TRP3 Outputs -------<")

        self.trp4_status = OutputWidget()
        self.trp4_status.output_widget_label.setText(">------- TRP4 Outputs -------<")

        vbox = QVBoxLayout()
        vbox.addWidget(self.systemstatus.StatusWidget)
        vbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        vbox.addStretch(1)
        vbox.addLayout(self.trp2_status.output_widget)
        vbox.addStretch(1)
        vbox.addLayout(self.trp3_status.output_widget)
        vbox.addStretch(1)
        vbox.addLayout(self.trp4_status.output_widget)

        status_layout = QGroupBox()
        status_layout.setLayout(vbox)

        return status_layout

    def SystemSettings(self):
        """This Widget allows to set the system parameters."""
        ## setpoint, PID, Autotune, manual power tuning

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.PID_settings = PIDSettings()

        vbox.addWidget(self.PID_settings.pidWidget)
        vbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        vbox.addStretch(1)

        self.manual_setting = manualSetting()

        vbox.addWidget(self.manual_setting.manualWidget)
        vbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        return vbox

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


        # The STOP button is used to immediately stop the current motion

        stop_button = QIcon(str(get_resource(":/icons/stop.svg")))

        self.stop_action = QAction(stop_button, "STOP", self)
        self.stop_action.setToolTip("STOP Movement")
        self.stop_action.triggered.connect(self.onClick)

        self.clear_errors = TouchButton(
            name="CLEAR-ERRORS",
            status_tip="clear the error list on the controller",
            selected=get_resource(":/icons/erase.svg"),
            disabled=get_resource(":/icons/erase-disabled.svg"),
        )
        self.clear_errors.clicked.connect(self.onClick)

        # The Reconnect action is used to reconnect to the control server

        self.cs_connection = ToggleButton(
            name="CS-CONNECT",
            status_tip="connect-disconnect hexapod control server.",
            selected=get_resource(":/icons/cs-connected.svg"),
            not_selected=get_resource(":/icons/cs-not-connected.svg"),
            disabled=get_resource(":/icons/cs-connected-disabled.svg")
        )
        self.cs_connection.clicked.connect(self.onClick)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.toolbar = self.addToolBar("MainToolbar")
        self.toolbar.addAction(self.reconnect_action)
        #self.toolbar.addWidget(spacer)
        self.toolbar.addWidget(self.clear_errors)
        #self.toolbar.addWidget(spacer)
        self.toolbar.addWidget(self.cs_connection)

        self.toolbar.addAction(self.stop_action)

        return self.toolbar

    def create_channel_group(self):

        group_box = QGroupBox("TRP2/3/4 Monitoring and Control")

        # Create the label fields that display the current measure
        self.widget_trp_2 = createTRPWidget()
        self.widget_trp_2.TRPWidget.setTitle("TRP2")
        self.widget_trp_2.trp_config.mode_label.setText("TRP2 regulation mode")
        self.widget_trp_2.setMinimumHeight(200)
        self.widget_trp_2.setMinimumWidth(700)

        self.widget_trp_3 = createTRPWidget()
        self.widget_trp_3.TRPWidget.setTitle("TRP3")
        self.widget_trp_3.trp_config.mode_label.setText("TRP3 regulation mode")
        self.widget_trp_3.setMinimumHeight(200)
        self.widget_trp_3.setMinimumWidth(700)

        self.widget_trp_4 = createTRPWidget()
        self.widget_trp_4.TRPWidget.setTitle("TRP4")
        self.widget_trp_4.trp_config.mode_label.setText("TRP4 regulation mode")
        self.widget_trp_4.setMinimumHeight(200)
        self.widget_trp_4.setMinimumWidth(700)

        # Create the edit text field for setting the position

        vbox = QVBoxLayout()

        vbox.addWidget(self.widget_trp_2.TRPWidget)
        vbox.addWidget(self.widget_trp_3.TRPWidget)
        vbox.addWidget(self.widget_trp_4.TRPWidget)

        vbox.addStretch(1)

        group_box.setLayout(vbox)

        return group_box

    ## widget init

    def init_gui(self):

        # Switch to using white background and black foreground for pyqtgraph stripcharts

        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")

        # The main frame in which all the other frames are located, the outer Application frame

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        hbox = QHBoxLayout()
        self.createToolbar()
        vbox = QVBoxLayout()

        vbox.addWidget(self.system_config)

        # connects the system mode selection event
        for mode in self.system_op:
            mode.clicked.connect(self.set_mode)

        vbox.addLayout(self.system_settings)
        self.PID_settings.auto_pid.clicked.connect(self.set_auto_pid)
        self.PID_settings.copy_right_button.clicked.connect(self.set_pid)


        vbox.addWidget(self.system_status)
        vbox.addStretch(1)

        hbox.addLayout(vbox)
        hbox.addWidget(self.TRPWidget)

        app_frame.setLayout(hbox)

        self.setCentralWidget(app_frame)

    #### GUI UPDATES

    def init_widgets_values(self):
        print("put here the initialization parameters")
        #TODO: the initial config needs to be read and passed
        ## Init system config values:

        self.system_op[0].setChecked(True)

        ## Init PID default values
        for pid in range(3):
            self.PID_settings.pid_parameters[pid][1].setText("0.0")
            self.PID_settings.pid_parameters[pid][1].repaint()

        self.update_gui()

    def update_gui(self):

        m = list()
        for _items in range(len(self.system_op)):
            m.append(self.system_op[_items].isChecked())
        current_mode = SYSTEM_MODES[int(np.where(m)[0])]
        self.gui_modes(current_mode)

    def gui_modes(self, mode):

        if mode == "Survival":
            self.PID_settings.auto_pid.setDisabled(False)
            self.PID_settings.setpoint_value.setValue(-10)
            self.PID_settings.setpoint_value.setDisabled(True)
            self.manual_setting.power_value.setDisabled(True)

            #Disabling TRPs custom:
            self.widget_trp_2.trp_config.operation_modes[2].setChecked(True)
            self.widget_trp_2.TRPWidget.setDisabled(True)
            self.widget_trp_3.trp_config.operation_modes[2].setChecked(True)
            self.widget_trp_3.TRPWidget.setDisabled(True)
            self.widget_trp_4.trp_config.operation_modes[2].setChecked(True)
            self.widget_trp_4.TRPWidget.setDisabled(True)
            #for x in range(len(self.pid_parameters)):
             #   self.pid_parameters[x][1].setDisabled(False)
        elif mode == "Regulation":
            self.PID_settings.auto_pid.setDisabled(False)
            self.PID_settings.setpoint_value.setDisabled(False)
            self.manual_setting.power_value.setDisabled(True)
            for x in range(len(self.PID_settings.pid_parameters)):
                self.PID_settings.pid_parameters[x][1].setDisabled(False)

            #Disabling TRPs custom:
            self.widget_trp_2.trp_config.operation_modes[2].setChecked(True)
            self.widget_trp_2.TRPWidget.setDisabled(True)
            self.widget_trp_3.trp_config.operation_modes[2].setChecked(True)
            self.widget_trp_3.TRPWidget.setDisabled(True)
            self.widget_trp_4.trp_config.operation_modes[2].setChecked(True)
            self.widget_trp_4.TRPWidget.setDisabled(True)

        elif mode == "Manual":
            self.PID_settings.copy_right_button.setDisabled(True)
            self.PID_settings.auto_pid.setDisabled(True)
            self.PID_settings.setpoint_value.setDisabled(True)
            self.manual_setting.power_value.setDisabled(False)

            #Disabling TRPs custom:
            self.widget_trp_2.trp_config.operation_modes[2].setChecked(True)
            self.widget_trp_2.TRPWidget.setDisabled(True)
            self.widget_trp_3.trp_config.operation_modes[2].setChecked(True)
            self.widget_trp_3.TRPWidget.setDisabled(True)
            self.widget_trp_4.trp_config.operation_modes[2].setChecked(True)
            self.widget_trp_4.TRPWidget.setDisabled(True)

        elif mode == "Custom":
            self.PID_settings.copy_right_button.setDisabled(True)
            self.PID_settings.auto_pid.setDisabled(True)
            self.PID_settings.setpoint_value.setDisabled(True)
            self.manual_setting.power_value.setDisabled(True)

            #Enabling TRPs custom:
            #May be here the best is to start with the latest system mode
            self.widget_trp_2.TRPWidget.setDisabled(False)
            self.widget_trp_2.trp_config.operation_modes[2].setChecked(False)
            self.widget_trp_3.TRPWidget.setDisabled(False)
            self.widget_trp_3.trp_config.operation_modes[2].setChecked(False)
            self.widget_trp_4.trp_config.operation_modes[2].setChecked(False)

            #for x in range(len(self.pid_parameters)):
                #self.pid_parameters[x][1].setDisabled(True)




    #### NOTIFIERS

    def set_mode(self):
        print("the mode has changed")
        self.update_gui()

    def set_pid(self):
        print("SET PID PARAMETERS")

    def set_auto_pid(self):
        print("AUTOPID")

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


class ptc10UIModel:
    def __init__(self, type_):
        self.type = type_

        if self.type == "proxy":
            self.temp = ptc10Proxy()
        elif self.type == "direct":
            self.temp = ptc10Controller()
            self.temp.connect()
        elif self.type == "simulator":
            self.temp = ptc10Simulator()
        else:
            raise Exception(
                f"Unknown type of Temperature Controller implementation passed into the model: {type}"
            )

        if self.temp is not None:
            MODULE_LOGGER.debug(
                f"SRS PTC10Controller initialized as {self.temp.__class__.__name__}"
            )

    def has_commands(self):
        if self.type == "proxy":
            return self.temp.has_commands()
        return True

    def load_commands(self):
        if self.type == "proxy":
            self.temp.load_commands()

    def is_simulator(self):
        return self.temp.is_simulator()

    def is_connected(self):
        if self.type == "proxy":
            return self.temp.is_cs_connected()
        else:
            return self.temp.is_connected()

    def reconnect(self):
        if self.type == "proxy":
            self.temp.reconnect_cs()
            return self.temp.is_cs_connected()
        else:
            self.temp.reconnect()
            return self.temp.is_connected()
        return False

    def disconnect(self):
        if self.type == "proxy":
            self.temp.disconnect_cs()
        else:
            self.temp.disconnect()


class ptc10UIController(Observer):
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
            self.view.init_widgets_values()
            self.start_timer()
        else:
            self.stop_timer()
            self.view.set_connection_state("disconnected")

    def create_timer(self):
        """Create a Timer that will update the States every second."""

        self.states_capture_timer = QTimer()

        self.states_capture_timer.setInterval(200)

        self.stripchart_timer = QTimer()

        self.stripchart_timer.setInterval(200)

    def start_timer(self):
        self.states_capture_timer.start()
        self.stripchart_timer.start()

    def stop_timer(self):
        self.states_capture_timer.stop()
        self.stripchart_timer.stop()

    def update(self, changed_object):

        text = changed_object.text()

        if text == "Reconnect":

            if changed_object.isChecked():
                MODULE_LOGGER.debug("Reconnecting the ptc10 model.")
                if self.model.reconnect():
                    self.view.set_connection_state("connected")
                    if not self.model.has_commands():
                        self.model.load_commands()
                    self.start_timer()
                else:
                    self.view.reconnect_action.setChecked(False)
            else:
                MODULE_LOGGER.debug("Disconnecting the ptc10 model.")
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
    lock_file = QLockFile(str(Path("~/ptc10_ui.app.lock").expanduser()))
    styles_location = find_file("styles.qss", in_dir="egse/gui")

    args = list(sys.argv)
    args[1:1] = ["-stylesheet", str(styles_location)]
    app = QApplication(args)

    if lock_file.tryLock(100):
        process_status = ProcessStatus()

        timer_thread = threading.Thread(target=do_every, args=(10, process_status.update))
        timer_thread.daemon = True
        timer_thread.start()

        args = parse_arguments()

        if args.profile:
            Settings.set_profiling(True)

        if args.type == "proxy":
            proxy = ptc10Proxy()
            if not proxy.ping():
                description = "Could not connect to SRS PTC10 Control Server"
                info_text = (
                    "The GUI will start, but the connection button will show a disconnected state. "
                    "Please check if the Control Server is running and start the server if needed. "
                    "Otherwise, check if the correct HOSTNAME for the control server is set in the "
                    "Settings.yaml "
                    "configuration file."
                )

                show_warning_message(description, info_text)

        view = ptc10UIView()
        model = ptc10UIModel(args.type)
        controller = ptc10UIController(model, view)

        view.show()

        return app.exec_()
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The PTC10 tempcontrol GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()


if __name__ == "__main__":
    sys.exit(main())
