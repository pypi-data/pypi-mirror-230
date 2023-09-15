import argparse
import logging
import multiprocessing
import pickle
from pathlib import Path

import sys
import zmq
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, Qt, QSize, QRect, QLockFile
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QFrame, QHBoxLayout, QGroupBox, QVBoxLayout, QGridLayout, \
    QLineEdit, QScrollArea, QWidget, QPushButton, QSpacerItem, QSizePolicy, QMessageBox
from zmq import ZMQError

from egse.filterwheel.eksma.fw8smc5 import CTRL_SETTINGS as FW_CTRL_SETTINGS
from egse.filterwheel.eksma.fw8smc5 import Fw8Smc5Proxy, Fw8Smc5Simulator
from egse.gui.led import Led
from egse.lampcontrol.beaglebone.beaglebone import BeagleboneProxy
from egse.lampcontrol.beaglebone.beaglebone import CTRL_SETTINGS as BB_CTRL_SETTINGS

from egse.gui.led import Led, Indic as LedIndic
from egse.observer import Observer, Observable
from egse.powermeter.thorlabs.pm100a import CTRL_SETTINGS as PM100_CTRL_SETTINGS
from egse.resource import get_resource
from egse.setup import get_setup
from egse.shutter.thorlabs.sc10 import CTRL_SETTINGS as SC10_CTRL_SETTINGS
from egse.shutter.thorlabs.sc10 import Sc10Proxy
from egse.stages.arun.smd3 import CTRL_SETTINGS as SMD3_CTRL_SETTINGS
from egse.stages.arun.smd3 import Smd3Proxy

from egse.zmq_ser import connect_address

multiprocessing.current_process().name = 'fw8smc5_ui'

logger = logging.getLogger(__name__)

class FilterWheelMonitoringWorker(QObject):
    
    fw_ri_signal        = pyqtSignal(float)
    fw_fwc_signal       = pyqtSignal(float)
    fw_pos_1_signal     = pyqtSignal(int)
    fw_pos_2_signal     = pyqtSignal(int)
    
    hartmann_status_signal = pyqtSignal(bool)
    
    shutter_status_signal = pyqtSignal(bool)
    
    pm100_power_signal    = pyqtSignal(float)
    
    lamp_on_signal          = pyqtSignal(bool)
    laser_on_signal         = pyqtSignal(bool)
    module_fault_signal     = pyqtSignal(bool)
    controller_fault_signal = pyqtSignal(bool)
    
    def __init__(self):
        super(FilterWheelMonitoringWorker, self).__init__()
        
        self.activate = False
        self.just_reconnected = True
        
        self.monitoring_socket = None
        self.sc10_monitoring_socket = None
        self.is_socket_connected = True
        self.monitoring_timeout = 0.5
        
        self.connect_socket()
        
        self.previous_fw_ri    = []
        self.previous_fw_fwc  = []
        self.previous_fw_pos_1 = []
        self.previous_fw_pos_2 = []
        
        self.previous_hartmann_status = []

        self.previous_shutter_status = []
        
        self.previous_pm100_power = []
        
        self.previous_laser_state = []
        self.previous_lamp_state = []
        self.previous_controller_fault = []
        self.previous_module_fault = []
        
    def connect_socket(self):
        """ Create a socket and connect to the monitoring port.
        """
        try:
            transport   = FW_CTRL_SETTINGS.PROTOCOL
            hostname    = FW_CTRL_SETTINGS.HOSTNAME
            
            monitoring_port = FW_CTRL_SETTINGS.MONITORING_PORT
            fw_monitoring_address = connect_address(transport, hostname, monitoring_port)
            
            transport   = SC10_CTRL_SETTINGS.PROTOCOL
            hostname    = SC10_CTRL_SETTINGS.HOSTNAME
            
            monitoring_port = SC10_CTRL_SETTINGS.MONITORING_PORT
            sc10_monitoring_address = connect_address(transport, hostname, monitoring_port)
            
            transport   = SMD3_CTRL_SETTINGS.PROTOCOL
            hostname    = SMD3_CTRL_SETTINGS.HOSTNAME
            
            monitoring_port = SMD3_CTRL_SETTINGS.MONITORING_PORT
            smd3_monitoring_address = connect_address(transport, hostname, monitoring_port)
            
            transport   = PM100_CTRL_SETTINGS.PROTOCOL
            hostname    = PM100_CTRL_SETTINGS.HOSTNAME
            
            monitoring_port = PM100_CTRL_SETTINGS.MONITORING_PORT
            pm100_monitoring_address = connect_address(transport, hostname, monitoring_port)
            
            transport   = BB_CTRL_SETTINGS.PROTOCOL
            hostname    = BB_CTRL_SETTINGS.HOSTNAME
            
            monitoring_port = BB_CTRL_SETTINGS.MONITORING_PORT
            bb_monitoring_address = connect_address(transport, hostname, monitoring_port)
            
            self.monitoring_socket = zmq.Context().socket(zmq.SUB)
            self.monitoring_socket.connect(fw_monitoring_address)
            self.monitoring_socket.connect(sc10_monitoring_address)
            self.monitoring_socket.connect(smd3_monitoring_address)
            self.monitoring_socket.connect(pm100_monitoring_address)
            self.monitoring_socket.connect(bb_monitoring_address)
            self.monitoring_socket.setsockopt_string(zmq.SUBSCRIBE, "")
            
            self.monitoring_timeout = 0.5
            
            self.is_socket_connected = True
            
        except:
            self.is_socket_connected = False
            
    def stop(self):
        
        """ Stop the monitoring worker.
        The monitoring socket is disconnected from the monitoring port and is then closed immediately.
        """
        
        self.monitoring_socket.close()
        self.is_socket_connected = False
        
        self.active = False
        
    def start_process(self):
        """Start updated the Filterwheel status"""
        self.run()
        
    @pyqtSlot()
    def run(self):
        """Keep on checkin whether the Filterwheel state has changed
        
        If the Filterwheel status has changed, update it in the GUI
        Raises:
            Exception: ZMQ Error
        """
        
        self.active = True
        while self.is_socket_connected and self.active:
            
            try:
                socket_list, _, exc_list = zmq.select([self.monitoring_socket], [], [], timeout=self.monitoring_timeout)

                if self.monitoring_socket in socket_list:
                    try:
                        pickle_string = self.monitoring_socket.recv()
                    except Exception:
                        raise Exception

                    monitoring_info = pickle.loads(pickle_string)

                    if 'fw8smc5_status' in monitoring_info:
                        fw_ri       = monitoring_info['fw8smc5_status']['RelativeIntensity']
                        fw_fwc      = monitoring_info['fw8smc5_status']['FullWellCapacity']
                        fw_pos_1    = monitoring_info['fw8smc5_status']['FW1Position']
                        fw_pos_2    = monitoring_info['fw8smc5_status']['FW2Position']
                        
                        if fw_ri != self.previous_fw_ri:
                            self.fw_ri_signal.emit(fw_ri)
                            
                        self.previous_fw_ri = fw_ri
                        
                        if fw_fwc != self.previous_fw_fwc:
                            self.fw_fwc_signal.emit(fw_fwc)
                            
                        self.previous_fw_fwc = fw_fwc
                        
                        if fw_pos_1 != self.previous_fw_pos_1:
                            self.fw_pos_1_signal.emit(fw_pos_1)
                        
                        self.previous_fw_pos_1 = fw_pos_1
                        
                        if fw_pos_2 != self.previous_fw_pos_2:
                            self.fw_pos_2_signal.emit(fw_pos_2)
                            
                        self.previous_fw_pos_2 = fw_pos_2
                        
                    if 'hartmann_status' in monitoring_info:
                        hartmann_status = bool(monitoring_info['hartmann_status'])
                        
                        if hartmann_status != self.previous_hartmann_status:
                            self.hartmann_status_signal.emit(hartmann_status)
                        
                        self.previous_hartmann_status = hartmann_status
                        
                    if 'shutter_state' in monitoring_info:
                        shutter_status = bool(monitoring_info['shutter_state'])
                        
                        if shutter_status != self.previous_shutter_status:
                            self.shutter_status_signal.emit(shutter_status)
                            
                        self.previous_shutter_status = shutter_status
                        
                    if 'pm100a_power' in monitoring_info:
                        pm100_power = float(monitoring_info['pm100a_power'])
                        
                        if pm100_power != self.previous_pm100_power:
                            self.pm100_power_signal.emit(pm100_power)
                            
                        self.previous_pm100_power = pm100_power
                    
                    if 'lamp_status' in monitoring_info:
                        laser_state      = monitoring_info['lamp_status']['laser_state']
                        lamp_state       = monitoring_info['lamp_status']['lamp_state']
                        module_fault     = monitoring_info['lamp_status']['module_fault']
                        controller_fault = monitoring_info['lamp_status']['controller_fault']

                        if laser_state != self.previous_laser_state:
                            self.laser_on_signal.emit(laser_state)
                        
                        self.previous_laser_state = laser_state
                        if lamp_state != self.previous_lamp_state:
                            self.lamp_on_signal.emit(lamp_state)
                        
                        self.previous_lamp_state = lamp_state
                        if module_fault != self.previous_module_fault:
                            self.module_fault_signal.emit(module_fault)
                        
                        self.previous_module_fault = module_fault
                        if controller_fault != self.previous_controller_fault:
                            self.controller_fault_signal.emit(controller_fault)
                        
                        self.previous_controller_fault = controller_fault
                        
            except ZMQError as exc:
                raise exc

class OGSEWindow(QGroupBox):
    def __init__(self, setup):
        super().__init__()
        
        self.setObjectName("OGSE Window")
        
        self.gridLayout_3 = QGridLayout(self)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupBox = QGroupBox(self)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_4 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.gridLayout_4 = QGridLayout()
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.label_3.setText("Relative intensity: ")
        self.gridLayout_4.addWidget(self.label_3, 0, 0, 1, 1)
        self.lineEdit_3 = QLineEdit(self.groupBox)
        self.lineEdit_3.setMaximumSize(QSize(250, 16777215))
        self.lineEdit_3.setReadOnly(True)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridLayout_4.addWidget(self.lineEdit_3, 0, 1, 1, 1)
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.label_4.setText("Full well capacity: ")
        self.gridLayout_4.addWidget(self.label_4, 1, 0, 1, 1)
        self.lineEdit_4 = QLineEdit(self.groupBox)
        self.lineEdit_4.setMaximumSize(QSize(250, 16777215))
        self.lineEdit_4.setReadOnly(True)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridLayout_4.addWidget(self.lineEdit_4, 1, 1, 1, 1)
        
        self.pushButton_34 = QPushButton()
        self.pushButton_34.setText("Home")
        self.gridLayout_4.addWidget(self.pushButton_34, 2, 0, 1, 2)    
        self.pushButton_32 = QPushButton()
        self.pushButton_32.setMinimumWidth(150)
        self.pushButton_32.setText("Decrease intensity")
        self.gridLayout_4.addWidget(self.pushButton_32, 3, 0, 1, 1)
        self.pushButton_33 = QPushButton()
        self.pushButton_33.setMinimumWidth(150)
        self.pushButton_33.setText("Increase Intensity")
        self.gridLayout_4.addWidget(self.pushButton_33, 3, 1, 1, 1)
        spacerItem_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem_2, 4, 0, 1, 2)
        self.horizontalLayout_4.addLayout(self.gridLayout_4)
        
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QScrollArea(self.groupBox)
        self.scrollArea.setMinimumSize(QSize(550, 0))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 546, 178))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_6 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout_16 = QHBoxLayout()
        self.label_12 = QLabel("Search: ")
        self.horizontalLayout_16.addWidget(self.label_12)
        self.lineEdit_6 = QLineEdit()
        self.horizontalLayout_16.addWidget(self.lineEdit_6)
        self.verticalLayout_6.addLayout(self.horizontalLayout_16)
        
        try:
            ri_list = setup.gse.ogse.calibration.relative_intensity_by_wheel
            
            row = 0
            column = 0
            self.ri_pushButtons = {}
            for idx, value in enumerate(ri_list.values()):
                self.ri_pushButtons[f"{value}_{idx}"] = QPushButton(self.scrollAreaWidgetContents)
                self.ri_pushButtons[f"{value}_{idx}"].setText(f"{value:5e}")
                self.ri_pushButtons[f"{value}_{idx}"].setObjectName(f"{value:5e}")
                self.gridLayout_2.addWidget(self.ri_pushButtons[f"{value}_{idx}"], row, column % 4, 1, 1)
                column +=  1
                if column >= 4 and column % 4 == 0:
                    row += 1
        except Exception as e:
            logger.exception("Could not generate the relative intensity buttons. This is most likely "\
                            f"caused by an incorrect setup.")
            sys.exit()
                
        spacerItem_3 = QSpacerItem(20, 383, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem_3, row+1, 0)     
        self.verticalLayout_6.addLayout(self.gridLayout_2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.horizontalLayout_4.addLayout(self.gridLayout)
        self.gridLayout_3.addWidget(self.groupBox, 1, 0, 1, 1)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox_3 = QGroupBox(self)
        self.groupBox_3.setMaximumSize(QSize(16777215, 370))
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label = QLabel(self.groupBox_3)
        self.label.setMaximumSize(QSize(16777215, 50))
        self.label.setText("Filterwheel 1")
        font = QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_4.addWidget(self.label)
        self.lineEdit = QLineEdit(self.groupBox_3)
        self.lineEdit.setMinimumSize(QSize(150, 290))
        font = QFont()
        font.setPointSize(150)
        self.lineEdit.setFont(font)
        self.lineEdit.setAlignment(Qt.AlignCenter)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout_4.addWidget(self.lineEdit)
        self.verticalLayout_3.addWidget(self.groupBox_3)
        self.groupBox_2 = QGroupBox(self)
        self.groupBox_2.setMaximumSize(QSize(16777215, 50))
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.pushButton = QPushButton(self.groupBox_2)
        self.pushButton.setMinimumSize(QSize(50, 0))
        self.pushButton.setObjectName("fw1_<")
        self.pushButton.setText("<")
        self.horizontalLayout_2.addWidget(self.pushButton)
        
        self.fw1_positions = {}
        
        for i in range(0, 8):
            self.fw1_positions[f"fw1_{i}"] = QPushButton(self.groupBox_2)
            self.fw1_positions[f"fw1_{i}"].setMinimumSize(QSize(30, 0))
            self.fw1_positions[f"fw1_{i}"].setObjectName(f"fw1_{i}")
            self.fw1_positions[f"fw1_{i}"].setText(f"{i}")
            self.horizontalLayout_2.addWidget(self.fw1_positions[f"fw1_{i}"])

        self.pushButton_2 = QPushButton(self.groupBox_2)
        self.pushButton_2.setMinimumSize(QSize(50, 0))
        self.pushButton_2.setObjectName("fw1_>")
        self.pushButton_2.setText(">")
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_4 = QGroupBox(self)
        self.groupBox_4.setMaximumSize(QSize(16777215, 370))
        self.groupBox_4.setTitle("")
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_2 = QLabel(self.groupBox_4)
        self.label_2.setMaximumSize(QSize(16777215, 50))
        self.label_2.setText("Filterwheel 2")
        font = QFont()
        font.setPointSize(20)
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_5.addWidget(self.label_2)
        self.lineEdit_2 = QLineEdit(self.groupBox_4)
        self.lineEdit_2.setMinimumSize(QSize(150, 290))
        font = QFont()
        font.setPointSize(150)
        self.lineEdit_2.setFont(font)
        self.lineEdit_2.setAlignment(Qt.AlignCenter)
        self.lineEdit_2.setReadOnly(True)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.verticalLayout_5.addWidget(self.lineEdit_2)
        self.verticalLayout_2.addWidget(self.groupBox_4)
        self.groupBox_5 = QGroupBox(self)
        self.groupBox_5.setMaximumSize(QSize(16777215, 50))
        self.groupBox_5.setTitle("")
        self.groupBox_5.setObjectName("groupBox_5")
        self.horizontalLayout_3 = QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_20 = QPushButton(self.groupBox_5)
        self.pushButton_20.setMinimumSize(QSize(50, 0))
        self.pushButton_20.setObjectName("fw2_<")
        self.pushButton_20.setText("<")
        self.horizontalLayout_3.addWidget(self.pushButton_20)
        
        self.fw2_positions = {}
        for i in range(0, 8):
            self.fw2_positions[f"fw2_{i}"] = QPushButton(self.groupBox_5)
            self.fw2_positions[f"fw2_{i}"].setMinimumSize(QSize(30, 0))
            self.fw2_positions[f"fw2_{i}"].setObjectName(f"fw2_{i}")
            self.fw2_positions[f"fw2_{i}"].setText(f"{i}")
            self.horizontalLayout_3.addWidget(self.fw2_positions[f"fw2_{i}"])
        
        self.pushButton_18 = QPushButton(self.groupBox_5)
        self.pushButton_18.setMinimumSize(QSize(50, 0))
        self.pushButton_18.setObjectName("fw2_>")
        self.pushButton_18.setText(">")
        self.horizontalLayout_3.addWidget(self.pushButton_18)
        self.verticalLayout_2.addWidget(self.groupBox_5)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.gridLayout_3.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.groupBox_6 = QGroupBox(self)
        self.groupBox_6.setMinimumSize(QSize(200, 0))
        self.groupBox_6.setTitle("")
        self.groupBox_6.setObjectName("groupBox_6")
        self.verticalLayout = QVBoxLayout(self.groupBox_6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.widget = Led(self.groupBox_6)
        self.widget.setMinimumSize(QSize(25, 25))
        self.widget.setMaximumSize(QSize(25, 25))
        self.horizontalLayout_5.addWidget(self.widget)
        self.label_5 = QLabel(self.groupBox_6)
        self.label_5.setMinimumSize(QSize(0, 0))
        self.label_5.setObjectName("label_5")
        self.label_5.setText("Shutter control")
        self.horizontalLayout_5.addWidget(self.label_5)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.pushButton_25 = QPushButton(self.groupBox_6)
        self.pushButton_25.setObjectName("pushButton_25")
        self.pushButton_25.setText("Open")
        self.pushButton_25.setEnabled(False)
        self.horizontalLayout_6.addWidget(self.pushButton_25)
        self.pushButton_26 = QPushButton(self.groupBox_6)
        self.pushButton_26.setObjectName("pushButton_26")
        self.pushButton_26.setText("Close")
        self.pushButton_26.setEnabled(False)
        self.horizontalLayout_6.addWidget(self.pushButton_26)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.line = QFrame(self.groupBox_6)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.widget_2 = Led(self.groupBox_6)
        self.widget_2.setMinimumSize(QSize(25, 25))
        self.widget_2.setMaximumSize(QSize(25, 25))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_7.addWidget(self.widget_2)
        self.label_6 = QLabel(self.groupBox_6)
        self.label_6.setObjectName("label_6")
        self.label_6.setText("Hartmann control")
        self.horizontalLayout_7.addWidget(self.label_6)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.pushButton_27 = QPushButton(self.groupBox_6)
        self.pushButton_27.setObjectName("pushButton_27")
        self.pushButton_27.setText("Unmask")
        self.pushButton_27.setEnabled(False)
        self.horizontalLayout_8.addWidget(self.pushButton_27)
        self.pushButton_28 = QPushButton(self.groupBox_6)
        self.pushButton_28.setObjectName("pushButton_28")
        self.pushButton_28.setText("Mask")
        self.pushButton_28.setEnabled(False)
        self.horizontalLayout_8.addWidget(self.pushButton_28)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        self.line_2 = QFrame(self.groupBox_6)
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_7 = QLabel(self.groupBox_6)
        self.label_7.setObjectName("label_7")
        self.label_7.setText("Powermeter")
        self.horizontalLayout_9.addWidget(self.label_7)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        self.lineEdit_5 = QLineEdit(self.groupBox_6)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.lineEdit_5.setEnabled(True)
        self.lineEdit_5.setReadOnly(True)
        self.verticalLayout.addWidget(self.lineEdit_5)
        
        self.line_3 = QFrame(self.groupBox_6)
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout.addWidget(self.line_3)
        self.label_13 = QLabel(self.groupBox_6)
        self.label_13.setObjectName("label_8")
        self.label_13.setText("Lamp controller")
        self.verticalLayout.addWidget(self.label_13)
        self.horizontalLayout_10 = QHBoxLayout()
        self.widget_3 = Led(self.groupBox_6)
        self.widget_3.setMinimumSize(QSize(25, 25))
        self.widget_3.setMaximumSize(QSize(25, 25))
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_10.addWidget(self.widget_3)
        self.label_8 = QLabel(self.groupBox_6)
        self.label_8.setObjectName("label_8")
        self.label_8.setText("Laser on")
        self.horizontalLayout_10.addWidget(self.label_8)
        self.verticalLayout.addLayout(self.horizontalLayout_10)
        
        self.horizontalLayout_11 = QHBoxLayout()
        self.widget_4 = Led(self.groupBox_6)
        self.widget_4.setMinimumSize(QSize(25, 25))
        self.widget_4.setMaximumSize(QSize(25, 25))
        self.widget_4.setObjectName("widget_4")
        self.horizontalLayout_11.addWidget(self.widget_4)
        self.label_9 = QLabel(self.groupBox_6)
        self.label_9.setObjectName("label_9")
        self.label_9.setText("Lamp on")
        self.horizontalLayout_11.addWidget(self.label_9)
        self.verticalLayout.addLayout(self.horizontalLayout_11)
        
        self.horizontalLayout_12 = QHBoxLayout()
        self.widget_5 = Led(self.groupBox_6)
        self.widget_5.setMinimumSize(QSize(25, 25))
        self.widget_5.setMaximumSize(QSize(25, 25))
        self.widget_5.setObjectName("widget_5")
        self.horizontalLayout_12.addWidget(self.widget_5)
        self.label_10 = QLabel(self.groupBox_6)
        self.label_10.setObjectName("label_10")
        self.label_10.setText("Controller fault")
        self.horizontalLayout_12.addWidget(self.label_10)
        self.verticalLayout.addLayout(self.horizontalLayout_12)
        
        self.horizontalLayout_13 = QHBoxLayout()
        self.widget_6 = Led(self.groupBox_6)
        self.widget_6.setMinimumSize(QSize(25, 25))
        self.widget_6.setMaximumSize(QSize(25, 25))
        self.widget_6.setObjectName("widget_6")
        self.horizontalLayout_13.addWidget(self.widget_6)
        self.label_11 = QLabel(self.groupBox_6)
        self.label_11.setObjectName("label_11")
        self.label_11.setText("Lamp module fault")
        self.horizontalLayout_13.addWidget(self.label_11)
        self.verticalLayout.addLayout(self.horizontalLayout_13)
        
        self.horizontalLayout_14 = QHBoxLayout()
        self.pushButton_29 = QPushButton(self.groupBox_6)
        self.pushButton_29.setObjectName("pushButton_29")
        self.pushButton_29.setText("Turn on")
        self.pushButton_29.setEnabled(False)
        self.horizontalLayout_14.addWidget(self.pushButton_29)
        self.pushButton_30 = QPushButton(self.groupBox_6)
        self.pushButton_30.setObjectName("pushButton_30")
        self.pushButton_30.setText("Turn off")
        self.pushButton_30.setEnabled(False)
        self.horizontalLayout_14.addWidget(self.pushButton_30)
        self.verticalLayout.addLayout(self.horizontalLayout_14)
        
        self.horizontalLayout_15 = QHBoxLayout()
        self.pushButton_31 = QPushButton(self.groupBox_6)
        self.pushButton_31.setObjectName("pushButton_31")
        self.pushButton_31.setText("Fix controller fault")
        self.pushButton_31.setEnabled(False)
        self.horizontalLayout_15.addWidget(self.pushButton_31)
        self.verticalLayout.addLayout(self.horizontalLayout_15)
 
        spacerItem = QSpacerItem(20, 383, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout_3.addWidget(self.groupBox_6, 0, 1, 2, 1)
        
        
class OGSEUIView(QMainWindow, Observable):
    WHEEL_POSITIONS = 8
    TOTAL_POSITIONS = WHEEL_POSITIONS * WHEEL_POSITIONS
    ROTATION_STEPS = 600
    POSITION_STEPS  = ROTATION_STEPS // WHEEL_POSITIONS
    
    def __init__(self):
        super().__init__()
        self.resize(1089, 650)
        self.setMaximumSize(1100, 850)
        self.setWindowTitle("Filterwheel GUI")
        
        self.fw_monitoring_thread = QThread(self)
        self.fw_monitoring_worker = FilterWheelMonitoringWorker()
        self.fw_monitoring_worker.moveToThread(self.fw_monitoring_thread)

        self.fw_monitoring_worker.fw_ri_signal.connect(self.on_fw_ri_changed)
        self.fw_monitoring_worker.fw_fwc_signal.connect(self.on_fw_fwc_changed)
        self.fw_monitoring_worker.fw_pos_1_signal.connect(self.on_fw_pos_1_changed)
        self.fw_monitoring_worker.fw_pos_2_signal.connect(self.on_fw_pos_2_changed)
        
        self.fw_monitoring_worker.shutter_status_signal.connect(self.on_shutter_changed)
        self.fw_monitoring_worker.hartmann_status_signal.connect(self.on_hartmann_changed)
        self.fw_monitoring_worker.pm100_power_signal.connect(self.on_power_meter_changed)
        
        self.fw_monitoring_worker.laser_on_signal.connect(self.on_laser_changed)
        self.fw_monitoring_worker.lamp_on_signal.connect(self.on_lamp_changed)
        self.fw_monitoring_worker.module_fault_signal.connect(self.on_module_fault_changed)
        self.fw_monitoring_worker.controller_fault_signal.connect(self.on_controller_fault_changed)
        
        self.fw_monitoring_thread.started.connect(self.fw_monitoring_worker.start_process)
        self.fw_monitoring_thread.start()

        self.initUI()
        
    def initUI(self):
        setup = get_setup()
        self.groupbox = OGSEWindow(setup)
        self.setCentralWidget(self.groupbox)
        
        # Connect relative intensity
        for button in self.groupbox.ri_pushButtons.values():
            button.clicked.connect(self.select_relative_intensity)
        
        # Connect filterwheel 1 buttons
        for button in self.groupbox.fw1_positions.values():
            button.clicked.connect(self.select_position_wheel)

        # Connect filterwheel 2 buttons
        for button in self.groupbox.fw2_positions.values():
            button.clicked.connect(self.select_position_wheel)

        self.groupbox.pushButton_25.clicked.connect(self.toggle_shutter_control)
        self.groupbox.pushButton_26.clicked.connect(self.toggle_shutter_control)

        self.groupbox.pushButton_27.clicked.connect(self.toggle_hartmann_control)
        self.groupbox.pushButton_28.clicked.connect(self.toggle_hartmann_control)

        self.groupbox.pushButton_29.clicked.connect(self.toggle_lamp_control)
        self.groupbox.pushButton_30.clicked.connect(self.toggle_lamp_control)
        self.groupbox.pushButton_31.clicked.connect(self.clear_lamp_fault)
        
        self.groupbox.lineEdit_6.textChanged.connect(self.update_scrollArea)
        
        self.groupbox.pushButton_34.clicked.connect(self.home_filterwheel)
        self.groupbox.pushButton_32.clicked.connect(self.decrease_intensity_wheel)
        self.groupbox.pushButton_33.clicked.connect(self.increase_intensity_wheel)
        
        self.groupbox.pushButton_20.clicked.connect(self.decrease_position_wheel)
        self.groupbox.pushButton_18.clicked.connect(self.increase_position_wheel)
        
        self.groupbox.pushButton.clicked.connect(self.decrease_position_wheel)
        self.groupbox.pushButton_2.clicked.connect(self.increase_position_wheel)
        
        self.home_offsets = setup.gse.filterwheel.home_offset

    def select_relative_intensity(self):
        sender = self.sender()
        try:
            self.actionObservers({"set_relative_intensity" : [float(sender.text())]})
        except Exception as e:
            warning_popup(f"set_relative_intensity {sender.text()}", e)
    
    def increase_position_wheel(self):
        sender  = self.sender()
        name    = sender.objectName()
        wheel = 0 if 'fw1' in name else 1
        if 'fw1' in name:
            current_pos = self.groupbox.lineEdit.text()
        elif 'fw2' in name:
            current_pos = self.groupbox.lineEdit_2.text()
        
        try:
            self.actionObservers({'set_position_wheel' : [int(wheel), int(current_pos) + 1]})
        except Exception as e:
            warning_popup(f"set_position_wheel {wheel} {int(current_pos) + 1}", e)
    
    def decrease_position_wheel(self):
        sender  = self.sender()
        name    = sender.objectName()
        wheel = 0 if 'fw1' in name else 1
        if 'fw1' in name:
            current_pos = self.groupbox.lineEdit.text()
        elif 'fw2' in name:
            current_pos = self.groupbox.lineEdit_2.text()
        
        try:
            self.actionObservers({'set_position_wheel' : [int(wheel), int(current_pos) - 1]})
        except Exception as e:
            warning_popup(f"set_position_wheel {wheel} {int(current_pos) - 1}", e)
    
    def increase_intensity_wheel(self):
        try:
            self.actionObservers({"increase_intensity":[]})
        except Exception as e:
            warning_popup(f"increase_intensity", e)
    
    def decrease_intensity_wheel(self):
        try:
            self.actionObservers({"decrease_intensity":[]})
        except Exception as e:
            warning_popup(f"decrease_intensity", e)
    
    def home_filterwheel(self):
        try:
            self.actionObservers({"home_filterwheel":[]})
        except Exception as e:
            warning_popup(f"home_filterwheel", e)
    
    def select_position_wheel(self):
        sender = self.sender()
        wheel = sender.objectName().split("_")[0]
        wheel = 0 if wheel == "fw1" else 1
        lens = sender.objectName().split("_")[1]
        try:
            self.actionObservers({"set_position_wheel" : [int(wheel), int(lens)]})
        except Exception as e:
            warning_popup(f"set_position_wheel {wheel} {lens}", e)
    
    def toggle_shutter_control(self):
        try:
            self.actionObservers({'set_shutter' : []})
        except Exception as e:
            warning_popup(f"set_shutter", e)

    def toggle_hartmann_control(self):
        sender = self.sender()
        state = True if sender.text() == 'Unmask' else False
        
        try:
            self.actionObservers({'set_hartmann' : [state]})
        except Exception as e:
            warning_popup(f"set_hartmann {state}", e)
    
    def toggle_lamp_control(self):
        sender = self.sender()
        state = True if 'on' in sender.text() else False
        
        try:
            self.actionObservers({'set_lamp' : [state]})
        except Exception as e:
            warning_popup(f"set_lamp {state}", e)
    
    def clear_lamp_fault(self):
        try:
            self.actionObservers({'fix_controller_fault': []})
        except Exception as e:
            warning_popup("fix_controller_fault", e)
    
    def update_scrollArea(self, text):
        for button in self.groupbox.ri_pushButtons.values():
            if text in button.text():
                button.show()
            else:
                button.hide()
        
        row     = 0
        column  = 0
        for button in self.groupbox.ri_pushButtons.values():
            self.groupbox.gridLayout_2.removeWidget(button)
            if button.isVisible():
                self.groupbox.gridLayout_2.addWidget(button, row, column % 4)
                column += 1
                if column >= 4 and column % 4 == 0:
                    row += 1

    
    def on_fw_ri_changed(self, monitoring_info: float):
        self.groupbox.lineEdit_3.setText(f"{monitoring_info:4e}")
    
    def on_fw_fwc_changed(self, monitoring_info: float):
        self.groupbox.lineEdit_4.setText(f"{monitoring_info:4e}")
    
    def on_fw_pos_1_changed(self, monitoring_info: int):
        self.groupbox.lineEdit.setText(f"{(monitoring_info - self.home_offsets[0]) // self.POSITION_STEPS % self.WHEEL_POSITIONS}")
    
    def on_fw_pos_2_changed(self, monitoring_info: int):
        self.groupbox.lineEdit_2.setText(f"{(monitoring_info - self.home_offsets[1]) // self.POSITION_STEPS % self.WHEEL_POSITIONS}")

    def on_shutter_changed(self, monitoring_info: bool):
        if monitoring_info:
            self.groupbox.widget.set_color(1)
            self.groupbox.pushButton_25.setEnabled(False)
            self.groupbox.pushButton_26.setEnabled(True)
        else:
            self.groupbox.widget.set_color(3)
            self.groupbox.pushButton_25.setEnabled(True)
            self.groupbox.pushButton_26.setEnabled(False)
    
    def on_hartmann_changed(self, monitoring_info: bool):
        if not monitoring_info:
            self.groupbox.widget_2.set_color(1)
            self.groupbox.pushButton_27.setEnabled(False)
            self.groupbox.pushButton_28.setEnabled(True)
        else:
            self.groupbox.widget_2.set_color(3)
            self.groupbox.pushButton_27.setEnabled(True)
            self.groupbox.pushButton_28.setEnabled(False)
    
    def on_power_meter_changed(self, monitoring_info):
            self.groupbox.lineEdit_5.setText(f'{monitoring_info:.3e} W')
    
    def on_laser_changed(self, monitoring_info: bool):
        if monitoring_info:
            self.groupbox.widget_3.set_color(1)
            self.groupbox.pushButton_29.setEnabled(False)
            self.groupbox.pushButton_30.setEnabled(True)
        else:
            self.groupbox.widget_3.set_color(3)
            self.groupbox.pushButton_29.setEnabled(True)
            self.groupbox.pushButton_30.setEnabled(False)
        
    
    def on_lamp_changed(self, monitoring_info: bool):
        if monitoring_info:
            self.groupbox.widget_4.set_color(1)
        else:
            self.groupbox.widget_4.set_color(3)
    
    def on_module_fault_changed(self, monitoring_info: bool):
        if monitoring_info:
            self.groupbox.widget_5.set_color(2)
        else:
            self.groupbox.widget_5.set_color(1)
    
    def on_controller_fault_changed(self, monitoring_info: bool):
        if monitoring_info:
            self.groupbox.widget_6.set_color(2)
            self.groupbox.pushButton_31.setEnabled(True) # Change to true when implemented and tested
        else:
            self.groupbox.widget_6.set_color(1)
            self.groupbox.pushButton_31.setEnabled(False)
    
def warning_popup(command, error):
    msgBox = QMessageBox()
    msgBox.setWindowTitle("OGSE error occured")
    msgBox.setIcon(QMessageBox.Warning)
    msgBox.setText(f"An error occured while executing: {command}")
    msgBox.setInformativeText(f"{error}")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec_()
   
class OGSEUIModel:
    def __init__(self, mode):
        pass
    
    def has_commands(self):
        if self.mode == 'proxy':
            with Fw8Smc5Proxy() as fw:
                fw.has_commands()
            
        return True
                
    
    def load_commands(self):
        if self.mode == 'proxy':
            with Fw8Smc5Proxy() as fw:
                fw.load_commands()
    
    def is_simulator(self):
        with Fw8Smc5Proxy() as fw:
            fw.is_simulator()

    
    def is_connected(self):
        with Fw8Smc5Proxy() as fw:
            fw.is_cs_connected()
    
    def reconnect(self):
        if self.mode == "proxy":
            with Fw8Smc5Proxy() as fw:
                fw.reconnect()
            return self.fw.is_cs_connected()
        return False
    
    def disconnect(self):
        if self.mode == "proxy":
            with Fw8Smc5Proxy() as fw:
                return fw.disconnect_cs()

        elif self.mode == 'simulator':
            return self.fw.disconnect()
        
    def set_position_wheel(self, id, position):
        with Fw8Smc5Proxy() as fw:
            fw.set_position_wheel(id, position)
    
    def set_relative_intensity(self, rel_intensity):
        with Fw8Smc5Proxy() as fw:
            fw.set_relative_intensity(rel_intensity)
            
    def toggle_shutter(self):
        with Sc10Proxy() as sc10:
            sc10.toggle_enable()
    
    def set_hartmann(self, state):
        with Smd3Proxy() as smd3:
            smd3.move_mask_fov(state)
    
    def increase_position_wheel(self):
        with Fw8Smc5Proxy() as fw:
            fw.intensity_level_up()
    
    def decrease_position_wheel(self):
        with Fw8Smc5Proxy() as fw:
            fw.intensity_level_down()
    
    def home_filterwheel(self):
        with Fw8Smc5Proxy() as fw:
            fw.home()
            
    def set_lamp(self, state):
        with BeagleboneProxy() as bb:
            bb.set_lamp(state)
            
    def fix_controller_fault(self):
        with BeagleboneProxy() as bb:
            bb.fix_controller_fault()
        
        
class OGSEUIController(Observer):
    def __init__(self, model: OGSEUIModel, view: OGSEUIView):
        self.model  = model
        self.view   = view
        self.view.addObserver(self)
        
    def update(self, changed_object):

        text = changed_object.text()

        if text == "Reconnect":

            if changed_object.isChecked():

                logger.debug("Reconnecting the Heater model.")

                if self.model.reconnect():

                    self.view.set_connection_state(True)

                    if not self.model.has_commands():

                        self.model.load_commands()

                else:
                    self.view.reconnect_action.setChecked(False)
            else:

                logger.debug("Disconnecting the Heater model.")
                self.model.disconnect()
                self.view.set_connection_state(False)

            return
        
    def do(self, actions):
        for action, value in actions.items():
            logger.debug(f"do {action} with {value}")
            
            if action == "set_relative_intensity":
                rel_intensity = value[0]
                
                self.model.set_relative_intensity(rel_intensity)
            if action == "set_position_wheel":
                idx = value[0]
                position = value[1]
                
                self.model.set_position_wheel(idx, position)
                
            if action == 'set_shutter':
                self.model.toggle_shutter()
            
            if action == 'set_hartmann':
                state = value[0]
                
                self.model.set_hartmann(state)
            if action == "increase_intensity":
                self.model.increase_position_wheel()
            if action == "decrease_intensity":
                self.model.decrease_position_wheel()
            if action == "home_filterwheel":
                self.model.home_filterwheel()
            if action == "set_lamp":
                state = value[0]
                self.model.set_lamp(state)
            if action == "fix_controller_fault":
                self.model.fix_controller_fault()
        
def parse_arguments():
    """
    Prepare the arguments that are specific for this application.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type",
        dest="type",
        action="store",
        choices={"proxy", "simulator"},
        help="Specify Filterwheel implementation you want to connect to.",
        default="proxy",
    )

    args = parser.parse_args()
    return args


def main():
    lock_file = QLockFile(str(Path("~/fw8scm5_ui.app.lock").expanduser()))

    args = list(sys.argv)
    app = QApplication(args)
    app.setWindowIcon(QIcon(str(get_resource(":/icons/color-scheme.svg"))))

    if lock_file.tryLock(100):
        args = parse_arguments()

        view = OGSEUIView()
        model = OGSEUIModel(args.type)
        controller = OGSEUIController(model, view)

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
