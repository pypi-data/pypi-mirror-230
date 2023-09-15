
import sys
import argparse
import zmq
import pickle
import logging
from datetime import datetime
import numpy as np

import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas

from PyQt5.QtCore       import QThread, QObject, pyqtSignal, pyqtSlot, QTimer, QEvent
from PyQt5.QtWidgets    import QMainWindow, QApplication, QWidget, QVBoxLayout, QTabWidget, \
                               QSizePolicy, QGridLayout, QGroupBox, QLabel, QFormLayout, \
                               QHBoxLayout, QComboBox, QSpinBox, QLineEdit, QPushButton, \
                               QSpacerItem, QCheckBox

from egse.observer import Observer, Observable
from egse.zmq_ser import connect_address

from egse.vacuum.mks.evision import CTRL_SETTINGS
from egse.vacuum.mks.evision import EvisionProxy, EvisionSimulator

logger = logging.getLogger(__name__)

class RGAMonitoringWorker(QObject):

    rga_new_data_signal         = pyqtSignal(list)
    rga_new_info_signal         = pyqtSignal(dict)
    rga_new_filament_signal     = pyqtSignal(dict)
    rga_new_scan_status_signal  = pyqtSignal(dict)
    rga_new_running_signal      = pyqtSignal(bool)
    
    def __init__(self):
        """ Initialisation of a monitoring worker.
        
        This worker keeps an eye on the monitoring port of the Beaglebone rga. When a change in
            Relevant information occurs, a signalw ill be emitted. These signals will be used to update the GUI
        """
        
        
        super(RGAMonitoringWorker, self).__init__()
        
        self.active = False
        self.just_reconnected = True
        
        self.monitoring_socket = None
        self.is_socket_connected = True
        self.monitoring_timeout = 0.5
        
        self.connect_socket()
        
        # Keep track of the rga status, so we only have to send a signal when the state has changed
        
        self.previous_rga_data      = {}
        self.previous_rga_info      = {}
        self.previous_filament_info = {}
        self.previous_scan_reading  = {}
        self.previous_running       = None
        
    def connect_socket(self):
        """ Create a socket and connect to the monitoring port.
        """
        

        try:
            transport   = CTRL_SETTINGS.PROTOCOL
            hostname    = CTRL_SETTINGS.HOSTNAME
            
            monitoring_port = CTRL_SETTINGS.MONITORING_PORT
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
                    
                    # logger.info(monitoring_info)
                
                    if 'MassReading' in monitoring_info:
                        mass_reading = monitoring_info['MassReading']
                        if mass_reading != self.previous_rga_data:
                            self.rga_new_data_signal.emit(mass_reading)
                        else:
                            running = False
                            if running != self.previous_running:
                                self.rga_new_running_signal.emit(running)
                        self.previous_rga_data = mass_reading
                    
                    if 'FilamentStatus' in monitoring_info:
                        info_reading = monitoring_info['FilamentStatus']
                        if info_reading != self.previous_filament_info:
                            self.rga_new_filament_signal.emit(info_reading)
                        self.previous_filament_info = info_reading
                        
                    if 'RGAStatus' in monitoring_info:
                        status_reading = monitoring_info['RGAStatus']
                        if status_reading != self.previous_rga_info:
                            self.rga_new_info_signal.emit(status_reading)
                        self.previous_filament_info = status_reading
                
                    if 'ScanStatus' in monitoring_info:
                        scan_reading = monitoring_info['ScanStatus']
                        if scan_reading != self.previous_scan_reading:
                            self.rga_new_scan_status_signal.emit(scan_reading)
                        self.previous_scan_reading = scan_reading
                
            except zmq.ZMQError as exc:
                raise exc

class mPlotCanvas(Canvas):
    def __init__(self):
        super().__init__()
        
        # self.fig, self.ax = 
        self.fig = Figure()
        self.ax  = self.fig.add_subplot(111)
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        Canvas.updateGeometry(self)
        

class RGAUIView(QMainWindow, Observable):
    def __init__(self, *args, **kwargs):
        super(RGAUIView, self).__init__(*args, **kwargs)
        
        self.setWindowTitle("E-Vision Residual Gas Analyzer")
        self.setGeometry(300, 300, 1000, 700)
        self.initUI()
        
        self.rga_monitoring_thread = QThread()
        self.rga_monitoring_worker = RGAMonitoringWorker()
        self.rga_monitoring_worker.moveToThread(self.rga_monitoring_thread)
        
        self.rga_monitoring_worker.rga_new_data_signal.connect(self._on_new_data_signal)
        self.rga_monitoring_worker.rga_new_info_signal.connect(self._on_new_info_signal)
        self.rga_monitoring_worker.rga_new_filament_signal.connect(self._on_new_filament_signal)
        self.rga_monitoring_worker.rga_new_scan_status_signal.connect(self._on_new_scan_status_signal)
        self.rga_monitoring_worker.rga_new_running_signal.connect(self._on_new_running_signal)
        
        self.rga_monitoring_thread.started.connect(self.rga_monitoring_worker.start_process)
        
        self.rga_monitoring_thread.start()
        
        self.barRingBuffer = [np.nan] * 201
        
        self.single_line = [[],[]]
        self.peak_lines  = [{},[]]
        
    def initUI(self):
        self.centerWidget = QWidget(self)
        
        self.gridLayout = QGridLayout(self.centerWidget)
        
        # Filament groupbox
        self.groupBox   = QGroupBox()
        self.verticalLayout = QVBoxLayout()
        self.label = QLabel("<b>Filament information</b>")
        self.formLayout = QFormLayout()
        self.label_2 = QLabel("")
        self.label_3 = QLabel("")
        self.label_4 = QLabel("")
        self.label_5 = QLabel("")
        self.formLayout.addRow(QLabel("Summary state"), self.label_2)
        self.formLayout.addRow(QLabel("Active filament"), self.label_3)
        self.formLayout.addRow(QLabel("Max on time"), self.label_4)
        self.verticalLayout.addWidget(self.label)
        self.verticalLayout.addLayout(self.formLayout)
        self.groupBox.setLayout(self.verticalLayout)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1 ,1)
        self.groupBox.setMinimumWidth(300)
        self.groupBox.setMaximumWidth(400)
        self.groupBox.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        
        
        # Sensor groupbox
        self.groupBox_2 = QGroupBox()
        self.verticalLayout_2 = QVBoxLayout()
        self.label_6 = QLabel("<b>Sensor information</b>")
        self.formLayout_2 = QFormLayout()
        self.label_7 = QLabel("")
        self.label_8 = QLabel("")
        self.label_9 = QLabel("")
        self.label_10 = QLabel("")
        self.label_11 = QLabel("")
        self.label_12 = QLabel("")
        self.label_13 = QLabel("")
        self.label_14 = QLabel("")
        self.label_15 = QLabel("")
        self.label_16 = QLabel("")
        self.label_17 = QLabel("")
        self.formLayout_2.addRow(QLabel("Name"), self.label_7)
        self.formLayout_2.addRow(QLabel("Serial number"), self.label_8)
        self.formLayout_2.addRow(QLabel("User application"), self.label_9)
        self.formLayout_2.addRow(QLabel("User address"), self.label_10)
        self.formLayout_2.addRow(QLabel("State"), self.label_11)
        self.formLayout_2.addRow(QLabel("Product ID"), self.label_12)
        self.formLayout_2.addRow(QLabel("Detector type"), self.label_13)
        self.formLayout_2.addRow(QLabel("Total pressure gauge"), self.label_14)
        self.formLayout_2.addRow(QLabel("Filament type"), self.label_15)
        self.formLayout_2.addRow(QLabel("Sensor type"), self.label_16)
        self.formLayout_2.addRow(QLabel("Max mass"), self.label_17)
        self.verticalLayout_2.addWidget(self.label_6)
        self.verticalLayout_2.addLayout(self.formLayout_2)
        self.groupBox_2.setLayout(self.verticalLayout_2)
        self.gridLayout.addWidget(self.groupBox_2, 1, 0, 1 ,1)
        self.groupBox_2.setMinimumWidth(300)
        self.groupBox_2.setMaximumWidth(400)
        self.groupBox_2.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        
        # Scan status
        self.groupBox_3 = QGroupBox()
        self.verticalLayout_3 = QVBoxLayout()
        self.label_18 = QLabel("<b>Scan information</b>")
        self.formLayout_6 = QFormLayout()
        self.label_20 = QLabel("")
        self.label_21 = QLabel("")
        self.label_22 = QLabel("")
        self.label_23 = QLabel("")
        self.label_24 = QLabel("")
        self.label_25 = QLabel("")
        self.label_26 = QLabel("")
        self.label_27 = QLabel("")
        self.formLayout_6.addRow(QLabel("Start mass"), self.label_20)
        self.formLayout_6.addRow(QLabel("End mass"), self.label_21)
        self.formLayout_6.addRow(QLabel("Filter mode"), self.label_22)
        self.formLayout_6.addRow(QLabel("Accuracy"), self.label_23)
        self.formLayout_6.addRow(QLabel("E Gain Index"), self.label_24)
        self.formLayout_6.addRow(QLabel("Source index"), self.label_25)
        self.formLayout_6.addRow(QLabel("Detector index"), self.label_26)
        self.formLayout_6.addRow(QLabel("Running"), self.label_27)
        self.verticalLayout_3.addWidget(self.label_18)
        self.verticalLayout_3.addLayout(self.formLayout_6)
        self.groupBox_3.setLayout(self.verticalLayout_3)
        self.gridLayout.addWidget(self.groupBox_3, 2, 0 ,1, 1)
        self.groupBox_3.setMinimumWidth(300)
        self.groupBox_3.setMaximumWidth(400)
        self.groupBox_3.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        # spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        
        # Plot navigation groupbox
        self.groupBox_4 = QGroupBox()
        self.horizontalLayout = QHBoxLayout()
        self.formLayout_3 = QFormLayout()
        self.label_29 = QLabel("Start mass:")
        self.spinBox = QSpinBox()
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(200)
        self.spinBox.setValue(1)
        self.spinBox.setMaximumWidth(150)
        self.spinBox.valueChanged.connect(self._set_plot_x_axis)
        self.label_30 = QLabel("End mass:")
        self.spinBox_2 = QSpinBox()
        self.spinBox_2.setMinimum(2)
        self.spinBox_2.setMaximum(200)
        self.spinBox_2.setValue(100)
        self.spinBox_2.setMaximumWidth(150)
        self.spinBox.valueChanged.connect(self._set_plot_x_axis)
        self.comboBox = QComboBox()
        self.comboBox.addItems(['PeakCenter', 'PeakMax', 'PeakAverage'])
        self.comboBox.setMaximumWidth(150)
        
        self.label_28 = QLabel("Mass:")
        self.spinBox_7 = QSpinBox()
        self.spinBox_7.setMinimum(1)
        self.spinBox_7.setMaximum(200)
        self.spinBox_7.setValue(4)
        self.spinBox_7.setMaximumWidth(150)
        self.label_28.hide()
        self.spinBox_7.hide()
        self.label_32 = QLabel("Filter mode:")
        self.formLayout_3.addRow(self.label_29, self.spinBox)
        self.formLayout_3.addRow(self.label_30, self.spinBox_2)
        self.formLayout_3.addRow(self.label_28, self.spinBox_7)
        self.formLayout_3.addRow(self.label_32, self.comboBox)
        self.horizontalLayout.addLayout(self.formLayout_3)
        
        self.formLayout_4 = QFormLayout()
        self.label_33 = QLabel("Accuracy:")
        self.spinBox_3 = QSpinBox()
        self.spinBox_3.setMinimum(0)
        self.spinBox_3.setMaximum(10)
        self.spinBox_3.setValue(5)
        self.spinBox_3.setMinimumWidth(150)
        self.label_34 = QLabel("EGain index:")
        self.spinBox_4 = QSpinBox()
        self.spinBox_4.setMinimumWidth(150)
        self.label_35 = QLabel("Source index:")
        self.spinBox_5 = QSpinBox()
        self.spinBox_5.setMinimumWidth(150)
        self.label_36 = QLabel("Detector index:")
        self.spinBox_6 = QSpinBox()
        self.spinBox_6.setMinimumWidth(150)
        self.formLayout_4.addRow(self.label_33, self.spinBox_3)
        self.formLayout_4.addRow(self.label_34, self.spinBox_4)
        self.formLayout_4.addRow(self.label_35, self.spinBox_5)
        self.formLayout_4.addRow(self.label_36, self.spinBox_6)
        self.horizontalLayout.addLayout(self.formLayout_4)
        
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        
        self.formLayout_5 = QFormLayout()
        # self.comboBox_2 = QComboBox()
        # self.comboBox_2.addItems(['bar', 'peak', 'leak'])
        # self.comboBox_2.currentTextChanged.connect(self._on_mode_changed)
        # self.formLayout_5.addRow(QLabel("Measurement mode:"), self.comboBox_2)
        self.checkbox = QCheckBox("Continous measurement")
        self.formLayout_5.addRow(None, self.checkbox)
        
        
        self.pushButton = QPushButton("Turn off filament")
        self.pushButton.clicked.connect(self._on_toggle_filament)
        self.formLayout_5.addRow(QLabel(""), self.pushButton)
        self.pushButton_2 = QPushButton("Start scanning")
        self.pushButton_2.clicked.connect(self._on_toggle_scan)
        self.spinBox_8 = QSpinBox()
        self.spinBox_8.setMinimum(0)
        self.spinBox_8.setMaximum(1000)
        self.spinBox_8.setValue(10)
        self.formLayout_5.addRow(self.spinBox_8, self.pushButton_2)
        self.pushButton_3 = QPushButton("Restart scan")
        self.pushButton_3.clicked.connect(self._on_restart_scan)
        self.formLayout_5.addRow(QLabel(""), self.pushButton_3)
        self.horizontalLayout.addLayout(self.formLayout_5)
        
        self.groupBox_4.setLayout(self.horizontalLayout)
        self.groupBox_4.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        self.gridLayout.addWidget(self.groupBox_4, 3, 0, 1, 3)
        
        # Plot widget
        self.canvas = mPlotCanvas()
        self.canvas.ax.set_xticks(range(self.spinBox.value(), self.spinBox_2.value(), 10))
        self.canvas.ax.grid(True, which='major')
        self.canvas.ax.grid(True, which='minor', linestyle='--')
        self.gridLayout.addWidget(self.canvas, 0, 1, 3, 2)
        self.canvas.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        self.setCentralWidget(self.centerWidget)
    
    def _set_plot_x_axis(self):
        self.canvas.ax.set_xticks(range(self.spinBox.value(), self.spinBox_2.value(), 10))
    
    def _on_mode_changed(self):
        sender = self.sender()
        mode = sender.currentText()
        if mode == 'leak':
            self.label_28.show()
            self.label_29.hide()
            self.label_30.hide()
            self.spinBox.hide()
            self.spinBox_2.hide()
            self.spinBox_7.show()
        if mode == 'bar':
            self.label_28.hide()
            self.label_28.show()
            self.label_30.show()
            self.spinBox.show()
            self.spinBox_2.show()
            self.spinBox_7.hide()
        if mode == 'peak':
            self.label_28.hide()
            self.label_28.hide()
            self.label_30.hide()
            self.spinBox.hide()
            self.spinBox_2.hide()
            self.spinBox_7.hide()
    
    def _on_restart_scan(self):
        try:
            self.actionObservers({'restart_scan' : []})
        except Exception as ex:
            logger.exception(ex)
    
    def setEnableControls(self, state):
        self.label_29.setEnabled(state)
        self.label_30.setEnabled(state)
        self.label_28.setEnabled(state)
        self.label_32.setEnabled(state)
        self.spinBox.setEnabled(state)
        self.spinBox_7.setEnabled(state)
        self.spinBox_2.setEnabled(state)
        self.comboBox.setEnabled(state)
        
        self.label_33.setEnabled(state)
        self.label_34.setEnabled(state)
        self.label_35.setEnabled(state)
        self.label_36.setEnabled(state)
        self.spinBox_3.setEnabled(state)
        self.spinBox_4.setEnabled(state)
        self.spinBox_5.setEnabled(state)
        self.spinBox_6.setEnabled(state)
    
    def _on_toggle_scan(self):
        # sender = self.sender()
        
        # scan_type = self.comboBox_2.currentText()
        name = datetime.now().strftime("%m%d%Y%H%M%S")
        # if scan_type == 'bar':
        start_mass = self.spinBox.value()
        end_mass = self.spinBox_2.value()
        filter_mode = self.comboBox.currentText()
        accuracy = self.spinBox_3.value()
        e_gain_index = self.spinBox_4.value()
        source_index = self.spinBox_5.value()
        detector_index = self.spinBox_6.value()
        num_scans = self.spinBox_8.value()
        try:
            if 'Start' in self.pushButton_2.text():
                self.pushButton_2.setText("Stop scan")
                self.actionObservers({'toggle_scan' : [False]})
                self.actionObservers({'add_bar_chart' : [name,
                                                        start_mass,
                                                        end_mass,
                                                        filter_mode,
                                                        accuracy,
                                                        e_gain_index,
                                                        source_index,
                                                        detector_index]})
                
                logger.info(f'Starting scan {name}, Start mass: {start_mass}, End mass: {end_mass},')
                self.actionObservers({'toggle_scan' : [True, num_scans]})
            elif 'Stop' in self.pushButton_2.text():
                self.pushButton_2.setText("Start scan")
                logger.info(f'Stopping scan {name}, Start mass: {start_mass}, End mass: {end_mass},')
                self.actionObservers({'toggle_scan' : [False]})
        except Exception as ex:
            logger.exception(ex)
                
    def _on_toggle_filament(self):
        sender = self.sender()
        try:
            if 'off' in sender.text():
                logger.info("Turning on filament")
                self.actionObservers({'toggle_filament' : [False]})
            elif 'on' in sender.text():
                logger.info("Turning off filament")
                self.actionObservers({'toggle_filament' : [True]})
        except Exception as ex:
            logger.exception(ex)
    
    def _on_new_running_signal(self, monitoring_info):
        if monitoring_info:
            self.label_27.setText('True')
            self.pushButton_2.setText("Stop scan")
            self.pushButton_3.setEnabled(True)
            self.setEnableControls(False)
        else:
            if 'Stop' in self.pushButton_2.text():
                if self.checkbox.isChecked():
                    nScans = self.spinBox_8.value()
                    self.actionObservers({'resume_scan' : [nScans]})
            else:
                self.label_27.setText('False')
                self.pushButton_2.setText("Start scan")
                self.pushButton_3.setEnabled(False)
                self.setEnableControls(True)
                self.barRingBuffer = [np.nan] * 200
    
    def _on_new_scan_status_signal(self, monitoring_info):
        
        if 'Running' in monitoring_info:
            running = monitoring_info['Running']
            
            if running:
                self.pushButton_2.setText("Stop scan")
                self.pushButton_3.setEnabled(True)
            else:
                self.pushButton_2.setText("Start scan")
                self.pushButton_3.setEnabled(False)
                try:
                    self.actionObservers({'toggle_scan' : [False]})
                except Exception as ex:
                    logger.exectpion(ex)
            

        self.label_20.setText(monitoring_info['StartMass'])
        self.label_21.setText(monitoring_info['EndMass'])
        self.label_22.setText(monitoring_info['FilterMode'])
        self.label_23.setText(monitoring_info['Accuracy'])
        self.label_24.setText(monitoring_info['EGainIndex'])
        self.label_25.setText(monitoring_info['SourceIndex'])
        self.label_26.setText(monitoring_info['DetectorIndex'])
        self.label_27.setText(str(monitoring_info['Running']))
    
    def _on_new_data_signal(self, monitoring_info):
        if monitoring_info != []:
            for i, value in enumerate(monitoring_info):
                if value != 0:
                    self.barRingBuffer[i] = value
            
            x = range(1, len(self.barRingBuffer)+1)
            self.canvas.ax.clear()
            self.canvas.ax.set_ylabel("Pressure")
            self.canvas.ax.set_yscale("log")
            self.canvas.ax.grid(True, which='major')
            self.canvas.ax.grid(True, which='minor', linestyle='--')
            self.canvas.ax.set_ylim((1E-9, 1E-4))
            self.canvas.ax.set_xlim((1, self.spinBox_2.value()))
            self.canvas.ax.bar(x, self.barRingBuffer, align='center')
            self.canvas.draw()

    def _on_new_info_signal(self, monitoring_info):
        self.label_7.setText(monitoring_info['Name'])
        self.label_8.setText(monitoring_info['SerialNumber'])
        self.label_9.setText(monitoring_info['UserApplication'])
        self.label_10.setText(monitoring_info['UserAddress'])
        self.label_11.setText(monitoring_info['State'])
        self.label_12.setText(monitoring_info['ProductID'])
        self.label_13.setText(monitoring_info['DetectorType'])
        self.label_14.setText(monitoring_info['TotalPressureGauge'])
        self.label_15.setText(monitoring_info['FilamentType'])
        self.label_16.setText(monitoring_info['SensorType'])
        self.label_17.setText(monitoring_info['MaxMass'])
    
    def _on_new_filament_signal(self, monitoring_info):
        self.label_2.setText(monitoring_info['SummaryState'])
        
        if monitoring_info['SummaryState'] == 'OFF':
            self.pushButton.setText('Turn on filament')
        else:
            self.pushButton.setText('Turn off filament')

        self.label_3.setText(monitoring_info['ActiveFilament'])
        self.label_4.setText(monitoring_info['MaxOnTime'])
        self.label_5.setText(monitoring_info['OnTimeRemaining'])
    

class RGAUIModel:
    def __init__(self, mode):
        self.mode = mode
        
        if self.mode == 'proxy':
            try:
                self.rga = EvisionProxy()
            except Exception as exc:
                raise exc
            
        elif self.mode == 'simulator':
            self.rga = EvisionSimulator()
        else:
            raise ValueError(f'Unknown type of rga implementation passed into the model')
            
            if self.rga is not None:
                logger.debug(f'RGA Controller initialized as {self.rga.__class__.__name__}')

    
    def stop_scan(self):
        self.rga.stop_scan()
        self.rga.measurement_remove_all()
    
    def resume_scan(self):
        pass
       
    def restart_scan(self):
        self.rga.restart_scan()
        
    def resume_scan(self, num):
        self.rga.resume_scan(num)
    
    def start_scan(self, num):
        self.rga.start_scan(num)
    
    def filament_control(self, state):
        self.rga.filament_control(state)

    def add_bar_chart(self, name, startMass, endMass, filterMode, accuracy, eGainIndex, sourceIndex, detectorIndex):
        self.rga.add_bar_chart(name, startMass, endMass, filterMode, accuracy, eGainIndex, sourceIndex, detectorIndex)

    def add_peak_jump(self, name, filterMode='PeakCenter', accuracy=5, eGainIndex=0, sourceIndex=0, detectorIndex=0):
        self.rga.add_peak_jump(name, filterMode, accuracy, eGainIndex, sourceIndex, detectorIndex)

    def add_single_peak(self, name, mass, accuracy, eGainIndex, sourceIndex, detectorIndex):
        self.rga.add_single_peak(name, mass, accuracy, eGainIndex, sourceIndex, detectorIndex)
    
    def add_scan(self, name):
        self.rga.add_scan(name)

class RGAUIController(Observer):
    def __init__(self, model: RGAUIModel, view:RGAUIView):
        self.model = model
        self.view  = view
        self.view.addObserver(self)
        
    def update(self, changed_object):
        text = changed_object.text()
        
        if text == "Reconnect":
            if changed_object.isChecked():
                logger.debug("Reconnecting the RGA model.")

            if self.model.reconnect():
                self.view.set_connection_state(True)
                
                if not self.model.has_commands():
                    self.model.load_commands()  
            else:
                self.view.reconnect_action.setChecked(False)
        else:
            self.view.reconnect_action.setChecked(False)
            self.model.disconnect()
            self.view.set_connection_state(False)
            
        return
    
    def do(self, actions):
        for action, value in actions.items():
            if action == "toggle_filament":
                self.model.filament_control(value[0])
            if action == 'toggle_scan':   
                if value[0]:
                    self.model.start_scan(value[1])
                else:
                    self.model.stop_scan()
            if action == 'add_bar_chart':
                self.model.stop_scan()
                self.model.add_bar_chart(value[0], value[1], value[2],value[3],value[4],value[5], value[6], value[7])
                self.model.add_scan(value[0])
            if action == 'restart_scan':
                self.model.restart_scan()
            if action == 'resume_scan':
                self.model.resume_scan(value[0])
        
def parse_arguments():
    """
    Prepare the arguments that are specific for this application.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type",
        dest="type",
        action="store",
        choices={"proxy", "simulator", "crio"},
        help="Specify AEU cRIO implementation you want to connect to.",
        default="proxy",
    )    
    args = parser.parse_args()
    return args

def main():
    args = list(sys.argv)

    app = QApplication(args)
    
    args = parse_arguments()

    view = RGAUIView()
    model = RGAUIModel(args.type)
    controller = RGAUIController(model, view)
    
    view.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()