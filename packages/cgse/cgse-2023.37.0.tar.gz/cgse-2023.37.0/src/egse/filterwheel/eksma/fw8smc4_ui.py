import argparse
import logging
from pathlib import Path

import sys
from itertools import compress

from egse.resource import get_resource

"""
Qt imports for the FilterwheelView class
"""
import pyqtgraph as pg
from PyQt5.QtGui import QFont, QIcon, QPalette, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFrame, QGroupBox, QHBoxLayout, QVBoxLayout, QLabel,
                             QMainWindow, QLineEdit, QComboBox, QPushButton, QToolButton, QRadioButton,
                             QMessageBox)
from PyQt5.QtCore import QTimer, Qt, QLockFile
from QLed import QLed

from egse.settings import Settings
from egse.observer import Observable
from egse.observer import Observer
from egse.state import UnknownStateError
from egse.config import find_file, set_logger_levels

from egse.filterwheel.eksma.fw8smc4 import FilterWheel8SMC4Controller, FilterWheel8SMC4Proxy, FilterWheel8SMC4Simulator
from egse.gui import show_warning_message

from egse.process import ProcessStatus
from egse.system import do_every

from prometheus_client import start_http_server

import threading

logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)
MODULE_LOGGER = logging.getLogger("8SMC4 GUI")

# Note that, in production, the logging level for the different loggers can be changed with a
# service command `set_logging_level(logger_name, level)`.

logger_levels = [
    ("egse.protocol", logging.INFO),
    ("egse.command", logging.INFO),
    ("egse.settings", logging.INFO),
    ("egse.config", logging.INFO),
    ("git.cmd", logging.INFO),
]


set_logger_levels(logger_levels)

SETTINGS = Settings.load("Filter Wheel 8SMC4 Controller")
GUI_SETTINGS = Settings.load("FW8SMC4 GUI")

FONT = QFont("Helvetica", 18)


class FilterWheelUIView(QMainWindow, Observable):
    def __init__(self):
        super().__init__()

        # Define those variables that we will need/use in different methods

        self.clear_action = None
        self.reconnect_action = None
        self.toolbar = None
        self.wheel_control = None

        #self.homing_led = None
        self.wheel_1 = None
        self.wheel_2 = None
        self.p_wheel_1 = None
        self.p_wheel_2 = None
        self.p_button = None
        self.wheelstatus = []
        self.attenuation_values = []

        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle("eksma Filter Wheel 8SMC4 Controller")

        self.init_gui()

    def createToolbar(self):
        image_location = Path(__file__).resolve().parent.parent.parent / "images"

        # Homing button:
        home_pix = QPixmap(str(find_file("home.svg", in_dir="images")))
        home_icon = QIcon()
        home_icon.addPixmap(home_pix)

        self.homing_action = QAction(home_icon, "Homing", self)
        self.homing_action.setToolTip("Homing")
        self.homing_action.triggered.connect(self.onClick)

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

        # Building the toolbar:
        self.toolbar = self.addToolBar("MainToolbar")
        self.toolbar.addAction(self.reconnect_action)
        self.toolbar.addAction(self.homing_action)
        return self.toolbar

    def createWheelPositionWidget(self):
        hbox = QHBoxLayout()
        # hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)

        tbox = QVBoxLayout()
        tbox.addWidget(QLabel(""))
        tbox.addWidget(QLabel("Position: "))
        tbox.addWidget(QLabel("Attenuation: "))
        tbox.setSpacing(15)
        tbox.setSizeConstraint(0)
        tbox.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        hbox.addLayout(tbox)
        hbox.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        hbox.setSpacing(0)

        for positions in range(8):
            hbox.setSpacing(0)
            # label
            pos_label = QLabel(f"{positions + 1}")
            pos_label.setAlignment(Qt.AlignHCenter)

            # led definitions:
            _led = QLed(self, offColour=QLed.Grey, onColour=QLed.Green)
            _led.setFixedSize(40, 40)

            # transmission boxes
            editbox = QLineEdit()
            editbox.setReadOnly(True)
            editbox.setAlignment(Qt.AlignHCenter)
            editbox.setFixedSize(40, 35)

            # building layout:
            vbox = QVBoxLayout()
            vbox.addWidget(pos_label)
            vbox.addWidget(_led)
            vbox.addWidget(editbox)
            vbox.setSpacing(5)
            vbox.setAlignment(Qt.AlignTop)
            hbox.setSpacing(0)
            hbox.addLayout(vbox)

        hbox.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        hbox.setSpacing(0)
        group_box = QGroupBox("Wheel position", self)
        group_box.setLayout(hbox)
        group_box.setFixedWidth(600)

        return group_box

    def createWheelControlWidget(self):
        vbox = QVBoxLayout()

        #### POSITION WIDGETS ####

        hposition = QHBoxLayout()

        wheel_label = QLabel("Set the wheels to position: ")
        self.p_wheel_1 = QComboBox()
        self.p_wheel_1.setCurrentIndex(-1)
        self.p_wheel_1.addItem("= wheel 1 =")
        self.p_wheel_1.model().item(0).setEnabled(False)
        self.p_wheel_1.addItems(["position 1", "position 2", "position 3", "position 4", "position 5", "position 6",
                                 "position 7", "position 8"])
        self.p_wheel_1.setFixedWidth(120)

        self.p_wheel_2 = QComboBox()
        self.p_wheel_2.setCurrentIndex(-1)
        self.p_wheel_2.addItem("= wheel 2 =")
        self.p_wheel_2.model().item(0).setEnabled(False)
        self.p_wheel_2.addItems(["position 1", "position 2", "position 3", "position 4", "position 5", "position 6",
                                 "position 7", "position 8"])
        # self.p_wheel_2.model()
        # self.p_wheel_2.setEnabled(False)
        self.p_wheel_2.setFixedWidth(120)
        self.p_button = QPushButton("Go to Position")
        self.p_button.setToolTip(
            "When you press this button, the Wheel will start moving \n"
            "to the position of the requested positions.\n"
        )
        self.p_button.setFixedWidth(150)
        self.p_button.clicked.connect(self.go_to_wheels_position)

        hposition.addWidget(wheel_label)
        hposition.addWidget(self.p_wheel_1)
        hposition.addWidget(self.p_wheel_2)
        hposition.addWidget(self.p_button)
        hposition.setAlignment(Qt.AlignTop)

        ### ATTENUATION WIDGET ###

        htransmittance = QHBoxLayout()
        t_label = QLabel("Set the wheels to attenuation: ")

        self.attenuation = QComboBox()
        self.attenuation.setCurrentIndex(-1)
        self.attenuation.addItem("= Attenuation =")
        self.attenuation.model().item(0).setEnabled(False)
        self.attenuation.setFixedWidth(230)

        self.t_button = QPushButton("Go to attenuation")
        self.t_button.setToolTip(
            "When you press this button, the Wheel will start moving \n"
            "to the position of the requested attenuation.\n"
        )
        self.t_button.setFixedWidth(150)
        self.t_button.clicked.connect(self.go_to_wheels_attenuation)

        htransmittance.addWidget(t_label)
        htransmittance.addWidget(self.attenuation)
        htransmittance.addWidget(self.t_button)


        htransmittance.setAlignment(Qt.AlignTop)

        ### JOG WIDGET ###
        hjog  = QHBoxLayout()
        j_label = QLabel("Jog attenuation position:")

        self.j_up_button = QToolButton()
        self.j_up_button.setArrowType(Qt.RightArrow)
        self.j_up_button.setToolTip("Jogs the Attenuation to the next upper level")
        self.j_up_button.setObjectName("up")
        self.j_up_button.setFixedWidth(35)
        self.j_up_button.clicked.connect(self.att_level)

        self.j_down_button = QToolButton()
        self.j_down_button.setArrowType(Qt.LeftArrow)
        self.j_down_button.setToolTip("Jogs the Attenuation to the next downer level")
        self.j_down_button.setObjectName("down")
        self.j_down_button.setFixedWidth(35)
        self.j_down_button.clicked.connect(self.att_level)

        hjog.addWidget(j_label)
        hjog.addWidget(self.j_down_button)
        hjog.setAlignment(Qt.AlignLeft)
        hjog.addWidget(self.j_up_button)
        hjog.setAlignment(Qt.AlignLeft)
        hjog.setAlignment(Qt.AlignTop)

        ## PUTTING ALL TOGETHER ###
        vbox.addLayout(hposition)
        vbox.setSpacing(0)
        vbox.addLayout(htransmittance)
        vbox.addLayout(hjog)
        vbox.setAlignment(Qt.AlignTop)

        group_box = QGroupBox("Commands", self)
        group_box.setLayout(vbox)
        group_box.setFixedWidth(600)
        return group_box

    def createWheelStatusWidget(self):

        group_box = QGroupBox("Eksma Filter Wheel Status")

        # Create the label fields that display the current measure

        vbox = QVBoxLayout()

        # FILTERWHEEL STATUS ###
        # HK Parameters from motor and wheels
        vstatusbox = QVBoxLayout()
        vstatusbox.setAlignment(Qt.AlignTop)

        self.wheelstatus = [[QLabel("Position (steps):"), QLineEdit()],
                            [QLabel("Wheel speed:"), QLineEdit()],
                            [QLabel("Temperature (°C)"), QLineEdit()],
                            [QLabel("Engine Current (mA):"), QLineEdit()],
                            [QLabel("Power Supply voltage (V):"), QLineEdit()],
                            [QLabel("Status Flags:"), QLineEdit()]]

        for elements in self.wheelstatus:
            hstatus = QHBoxLayout()
            hstatus.setSpacing(3)
            # elements[0].setStyleSheet("QLabel { background-color : LightGray; }") --> here we see the widget policy
            elements[0].setFixedWidth(210)
            elements[1].setReadOnly(True)
            elements[1].setFixedWidth(70)
            hstatus.addWidget(elements[0])
            hstatus.addWidget(elements[1])

            vstatusbox.addLayout(hstatus)

        ## FLAGS WIDGET ##
        vflagbox = QVBoxLayout()

        self.wheel_flags = [[QLabel("Is homed"), QLed(self, offColour=QLed.Red, onColour=QLed.Green, shape=QLed.Square)],
                            [QLabel("Secur"), QLed(self, offColour=QLed.Green, onColour=QLed.Red, shape=QLed.Square)],
                            [QLabel("Alarm"), QLed(self, offColour=QLed.Green, onColour=QLed.Red, shape=QLed.Square)],
                            [QLabel("Error"), QLed(self, offColour=QLed.Green, onColour=QLed.Red, shape=QLed.Square)]]

        for element in self.wheel_flags:
            hflags = QHBoxLayout()
            hflags.setSpacing(3)
            element[1].setFixedSize(15, 15)
            hflags.addWidget(element[1])
            hflags.addWidget(element[0])

            vflagbox.addLayout(hflags)

        # vledbox = QVBoxLayout()
        # hbox = QHBoxLayout()
        # self.homing_led = QLed(self, offColour=QLed.Red, onColour=QLed.Green, shape=QLed.Square)
        # self.homing_led.setFixedSize(15, 15)
        #
        # hbox.addWidget(self.homing_led)
        # hbox.setAlignment(Qt.AlignTop)
        #
        # hbox.addWidget(QLabel("Is Homed"))
        # hbox.setAlignment(Qt.AlignTop)
        # hbox.setSpacing(5)
        # vledbox.addLayout(hbox)

        # ATTENUATION UNITS WIDGET
        vattbox = QVBoxLayout()
        vattbox.setAlignment(Qt.AlignTop)

        att_label = QLabel("== ATTENUATION PARAMETERS ==")

        vattbox.addWidget(att_label)

        self.wheelconfiguration = [[QLabel("Actual wheel attenuation:"), QLineEdit()]]
        for elements in self.wheelconfiguration:
            hconf = QHBoxLayout()
            hconf.setSpacing(3)
            elements[0].setFixedWidth(210)
            elements[1].setReadOnly(True)
            elements[1].setFixedWidth(70)
            hconf.addWidget(elements[0])
            hconf.addWidget(elements[1])

            vattbox.addLayout(hconf)

        self.att_modes = [[QRadioButton("OD")],
                                [QRadioButton("Transmittance (%)")],
                                [QRadioButton("Irradiance (W/cm2)")],
                                [QRadioButton("Star Magnitude")]
                                ]
        for mode in self.att_modes:
            mode[0].clicked.connect(self.set_mode)
            vattbox.addWidget(mode[0])

        vbox.addLayout(vstatusbox)
        vbox.addLayout(vflagbox)
        #vbox.addLayout(vledbox)
        vbox.addLayout(vattbox)

        group_box.setLayout(vbox)
        group_box.setFixedWidth(290)
        return group_box

    def init_gui(self):

        # Switch to using white background and black foreground for pyqtgraph stripcharts

        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")

        # The main frame in which all the other frames are located, the outer Application frame

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        self.wheel_1 = self.createWheelPositionWidget()
        self.wheel_1.setTitle("Wheel 1")
        self.wheel_2 = self.createWheelPositionWidget()
        self.wheel_2.setTitle("Wheel 2")

        self.wheel_control = self.createWheelControlWidget()
        wheel_box = QVBoxLayout()
        wheel_box.addWidget(self.wheel_1)
        wheel_box.addWidget(self.wheel_2)
        wheel_box.addWidget(self.wheel_control)
        wheel_box.setSpacing(3)

        hbox = QHBoxLayout()
        self.createToolbar()
        hbox.addWidget(self.createWheelStatusWidget())
        hbox.addLayout(wheel_box)

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

    def onClick(self):

        sender = self.sender()

        MODULE_LOGGER.debug(f"sender.text() = {sender.text()}")
        MODULE_LOGGER.debug(f"sender.isChecked() = {sender.isChecked()}")

        self.notifyObservers(sender)

    def set_mode(self):
        #todo: convert attenuation values to the mode selected
        print("new mode selected")

    def set_connection_state(self, state):

        if state == "connected":
            self.reconnect_action.setChecked(True)
        elif state == "disconnected":
            self.reconnect_action.setChecked(False)
        else:
            raise UnknownStateError(
                f"Unknown State ({state}), expected 'connected' or 'disconnected'."
            )

    def update_position(self, new_position):
        #print(new_position)
        ## resetting to false:
        self.wheel_1.findChildren(QLed)[new_position[0]].blockSignals(True)  # Block signals just in case: to be removed if any other way is used to select the wheels position
        for x in self.wheel_1.findChildren(QLed):
            x.value = False
            x.repaint() # this is now needed to update the QLed widget, depends on OS and pyqt versions
        self.wheel_1.findChildren(QLed)[new_position[0]].value = True
        self.wheel_1.findChildren(QLed)[new_position[0]].repaint() # this is now needed to update the QLed widget, depends on OS and pyqt versions
        self.wheel_1.findChildren(QLed)[new_position[0]].blockSignals(False)

        self.wheel_2.findChildren(QLed)[new_position[1]].blockSignals(True)
        for x in self.wheel_2.findChildren(QLed):
            x.value = False
            x.repaint() # this is now needed to update the QLed widget, depends on OS and pyqt versions
        self.wheel_2.findChildren(QLed)[new_position[1]].value = True
        self.wheel_2.findChildren(QLed)[new_position[1]].repaint() # this is now needed to update the QLed widget, depends on OS and pyqt versions
        self.wheel_2.findChildren(QLed)[new_position[1]].blockSignals(False)

        self.update_attenuation_value()

    def update_attenuations(self, levels):
        ## setting the wheel transmittances:
        for elements in range(8):
            self.wheel_1.findChildren(QLineEdit)[elements].setText(levels[0][elements])
            self.wheel_2.findChildren(QLineEdit)[elements].setText(levels[1][elements])

    def update_attenuation_value(self):
        # boolean list of Qleds for each wheel:
        att_pos1 = [i.value for i in self.wheel_1.findChildren(QLed)]
        att_pos2 = [i.value for i in self.wheel_2.findChildren(QLed)]

        # getting the required index from the position:
        index1 = list(compress(range(len(att_pos1)), att_pos1))[0]
        index2 = list(compress(range(len(att_pos2)), att_pos2))[0]

        # Some indexes might not exist as they are lead to duplicated attenuation levels, that is why the ValueError
        # is used
        try:
            att_index = self.attenuation_values[1].index([index1, index2]) + 1

        except ValueError:
            # Normally only numbers are thrown here:
            att_1 = float(self.wheel_1.findChildren(QLineEdit)[index1].text())
            att_2 = float(self.wheel_2.findChildren(QLineEdit)[index2].text())
            att_index = self.attenuation_values[0].index(att_1 + att_2)

        # updates attenuation combobox
        self.attenuation.blockSignals(True)
        self.attenuation.setCurrentIndex(att_index)
        self.attenuation.repaint()
        self.attenuation.blockSignals(False)

        # updates attenuation value in the config widget
        self.wheelconfiguration[0][1].setText(self.attenuation.currentText())
        self.wheelconfiguration[0][1].repaint()

    def initialize_position_values(self, init_values, levels):
        pos_wheel_1 = init_values[0]
        pos_wheel_2 = init_values[1]

        # fixme: there is an issue here as the wheel might not be at (0,0) position on sw boot ...
        #  for the moment a warning message is sent on init
        if self.wheel_flags[0][1].value == 0:
            self.wheel_flags[0][1].setToolTip("Homing is needed")
            for elements in range(8):
                self.wheel_1.findChildren(QLineEdit)[elements].setText("None")
                self.wheel_2.findChildren(QLineEdit)[elements].setText("None")

        else:
            if any(i !=0 for i in init_values):
                description = "The filter wheel has been started in a non zero position."
                info_text = (
                    "The GUI will start, but the initial position of the filter wheel might not be the real one."
                    "In order to correctly initialize the wheel, please do a homing command first "
                    "Otherwise, move both wheel 1 and wheel 2 to their zero position "
                )

                show_warning_message(description, info_text)
            else:
                # setting the initial wheel positions:
                self.wheel_1.findChildren(QLed)[pos_wheel_1].blockSignals(
                    True)  # Block signals just in case: to be removed if any other way is used to select the wheels position
                self.wheel_1.findChildren(QLed)[pos_wheel_1].value = True
                self.wheel_1.findChildren(QLed)[pos_wheel_1].blockSignals(False)
                self.wheel_2.findChildren(QLed)[pos_wheel_2].blockSignals(True)
                self.wheel_2.findChildren(QLed)[pos_wheel_2].value = True
                self.wheel_2.findChildren(QLed)[pos_wheel_2].blockSignals(False)

                self.update_attenuation_value()

            self.wheel_flags[0][1].setToolTip("The wheel is calibrated, no homing needed")

            # setting the wheel transmittances:
            for elements in range(8):
                self.wheel_1.findChildren(QLineEdit)[elements].setText(repr(levels[0][elements]))
                self.wheel_2.findChildren(QLineEdit)[elements].setText(repr(levels[1][elements]))



    def initialize_status_values(self, _status, s_flags):
        # building status flags list:
        sf = [s_flags["Is homed"], s_flags["Secur"], s_flags["Alarm"], 0]

        # first we see if there are complicated errors:
        error = [s_flags["Control"], s_flags["Err C"], s_flags["Err D"], s_flags["Err V"], s_flags["EEPROM Connected"],
                 s_flags["CTP error"], s_flags["Borders Swap Misset"], s_flags["H bridge fault"]]

        if any(value == 1 for value in error):
            sf[3] = 1

        for i in range(len(_status)):
            self.wheelstatus[i][1].setText(repr(_status[i]))

        # update of the status flags:
        for i in range(len(sf)):
            self.wheel_flags[i][1].value = sf[i]

        # checks if homing state changed thus goes to enable

        if sf[0] == 0:
            self.enable_control_layout()
        else:
            pass

    def initialize_attenuator_values(self, value):
        # Initializes the attenuator combobox from the Commanding widget
        self.attenuation_values = value
        _factors = self.attenuation_values[0]
        _values = map(str, _factors)
        self.attenuation.addItems(_values)

        # Initializes the attenuator configuration spinbox from the status widget
        self.att_modes[0][0].blockSignals(True)
        self.att_modes[0][0].setChecked(True)
        self.att_modes[0][0].blockSignals(False)


    def enable_control_layout(self):
        # Now we check homing from the new flags coming from the controller:
        _homing = self.wheel_flags[0][1].value
        for elements in self.wheel_control.findChildren(QComboBox):
            elements.setEnabled(_homing)
        for elements in self.wheel_control.findChildren(QToolButton):
            elements.setEnabled(_homing)
        for elements in self.wheel_control.findChildren(QPushButton):
            elements.setEnabled(_homing)

    def go_to_wheels_position(self):
        new_position = [self.p_wheel_1.currentIndex() - 1, self.p_wheel_2.currentIndex() - 1]
        if any(pos < 0 for pos in new_position):
            MODULE_LOGGER.warning("Please select a position for each of the filter wheels")
        else:
            self.actionObservers({"set_position": new_position})

    def go_to_wheels_attenuation(self):
        # takes the index value of transmittance, calculates the wheels position and moves the wheels to the position.
        t_value = self.attenuation.currentIndex()
        if t_value == 0:
            MODULE_LOGGER.warning("Please select an attenuation from the combo box")
        else:
            index = self.attenuation_values[1]
            index = index[t_value-1]
            self.actionObservers({"set_position": index})

    def att_level(self):
        sender = self.sender()
        object_name = sender.objectName()
        self.actionObservers({"att_level": object_name})


class FilterWheelUIModel:
    def __init__(self, type_):
        self.type = type_

        if self.type == "proxy":
            self.fw = FilterWheel8SMC4Proxy()
        elif self.type == "direct":
            self.fw = FilterWheel8SMC4Controller()
            self.fw.connect()
        elif self.type == "simulator":
            self.fw = FilterWheel8SMC4Simulator()
        else:
            raise Exception(
                f"Unknown type of Filter Wheel implementation passed into the model: {type}"
            )
        if self.fw is not None:
            MODULE_LOGGER.debug(
                f"FilterWheel8SMC4Controller initialized as {self.fw.__class__.__name__}"
            )

    def has_commands(self):
        if self.type == "proxy":
            return self.fw.has_commands()
        return True

    def load_commands(self):
        if self.type == "proxy":
            self.fw.load_commands()

    def is_simulator(self):
        return self.fw.is_simulator()

    def is_connected(self):
        if self.type == "proxy":
            return self.fw.is_cs_connected()
        else:
            return self.fw.is_connected()

    def reconnect(self):
        # I need a better insight in what could be wrong and how to reconnect
        # This is probably also dependent on Proxy or other Hexapod implementation

        if self.type == "proxy":
            self.fw.reconnect_cs()
            return self.fw.is_cs_connected()
        else:
            self.fw.reconnect()
            return self.fw.is_connected()
        return False

    def disconnect(self):
        if self.type == "proxy":
            self.fw.disconnect_cs()
        else:
            self.fw.disconnect()

    def load_wheels(self):
        _setup = self.fw.load_wheels()

    def homing(self):
        self.fw.homing()

    def get_position(self):
        position = self.fw.get_position()
        return position

    def set_position(self, pos_wheel1, pos_wheel2):
        _output = self.fw.set_position(pos_wheel1, pos_wheel2)
        return _output

    def get_status(self):
        return self.fw.get_status()

    def wheel_factors(self):
        return self.fw.wheel_factors()

    def att_get_level(self):
        return self.fw.att_get_level()

    def att_level_up(self):
        _position = self.fw.att_level_up()
        return _position

    def att_level_down(self):
        _position = self.fw.att_level_down()
        return _position

    def att_status(self, _flags):
        s_flags = self.fw.att_status(_flags)
        return s_flags


class FilterWheelUIController(Observer):
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.addObserver(self)
        self.create_timer()

        if self.model.is_connected():
            self.initialize_status_values()
            self.initialize_attenuator_values()
            self.initialize_position_values()
            #self.enable_control_layout()

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

        self.states_capture_timer.timeout.connect(self.update_status_values)
        self.states_capture_timer.setInterval(200)

    def start_timer(self):
        self.states_capture_timer.start()

    def stop_timer(self):
        self.states_capture_timer.stop()

    def update(self, changed_object):

        text = changed_object.text()

        if text == "Reconnect":

            if changed_object.isChecked():
                MODULE_LOGGER.debug("Reconnecting the Filter Wheel model.")
                if self.model.reconnect():
                    self.view.set_connection_state("connected")
                    if not self.model.has_commands():
                        self.model.load_commands()
                    self.start_timer()
                else:
                    self.view.reconnect_action.setChecked(False)
            else:
                MODULE_LOGGER.debug("Disconnecting the Filter Wheel model.")
                self.stop_timer()
                self.model.disconnect()
                self.view.set_connection_state("disconnected")

            return

        if text == "Homing":
            MODULE_LOGGER.debug("Trying to perform homing to calibrate the Filter Wheel position")
            self.model.homing()
            self.initialize_position_values()
            self.enable_control_layout()

        if text == "ClearErrors":
            self.model.clearError()

        if text == "Reset":
            pass

    def update_status_values(self):
        _status = self.model.get_status()
        s_flags = self.model.att_status(_status[5])
        self.view.initialize_status_values(_status, s_flags)

    def do(self, actions):

        for action, value in actions.items():
            MODULE_LOGGER.debug(f"do {action} with {value}")
            if action == "set_position":
                position = value
                MODULE_LOGGER.debug(
                    f"do: set_position({position[0]}:{type(position[0])}, {position[1]}:{type(position[1])})")
                _ouput = self.model.set_position(position[0], position[1])
                # fake change of the position value: if set_position is OK then we assume the position is correct
                self.view.update_position(position)

            if action == "att_level":
                jog = value
                MODULE_LOGGER.debug(f"do: att_level_up({jog}):{type(jog)}")
                if jog == "up":
                    position = self.model.att_level_up()
                elif jog == "down":
                    position = self.model.att_level_down()
                else:
                    MODULE_LOGGER.warning("Something went wrong when trying to move the wheel")
                self.view.update_position(position)

    def initialize_position_values(self):
        init_position = self.model.get_position()
        levels = self.model.att_get_level()
        self.view.initialize_position_values(init_position, levels)

    def initialize_status_values(self):
        _status = self.model.get_status()
        s_flags = self.model.att_status(_status[5])
        self.view.initialize_status_values(_status, s_flags)

    def initialize_attenuator_values(self):
        self.model.load_wheels()

        _factors = self.model.wheel_factors()
        self.view.initialize_attenuator_values(_factors)

    def enable_control_layout(self):
        self.view.enable_control_layout()


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

    lock_file = QLockFile(str(Path("~/fw8scm4_ui.app.lock").expanduser()))

    STYLES_LOCATION = find_file("styles.qss", in_dir="egse/gui")

    args = list(sys.argv)
    args[1:1] = ["-stylesheet", str(STYLES_LOCATION)]

    app = QApplication(args)
    app.setWindowIcon(QIcon(str(get_resource(":/icons/color-scheme.svg"))))

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
            proxy = FilterWheel8SMC4Proxy()
            if not proxy.ping():
                description = "Could not connect to Filter Wheel Control Server"
                info_text = (
                    "The GUI will start, but the connection button will show a disconnected state. "
                    "Please check if the Control Server is running and start the server if needed. "
                    "Otherwise, check if the correct HOSTNAME for the control server is set in the "
                    "Settings.yaml "
                    "configuration file."
                )

                show_warning_message(description, info_text)

        view = FilterWheelUIView()
        model = FilterWheelUIModel(args.type)
        controller = FilterWheelUIController(model, view)

        view.show()
        return app.exec_()
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The FW8SMC4 GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()

if __name__ == "__main__":
    sys.exit(main())
