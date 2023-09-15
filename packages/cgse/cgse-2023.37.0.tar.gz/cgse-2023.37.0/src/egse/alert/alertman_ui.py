
import sys
import argparse
import logging
import zmq
import pickle
import multiprocessing
import os

from datetime import datetime

from PyQt5.QtCore import QThread, QObject, Qt, pyqtSignal, pyqtSlot, QRect, QSize
from PyQt5.QtGui import QCloseEvent, QIcon, QResizeEvent
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, \
    QWidget, QPushButton, QScrollArea, QComboBox, QMessageBox, QSpacerItem, QSizePolicy

from egse.setup  import load_setup
from egse.system import EPOCH_1958_1970
from egse.gui.led import Led
from egse.zmq_ser import connect_address
from egse.observer import Observer, Observable

from egse.alert import AlertManagerProxy, load_alert_configuration
from egse.alert import CTRL_SETTINGS as ALERT_CTRL_SETTINGS

multiprocessing.current_process().name = "alert_manager_ui"

logger = logging.getLogger(__name__)

class AlertMonitoringWorker(QObject):
    alert_values_status_signal      = pyqtSignal(dict)
    alert_sensor_status_signal      = pyqtSignal(dict)
    alert_fdir_status_signal        = pyqtSignal(dict)
    alert_phase_change_signal       = pyqtSignal(str)
    alert_status_change_signal      = pyqtSignal(dict)
    alert_timestamp_change_signal   = pyqtSignal(dict)
    # alert_exception_change_signal   = pyqtSignal(dict)
    
    def __init__(self):
        super(AlertMonitoringWorker, self).__init__()
        self.activate = False
        self.just_reconnected = True
        
        self.monitoring_socket = None
        self.is_socket_connected = True
        self.monitoring_timeout = 0.5
        
        self.connect_socket()
        
        self.previous_alert_update_status_signal = {}
        self.previous_sensors   = {}
        self.previous_fdir      = {}
        self.previous_values    = {}
        self.pervious_timestamp = {}
        self.previous_status = False
        self.previous_phase = ""
        # self.previous_exception = {}
    
    def reset_monitor(self):
        self.previous_alert_update_status_signal = {}
        self.previous_sensors   = {}
        self.previous_fdir      = {}
        self.previous_values    = {}
        self.pervious_timestamp = {}
        self.previous_status = False
        
        
    def connect_socket(self):
        try:
            transport           = ALERT_CTRL_SETTINGS.PROTOCOL
            hostname            = ALERT_CTRL_SETTINGS.HOSTNAME
            
            monitoring_port     = ALERT_CTRL_SETTINGS.MONITORING_PORT
            monitoring_address  = connect_address(transport, hostname, monitoring_port)
        
            self.monitoring_socket = zmq.Context().socket(zmq.SUB)
            self.monitoring_socket.connect(monitoring_address)
            self.monitoring_socket.setsockopt_string(zmq.SUBSCRIBE, "")
            
            self.monitoring_timeout = 0.5
            
            self.is_socket_connected = True
        except:
            self.is_socket_connected = False
            
    def stop(self):
        self.monitoring_socket.close()
        self.is_socket_connected = False
        
        self.active = False
        
    def start_process(self):
        self.run()
        
    @pyqtSlot()
    def run(self):
        self.active = True
        timeout = 0
        while self.is_socket_connected and self.active:
            try:
                socket_list, _, exc_list = zmq.select([self.monitoring_socket], [], [], timeout=self.monitoring_timeout)
                
                if self.monitoring_socket in socket_list:
                    try:
                        pickle_string = self.monitoring_socket.recv()
                    except Exception:
                        raise Exception
                    
                    monitoring_info = pickle.loads(pickle_string)
                    
                    values      = {}
                    sensors     = {}
                    running     = {}
                    timestamp   = {}
                    # exception   = {}

                    phase   = monitoring_info['phase']

                    if phase != self.previous_phase:
                        self.alert_phase_change_signal.emit(phase)
                        continue
                            
                    self.previous_phase = phase
                    
                    if monitoring_info['alert_status'] != None:
                        for key, value in monitoring_info['alert_status'].items():
                            values[key] = value['value']
                            sensors[key] = {'triggered' : value['triggered'],
                                            'active'    : value['active']}
                            running[key] = value['active']
                            timestamp[key] = datetime.fromtimestamp(float(value['lastTimestamp']) - EPOCH_1958_1970)
                            # exception[key] = value['lastException']

                        if values != self.previous_values:
                            self.alert_values_status_signal.emit(values)
                        
                        self.previous_values = values
                        
                        if running != self.previous_status:
                            self.alert_status_change_signal.emit(running)

                        self.previous_status = running

                        if sensors != self.previous_sensors:
                            self.alert_sensor_status_signal.emit(sensors)
                        
                        self.previous_sensors = sensors
                        
                        if timestamp != self.pervious_timestamp:
                            self.alert_timestamp_change_signal.emit(timestamp)
                        
                        self.pervious_timestamp = timestamp
                        
                        # if exception != self.previous_exception:
                        #     self.alert_exception_change_signal.emit(exception)
                            
                        # self.previous_exception = exception
                        
            except zmq.ZMQError as exc:
                raise exc


class AlertWidget(QGroupBox):
    def __init__(self, configuration):
        super().__init__()
        self.name = configuration.name
        
        self.setMaximumSize(400, 120)
        self.setMinimumSize(350, 100)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget = Led(self)
        self.widget.setMinimumSize(25, 25)
        self.widget.setMaximumSize(25, 25)
        self.widget.setObjectName("widget")
        self.horizontalLayout.addWidget(self.widget)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QLabel(self)
        self.label.setText(f"<b>{configuration.name}</b>")
        self.label.setMinimumSize(200, 0)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QLabel(self)
        self.label_2.setText("[Current value]")
        self.label_2.setMinimumSize(100, 0)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.label_3 = QLabel(self)
        self.label_3.setText(f"{configuration.unit}")
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.label_4 = QLabel(self)  

        if configuration.alert_type == 0:
            if configuration.limits['min'] and configuration.limits['max']:
                self.label_4.setText(f"Min: {configuration.limits['min']}, Max: {configuration.limits['max']}")
            else:   
                if configuration.limits['min']:
                    self.label_4.setText(f"Min: {configuration.limits['min']}")
                if configuration.limits['max']:
                    self.label_4.setText(f"Max: {configuration.limits['max']}")
                
        if configuration.alert_type == 2:
            self.label_4.setText(f"Rate of change: {configuration.limits['limit']}")
            
        self.label_4.setObjectName("label_4")
        self.verticalLayout_2.addWidget(self.label_4)
         
        self.label_5 = QLabel(self)
        self.label_5.setText("00:00:00 00-00-00")
        self.verticalLayout_2.addWidget(self.label_5)

        self.horizontalLayout.addLayout(self.verticalLayout_2)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        spacerItem1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.pushButton = QPushButton(self)
        self.pushButton.setText("Start")
        self.pushButton.setMinimumSize(100, 0)
        icon = QIcon.fromTheme("media-playback-start")
        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_3.addWidget(self.pushButton)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout)

class AlertWindow(QGroupBox):
    def __init__(self, configuration):
        super().__init__()
        self.configuration = configuration
        self._phases = load_setup().gse.alert_manager.configuration
        self.alerts = {}
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_2 = QPushButton(self)
        self.pushButton_2.setMaximumSize(QSize(90, 16777215))
        self.pushButton_2.setMinimumSize(QSize(90, 0))
        icon = QIcon.fromTheme("media-playback-start")
        self.pushButton_2.setIcon(icon)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setText("Start")
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.pushButton = QPushButton(self)
        self.pushButton.setMaximumSize(QSize(90, 16777215))
        self.pushButton.setMinimumSize(QSize(90, 0))
        icon = QIcon.fromTheme("media-playback-stop")
        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Stop")
        self.horizontalLayout_2.addWidget(self.pushButton)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.pushButton_3 = QPushButton(self)
        self.pushButton_3.setText("Clear FDIR")
        self.pushButton_3.setMaximumSize(QSize(90, 16777215))
        self.pushButton_3.setMinimumSize(QSize(90, 0))
        icon = QIcon.fromTheme('edit-clear-all-symbolic')
        self.pushButton_3.setIcon(icon)
        self.horizontalLayout_2.addWidget(self.pushButton_3)
        self.comboBox = QComboBox(self)
        self.comboBox.setMinimumSize(QSize(90, 0))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem('none')
        self.comboBox.addItems([phase for phase in self._phases.keys()])
        # self.comboBox.addItems(['none', 'warm', 'transition', 'cold']) 
        self.horizontalLayout_2.addWidget(self.comboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setMinimumWidth(420)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 350, 700))
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_3)
        self.setLayout(self.verticalLayout)   

        self.initialize(self.configuration)
        
    def initialize(self, config=None):
        if config != None:
            self.configuration = config
            self.alerts = {}
            for idx, (key, config) in enumerate(self.configuration.items()):
                self.alerts[key] = AlertWidget(config)
            self.drawScrollArea()
            self.resizeScrollArea()
        else:
            self.drawScrollArea()
    
    def drawScrollArea(self):
        # if self.configuration != None:
        self.verticalLayout.removeWidget(self.scrollArea)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setMinimumWidth(420)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 350, 700))
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_3)
        self.verticalLayout.insertWidget(1, self.scrollArea)
    
    def resizeScrollArea(self):   
        width = self.parent().frameGeometry().width()
        
        widget_width    = 350
        
        num_cols = int(width / widget_width)

        row     = 0
        column  = 0    
        
        if len(self.alerts) == 0:
            return
        
        for idx, value in enumerate(self.alerts.values()):
            if column >= num_cols and (column % num_cols) == 0:
                row += 1
            self.gridLayout.addWidget(value, row, column % num_cols)
            column += 1

            
        spacerItem_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem_2)   
           
    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.resizeScrollArea()



class AlertUIView(QMainWindow, Observable):
    def __init__(self):
        super().__init__()
        self.setGeometry(600, 300, 100, 700)
        self.setWindowTitle("Alert Manager GUI")
        self.configuration = None
        self.phases = load_setup().gse.alert_manager.configuration.keys()
        self.alert_monitoring_thread = QThread(self)
        self.alert_monitoring_worker = AlertMonitoringWorker()
        self.alert_monitoring_worker.moveToThread(self.alert_monitoring_thread)
        
        self.alert_monitoring_worker.alert_phase_change_signal.connect(self.on_phase_change_signal)
        self.alert_monitoring_worker.alert_values_status_signal.connect(self.on_alert_value_status_signal)
        self.alert_monitoring_worker.alert_sensor_status_signal.connect(self.on_alert_sensor_status_signal)
        self.alert_monitoring_worker.alert_status_change_signal.connect(self.on_alert_status_change_signal)
        self.alert_monitoring_worker.alert_timestamp_change_signal.connect(self.on_alert_timestamp_change_signal)
        # self.alert_monitoring_worker.alert_exception_change_signal.connect(self.on_alert_exception_raised_signal)
        self.alert_monitoring_thread.started.connect(self.alert_monitoring_worker.start_process)
        
        self.alert_monitoring_thread.start()
    
        self.initUI()
        
    def initUI(self):
        self.groupbox = AlertWindow(self.configuration)  

        self.groupbox.pushButton_2.clicked.connect(self.start_all_alerts)
        self.groupbox.pushButton.clicked.connect(self.stop_all_alerts)        
           
        self.groupbox.comboBox.activated[str].connect(self.configuration_dialog)   
        self.setCentralWidget(self.groupbox)
    
    def configuration_dialog(self):
        sender = self.sender()
        phase = sender.currentText()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(f"You are about to configure the alert manager for the {phase} phase")
        msg.setInformativeText(f"Are you sure that you want to configure the alert manager for the {phase} phase?")
        msg.setWindowTitle(f"Configuration confirmation")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Abort)

        retval = msg.exec_()
        if retval == QMessageBox.Ok:
            self.actionObservers({"load_new_configuration" : [phase]})
            self.load_new_phase(phase)
        else:
            self.groupbox.comboBox.setCurrentText(phase)
    
    def load_new_phase(self, phase):
        if phase != 'none':
            self.load_configuration(phase)
            self.alert_monitoring_worker.previous_phase = phase
            self.groupbox.initialize(self.configuration)
            
            for key in self.configuration.keys():
                self.groupbox.alerts[key].pushButton.clicked.connect(self.on_alert_pushbutton_clicked)
            
            self.alert_monitoring_worker.reset_monitor()
        else:
            self.alert_monitoring_worker.previous_phase = phase
            self.groupbox.initialize()
            self.alert_monitoring_worker.reset_monitor()
            
        self.setCentralWidget(self.groupbox)
                
    def start_all_alerts(self):
        self.actionObservers({"start_all_alerts" : []})
    
    def stop_all_alerts(self):
        self.actionObservers({"stop_all_alerts" : []})
    
    def load_configuration(self, phase):
        _, self.configuration = load_alert_configuration(phase)
    
    def on_alert_status_change_signal(self, monitoring_info: bool):
        for idx, (name, value) in enumerate(monitoring_info.items()):
            if value:
                self.groupbox.alerts[name].widget.set_color(1)
                icon = QIcon.fromTheme("media-playback-stop")
                self.groupbox.alerts[name].pushButton.setIcon(icon)
                self.groupbox.alerts[name].pushButton.setText("Stop")
            else:
                self.groupbox.alerts[name].widget.set_color(2)
                icon = QIcon.fromTheme("media-playback-start")
                self.groupbox.alerts[name].pushButton.setIcon(icon)
                self.groupbox.alerts[name].pushButton.setText("Start")
    
    def on_alert_timestamp_change_signal(self, monitoring_info):
        for idx, (name, value) in enumerate(monitoring_info.items()):
            self.groupbox.alerts[name].label_5.setText(f"{value.strftime('%d/%m/%Y, %H:%M:%S')}")
    
    def on_alert_value_status_signal(self, monitoring_info: dict):
        for idx, (name, value) in enumerate(monitoring_info.items()):
            self.groupbox.alerts[name].label_2.setText(f"Value: {float(value):2f}")
    
    def on_alert_sensor_status_signal(self, monitoring_info: dict):
        for idx, (name, state) in enumerate(monitoring_info.items()):
            if state['triggered']:
                if state['active']:
                    self.groupbox.alerts[name].widget.set_color(3)
                else:
                    self.groupbox.alerts[name].widget.set_color(2)

                self.groupbox.alerts[name].setStyleSheet("""QGroupBox {border: 1px solid red;}""")
            else:
                if state['active']:
                    self.groupbox.alerts[name].widget.set_color(1)
                else:
                    self.groupbox.alerts[name].widget.set_color(2)
                
                self.groupbox.alerts[name].setStyleSheet('fusion')
    
    def on_phase_change_signal(self, monitoring_info: dict):
        self.load_new_phase(monitoring_info)
        self.groupbox.comboBox.setCurrentText(monitoring_info)
    
    def on_alert_pushbutton_clicked(self):
        name = self.sender().parent().name
        text = self.sender().text()
        if text != "Start":
            self.actionObservers({'stop_alert': [name]})
        elif text != "Stop":
            self.actionObservers({'start_alert' : [name]})
    
    

class AlertUIModel:
    def __init__(self, mode):
        self.mode = mode
        
        if self.mode == 'proxy':
            try:
                self.alert_manager = AlertManagerProxy()
            except Exception as exc:
                raise exc
        elif self.mode == 'simulator':
            self.alert_manager = AlertManagerProxy()
        else:
            raise ValueError(f'Unknown type of alert manager implementation passed into the model')

        if self.alert_manager is not None:
            logger.debug(f"Alert manager controller initialized as {self.mode}")    
    
    def load_configuration(self, phase: str):
        with AlertManagerProxy() as am:
            am.load_configuration(phase)
    
    def start_alert(self, name):
        with AlertManagerProxy() as am:
            am.start_alert(name)

    def stop_alert(self, name):
        with AlertManagerProxy() as am:
            am.stop_alert(name)
    
    def stop_all_alerts(self):
        with AlertManagerProxy() as am:
            am.stop_alert(None)
 
    def start_all_alerts(self):
        with AlertManagerProxy() as am:
            am.start_alert(None)
    
class AlertUIController(Observer):
    def __init__(self, model: AlertUIModel, view: AlertUIView):
        self.model  = model
        self.view   = view
        self.view.addObserver(self)
        
    def update(self, changed_object):

        text = changed_object.text()

        if text == "Reconnect":

            if changed_object.isChecked():

                logger.debug("Reconnecting the Alert manager model.")

                if self.model.reconnect():

                    self.view.set_connection_state(True)

                    if not self.model.has_commands():

                        self.model.load_commands()

                else:
                    self.view.reconnect_action.setChecked(False)
            else:

                logger.debug("Disconnecting the Alert manager model.")
                self.model.disconnect()
                self.view.set_connection_state(False)

        
    def do(self, actions):
        for action, value in actions.items():
            logger.debug(f'do {action} with {value}')
            if action == 'load_new_configuration':
                self.model.load_configuration(value[0])
            if action == 'start_alert':
                self.model.start_alert(value[0])
            if action == 'stop_alert':
                self.model.stop_alert(value[0])
            if action == 'stop_all_alerts':
                self.model.stop_all_alerts()
            if action == 'start_all_alerts':
                self.model.start_all_alerts()

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
        help="Specify Alert implementation you want to connect to.",
        default="proxy",
    )

    args = parser.parse_args()
    return args

def main():
    args = list(sys.argv)
    app = QApplication(args)
    
    args = parse_arguments()
    
    if args.type == 'proxy':
        try:
            proxy = AlertManagerProxy
        except Exception:
            raise Exception
        
    view        = AlertUIView()
    model       = AlertUIModel(args.type)
    controller  = AlertUIController(model, view)
    
    view.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()