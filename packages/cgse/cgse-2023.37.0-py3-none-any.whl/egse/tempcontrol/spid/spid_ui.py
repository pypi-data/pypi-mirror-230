from pathlib import Path

import sys
import argparse
import logging
import multiprocessing
import zmq
import pickle

import numpy as np
from zmq import ZMQError
from datetime import datetime

from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, Qt, QSize, QLockFile

from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QFrame, QHBoxLayout, QVBoxLayout, QGroupBox, QVBoxLayout, QGridLayout, \
    QLineEdit, QSizePolicy, QSpacerItem, QPushButton, QDoubleSpinBox, QScrollArea, QMessageBox

from egse.tempcontrol.spid.spid import PidProxy, PidSimulator
from egse.tempcontrol.spid.spid import CTRL_SETTINGS as PID_CTRL_SETTINGS

from egse.setup import get_setup
from egse.gui.led import LED
from egse.gui.buttons import ToggleButton
from egse.resource import get_resource
from egse.zmq_ser import connect_address
from egse.observer import Observer, Observable

multiprocessing.current_process().name = 'spid_ui'

logger = logging.getLogger(__name__)

class PidMonitoringWorker(QObject):
    
    pid_timestamp_status_signal = pyqtSignal(list)
    pid_update_status_signal = pyqtSignal(list)
    pid_enabled_status_signal = pyqtSignal(dict)
    pid_setpoint_status_signal = pyqtSignal(list)
    pid_constants_status_signal = pyqtSignal(list)
    
    def __init__(self):
        super(PidMonitoringWorker, self).__init__()
        
        self.activate = False
        self.just_reconnected = True
        
        self.monitoring_socket = None
        self.is_socket_connected = True
        self.monitoring_timeout = 0.5
        
        self.connect_socket()
        
        self.previous_pid_update_status_signal = []
        self.previous_pid_timestamp_status_signal = []
        self.previous_pid_setpoint = []
        self.previous_pid_enabled_status_signal = []
        self.previous_pid_constants_status_signal = []
        
    def connect_socket(self):
        """ Create a socket and connect to the monitoring port.
        """
        

        try:
            transport   = PID_CTRL_SETTINGS.PROTOCOL
            hostname    = PID_CTRL_SETTINGS.HOSTNAME
            
            monitoring_port = PID_CTRL_SETTINGS.MONITORING_PORT
            monitoring_address = connect_address(transport, hostname, monitoring_port)
            
            self.monitoring_socket = zmq.Context().socket(zmq.SUB)
            self.monitoring_socket.connect(monitoring_address)
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
        """Start updated the Beaglebone status"""
        self.run()
        
    @pyqtSlot()
    def run(self):
        """Keep on checkin whether the Beaglebone state has changed
        
        If the beaglebone status has changed, update it in the GUI
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
                    
                    pid_enabled     = monitoring_info['Enabled']
                    pid_setpoint    = monitoring_info['Setpoint']
                    pid_timestamp   = monitoring_info['Timestamp']
                    pid_error       = monitoring_info['Error']
                    pid_isum        = monitoring_info['Isum']
                    pid_input       = monitoring_info['Input']
                    pid_output      = monitoring_info['Output']
                    pid_const       = monitoring_info['PidConst']
                    pid_state       = [pid_error, pid_isum, pid_input, pid_output]
                    
                    if pid_timestamp != self.previous_pid_timestamp_status_signal:
                        self.pid_timestamp_status_signal.emit(pid_timestamp)
                        
                    self.previous_pid_timestamp_status_signal = pid_timestamp
                    
                    if pid_setpoint != self.previous_pid_setpoint:
                        self.pid_setpoint_status_signal.emit(pid_setpoint)
                    
                    self.previous_pid_setpoint = pid_setpoint
                    
                    if pid_enabled != self.previous_pid_enabled_status_signal:
                        self.pid_enabled_status_signal.emit(pid_enabled)
                        
                    self.previous_pid_enabled_status_signal = pid_enabled
                    
                    if pid_state != self.previous_pid_update_status_signal:
                        self.pid_update_status_signal.emit(pid_state)
                    
                    self.previous_pid_update_status_signal = pid_state
                    
                    if pid_const != self.previous_pid_constants_status_signal:
                        self.pid_constants_status_signal.emit(pid_const)
                    
                    self.previous_pid_constants_status_signal = pid_const
                             
            except ZMQError as exc:
                raise exc



class pidChannelWidget(QGroupBox):
    def __init__(self, channel_info, parent=None):
        super().__init__(parent=parent)
     
        
        self.pid = channel_info[0]
        self.htr = channel_info[3]
        self.ch  = channel_info[4]
        self.setObjectName("PID channel {} widget".format(self.ch))
        self.setMinimumWidth(380)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setContentsMargins(0, -1, 0, -1)
        self.gridLayout.setObjectName("gridLayout")
        
        self.widget = ToggleButton(
            name="Turn On\Off PID Channel",
            status_tip=f"Heater {self.htr} Channel {self.ch} On\Off",
            selected=get_resource(":/icons/switch-on.svg"),
            not_selected=get_resource(":/icons/switch-off.svg"),
        )
        self.widget.setMinimumSize(QSize(35, 35))
        self.widget.setObjectName("widget")    
        self.gridLayout.addWidget(self.widget, 0, 0)
        self.label = QLabel(self)
        self.label.setMinimumSize(QSize(0, 0))
        self.label.setObjectName("label")
        self.label.setText("Heater {} Channel {}".format(int(self.htr + 1), chr(int(self.ch) + 65)))
        self.gridLayout.addWidget(self.label, 0, 1, 1, 5)
        self.label_2 = QLabel(self)
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.label_2.setText("Setpoint:")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.label_3 = QLabel(self)
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.label_3.setText("Input:")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.label_6 = QLabel(self)
        self.label_6.setObjectName("label_6")
        self.label_6.setText("Err:")
        self.gridLayout.addWidget(self.label_6, 2, 2, 1, 1)
        self.doubleSpinBox = QDoubleSpinBox(self)
        self.doubleSpinBox.setMinimumSize(QSize(90, 0))
        self.doubleSpinBox.setProperty("value", 21.0)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.doubleSpinBox.setMinimum(-250)
        self.gridLayout.addWidget(self.doubleSpinBox, 2, 1, 1, 1)
        self.label_13 = QLabel(self)
        self.label_13.setObjectName("label_13")
        self.label_13.setText("Timestamp:")
        self.gridLayout.addWidget(self.label_13, 5, 1, 1, 2)
        self.label_12 = QLabel(self)
        self.label_12.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_12.setObjectName("label_12")
        self.label_12.setText("Out:")
        self.gridLayout.addWidget(self.label_12, 4, 0, 1, 1)
        self.label_7 = QLabel(self)
        self.label_7.setObjectName("label_7")
        self.label_7.setText("I:")
        self.gridLayout.addWidget(self.label_7, 3, 2, 1, 1)
        self.label_14 = QLabel(self)
        self.label_14.setObjectName("label_14")
        self.gridLayout.addWidget(self.label_14, 6, 1, 1, 4)
        self.lineEdit_3 = QLineEdit(self)
        self.lineEdit_3.setMinimumSize(QSize(90, 0))
        self.lineEdit_3.setReadOnly(True)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridLayout.addWidget(self.lineEdit_3, 3, 3, 1, 1)
        self.lineEdit_4 = QLineEdit(self)
        self.lineEdit_4.setMinimumSize(QSize(90, 0))
        self.lineEdit_4.setReadOnly(True)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridLayout.addWidget(self.lineEdit_4, 4, 1, 1, 1)
        self.lineEdit_2 = QLineEdit(self)
        self.lineEdit_2.setMinimumSize(QSize(90, 0))
        self.lineEdit_2.setReadOnly(True)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 3, 1, 1, 1)
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setMinimumSize(QSize(90, 0))
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 2, 3, 1, 1)
        self.pushButton = QPushButton(self)
        self.pushButton.setMaximumSize(QSize(50, 16777215))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Set")
        self.gridLayout.addWidget(self.pushButton, 2, 4, 1, 1)
        self.widget_2 = ToggleButton(
            width=10,
            height=10,
            name="More PID information",
            status_tip=f"Show more information about pid channel",
            selected=get_resource(":/icons/more.svg"),
            not_selected=get_resource(":/icons/arrow-up.svg")
        )
        self.widget_2.setObjectName("widget_2")
        self.gridLayout.addWidget(self.widget_2, 6, 5, 1, 1)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QLabel(self)
        self.label_4.setObjectName("label_4")
        self.label_4.setText("Kp:")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.label_5 = QLabel(self)
        self.label_5.setObjectName("label_5")
        self.label_5.setText("0")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.label_8 = QLabel(self)
        self.label_8.setObjectName("label_8")
        self.label_8.setText("Ki:")
        self.horizontalLayout_2.addWidget(self.label_8)
        self.label_9 = QLabel(self)
        self.label_9.setObjectName("label_9")
        self.label_9.setText("0")
        self.horizontalLayout_2.addWidget(self.label_9)
        self.label_10 =QLabel(self)
        self.label_10.setObjectName("label_10")
        self.label_10.setText("Kd:")
        self.horizontalLayout_2.addWidget(self.label_10)
        self.label_11 = QLabel(self)
        self.label_11.setObjectName("label_11")
        self.label_11.setText("0")
        self.horizontalLayout_2.addWidget(self.label_11)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 6)
        self.verticalLayout.addLayout(self.gridLayout)

        self.widget_2.clicked.connect(self.show_more_less)
        
        self.show_less()
        
    def show_less(self):
        self.lineEdit_3.hide()
        self.lineEdit_4.hide()
        self.label_4.hide()
        self.label_5.hide()
        self.label_7.hide()
        self.label_8.hide()
        self.label_9.hide()
        self.label_10.hide()
        self.label_11.hide()
        self.label_12.hide()
    
    def show_more(self):
        self.lineEdit_3.show()
        self.lineEdit_4.show()
        self.label_4.show()
        self.label_5.show()
        self.label_7.show()
        self.label_8.show()
        self.label_9.show()
        self.label_10.show()
        self.label_11.show()
        self.label_12.show()
    
    def show_more_less(self):
        if not self.widget_2.is_selected():
            self.show_more()
        else:
            self.show_less()

class pidGroupbox(QGroupBox):
    def __init__(self, pid_name, channels, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("{}".format(pid_name))
        self.setMaximumWidth(400)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QLabel(self)
        self.label.setText(pid_name)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        
        self.widget_2 = ToggleButton(
            name="Turn On\Off PID Channel",
            status_tip=pid_name,
            selected=get_resource(":/icons/switch-on.svg"),
            not_selected=get_resource(":/icons/switch-off.svg"),
        )
        
        self.doubleSpinBox = QDoubleSpinBox(self)
        self.doubleSpinBox.setMinimumSize(QSize(90, 0))
        self.doubleSpinBox.setMinimum(-250)
        
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        
        self.pushButton = QPushButton('set')
        self.pushButton.setMaximumSize(QSize(50, 16777215))
        
        self.horizontalLayout.addWidget(self.widget_2)
        spacerItem =QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.horizontalLayout.addWidget(self.doubleSpinBox)
        self.horizontalLayout.addWidget(self.pushButton)
        
        
        self.widget = LED()
        self.widget.setMinimumSize(QSize(25, 25))
        self.widget.setObjectName("widget")
        self.horizontalLayout.addWidget(self.widget)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.channels = [None] * len(channels)
        for idx, channel in enumerate(channels):
            if (channel[1] == 0 and channel[2] == 0):
                continue
            self.channels[idx] = pidChannelWidget(channel)
            self.verticalLayout.addWidget(self.channels[idx])
        spacerItem_2 =QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem_2)

class pidMainWindow(QMainWindow, Observable):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Beaglebone PID Controller")
        self.setGeometry(600, 100, 1250, 670)
        self.setMaximumWidth(1250)
        
        setup = get_setup()
        self.pid_configuration = setup.gse.spid.configuration.heaters
        self.pid_configuration['MaRi'] = self.pid_configuration['TRP2'] + self.pid_configuration['TRP3'] + self.pid_configuration['TRP4']
        del self.pid_configuration['TRP2'], self.pid_configuration['TRP3'], self.pid_configuration['TRP4']

        self.pid_monitoring_thread = QThread(self)
        self.pid_monitoring_worker = PidMonitoringWorker()
        self.pid_monitoring_worker.moveToThread(self.pid_monitoring_thread)
        
        self.pid_monitoring_worker.pid_enabled_status_signal.connect(self.on_pid_enabled_status_signal)
        self.pid_monitoring_worker.pid_setpoint_status_signal.connect(self.on_pid_setpoint_status_signal)
        self.pid_monitoring_worker.pid_timestamp_status_signal.connect(self.on_pid_timestamp_status_signal)
        self.pid_monitoring_worker.pid_update_status_signal.connect(self.on_pid_update_status_signal)
        self.pid_monitoring_worker.pid_constants_status_signal.connect(self.on_pid_constant_status_signal)
        
        self.pid_monitoring_thread.started.connect(self.pid_monitoring_worker.start_process)
        self.pid_monitoring_thread.start()
        
        self.initUI()

    def on_pid_enabled_status_signal(self, monitoring_info:dict):
        monitoring_info = list(monitoring_info.values())
        
        for idx, (_, configuration) in enumerate(self.pid_configuration.items()):
            state_lin = len(self.pid_channels[idx].channels)
            pid_state = 0
            for ch_idx, ch in enumerate(configuration):
                if (ch[1] == 0 and ch[2] == 0):
                    state_lin -= 1
                    continue
                self.pid_channels[idx].channels[ch_idx].widget.set_selected(bool(monitoring_info[ch[0]]))
                ch_enabled = self.pid_channels[idx].channels[ch_idx].widget.is_selected()
                pid_state += 1 if int(ch_enabled) else 0
            if pid_state == state_lin:
                self.pid_channels[idx].widget.set_color(1)
                self.pid_channels[idx].widget_2.set_selected(True)
            elif  0 < pid_state < state_lin:
                self.pid_channels[idx].widget_2.set_selected(False)
                self.pid_channels[idx].widget.set_color(2)
            else:
                self.pid_channels[idx].widget_2.set_selected(False)
                self.pid_channels[idx].widget.set_color(0)
    
    def on_pid_constant_status_signal(self, monitoring_info):
        for idx, (_, configuration) in enumerate(self.pid_configuration.items()):
            for ch_idx, ch in enumerate(configuration):
                if (ch[1] == 0 and ch[2] == 0):
                    continue                
                self.pid_channels[idx].channels[ch_idx].label_5.setText(f"{monitoring_info[idx][0]:.2e}")
                self.pid_channels[idx].channels[ch_idx].label_9.setText(f"{monitoring_info[idx][1]:.2e}")  
                self.pid_channels[idx].channels[ch_idx].label_11.setText(f"{monitoring_info[idx][2]:.2e}")  
    
    def on_pid_setpoint_status_signal(self, monitoring_info):
        for idx, (_, configuration) in enumerate(self.pid_configuration.items()):
            setpoint = []
            for ch_idx, ch in enumerate(configuration):
                if (ch[1] == 0 and ch[2] == 0):
                    continue                
                self.pid_channels[idx].channels[ch_idx].doubleSpinBox.setValue(float(monitoring_info[ch[0]]))
                setpoint.append(float(monitoring_info[ch[0]]))
            self.pid_channels[idx].doubleSpinBox.setValue(float(np.amax(setpoint)))
                
    def on_pid_timestamp_status_signal(self, monitoring_info):
        for idx, (_, configuration) in enumerate(self.pid_configuration.items()):
            for ch_idx, ch in enumerate(configuration):
                if (ch[1] == 0 and ch[2] == 0):
                    continue
                self.pid_channels[idx].channels[ch_idx].label_14.setText(str(datetime.fromtimestamp(monitoring_info[int(ch[0])])))
    
    def on_pid_update_status_signal(self, monitoring_info):
        channels = 0
        for idx, (pid, configuration) in enumerate(self.pid_configuration.items()):
            for ch_idx, ch in enumerate(configuration):
                if (ch[1] == 0 and ch[2] == 0):
                    continue
                self.pid_channels[idx].channels[ch_idx].lineEdit.setText(f"{monitoring_info[0][channels]:.2e}")
                self.pid_channels[idx].channels[ch_idx].lineEdit_3.setText(f"{monitoring_info[1][channels]:.2e}")
                self.pid_channels[idx].channels[ch_idx].lineEdit_2.setText(f"{monitoring_info[2][channels]:.2e}")
                self.pid_channels[idx].channels[ch_idx].lineEdit_4.setText(f"{monitoring_info[3][channels]:.2e}")
                channels += 1

    def initUI(self):
        scroll_frame = QScrollArea()
        scroll_frame.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_frame.setWidgetResizable(True)
        app_frame = QFrame()
        grid_layout = QGridLayout()
        self.pid_channels = [None] * len(self.pid_configuration)
        for idx, (pid, configuration) in enumerate(self.pid_configuration.items()):
            configuration.sort( key = lambda configuration: (configuration[3], configuration[4]))
            self.pid_channels[idx] = pidGroupbox(pid, configuration)
            
            self.pid_channels[idx].pushButton.clicked.connect(self.set_all_pid_setpoint)
            self.pid_channels[idx].widget_2.clicked.connect(self.set_all_pid_control)
            
            grid_layout.addWidget(self.pid_channels[idx], int(idx / 3), idx % 3)
            for ch_idx, ch in enumerate(configuration):
                if (ch[1] == 0 and ch[2] == 0):
                    continue
                self.pid_channels[idx].channels[ch_idx].widget.clicked.connect(self.set_pid_control)
                self.pid_channels[idx].channels[ch_idx].pushButton.clicked.connect(self.set_pid_setpoint)
        app_frame.setLayout(grid_layout)
        scroll_frame.setWidget(app_frame)
        self.setCentralWidget(scroll_frame)

    def set_all_pid_control(self):
        sender = self.sender()
        name = sender.parent().objectName()
        new_state = sender.is_selected()
        sender.set_selected(on=new_state)
        for channel in self.pid_configuration[name]:
            try:
                self.actionObservers({"set_pid_control" : [channel[0], bool(new_state)]})
            except Exception as e:
                warning_popup("set_pid_control : Channel {} {}".format(pid, "Enabled" 
                                                                        if new_state else "Disabled"), e)
    def set_pid_control(self):
        sender = self.sender()
        state = sender.is_selected()
        new_state = state
        sender.set_selected(on=new_state)
        pid = sender.parent().pid
        htr = sender.parent().htr
        ch  = sender.parent().ch

        try:
            self.actionObservers({"set_pid_control" : [pid, bool(new_state)]})
        except Exception as e:
            warning_popup("set_pid_control : Channel {} {}".format(pid, "Enabled" 
                                                                   if new_state else "Disabled"), e)
    
    def set_all_pid_setpoint(self):
        sender = self.sender()
        setpoint = float(sender.parent().doubleSpinBox.value())
        name = sender.parent().objectName()
        
        for channel in self.pid_configuration[name]:
            try:
                self.actionObservers({"set_pid_setpoint" : [channel[0], float(setpoint)]})
            except Exception as e:
                 warning_popup("set_pid_control : Channel {} {}".format(pid, "Enabled" 
                                                                    if new_state else "Disabled"), e)
    
    def set_pid_setpoint(self):
        sender = self.sender()
        setpoint = float(sender.parent().doubleSpinBox.value())
        pid = sender.parent().pid
        htr = sender.parent().htr
        ch  = sender.parent().ch

        try:
            self.actionObservers({"set_pid_setpoint" : [pid, float(setpoint)]})
        except Exception as e:
            warning_popup("set_pid_setpoint : PID Channel {} to {} C".format(pid, setpoint), e)      
              
    def closeEvent(self, close_Event: QCloseEvent) -> None:
        self.pid_monitoring_thread.quit()
        self.pid_monitoring_worker.stop()

def warning_popup(command, error):
    msgBox = QMessageBox()
    msgBox.setWindowTitle("OGSE error occured")
    msgBox.setIcon(QMessageBox.Warning)
    msgBox.setText(f"An error occured while executing: {command}")
    msgBox.setInformativeText(f"{error}")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec_()

class PIDUIModel:
    def __init__(self, mode):
        self.mode = mode
        if self.mode == "proxy":
            try:
                self.pid = PidProxy()
            except Exception as exc:
                raise exc
            
        elif self.mode == 'simulator':
            self.pid = PidSimulator()
        else:
            raise ValueError(f'Unknown type of PID implementation passed into the model')
        
       
        if self.pid is not None:
                logger.debug(f'Heater Controller initialized as {self.pid.__class__.__name__}')

    def set_pid_control(self, ch, state):
        with PidProxy() as pid:
            if state:
                pid.enable(int(ch))
            else:
                pid.disable(int(ch))

    
    def set_pid_setpoint(self, ch, sp):
        with PidProxy() as pid:
            pid.set_temperature(int(ch), float(sp))
    
    def has_commands(self):
        if self.mode == 'proxy':
            with PidProxy() as pid:
                pid.has_commands()
            
        return True
                
    
    def load_commands(self):
        if self.mode == 'proxy':
            with PidProxy() as pid:
                pid.load_commands()
    
    def is_simulator(self):
        with PidProxy() as pid:
            pid.is_simulator()

    
    def is_connected(self):
        with PidProxy() as pid:
            pid.is_cs_connected()
    
    def reconnect(self):
        if self.mode == "proxy":
            with PidProxy() as pid:
                pid.reconnect()
            return self.pid.is_cs_connected()
        return False
    
    def disconnect(self):
        if self.mode == "proxy":
            with PidProxy() as pid:
                return pid.disconnect_cs()

        elif self.mode == 'simulator':
            return self.pid.disconnect()


class PIDUIController(Observer):
    def __init__(self, model: PIDUIModel, view: pidMainWindow):
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
            if action == "set_pid_control":
                ch      = value[0]
                state   = value[1]

                self.model.set_pid_control(ch, state)
 
            if action == "set_pid_setpoint":
                ch      = value[0]
                temp    = value[1]
                self.model.set_pid_setpoint(ch, temp)
        
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
        help="Specify PID implementation you want to connect to.",
        default="proxy",
    )

    args = parser.parse_args()
    return args


def main():

    lock_file = QLockFile(str(Path("~/spid_ui.app.lock").expanduser()))

    args = list(sys.argv)
    app = QApplication(args)

    if lock_file.tryLock(100):

        args = parse_arguments()
        if args.type == 'proxy':
            try:
                proxy = PidProxy()
            except Exception:
                raise Exception
        view = pidMainWindow()
        model = PIDUIModel(args.type)
        controller = PIDUIController(model, view)
        view.show()
        app.exec_()
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The SPID tempcontrol GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()


if __name__ == "__main__":
    main()
        