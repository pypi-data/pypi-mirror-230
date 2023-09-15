import argparse
import logging
import pickle
from pathlib import Path

import sys
import zmq
from PyQt5.QtCore import QThread, QObject, pyqtSignal, QSize, QLockFile
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QFrame, QVBoxLayout, QGroupBox, QGridLayout, \
    QPushButton, QSpacerItem, QSizePolicy, QMessageBox

from egse.gui import QHLine
from egse.gui.led import Led, Indic
from egse.observer import Observer, Observable
from egse.resource import get_resource
from egse.vacuum.beaglebone.beaglebone import BeagleboneProxy
from egse.vacuum.beaglebone.beaglebone import BeagleboneSimulator
from egse.vacuum.beaglebone.beaglebone import CTRL_SETTINGS
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

class ValveMonitoringWorker(QObject):
    valve_remote_status_signal = pyqtSignal(dict)
    valve_feedback_status_signal = pyqtSignal(dict)
    
    def __init__(self):
        super(ValveMonitoringWorker, self).__init__()
        
        self.active = False
        self.just_reconnected = True
        
        self.monitoring_socket = None
        self.is_socket_connected = True
        self.monitoring_timeout = 1
        
        self.connect_socket()
        
        self.previous_valve_remote_status_signal   = {}
        self.previous_valve_feedback_status_signal = {}


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
        self.monitoring_socket.close()
        self.is_socket_connected = False
        
        self.active = False
        
    def start_process(self):
        self.run()
        
    def run(self):
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
                    
                    valve_remote      = monitoring_info['Remote']
                    valve_feedback   = monitoring_info['Feedback']

                    if valve_remote != self.previous_valve_remote_status_signal:
                        self.valve_remote_status_signal.emit(valve_remote)

                    self.previous_valve_remote_status_signal = valve_remote
                    
                    if valve_feedback != self.previous_valve_feedback_status_signal:
                        self.valve_feedback_status_signal.emit(valve_feedback)

                    self.previous_valve_feedback_status_signal = valve_feedback
                    
                    
            except Exception as exc:
                logger.info(exc)
                raise exc


class ValveControl(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setObjectName("Valve Controls")
        
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("Valve controls layout")    

        self.ln2Line        = QHLine()
        self.n2Line         = QHLine()
        self.miscLine       = QHLine()

        self.ln2Label       = QLabel("LN2")
        self.ln2ShroudLabel = QLabel("Shroud")
        self.ln2ShroudLed   = Led(self)
        self.ln2ShroudLed.setObjectName("MV011-led")
        self.ln2ShroudLed.setMinimumSize(QSize(25, 0))
        self.ln2TebFeeLabel = QLabel("TEB-FEE / MaRi")
        self.ln2TebFeeLed   = Led(self)
        self.ln2TebFeeLed.setObjectName("MV012-led")
        self.ln2TebFeeLed.setMinimumSize(QSize(25, 0))
        self.ln2TebTouLabel = QLabel("TEB-TOU")
        self.ln2TebTouLed   = Led(self)
        self.ln2TebTouLed.setObjectName("MV013-led")
        self.ln2TebTouLed.setMinimumSize(QSize(25, 0))
        self.ln2TrapLabel   = QLabel("Trap")
        self.ln2TrapLed   = Led(self)
        self.ln2TrapLed.setObjectName("MV014-led")
        self.ln2TrapLed.setMinimumSize(QSize(25, 0))
        
        self.ln2ShroudOpen  = QPushButton("Open")
        self.ln2ShroudOpen.setObjectName("MV011-open")
        self.ln2ShroudClose = QPushButton("Close")
        self.ln2ShroudClose.setObjectName("MV011-close")
        self.ln2TebFeeOpen  = QPushButton("Open")
        self.ln2TebFeeOpen.setObjectName("MV012-open")
        self.ln2TebFeeClose = QPushButton("Close")
        self.ln2TebFeeClose.setObjectName("MV012-close")
        self.ln2TebTouOpen  = QPushButton("Open")
        self.ln2TebTouOpen.setObjectName("MV013-open")
        self.ln2TebTouClose = QPushButton("Close")
        self.ln2TebTouClose.setObjectName("MV013-close")
        self.ln2TrapOpen    = QPushButton("Open")
        self.ln2TrapOpen.setObjectName("MV014-open")
        self.ln2TrapClose   = QPushButton("Close")
        self.ln2TrapClose.setObjectName("MV014-close")
                
        self.n2Label        = QLabel("N2")
        self.n2ShroudLabel  = QLabel("Shroud")
        self.n2ShroudLed    = Led(self)
        self.n2ShroudLed.setObjectName("MV021-led")
        self.n2TebFeeLabel  = QLabel("TEB-FEE / MaRi")
        self.n2TebFeeLed    = Led(self)
        self.n2TebFeeLed.setObjectName("MV022-led")
        self.n2TebTouLabel  = QLabel("TEB-TOU")
        self.n2TebTouLed    = Led(self)
        self.n2TebTouLed.setObjectName("MV023-led")
        self.n2TrapLabel    = QLabel("Trap")
        self.n2TrapLed      = Led(self)
        self.n2TrapLed.setObjectName("MV024-led")
        
        self.n2ShroudOpen  = QPushButton("Open")
        self.n2ShroudOpen.setObjectName("MV021-open")
        self.n2ShroudClose = QPushButton("Close")
        self.n2ShroudClose.setObjectName("MV021-close")
        self.n2TebFeeOpen  = QPushButton("Open")
        self.n2TebFeeOpen.setObjectName("MV022-open")
        self.n2TebFeeClose = QPushButton("Close")
        self.n2TebFeeClose.setObjectName("MV022-close")
        self.n2TebTouOpen  = QPushButton("Open")
        self.n2TebTouOpen.setObjectName("MV023-open")
        self.n2TebTouClose = QPushButton("Close")
        self.n2TebTouClose.setObjectName("MV023-close")
        self.n2TrapOpen    = QPushButton("Open")
        self.n2TrapOpen.setObjectName("MV024-open")
        self.n2TrapClose   = QPushButton("Close")
        self.n2TrapClose.setObjectName("MV024-close")
        
        self.miscLabel      = QLabel("Misc.")
        self.ventLabel      = QLabel("Vent valve")
        self.ventLed        = Led(self)
        self.ventLed.setObjectName("MV002-led")
        self.gateLabel      = QLabel("Gate valve")
        self.gateLed        = Led(self)
        self.gateLed.setObjectName("MV001-led")
        self.guiLabel       = QLabel("GUI lock")

        self.ventClose = QPushButton("Close")
        self.ventClose.setObjectName("MV002-close")
        self.ventClose.setEnabled(False)
        self.ventOpen  = QPushButton("Open")
        self.ventOpen.setObjectName("MV002-open")
        self.ventOpen.setEnabled(False)
        self.gateClose = QPushButton("Close")
        self.gateClose.setObjectName("MV001-close")
        self.gateOpen    = QPushButton("Open")
        self.gateOpen.setObjectName("MV001-open")
        self.guiLock = QPushButton("Lock")
        self.guiLock.setObjectName("GUI-lock/unlock")


        ln2N2Spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        n2MiscSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addWidget(self.ln2Label, 0, 0, 1, 2)
        self.gridLayout.addWidget(self.n2Label, 0, 4, 1, 2)
        self.gridLayout.addWidget(self.miscLabel, 0, 8, 1, 2)
        
        self.gridLayout.addWidget(self.ln2Line, 1, 0, 1, 4)
        self.gridLayout.addWidget(self.n2Line, 1, 4, 1, 4)
        self.gridLayout.addWidget(self.miscLine, 1, 8, 1, 4)
        
        self.gridLayout.addWidget(self.ln2ShroudLed, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.ln2ShroudLabel, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.ln2ShroudClose, 2, 2, 1, 1)
        self.gridLayout.addWidget(self.ln2ShroudOpen, 2, 3, 1, 1)
        
        self.gridLayout.addWidget(self.ln2TebFeeLed, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.ln2TebFeeLabel, 3, 1, 1, 1)
        self.gridLayout.addWidget(self.ln2TebFeeClose, 3, 2, 1, 1)
        self.gridLayout.addWidget(self.ln2TebFeeOpen, 3, 3, 1, 1)
        
        self.gridLayout.addWidget(self.ln2TebTouLed, 4, 0, 1, 1)
        self.gridLayout.addWidget(self.ln2TebTouLabel, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.ln2TebTouClose, 4, 2, 1, 1)
        self.gridLayout.addWidget(self.ln2TebTouOpen, 4, 3, 1, 1)
        
        self.gridLayout.addWidget(self.ln2TrapLed, 5, 0, 1, 1)
        self.gridLayout.addWidget(self.ln2TrapLabel, 5, 1, 1, 1)
        self.gridLayout.addWidget(self.ln2TrapClose, 5, 2, 1, 1)
        self.gridLayout.addWidget(self.ln2TrapOpen, 5, 3, 1, 1)
        
        self.gridLayout.addItem(ln2N2Spacer, 2, 3, 1, 1)
        
        self.gridLayout.addWidget(self.n2ShroudLed, 2, 4, 1, 1)
        self.gridLayout.addWidget(self.n2ShroudLabel, 2, 5, 1, 1)
        self.gridLayout.addWidget(self.n2ShroudClose, 2, 6, 1, 1)
        self.gridLayout.addWidget(self.n2ShroudOpen, 2, 7, 1, 1)
        
        self.gridLayout.addWidget(self.n2TebFeeLed, 3, 4, 1, 1)
        self.gridLayout.addWidget(self.n2TebFeeLabel, 3, 5, 1, 1)
        self.gridLayout.addWidget(self.n2TebFeeClose, 3, 6, 1, 1)
        self.gridLayout.addWidget(self.n2TebFeeOpen, 3, 7, 1, 1)
        
        self.gridLayout.addWidget(self.n2TebTouLed, 4, 4, 1, 1)
        self.gridLayout.addWidget(self.n2TebTouLabel, 4, 5, 1, 1)
        self.gridLayout.addWidget(self.n2TebTouClose, 4, 6, 1, 1)
        self.gridLayout.addWidget(self.n2TebTouOpen, 4, 7, 1, 1)
        
        self.gridLayout.addWidget(self.n2TrapLed, 5, 4, 1, 1)
        self.gridLayout.addWidget(self.n2TrapLabel, 5, 5, 1, 1)
        self.gridLayout.addWidget(self.n2TrapClose, 5, 6, 1, 1)
        self.gridLayout.addWidget(self.n2TrapOpen, 5, 7, 1, 1)       

        self.gridLayout.addItem(n2MiscSpacer, 2, 7, 1, 1)

        self.gridLayout.addWidget(self.ventLed, 2, 8, 1, 1)
        self.gridLayout.addWidget(self.ventLabel, 2, 9, 1, 1)
        self.gridLayout.addWidget(self.ventClose, 2, 10, 1, 1)
        self.gridLayout.addWidget(self.ventOpen, 2, 11, 1, 1)
        
        self.gridLayout.addWidget(self.gateLed, 3, 8, 1, 1)
        self.gridLayout.addWidget(self.gateLabel, 3, 9, 1, 1)
        self.gridLayout.addWidget(self.gateClose, 3, 10, 1, 1)
        self.gridLayout.addWidget(self.gateOpen, 3, 11, 1, 1) 
        
        self.gridLayout.addWidget(self.guiLabel, 5, 9, 1, 2)
        self.gridLayout.addWidget(self.guiLock, 5, 11, 1, 1)      

        self.setLayout(self.gridLayout)

class ValveUIView(QMainWindow, Observable):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beaglebone Valves")
        self.initUI()
        self.guiEnabled = True
        self.remote = {
            'MV011' : None,
            'MV012' : None,
            'MV013' : None,
            'MV014' : None,
            'MV021' : None,
            'MV022' : None,
            'MV023' : None,
            'MV024' : None,
            'MV001' : None,
            'MV002' : None
        }
        
        self.feedback = {
            'MV011' : None,
            'MV012' : None,
            'MV013' : None,
            'MV014' : None,
            'MV021' : None,
            'MV022' : None,
            'MV023' : None,
            'MV024' : None,
            'MV001-OPEN' : None,
            'MV001-CLOSE' : None,
            'MV002' : None,
            'DOOR' : None
        }
        
        self.valve_monitoring_thread = QThread(self)
        self.valve_monitoring_worker = ValveMonitoringWorker()
        self.valve_monitoring_worker.moveToThread(self.valve_monitoring_thread)
        
        self.valve_monitoring_worker.valve_feedback_status_signal.connect(self.on_feedback_status_change)
        self.valve_monitoring_worker.valve_remote_status_signal.connect(self.on_remote_status_change)
        
        for child in self.findChildren(QPushButton):
            if 'open' in child.objectName():
                child.clicked.connect(self.on_open_click)
            if 'close' in child.objectName():
                child.clicked.connect(self.on_close_click)
        
        self.valve_ctrl.guiLock.clicked.connect(self.on_lock_click)
        
        self.valve_monitoring_thread.started.connect(self.valve_monitoring_worker.start_process)
        self.valve_monitoring_thread.start()
        
    def initUI(self):
        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")
        
        layout = QVBoxLayout()
        self.valve_ctrl = ValveControl()
        layout.addWidget(self.valve_ctrl)
        
        app_frame.setLayout(layout)
        self.setCentralWidget(app_frame)
    
    def on_lock_click(self):
        sender = self.sender()
        self.guiEnabled = False
        if sender.text() == 'Lock':
            sender.setText('Unlock')
            for child in self.findChildren(QPushButton):
                if 'open' in child.objectName() or 'close' in child.objectName():
                    child.setEnabled(False)
        elif sender.text() == 'Unlock':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Valve GUI lock")
            msg.setText("You are about to unlock the valve controller GUI")
            msg.setInformativeText("Are you sure that you want to unlock the valve controller GUI?")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Abort)
            
            retval = msg.exec_()
            if retval == QMessageBox.Ok:
                sender.setText('Lock')
                self.guiEnabled = True    
            else:
                return
                

    
    def on_open_click(self):
        sender = self.sender()
        code = sender.objectName().split('-')[0]
        if code == 'MV002':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Vent valve warning")
            msg.setText("You are about to open the vent valve")
            msg.setInformativeText("Are you sure that you want to open the vent valve?")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Abort)
            
            retval = msg.exec_()
            if retval == QMessageBox.Ok:
                self.actionObservers({'set_valve': [code, True]})   
            else:
                return
        else:
            self.actionObservers({'set_valve': [code, True]})
    
    def on_close_click(self):
        sender = self.sender()
        code = sender.objectName().split('-')[0]
        self.actionObservers({'set_valve': [code, False]})
        
    def on_feedback_status_change(self, monitoring_info):
        monitoring_info.pop('GSRON_VALVE_INTERLOCK_DOOR')
        if self.guiEnabled:
            for key, value in monitoring_info.items():
                if 'MV002' in key:
                    continue
                code  = key.split("_")[-1]
                if self.remote[code]:
                    for child in self.findChildren(QPushButton):
                        if code in child.objectName():
                            if code != 'MV001':
                                if value:
                                    led = self.findChild(QLabel, f'{code}-led')
                                    # print(led)
                                    led.set_color(Indic.RED)
                                    if 'open' in child.objectName():
                                        child.setEnabled(False)
                                    if 'close' in child.objectName():
                                        child.setEnabled(True)
                                else:
                                    led = self.findChild(QLabel, f'{code}-led')
                                    led.set_color(Indic.GREEN)
                                    if 'open' in child.objectName():
                                        child.setEnabled(True)
                                    if 'close' in child.objectName():
                                        child.setEnabled(False)
                            else:
                                led = self.findChild(QLabel, f'MV001-led')
                                if 'OPEN' in key:
                                    if value:
                                        led.set_color(Indic.RED)
                                        if 'open' in child.objectName():
                                            child.setEnabled(True)
                                        if 'close' in child.objectName():
                                            child.setEnabled(False)
                                elif 'CLOSE' in key:
                                    if value:
                                        led.set_color(Indic.GREEN)
                                        if 'open' in child.objectName():
                                            child.setEnabled(False)
                                        if 'close' in child.objectName():
                                            child.setEnabled(True)
                                                   
    
    def on_remote_status_change(self, monitoring_info):
        if self.guiEnabled:
            for key, value in monitoring_info.items():
                if 'MV002' in key:
                    continue
                code  = key.split("_")[-1]
                if self.remote[code] != value:
                    if value:
                        if 'MV001' in key:
                            if self.feedback['MV001-OPEN']:
                                child = self.findChild(QPushButton, f'{code}-close')
                                child.setEnabled(True)
                            elif self.feedback['MV001-CLOSE']:
                                child = self.findChild(QPushButton, f'{code}-open')
                                child.setEnabled(True)
                        else:
                            if self.feedback[code]:
                                child = self.findChild(QPushButton, f'{code}-open')
                                child.setEnabled(True)
                            else:
                                child = self.findChild(QPushButton, f'{code}-close')
                                child.setEnabled(True)
                    else:
                        code  = key.split("_")[-1]
                        child = self.findChild(QPushButton, f'{code}-open')
                        child.setEnabled(False)
                        child = self.findChild(QPushButton, f'{code}-close')
                        child.setEnabled(False)
                self.remote[code] = value        
    
    
    def closeEvent(self, close_event:QCloseEvent) -> None:
        self.valve_monitoring_worker.stop()
        self.valve_monitoring_thread.quit()
    
class ValveUIModel:
    def __init__(self, mode):
        self.mode = mode
        
        if self.mode == 'proxy':
            try:
                self.valve = BeagleboneProxy()
            except Exception as exc:
                raise exc
            
        elif self.mode == 'simulator':
            self.valve = BeagleboneSimulator()
        else:
            raise ValueError(f'Unknown type of Valve implementation passed into the model')
            
        if self.valve is not None:
            logger.debug(f'Valve Controller initialized as {self.valve.__class__.__name__}')

    def set_valve(self, name, state):
        with BeagleboneProxy() as proxy:
            proxy.set_valve(name, state)
    
    def get_valve(self, name):
        with BeagleboneProxy() as proxy:
            return proxy.get_valve(name)
        
    def has_commands(self):
        if self.mode == "proxy":
            with BeagleboneProxy() as valve:
                return valve.has_commands()

        return True

    def load_commands(self):
        if self.mode == "proxy":
            with BeagleboneProxy() as valve:
                    valve.load_commands()

    def is_simulator(self):
        with BeagleboneProxy() as valve:
            return valve.is_simulator()

    def is_connected(self):
        if self.mode == "proxy":
            with BeagleboneProxy() as valve:
                return valve.is_cs_connected()

        else:

            return self.valve.is_connected()

    def reconnect(self):
        if self.mode == "proxy":
            with BeagleboneProxy() as valve:

                valve.reconnect_cs()

                return valve.is_cs_connected()

        else:

            self.valve.reconnect()

            return self.valve.is_connected()

        return False

    def disconnect(self):
        if self.mode == "proxy":

            self.mode.disconnect_cs()     
        
class ValveUIController(Observer):
    def __init__(self, model: ValveUIModel, view: ValveUIView):
        self.model = model
        self.view  = view
        self.view.addObserver(self)
        
    def update(self, changed_object):
        text = changed_object.text()

        if text == "Reconnect":

            if changed_object.isChecked():

                logger.debug("Reconnecting the Valve model.")

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
            if action == 'set_valve':
                name = value[0]
                state = value[1]
                logger.debug(f"do: set_valve({name}, {state})")
                self.model.set_valve(name, state)
            if action == 'get_valve':
                name = value[0]
                logger.debug(f"do: get_valve({name})")
                return self.model.get_valve(name)
    
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type",
        dest="type",
        action="store",
        choices={"proxy", "simulator"},
        help="Specify Beaglebone Valve controller implementation you want to connect to.",
        default="proxy",
    )    
    args = parser.parse_args()
    return args


def main():
    lock_file = QLockFile(str(Path("~/vacuum_beaglebone_ui.app.lock").expanduser()))

    args = list(sys.argv)
    app = QApplication(args)
    app.setWindowIcon(QIcon(str(get_resource(":/icons/vacuum.svg"))))

    if lock_file.tryLock(100):
        args = parse_arguments()

        if args.type == 'proxy':
            try:
                proxy = BeagleboneProxy()
            except Exception:
                raise Exception

        view = ValveUIView()
        model = ValveUIModel(args.type)
        controller = ValveUIController(model, view)

        view.show()
        app.exec_()
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The Beaglebone vacuum GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()


if __name__ == "__main__":
    main()
