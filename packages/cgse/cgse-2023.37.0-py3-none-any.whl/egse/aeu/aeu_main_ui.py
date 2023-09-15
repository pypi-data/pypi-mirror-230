import argparse
import logging
import pickle
import sys

import zmq
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtGui import QCloseEvent, QPixmap, QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QFrame, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, \
    QAction, QLineEdit, QSpinBox, QPushButton
from deepdiff import DeepDiff
from zmq import ZMQError

from egse.aeu.aeu import IntSwitch, CRIOProxy, CRIOController, CRIOSimulator, PSUProxy, AWGProxy, PSUController, \
    AWGController, PSUSimulator, AWGSimulator
from egse.aeu.aeu import CTRL_SETTINGS
from egse.config import find_file
from egse.gui.led import Led, Indic
from egse.observer import Observer, Observable
from egse.settings import Settings
from egse.zmq_ser import connect_address

MODULE_LOGGER = logging.getLogger(__name__)

NUM_POWERLINES = 6

# Leds that always have to be shown (no matter which camera has been selected)


RELEVANT_COMMON_KEYS = {
    "Standby": "Stand-by", "Selftest": "Self-test", "FC_TVAC": "Functional check & TVAC", "Alignment": "Alignment",
    "N-CAM": "N-CAM", "F-CAM": "F-CAM", "V_CCD": "V_CCD", "V_CLK": "V_CLK", "V_AN1": "V_AN1", "V_AN2": "V_AN2",
    "V_AN3": "V_AN3", "V_DIG": "V_DIG", "S_voltage_oor": "Secondary voltage generation out-of-range",
    "S_current_oor": "Secondary current generation out-of-range", "Sync_gf": "Synchronisation generator failure",
    "Clk_TCS_50MHz_nom": "Clk_TCS_50MHz_nom", "Clk_TCS_50MHz_red": "Clk_TCS_50MHz_red",
    "Clk_heater_nom": "Clk_heater_nom", "Clk_heater_red": "Clk_heater_red", "TestPort": "Test port"
}

# Leds that have to be shown only if the N-CAM has been selected

RELEVANT_N_CAM_KEYS = ["Clk_N_50MHz", "Clk_N_ccdread"]

# Leds that have to be shown only if the F-CAM has been selected

RELEVANT_F_CAM_KEYS = ["Clk_F_50MHz_nom", "Clk_F_50MHz_red", "Clk_F_ccdread_nom", "Clk_F_ccdread_red"]

PSU_NAMES = {1: "CCD", 2: "CLK", 3: "AN1", 4: "AN2", 5: "AN3", 6: "DIG"}

# class MonitoringWorker(QObject):
#     """ Worker for monitoring the led status of the AEU cRIO. """
#
#     # The worker will send a signal with the AEU cRIO led status
#
#     common_led_status_signal = pyqtSignal(dict)
#     hide_clk_signal = pyqtSignal()
#     n_cam_clk_led_status_signal = pyqtSignal(dict)
#     f_cam_clk_led_status_signal = pyqtSignal(dict)
#
#     def __init__(self):
#         """ Initialisation of a monitoring worker.
#
#         This worker keeps on eye on the monitoring port of the AEU cRIO.  When a changed in (relevant) monitoring
#         information occurs, a signal will be emitted.  These signals will be used to update the GUI.
#         """
#
#         super(MonitoringWorker, self).__init__()
#
#         self.active = False
#         self.just_reconnected = True
#
#         self.monitoring_socket = None
#         self.is_socket_connected = True
#         self.monitoring_timeout = 0.5  # [s]
#
#         self.connect_socket()
#
#         # Keep track of the previous led status, so we only have to send a signal when the led status has changed
#
#         self.previous_common_led_status = {}
#         self.previous_n_cam_clk_led_status = {}
#         self.previous_f_cam_clk_led_status = {}
#
#     def connect_socket(self):
#         """ Create a socket and connect to the monitoring port.
#         """
#
#         try:
#
#             transport = CTRL_SETTINGS.PROTOCOL
#             hostname = CTRL_SETTINGS.HOSTNAME
#             # commanding_port = CTRL_SETTINGS.CRIO["COMMANDING_PORT"]
#             monitoring_port = CTRL_SETTINGS.CRIO["MONITORING_PORT"]
#
#             monitoring_address = connect_address(transport, hostname, monitoring_port)
#
#             self.monitoring_socket = zmq.Context().socket(zmq.SUB)
#             self.monitoring_socket.connect(monitoring_address)
#             self.monitoring_socket.setsockopt_string(zmq.SUBSCRIBE, "")
#
#             self.monitoring_timeout = 0.5   # [s]
#
#             # Address of the commanding port
#             # This is needed when checking whether or not the CS is active
#             # TODO
#
#             self.is_socket_connected = True
#
#         except AttributeError:
#
#             self.is_socket_connected = False
#
#     def stop(self):
#
#         """ Stop the monitoring worker.
#
#         The monitoring socket is disconnected from the monitoring port and is then closed immediately.
#         """
#
#         self.monitoring_socket.close()
#         self.is_socket_connected = False
#
#         self.active = False
#
#     def start_process(self):
#         """ Start updating the led status of the AEU cRIO."""
#
#         self.run()
#
#     @pyqtSlot()
#     def run(self):
#         """ Keep on checking whether the led status of the AEU cRIO has changed.
#
#         If the led status of the AEU cRIO has changed, update it in the GUI.
#         """
#
#         self.active = True
#
#         while self.is_socket_connected and self.active:
#
#             try:
#
#                 socket_list, _, _ = zmq.select([self.monitoring_socket], [], [], timeout=self.monitoring_timeout)
#
#                 # Monitoring information was received (before timeout)
#
#                 if self.monitoring_socket in socket_list:
#
#                     pickle_string = self.monitoring_socket.recv()
#                     monitoring_info = pickle.loads(pickle_string)
#
#                     # Select the monitoring information that is relevant for the GUI
#
#                     common_led_status = {key: monitoring_info[key] for key in RELEVANT_COMMON_KEYS.keys()}
#
#                     n_cam_clk_led_status = {}
#                     f_cam_clk_led_status = {}
#
#                     n_cam_powered = common_led_status["N-CAM"]
#                     f_cam_powered = common_led_status["F-CAM"]
#
#                     if n_cam_powered:
#                         n_cam_clk_led_status = {key: monitoring_info[key] for key in RELEVANT_N_CAM_KEYS}
#                     elif f_cam_powered:
#                         f_cam_clk_led_status = {key: monitoring_info[key] for key in RELEVANT_F_CAM_KEYS}
#
#                     diff_common = DeepDiff(common_led_status, self.previous_common_led_status)
#                     diff_n_cam_clk = DeepDiff(n_cam_clk_led_status, self.previous_n_cam_clk_led_status)
#                     diff_f_cam_clk = DeepDiff(f_cam_clk_led_status, self.previous_f_cam_clk_led_status)
#
#                     error_detected = monitoring_info["S_voltage_oor"] or monitoring_info["S_current_oor"] \
#                                      or monitoring_info["Sync_gf"]
#
#                     # Change in common led status
#
#                     if self.just_reconnected:
#
#                         if error_detected or not (n_cam_powered or f_cam_powered):
#
#                             self.hide_clk_signal.emit()
#
#                     if len(diff_common) != 0 or self.just_reconnected:
#
#                         self.previous_common_led_status = common_led_status
#                         self.common_led_status_signal.emit(common_led_status)
#
#                     if error_detected:
#
#                         self.hide_clk_signal.emit()
#
#                     # Change in N-CAM led status
#
#                     elif len(diff_n_cam_clk) != 0:
#
#                         self.previous_n_cam_clk_led_status = n_cam_clk_led_status
#                         self.n_cam_clk_led_status_signal.emit(n_cam_clk_led_status)
#
#                     # Change in F-CAM led status
#
#                     elif len(diff_f_cam_clk) != 0:
#
#                         self.previous_f_cam_clk_led_status = f_cam_clk_led_status
#                         self.f_cam_clk_led_status_signal.emit(f_cam_clk_led_status)
#
#                     self.just_reconnected = False
#
#             except ZMQError:
#
#                 pass


class PSUWidget(QGroupBox):

    def __init__(self, psu_index: int, name: str):

        super().__init__(f"PSU{psu_index}")

#         label = QLabel(name)
#         self.led = Led(self)
#         self.on_color = on_color
#         self.set_led_color(False)
#
        values_layout = QGridLayout()

        self.measured_voltage = QLineEdit()
        self.measured_current = QLineEdit()

        self.voltage_setpoint = QSpinBox()
        self.current_setpoint = QSpinBox()

        self.power_button = QPushButton("Power on/off")
        self.power_led = Led()
        # self.power_led.setText("Powered on")

        index = 0

        values_layout.addWidget(QLabel(f"Measured V_{name} [V]"), index, 0)
        values_layout.addWidget(QLabel(f"Measured I_{name} [V]"), index, 1)
        index += 1

        values_layout.addWidget(self.measured_voltage, index, 0)
        values_layout.addWidget(self.measured_current, index, 1)
        index += 1

        values_layout.addWidget(QLabel(f"V_{name} setpoint [V]"), index, 0)
        values_layout.addWidget(QLabel(f"I_{name} setpoint"), index, 1)
        index += 1

        values_layout.addWidget(self.voltage_setpoint, index, 0)
        values_layout.addWidget(self.current_setpoint, index, 1)
        index += 1

        values_layout.addWidget(self.power_button, index, 0)
        values_layout.addWidget(self.power_led, index, 1)

        power_layout = QHBoxLayout()

        power_layout.addWidget(self.power_button)
        power_layout.addWidget(self.power_led)

        layout = QVBoxLayout()
        layout.addLayout(values_layout)
        layout.addLayout(power_layout)

#         layout.addWidget(label)
#         layout.addWidget(self.led)

        self.setLayout(layout)
#
#     def set_on_color(self, on_color: Indic):
#         """ Set the colour that the led should have when turned on.
#
#         Args:
#             - on_color: Colour the led should have when turned on.
#         """
#
#         self.on_color = on_color
#
#     def set_led_color(self, status: IntSwitch):
#         """ Change the colour of the led.
#
#         Args:
#             - status: Indicates whether the led should be turned on.
#         """
#
#         if status:
#
#             self.led.set_color(self.on_color)
#
#         else:
#
#             self.led.set_color(Indic.BLACK)
#
#
class AEUUIView(QMainWindow, Observable):

    def __init__(self):
        """ Initialisation of the AEU GUI.

        In the current implementation, the GUI reflects the front panel of the UI, showing the following status
        information:

            - EGSE (operating) mode;
            - camera selection: N-CAM vs. F-CAM;
            - output status of the the six power lines (V_CCD, V_CLK, V_AN1, V_AN2, V_AN3, and V_DIG);
            - error detection: secondary voltage/current out-of-range & synchronisation generator failure;
            - Clk signals selection: Clk_N_50MHz, Clk_N_ccdread, Clk_F_50MHz_nom, Clk_F_50MHz_red, Clk_F_ccdread_nom,
              Clk_F_ccdread_red, Clk_TCS_50MHz_nom, Clk_TCS_50MHz_red, Clk_heater_nom, Clk_heater_red, and test port.
        """

        super().__init__()

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle("Ancillary Electrical Units (AEU)")

        self.psu_widgets = {}

#         self.widgets = {}
#         self.connected_pix, self.disconnected_pix, self.connection_status_icon = None, None, None
#
#         self.monitoring_thread = QThread(self)
#         self.monitoring_worker = MonitoringWorker()
#         self.monitoring_worker.moveToThread(self.monitoring_thread)
#
#         self.monitoring_worker.common_led_status_signal.connect(self.on_common_led_status_changed_signal)
#         self.monitoring_worker.hide_clk_signal.connect(self.on_hide_clk_signal)
#         self.monitoring_worker.n_cam_clk_led_status_signal.connect(self.on_n_cam_clk_led_status_changed_signal)
#         self.monitoring_worker.f_cam_clk_led_status_signal.connect(self.on_f_cam_clk_led_status_changed_signal)
#
#         self.monitoring_thread.started.connect(self.monitoring_worker.start_process)
#         self.monitoring_thread.start()
#
#         self.reconnect_action = None
#         self.n_cam_clk_signals_selection_widget = QGroupBox("", self)
#         self.f_cam_clk_signals_selection_widget = QGroupBox("", self)
#         self.tcs_clk_signals_selection_widget = QGroupBox("", self)
#
        self.init_ui()

    def init_ui(self):

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        layout = QGridLayout()

        for psu_index in range(1, NUM_POWERLINES + 1):

            psu_widget = PSUWidget(psu_index, PSU_NAMES[psu_index])
            self.psu_widgets[psu_index] = psu_widget

            row = (psu_index - 1) // 3
            column = (psu_index - 1) % 3

            layout.addWidget(psu_widget, row, column)
#
#         self.create_toolbar()
#
#         # self.widgets = {}
#
#         for key, label in RELEVANT_COMMON_KEYS.items():
#
#             self.widgets[key] = LedWidget(label)
#             self.widgets[key].setFixedHeight(50)
#
#         for key in RELEVANT_N_CAM_KEYS + RELEVANT_F_CAM_KEYS:
#
#             self.widgets[key] = LedWidget(key)
#             self.widgets[key].setFixedHeight(50)
#
#         self.widgets["S_voltage_oor"].set_on_color(Indic.RED)
#         self.widgets["S_current_oor"].set_on_color(Indic.RED)
#         self.widgets["Sync_gf"].set_on_color(Indic.RED)
#
#         layout = QHBoxLayout()
#
#         # EGSE mode
#
#         egse_mode_layout = QVBoxLayout()
#         egse_mode_widget = QGroupBox("EGSE mode", self)
#
#         egse_mode_layout.addWidget(self.widgets["Standby"])
#         egse_mode_layout.addWidget(self.widgets["Selftest"])
#         egse_mode_layout.addWidget(self.widgets["FC_TVAC"])
#         egse_mode_layout.addWidget(self.widgets["Alignment"])
#
#         egse_mode_widget.setLayout(egse_mode_layout)
#
#         # Camera selection
#
#         cam_selection_layout = QVBoxLayout()
#         cam_selection_widget = QGroupBox("Camera selection", self)
#
#         cam_selection_layout.addWidget(self.widgets["N-CAM"])
#         cam_selection_layout.addWidget(self.widgets["F-CAM"])
#
#         cam_selection_widget.setLayout(cam_selection_layout)
#
#         # Power lines
#
#         power_lines_layout = QGridLayout()
#         power_lines_widget = QGroupBox("Power lines", self)
#
#         power_lines_layout.addWidget(self.widgets["V_CCD"], 0, 0)
#         power_lines_layout.addWidget(self.widgets["V_CLK"], 1, 0)
#         power_lines_layout.addWidget(self.widgets["V_AN1"], 2, 0)
#         power_lines_layout.addWidget(self.widgets["V_AN2"], 0, 1)
#         power_lines_layout.addWidget(self.widgets["V_AN3"], 1, 1)
#         power_lines_layout.addWidget(self.widgets["V_DIG"], 2, 1)
#
#         power_lines_widget.setLayout(power_lines_layout)
#
#         # Error detection
#
#         error_detection_layout = QVBoxLayout()
#         error_detection_widget = QGroupBox("Error detection", self)
#
#         error_detection_layout.addWidget(self.widgets["S_voltage_oor"])
#         error_detection_layout.addWidget(self.widgets["S_current_oor"])
#         error_detection_layout.addWidget(self.widgets["Sync_gf"])
#
#         error_detection_widget.setLayout(error_detection_layout)
#
#         # Clk signals selection
#
#         clk_signals_selection_layout = QVBoxLayout()
#         clk_signals_selection_widget = QGroupBox("Clk signals selection", self)
#
#         n_cam_clk_signals_selection_layout = QHBoxLayout()
#         f_cam_clk_signals_selection_layout = QGridLayout()
#         tcs_clk_signals_selection_layout = QGridLayout()
#
#         n_cam_clk_signals_selection_layout.addWidget(self.widgets["Clk_N_50MHz"])
#         n_cam_clk_signals_selection_layout.addWidget(self.widgets["Clk_N_ccdread"])
#
#         f_cam_clk_signals_selection_layout.addWidget(self.widgets["Clk_F_50MHz_nom"], 0, 0)
#         f_cam_clk_signals_selection_layout.addWidget(self.widgets["Clk_F_50MHz_red"], 0, 1)
#         f_cam_clk_signals_selection_layout.addWidget(self.widgets["Clk_F_ccdread_nom"], 1, 0)
#         f_cam_clk_signals_selection_layout.addWidget(self.widgets["Clk_F_ccdread_red"], 1, 1)
#
#         tcs_clk_signals_selection_layout.addWidget(self.widgets["Clk_TCS_50MHz_nom"], 0, 0)
#         tcs_clk_signals_selection_layout.addWidget(self.widgets["Clk_TCS_50MHz_red"], 0, 1)
#         tcs_clk_signals_selection_layout.addWidget(self.widgets["Clk_heater_nom"], 1, 0)
#         tcs_clk_signals_selection_layout.addWidget(self.widgets["Clk_heater_red"], 1, 1)
#
#         self.n_cam_clk_signals_selection_widget.setLayout(n_cam_clk_signals_selection_layout)
#         self.f_cam_clk_signals_selection_widget.setLayout(f_cam_clk_signals_selection_layout)
#         self.tcs_clk_signals_selection_widget.setLayout(tcs_clk_signals_selection_layout)
#
#         clk_signals_selection_layout.addWidget(self.n_cam_clk_signals_selection_widget)
#         clk_signals_selection_layout.addWidget(self.f_cam_clk_signals_selection_widget)
#         clk_signals_selection_layout.addWidget(self.tcs_clk_signals_selection_widget)
#
#         self.n_cam_clk_signals_selection_widget.setVisible(False)
#         self.f_cam_clk_signals_selection_widget.setVisible(False)
#         self.tcs_clk_signals_selection_widget.setVisible(False)
#
#         clk_signals_selection_layout.addWidget(self.widgets["TestPort"])
#
#         clk_signals_selection_widget.setLayout(clk_signals_selection_layout)
#
#         egse_mode_layout.addStretch(True)
#         cam_selection_layout.addStretch(True)
#         power_lines_layout.setRowStretch(3, 2)
#         error_detection_layout.addStretch(True)
#         clk_signals_selection_layout.addStretch(True)
#
#         layout.addWidget(egse_mode_widget)
#         layout.addWidget(cam_selection_widget)
#         layout.addWidget(power_lines_widget)
#         layout.addWidget(error_detection_widget)
#         layout.addWidget(clk_signals_selection_widget)

        app_frame.setLayout(layout)

        self.setCentralWidget(app_frame)
#
#     def create_toolbar(self):
#         """ Create toolbar showing the state of the connection with the device."""
#
#         connected_pix = QPixmap(str(find_file("connected-100.png", in_dir="images")))
#         disconnected_pix = QPixmap(str(find_file("disconnected-100.png", in_dir="images")))
#         reconnect_icon = QIcon()
#         reconnect_icon.addPixmap(connected_pix, QIcon.Normal, QIcon.On)
#         reconnect_icon.addPixmap(disconnected_pix, QIcon.Normal, QIcon.Off)
#
#         self.reconnect_action = QAction(reconnect_icon, "Reconnect", self)
#         self.reconnect_action.setToolTip("Reconnect")
#         self.reconnect_action.setCheckable(True)
#         self.reconnect_action.triggered.connect(self.on_click)
#
#         toolbar = self.addToolBar("MainToolbar")
#         toolbar.addAction(self.reconnect_action)
#
#     def on_common_led_status_changed_signal(self, monitoring_info: dict):
#         """ Update the status of the leds in case the common led status has changed.
#
#         Args:
#             - monitoring_info: Monitoring information regarding the EGSE mode, camera selection, power lines, and
#                                error detection.
#         """
#
#         if not self.reconnect_action.isChecked():
#
#             return
#
#         for name, status in monitoring_info.items():
#
#             self.widgets[name].set_led_color(status)
#
#         # self.set_connection_state(True)
#
#     def on_hide_clk_signal(self):
#         """ Hide the information about the clocks."""
#
#         if not self.reconnect_action.isChecked():
#
#             return
#
#         self.n_cam_clk_signals_selection_widget.setVisible(False)
#         self.f_cam_clk_signals_selection_widget.setVisible(False)
#         self.tcs_clk_signals_selection_widget.setVisible(False)
#
#         # self.set_connection_state(True)
#
#     def on_n_cam_clk_led_status_changed_signal(self, monitoring_info: dict):
#         """ Update the status of the leds in case the N-CAM Clk led status has changed.
#
#         When the given monitoring information is empty, the status of the N-CAM Clk is hidden.
#
#         Args:
#             - monitoring_info: Monitoring information regarding the N-CAM Clk signal selection.  Empty when the N-CAM is
#                                not selected.
#         """
#
#         if not self.reconnect_action.isChecked():
#
#             return
#
#         if len(monitoring_info) == 0:
#
#             self.n_cam_clk_signals_selection_widget.setVisible(False)
#             self.tcs_clk_signals_selection_widget.setVisible(False)
#
#         else:
#
#             self.n_cam_clk_signals_selection_widget.setVisible(True)
#             self.tcs_clk_signals_selection_widget.setVisible(True)
#
#             for name, status in monitoring_info.items():
#
#                 self.widgets[name].set_led_color(status)
#
#         # self.set_connection_state(True)
#
#     def on_f_cam_clk_led_status_changed_signal(self, monitoring_info: dict):
#         """ Update the status of the leds in case the F-CAM Clk led status has changed.
#
#         When the given monitoring information is empty, the status of the F-CAM Clk is hidden
#
#         Args:
#             - monitoring_info: Monitoring information regarding the F-CAM Clk signal selection.  Empty when the F-CAM is
#                                not selected.
#         """
#
#         if not self.reconnect_action.isChecked():
#
#             return
#
#         if len(monitoring_info) == 0:
#
#             self.f_cam_clk_signals_selection_widget.setVisible(False)
#             self.tcs_clk_signals_selection_widget.setVisible(False)
#
#         else:
#
#             self.f_cam_clk_signals_selection_widget.setVisible(True)
#             self.tcs_clk_signals_selection_widget.setVisible(True)
#
#             for name, status in monitoring_info.items():
#
#                 self.widgets[name].set_led_color(status)
#
#         # self.set_connection_state(True)
#
#     # def on_connection_lost_signal(self):
#     #     """ Switch off all leds when the connection to the cRIO is lost."""
#     #
#     #     print("Connection lost")
#     #
#     #     self.disable_leds()
#     #
#     #     # self.set_connection_state(False)
#
#     def disable_leds(self):
#         """ Disable all the leds."""
#
#         for led in self.widgets.values():
#
#             led.set_led_color(0)
#
#     def on_click(self):
#         """ Notify the observers in case of a click."""
#         sender = self.sender()
#
#         MODULE_LOGGER.log(0, f"sender.text() = {sender.text()}")
#         MODULE_LOGGER.log(0, f"sender.isChecked() = {sender.isChecked()}")
#
#         self.notifyObservers(sender)
#
#     def set_connection_state(self, is_connected):
#         """ Update the connection state in the toolbar.
#
#         Args:
#             - is_connected: Connection status to show.
#         """
#         if is_connected:
#
#             self.reconnect_action.setChecked(True)
#             self.monitoring_worker.just_reconnected = True
#
#         elif not is_connected:
#
#             self.reconnect_action.setChecked(False)
#             self.disable_leds()
#
#     def closeEvent(self, close_event: QCloseEvent) -> None:
#         """ Make sure that all threads are stopped when the GUI is closed.
#
#         Args:
#             - close_event: Close event received when the GUI is closed.
#         """
#
#         self.monitoring_worker.stop()
#
#         self.monitoring_thread.quit()
#         self.monitoring_thread.wait()


class AEUUIModel:

    def __init__(self, aeu_type: str):
        """ Initialisation of the mode, based on the given AEU cRIO type.

        Allowed values are:

            - proxy: to use the CRIOProxy;
            - crio: to use the CRIOController;
            - simulator: to use the CRIOSimulator.

        Args:
            - aeu_type: Type of AEU cRIO to use as UI model.
        """

        self.type = aeu_type

        # Proxy

        if self.type == "proxy":

            self.crio = CRIOProxy()
            self.psu = {psu_index: PSUProxy(psu_index) for psu_index in range(1, NUM_POWERLINES + 1)}
            # self.awg = {awg_index: AWGProxy(awg_index) for awg_index in range(1, 3)}

        # Controller

        elif self.type == "aeu":

            self.crio = CRIOController()
            self.psu = {psu_index: PSUController(psu_index) for psu_index in range(1, NUM_POWERLINES + 1)}
            self.awg = {awg_index: AWGController(awg_index) for awg_index in range(1, 3)}

            self.crio.connect()

            for psu in self.psu.values():
                psu.connect()

            # for awg in self.awg.values():
            #     awg.connect()

        # Simulator

        elif self.type == "simulator":

            self.crio = CRIOSimulator()
            self.psu = {psu_index: PSUSimulator(psu_index) for psu_index in range(1, NUM_POWERLINES + 1)}
            # self.awg = {awg_index: AWGSimulator(awg_index) for awg_index in range(1, 3)}

        else:

            raise ValueError(f"Unknown type of AEU cRIO implementation passed into the model: {type}")

        if self.crio is not None:

            MODULE_LOGGER.debug(f"AEU cRIO Controller initialized as {self.crio.__class__.__name__}")

    # def has_commands(self):
    #     """ Check whether the AEU cRIO has commands.
    #
    #     Returns: True if the AEU cRIO has commands; False otherwise.
    #     """
    #
    #     if self.type == "proxy":
    #
    #         return self.crio.has_commands()
    #
    #     return True
    #
    # def load_commands(self):
    #     """ Load the commands for the CRIOProxy."""
    #
    #     if self.type == "proxy":
    #
    #         self.crio.load_commands()
    #
    # def is_simulator(self):
    #     """ Checks whether the AEU cRIO is a simulator.
    #
    #     Returns: True if the AEU cRIO is a simulator; False otherwise.
    #     """
    #
    #     return self.crio.is_simulator()
    #
    # def is_connected(self):
    #     """ Check whether the AEU cRIO is connected.
    #
    #     Returns: True if the AEU cRIO is connected; False otherwise.
    #     """
    #
    #     if self.type == "proxy":
    #
    #         return self.crio.is_cs_connected()
    #
    #     else:
    #
    #         return self.crio.is_connected()
    #
    # def reconnect(self):
    #     """ Reconnect the AEU cRIO.
    #
    #     Returns: True if the connection could be established; False otherwise.
    #     """
    #
    #     if self.type == "proxy":
    #
    #         self.crio.reconnect_cs()
    #
    #         return self.crio.is_cs_connected()
    #
    #     else:
    #
    #         self.crio.reconnect()
    #
    #         return self.crio.is_connected()
    #
    #     return False
    #
    # def disconnect(self):
    #     """ Disconnect the AEU cRIO Control Server."""
    #
    #     if self.type == "proxy":
    #
    #         self.crio.disconnect_cs()
    #

class AEUUIController(Observer):

    def __init__(self, model: AEUUIModel, view: AEUUIView):

        self.model = model
        self.view = view
        self.view.addObserver(self)

        # self.states_capture_timer = None
        # self.timer_interval = 200
        # self.create_timer()

        # if self.model.is_connected():
        #
        #     self.view.set_connection_state(True)
        #     # self.start_timer()
        #
        # else:
        #
        #     self.view.set_connection_state(False)
        #     # self.stop_timer()

    # def create_timer(self):
    #
    #     print("Create timer")
    #     """Create a Timer that will update the States every second."""
    #
    #     self.states_capture_timer = QTimer()
    #     # This is only needed when the Timer needs to run in another Thread
    #     # self.states_capture_timer.moveToThread(self)
    #     self.states_capture_timer.timeout.connect(self.update_connection_state)
    #     self.states_capture_timer.setInterval(self.timer_interval)
    #
    # def start_timer(self):
    #     print("Start timer")
    #     self.states_capture_timer.start()
    #
    # def stop_timer(self):
    #     print("Stop timer")
    #     self.states_capture_timer.stop()
    #
    # def update_connection_state(self):
    #     """Updates the common view widgets."""
    #
    #     if not self.model.is_connected():
    #
    #         self.view.set_connection_state(False)

    def update(self, changed_object):

        text = changed_object.text()

        if text == "Reconnect":

            if changed_object.isChecked():

                MODULE_LOGGER.debug("Reconnecting the AEU model.")

                if self.model.reconnect():

                    self.view.set_connection_state(True)

                    if not self.model.has_commands():

                        self.model.load_commands()

                else:
                    self.view.reconnect_action.setChecked(False)
            else:

                MODULE_LOGGER.debug("Disconnecting the AEU model.")
                self.model.disconnect()
                self.view.set_connection_state(False)

            return

    def do(self):

        pass

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
    parser.add_argument(
        "--profile",
        default=False,
        action="store_true",
        help="Enable info logging messages with method profile information.",
    )
    args = parser.parse_args()
    return args


def main():
    """ Main method to launch the AEU GUI."""

    args = list(sys.argv)
    app = QApplication(args)

    # process_status = ProcessStatus()
    #
    # timer_thread = threading.Thread(target=do_every, args=(10, process_status.update))
    # timer_thread.daemon = True
    # timer_thread.start()
    #
    # start_http_server(8541)

    args = parse_arguments()

    if args.profile:
        Settings.set_profiling(True)

    if args.type == "proxy":
        proxy = CRIOProxy()
        # if not proxy.ping():
        #     description = "Could not connect to Stages Control Server"
        #     info_text = (
        #         "The GUI will start, but the connection button will show a disconnected state. "
        #         "Please check if the Control Server is running and start the server if needed. "
        #         "Otherwise, check if the correct HOSTNAME for the control server is set in the "
        #         "Settings.yaml "
        #         "configuration file."
        #     )
        #
        #     show_warning_message(description, info_text)


    view = AEUUIView()
    model = AEUUIModel(args.type)
    controller = AEUUIController(model, view)

    view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":

    main()
