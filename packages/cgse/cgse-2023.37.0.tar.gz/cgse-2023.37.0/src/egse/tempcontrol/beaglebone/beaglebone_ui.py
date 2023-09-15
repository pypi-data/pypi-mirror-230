import argparse
import logging
import pickle
from pathlib import Path
from re import S
import sys
import zmq
from zmq import ZMQError

from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QTimer, QEvent, QSize, QLockFile
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QFrame, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, \
    QAction, QWidget, QLineEdit,  QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QCheckBox, QMessageBox

from egse.gui.led import LED
from egse.gui.buttons import ToggleButton

from egse.tempcontrol.beaglebone.beaglebone import BeagleboneProxy, BeagleboneSimulator
from egse.tempcontrol.beaglebone.beaglebone import CTRL_SETTINGS as HEATER_CTRL_SETTINGS
from egse.tempcontrol.spid.spid import PidProxy, PidSimulator
from egse.tempcontrol.spid.spid import CTRL_SETTINGS as PID_CTRL_SETTINGS

from egse.setup import get_setup
from egse.gui.buttons import ToggleButton
from egse.observer import Observer, Observable
from egse.settings import Settings
from egse.setup import Setup
from egse.zmq_ser import connect_address
from egse.resource import get_resource

logger = logging.getLogger("BBB heater UI")

class HeaterMonitoringWorker(QObject):
    """Worker for monitoring the state and duty cycle of the Beaglebone Black Heaters

    The worker will send a signal when a heater state changes or 
        when the duty cycle changes

    """

    heater_enabled_status_signal        = pyqtSignal(list)
    heater_duty_cycle_status_signal     = pyqtSignal(list)
    heater_connected_signal             = pyqtSignal(list)
    
    def __init__(self):
        """ Initialisation of a monitoring worker.
        
        This worker keeps an eye on the monitoring port of the Beaglebone Heater. When a change in
            Relevant information occurs, a signalw ill be emitted. These signals will be used to update the GUI
        """
        
        
        super(HeaterMonitoringWorker, self).__init__()
        
        self.active = False
        self.just_reconnected = True
        
        self.monitoring_socket = None
        self.is_socket_connected = True
        self.monitoring_timeout = 0.5
        
        self.connect_socket()
        
        # Keep track of the heater status, so we only have to send a signal when the state has changed
        
        self.previous_heater_status_signal = {}
        self.previous_heater_duty_cycle    = {}
        self.previous_heater_connected     = {}
        
    def connect_socket(self):
        """ Create a socket and connect to the monitoring port.
        """
        

        try:
            transport   = HEATER_CTRL_SETTINGS.PROTOCOL
            hostname    = HEATER_CTRL_SETTINGS.HOSTNAME
            
            monitoring_port = HEATER_CTRL_SETTINGS.MONITORING_PORT
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
                    heater_enabled      = monitoring_info['Enabled']
                    heater_duty_cycle   = monitoring_info['duty_cycle']
                    heater_connected    = monitoring_info['Connected']
                    
                    print(heater_enabled)
                    
                    self.heater_connected_signal.emit(heater_connected)
                    
                    self.heater_enabled_status_signal.emit(heater_enabled)
                    
                    if heater_duty_cycle != self.previous_heater_duty_cycle:
                        self.heater_duty_cycle_status_signal.emit(heater_duty_cycle)
                    
                    self.previous_heater_duty_cycle = heater_duty_cycle
                    
                    
            except ZMQError as exc:
                raise exc
 
class PidMonitoringWorker(QObject):
    """Worker for monitoring the state of the individual PID channels

   The worker will send a signal when the state of a PID channel has changed

    """
    
    pid_control_server_status_signal = pyqtSignal(bool)
    pid_enabled_status_signal        = pyqtSignal(dict)
    
    def __init__(self):
        super(PidMonitoringWorker, self).__init__()
        
        self.active = False
        self.just_reconnected = True
        
        self.enabled = False
        self.pid_enabled = []
        
        self.monitoring_socket = None
        self.is_socket_connected = True
        self.monitoring_timeout = 0.5
        
        self.connect_socket()
        
        self.previous_control_server_status_signal = ()
        self.previous_pid_enabled_status_signal = {}


    def connect_socket(self):
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
        self.monitoring_socket.close()
        self.is_socket_connected = False
        
        self.active = False
        
    def start_process(self):
        self.run()
        
    @pyqtSlot()
    def run(self):
        self.active = True
        while self.is_socket_connected and self.active:
            
            try:
                socket_list, _, exc_list = zmq.select([self.monitoring_socket], [], [], timeout=self.monitoring_timeout)
                if self.monitoring_socket in socket_list:
                    self.enabled = True
                    pickle_string = self.monitoring_socket.recv()

                    monitoring_info = pickle.loads(pickle_string)
                    self.pid_enabled      = monitoring_info['Enabled']
                    
                    if self.previous_pid_enabled_status_signal != self.pid_enabled:
                        self.pid_enabled_status_signal.emit(self.pid_enabled)
                    
                if self.previous_control_server_status_signal != self.enabled:
                    self.pid_control_server_status_signal.emit(self.enabled)
                    
                self.previous_control_server_status_signal = self.enabled
                self.previous_pid_enabled_status_signal = self.pid_enabled
            except ZMQError as exc:
                raise exc
            
            
class ChannelGroupbox(QGroupBox):
    def __init__(self, parent, name):
        super().__init__(parent=parent)
        self.setObjectName(name)
        self.resize(250, 80)
        self.setMinimumSize(QSize(250, 80))
        self.setMaximumSize(QSize(300, 100))
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QLabel(self)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton = QPushButton(self)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Stop PID")
        self.pushButton.setMaximumSize(QSize(150, 25))
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.checkBox = ToggleButton(
            name="Turn On\Off Heater Channel",
            status_tip=f"Heater {parent.objectName()} Channel {self.objectName()} On\Off",
            selected=get_resource(":/icons/switch-on.svg"),
            not_selected=get_resource(":/icons/switch-off.svg"),
        )
        self.horizontalLayout_2.addWidget(self.checkBox)
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.label_2 = QLabel(self)
        self.label_2.setObjectName("label_2")
        self.label_2.setText("P")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.spinBox = QSpinBox(self)
        self.spinBox.setMaximumSize(QSize(150, 16777215))
        self.spinBox.setObjectName("spinBox")
        self.spinBox.setSuffix(" %")
        self.horizontalLayout_2.addWidget(self.spinBox)
        self.pushButton_2 = QPushButton(self)
        self.pushButton_2.setMaximumSize(QSize(150, 25))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setText("Set")
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
    
class HeaterGroupbox(QGroupBox):
    def __init__(self, parent, name):
        super().__init__(parent=parent)
        self.setObjectName(name)
        self.resize(280, 407)
        self.setMaximumSize(QSize(280, 410))
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QLabel(self)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.reconnectButton = QPushButton("Reconnect")
        self.horizontalLayout.addWidget(self.reconnectButton)
        self.widget = LED(self)
        self.widget.setMinimumSize(QSize(25, 25))
        self.widget.setMaximumSize(QSize(25, 25))
        self.widget.setObjectName("widget")
        self.horizontalLayout.addWidget(self.widget)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.groupBox = ChannelGroupbox(self, "Channel A")
        self.groupBox.setTitle("")
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = ChannelGroupbox(self, "Channel B")
        self.groupBox_2.setTitle("")
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = ChannelGroupbox(self, "Channel C")
        self.groupBox_3.setTitle("")
        self.verticalLayout.addWidget(self.groupBox_3)
        self.groupBox_4 = ChannelGroupbox(self, "Channel D")
        self.groupBox_4.setTitle("")
        self.verticalLayout.addWidget(self.groupBox_4)   
        
class HeaterMainWindow(QMainWindow, Observable):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("BeagleBone Black Heater Controller")
        
        self.setMaximumSize(QSize(1700, 420))
        
        self.horizontalLayout = QHBoxLayout()
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.horizontalLayout)
        
        self.setCentralWidget(self.centralWidget)
        
        self.initUI()
        
        self.heater_monitoring_thread = QThread(self)
        self.heater_monitoring_worker = HeaterMonitoringWorker()
        self.heater_monitoring_worker.moveToThread(self.heater_monitoring_thread)
        
        self.pid_monitoring_thread = QThread(self)
        self.pid_monitoring_worker = PidMonitoringWorker()
        self.pid_monitoring_worker.moveToThread(self.pid_monitoring_thread)

        self.heater_monitoring_worker.heater_enabled_status_signal.connect(self.on_heater_enabled_status_signal)
        self.heater_monitoring_worker.heater_duty_cycle_status_signal.connect(self.on_heater_duty_cycle_status_signal)
        self.heater_monitoring_worker.heater_connected_signal.connect(self.on_heater_connected_signal)
        
        self.pid_monitoring_worker.pid_enabled_status_signal.connect(self.on_pid_enabled_status_signal)

        self.heater_monitoring_thread.started.connect(self.heater_monitoring_worker.start_process)
        self.heater_monitoring_thread.start()
        
        self.pid_monitoring_thread.started.connect(self.pid_monitoring_worker.start_process)
        self.pid_monitoring_thread.start()
        
    def initUI(self):
        setup = get_setup()
        
        self.htr_availability =  [True for available in setup.gse.beaglebone_heater.availability if available]
        self.heaters = [None] * len(self.htr_availability)
        self.channels = [None] * len(self.htr_availability)
        pid_configuration                = setup.gse.spid.configuration.heaters
        self.pids = [channel for heater in pid_configuration.values() for channel in heater]
        
        for idx, heater in enumerate(self.heaters):
            heater_name = "Heater {}".format(idx + 1)
            avail = self.htr_availability[idx]
            self.heaters[idx] = HeaterGroupbox(self, heater_name)
            self.heaters[idx].widget.set_color(1 if avail else 0)
            self.heaters[idx].label.setText(heater_name)
            self.heaters[idx].reconnectButton.clicked.connect(self.on_heater_reconnect)
            self.horizontalLayout.addWidget(self.heaters[idx])
            
            self.channels[idx] = [None] * 4
            
            for ch_idx, channel in enumerate(self.channels[idx]):
                channel_name = "Channel A" if ch_idx == 0 else \
                                "Channel B" if ch_idx == 1 else \
                                "Channel C" if ch_idx == 2 else \
                                "Channel D"    
                self.channels[idx][ch_idx]  = self.heaters[idx].findChild(QGroupBox, channel_name)
                self.channels[idx][ch_idx].pushButton.hide()
                # channel.setObjectName(heater_name + channel_name)
                self.channels[idx][ch_idx].label.setText(channel_name)
                self.channels[idx][ch_idx].pushButton_2.clicked.connect(self.set_duty_cycle)
                self.channels[idx][ch_idx].checkBox.clicked.connect(self.set_enable)
                self.channels[idx][ch_idx].pushButton.clicked.connect(self.turn_off_pid)
    
    def on_heater_reconnect(self, _):
        htr_idx = int(self.sender().parent().objectName().split(" ")[1]) - 1
        self.actionObservers({'connect_beaglebone': [htr_idx]})
    
    def on_heater_enabled_status_signal(self, monitoring_info: dict):
        for htr_idx, heater in enumerate(self.heaters):
            for ch_idx, channel in enumerate(self.channels[htr_idx]):
                channel.checkBox.set_selected(monitoring_info[htr_idx][ch_idx])
    
    def on_heater_duty_cycle_status_signal(self, monitoring_info: dict):
        for htr_idx, heater in enumerate(self.heaters):
            for ch_idx, channel in enumerate(self.channels[htr_idx]):
                channel.spinBox.setValue(int(monitoring_info[htr_idx][ch_idx] / 100))
    
    def on_heater_connected_signal(self, monitoring_info: list):
        for htr_idx, heater in enumerate(self.heaters):
            if monitoring_info[htr_idx]:
                heater.widget.set_color(1)
                heater.reconnectButton.setEnabled(False)
            else:
                heater.widget.set_color(2)
                heater.reconnectButton.setEnabled(True)
    
    def on_pid_enabled_status_signal(self, monitoring_info: dict):
        for heater_channel, enabled in monitoring_info.items():
            command = heater_channel.split("_")
            htr = int(command[0])
            ch = int(command[1])
            if enabled:

                self.channels[htr][ch].pushButton.show()
                self.channels[htr][ch].spinBox.setReadOnly(True)
                self.channels[htr][ch].setStyleSheet("""QGroupBox {border: 1px solid red;}""")
            
            else:
                self.channels[htr][ch].pushButton.hide()
                self.channels[htr][ch].spinBox.setReadOnly(False)
                self.channels[htr][ch].setStyleSheet('fusion') 
    
    def set_duty_cycle(self):
        htr = self.sender().parent().parent().objectName().split(" ")[1]
        channel = self.sender().parent().objectName().split(" ")[1]
        value = self.sender().parent().spinBox.value()
        duty_cycle = int(value * 100)

        try:
            self.actionObservers({"set_duty_cycle": [int(htr)-1, int(ord(channel)-65), duty_cycle]})
        except Exception as e:
            warning_popup("set_duty_cycle : Heater {} Channel {} duty_cycle {}".format(
                htr, channel, duty_cycle
            ), e)
    
    
    def turn_off_pid(self):
        htr = self.sender().parent().parent().objectName().split(" ")[1]
        channel = self.sender().parent().objectName().split(" ")[1]
        
        for idx, pid in enumerate(self.pids):
            if (pid[3] is htr) and (pid[4] is channel):
                try:
                    self.actionObservers({"set_pid_disable": [int(idx)]}) if (pid[3] is htr and pid[4] is channel) else None
                except Exception as e:
                    warning_popup("set_pid_disable : {}".format(idx), e)
    
    def set_enable(self):
        htr = self.sender().parent().parent().objectName().split(" ")[1]
        channel = self.sender().parent().objectName().split(" ")[1]
        value = self.sender().is_selected()
        self.sender().set_selected(on=value)
        # logger.info("{} {} {}".format(int(htr), int(channel), bool(value)))
        try:
            self.actionObservers({"set_enable" : [int(htr)-1, int(ord(channel)-65), bool(value)]})
        except Exception as e:
            warning_popup('set_enable : Heater {} Channel {} to {}'.format(
                htr, channel, "Enabled" if value else "Disabled"
            ), e)


def warning_popup(command, error):
    msgBox = QMessageBox()
    msgBox.setWindowTitle("OGSE error occured")
    msgBox.setIcon(QMessageBox.Warning)
    msgBox.setText(f"An error occured while executing: {command}")
    msgBox.setInformativeText(f"{error}")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec_()
        
class HeaterUIModel:
    def __init__(self, mode):
            self.mode = mode

            if self.mode == 'proxy':
                try:
                    self.heater = BeagleboneProxy()
                except Exception as exc:
                    raise exc

            elif self.mode == 'simulator':
                self.heater = BeagleboneSimulator()
            else:
                raise ValueError(f'Unknown type of Heater implementation passed into the model')
            
            if self.heater is not None:
                logger.debug(f'Heater Controller initialized as {self.heater.__class__.__name__}')


    def set_enable(self, htr_idx, ch_idx, enable):
        with BeagleboneProxy() as heater:
            heater.set_enable(htr_idx, ch_idx, enable)
        
    def set_duty_cycle(self, htr_idx, ch_idx, duty_cycle):
        with BeagleboneProxy() as heater:
            heater.set_duty_cycle(htr_idx, ch_idx, duty_cycle)

    def set_pid_enable(self, ch):
        try:
            with PidProxy() as pid:
                pid.enable(ch)
        except:
            logger.info("PID Control Server could not be found")
        
    def set_pid_disable(self, ch):
        logger.info(f"PID channel {ch} has been disabled")
        try:
            with PidProxy() as pid:
                pid.disable(ch)
        except:
            logger.info("PID Control Server could not be found")
            
    def connect_beaglebone(self, htr_idx):
        with BeagleboneProxy() as heater:
            heater.connect_beaglebone(htr_idx)
    
    def has_commands(self):
        if self.mode == "proxy":
            with BeagleboneProxy() as heater:
                return heater.has_commands()

        return True

    def load_commands(self):
        if self.mode == "proxy":
            with BeagleboneProxy() as heater:
                with PidProxy() as pid:
                    pid.load_commands()
                    heater.load_commands()

    def is_simulator(self):
        with BeagleboneProxy() as heater:
            return heater.is_simulator()

    def is_connected(self):
        if self.mode == "proxy":
            with BeagleboneProxy() as heater:
                return heater.is_cs_connected()

        else:

            return self.heater.is_connected()

    def reconnect(self):
        if self.mode == "proxy":
            with BeagleboneProxy() as heater:

                heater.reconnect_cs()

                return heater.is_cs_connected()

        else:

            self.heater.reconnect()

            return self.heater.is_connected()

        return False

    def disconnect(self):
        if self.mode == "proxy":

            self.mode.disconnect_cs()

class HeaterUIController(Observer):
    def __init__(self, model: HeaterUIModel, view: HeaterMainWindow):
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
            if action == "set_duty_cycle":
                htr_idx     = value[0]
                ch_idx      = value[1]
                duty_cycle  = value[2]
                logger.debug(f"do: set_duty_cycle({htr_idx}, {ch_idx}, {duty_cycle})")
                self.model.set_duty_cycle(htr_idx, ch_idx, duty_cycle)

                
            if action == "set_enable":
                htr_idx     = value[0]
                ch_idx      = value[1]
                state  = value[2]
                logger.debug(f"do: set_enable({htr_idx}, {ch_idx}, {state})")
                self.model.set_enable(htr_idx, ch_idx, state)
                
            if action == "set_pid_enable":
                ch          = value[0]
                logger.debug(f"do: set_pid_enable({ch}")
                self.model.set_pid_enable(ch)
                
            if action == "set_pid_disable":
                ch          = value[0]
                logger.info(f"do: set_pid_disable({ch})")
                self.model.set_pid_disable(ch)
            if action == 'connect_beaglebone':
                htr_idx = value[0]
                self.model.connect_beaglebone(htr_idx)
    
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
        help="Specify Beaglebone Black Heater implementation you want to connect to.",
        default="proxy",
    )    
    args = parser.parse_args()
    return args


def main():
    lock_file = QLockFile(str(Path("~/tempcontrol_beaglebone_ui.app.lock").expanduser()))

    args = list(sys.argv)
    app = QApplication(args)
    # app.setWindowIcon(QIcon(str(get_resource(":/icons/temperature-control.svg"))))

    # if lock_file.tryLock(100):
    args = parse_arguments()
    if args.type == 'proxy':
        try:
            proxy = BeagleboneProxy()
        except Exception:
            logger.info("Beaglebone Black Heater Control Server is not running")
    view = HeaterMainWindow()
    model = HeaterUIModel(args.type)
    controller = HeaterUIController(model, view)
    view.show()
    return app.exec_()
        # else:
        #     error_message = QMessageBox()
        #     error_message.setIcon(QMessageBox.Warning)
        #     error_message.setWindowTitle("Error")
        #     error_message.setText("The Beaglebone tempcontrol GUI application is already running!")
        #     error_message.setStandardButtons(QMessageBox.Ok)

        #     return error_message.exec()

    
if __name__ == "__main__":
    main()
