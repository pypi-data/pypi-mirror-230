"""
This module implements the image display for the N-FEE data and housekeeping.

The DPU GUI can be started from the command line with the `dpu_ui` command. The GUI will connect to the
data distribution port of the DPU Processor. For this to work, you will need to have at least a DPU control server
running.

"""
import contextlib
import logging
import multiprocessing
import os
import pickle
import threading
from functools import partial
from pathlib import Path

import sys
from PyQt5.QtCore import QLockFile, QModelIndex
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QMessageBox, QTableView

from egse.bits import bit_set
from egse.dpu.hdf5_model import RegisterTableModel
from egse.gui.led import Indic
from egse.gui.led import LED
from egse.setup import SetupError
from egse.state import GlobalState

multiprocessing.current_process().name = "dpu_ui"

import zmq
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QRunnable
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from prometheus_client import start_http_server

from egse.dpu.ccd_ui import ImageCreatorFullSize
from egse.dpu.ccd_ui import NFEE4CCDWidget
from egse.dpu.hk_ui import NFEEHousekeepingWidget
from egse.fee import convert_ccd_order_value
from egse.fee import n_fee_mode
from egse.process import ProcessStatus
from egse.reg import RegisterMap
from egse.resource import get_resource
from egse.settings import Settings
from egse.system import do_every
from egse.zmq import MessageIdentifier

LOGGER = logging.getLogger("egse.dpu.dpu_ui")

DPU_SETTINGS = Settings.load("DPU Processor")
GUI_SETTINGS = Settings.load("DPU GUI")


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `str` Exception string

    result
        `dict` data returned from processing

    """

    finished = pyqtSignal()
    error = pyqtSignal(str)
    data = pyqtSignal(int, object)
    stalled = pyqtSignal(bool)


class DataMonitor(QRunnable):
    def __init__(self, hostname: str, port: int):
        super().__init__()
        self.signals = WorkerSignals()
        self.hostname = hostname
        self.port = port
        self.quit_request = False
        self.receiver = None

    @pyqtSlot()
    def run(self):

        context = zmq.Context.instance()
        self.receiver = context.socket(zmq.SUB)
        self.receiver.subscribe("")

        LOGGER.debug(f"Data Monitor connecting to {self.hostname}:{self.port}")

        self.receiver.connect(f"tcp://{self.hostname}:{self.port}")

        while True:
            if self.quit_request:
                break

            socket_list, _, _ = zmq.select([self.receiver], [], [], timeout=1.0)

            if self.receiver in socket_list:
                try:
                    sync_id, pickle_string = self.receiver.recv_multipart()
                    sync_id = int.from_bytes(sync_id, byteorder='big')
                    data = pickle.loads(pickle_string)
                    self.signals.data.emit(sync_id, data)
                except Exception as exc:
                    LOGGER.error("Exception caught!", exc_info=True)
                    self.signals.error.emit(str(exc))

        self.receiver.disconnect(f"tcp://{self.hostname}:{self.port}")
        self.receiver.close()
        self.signals.finished.emit()

    def quit(self):
        self.quit_request = True


class DataPuller(QRunnable):
    def __init__(self, hostname: str, port: int):
        super().__init__()
        self.signals = WorkerSignals()
        self.hostname = hostname
        self.port = port
        self.quit_request = False
        self.receiver = None

    @pyqtSlot()
    def run(self):

        n_timeouts = 0
        """The timeout is 1s, we count the number of timeouts to detect if the DPU or N-FEE might be dead or stalled."""

        context = zmq.Context.instance()
        self.receiver = context.socket(zmq.SUB)
        self.receiver.setsockopt_string(zmq.SUBSCRIBE, "")

        # It's not really clear if the 'client' needs to connect to the port or
        # needs to bind to the port. What I see currently is that when the server (DPU Processor)
        # binds, then that process hangs. So, for the moment the DPU Processor connects to the
        # socket but PUSH the data. The result is that only one other process can bind!
        # Needs further investigation.... perhaps we should go back to PUB–SUB...
        # We went back to PUB-SUB...

        LOGGER.debug(f"Data Puller connecting to {self.hostname}:{self.port}")

        self.receiver.connect(f"tcp://{self.hostname}:{self.port}")

        while True:
            if self.quit_request:
                break

            socket_list, _, _ = zmq.select([self.receiver], [], [], timeout=1.0)

            if self.receiver in socket_list:
                n_timeouts = 0
                try:
                    sync_id, pickle_string = self.receiver.recv_multipart()
                    sync_id = int.from_bytes(sync_id, byteorder='big')
                    data = pickle.loads(pickle_string)
                    self.signals.data.emit(sync_id, data)
                except Exception as exc:
                    LOGGER.error("Exception caught!", exc_info=True)
                    self.signals.error.emit(str(exc))

            if len(socket_list) == 0:
                n_timeouts += 1
                if n_timeouts > 7:  # at least a timecode should arrive every 6.25s
                    self.signals.stalled.emit(True)

        self.receiver.disconnect(f"tcp://{self.hostname}:{self.port}")
        self.receiver.close()
        self.signals.finished.emit()

    def quit(self):
        self.quit_request = True


class ModeParameterWidget(QWidget):
    def __init__(self, params: dict):
        super().__init__()

        self.params = params

        # Use the following line to put a small border around all the parameters
        # self.setStyleSheet('border: 1px solid red;')

        vbox = QVBoxLayout()
        vbox.setSpacing(4)
        vbox.setContentsMargins(10, 0, 10, 0)

        vbox.addWidget(QLabel("<b>Mode Parameters</b>"))

        for name, widget in self.params.items():
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(name))
            hbox.addWidget(widget)
            vbox.addLayout(hbox)

        self.setLayout(vbox)

    def update_par(self, name, value):
        self.params[name].setText(f"{value}")

    def update_params(self, params: dict):
        for name, value in params.items():
            self.params[name].setText(f"{value}")


class ReadoutParameterWidget(QWidget):
    def __init__(self, params: dict):
        super().__init__()

        self.params = params

        # Use the following line to put a small border around all the parameters
        # self.setStyleSheet('border: 1px solid red;')

        vbox = QVBoxLayout()
        vbox.setSpacing(4)
        vbox.setContentsMargins(10, 0, 10, 0)

        vbox.addWidget(QLabel("<b>Readout Parameters</b>"))

        for name, widget in self.params.items():
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(name))
            hbox.addWidget(widget)
            vbox.addLayout(hbox)

        self.setLayout(vbox)

    def get_value(self, name):
        return self.params[name].text()

    def update_par(self, name, value):
        self.params[name].setText(f"{value}")

    def update_params(self, params: dict):
        for name, value in params.items():
            self.params[name].setText(f"{value}")


class StatusParameterWidget(QWidget):
    def __init__(self, params: dict):
        super().__init__()

        self.params = params
        self.error_flag_names = [
            "Wrong X-Coordinate", "Wrong Y-Coordinate", "E SRAM Full", "F SRAM Full", "AWLA Error",
            "SRAM EDAC Correct", "SRAM EDAC Uncorrect", "Block R EDAC",
            "Disconnect Error", "Escape Error", "Credit Error", "Parity Error", "Lock Error",
        ]

        # Use the following line to put a small border around all the parameters
        # self.setStyleSheet('border: 1px solid red;')

        vbox = QVBoxLayout()
        vbox.setSpacing(4)
        vbox.setContentsMargins(10, 0, 10, 0)

        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignLeft)
        hbox.addWidget(QLabel("<b>Status Parameters</b> ("))
        clear_error_flags = QLabel("Clear")
        clear_error_flags.setStyleSheet("color: blue; text-decoration: underline")
        clear_error_flags.mousePressEvent = self.clear_error_flags
        hbox.addWidget(clear_error_flags)
        hbox.addWidget(QLabel(")"))
        vbox.addLayout(hbox)

        for name, item in self.params.items():
            self.set_format(name, 0)
            self.update_param(name, 0)
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(name))
            hbox.addWidget(item['led'])
            label: QLabel = item['label']
            font = label.font()
            font.setStyleHint(QFont.TypeWriter)
            label.setFont(font)
            label.mousePressEvent = partial(self.toggle_format, name)
            hbox.addWidget(label)
            vbox.addLayout(hbox)

        vbox.addStretch()
        self.setLayout(vbox)

    def toggle_format(self, name, event):
        LOGGER.info(f"{name = }, {event = }")
        format_type = self.params[name]['format_type'] + 1
        format_type = self.params[name]['format_type'] = format_type if 0 <= format_type < 3 else 0
        self.set_format(name, format_type)
        self.refresh_param(name)

    def set_format(self, name, format_type):
        LOGGER.info(f"{name = }, {format_type = }")
        formats = ["0x{0:04X}", "0b{0:012b}", "  {0:d}"]
        self.params[name]['format_type'] = format_type
        self.params[name]['format'] = formats[format_type]

    def set_value(self, name, value):
        self.params[name]['value'] = value

    def get_value(self, name):
        return self.params[name]['value']

    def refresh_param(self, name):
        self.update_param(name, self.params[name]['value'])

    def clear_error_flags(self, *args):
        self.update_param("Error Flags", 0, "no errors detected")

    def update_param(self, name, value, tooltip=None):
        format = self.params[name]['format']
        self.params[name]['value'] = value
        self.params[name]['label'].setText(format.format(value))
        if tooltip:
            self.params[name]['label'].setToolTip(tooltip)
        self.params[name]['led'].set_color(Indic.BLACK if value == 0 else self.params[name]['color'])

    def update_params(self, params: dict):
        LOGGER.info(f"{params = }")
        for name, data in params.items():
            if name == "Error Flags":
                error_flags, frame_counter, timestamp = data
                if self.params[name]['value'] == 0 and error_flags != 0:
                    self.update_param(name, error_flags, self._decode_error_flags(error_flags, frame_counter, timestamp))
                # self.refresh_param(name)

    def _decode_error_flags(self, error_flags, frame_counter, timestamp) -> str:

        if error_flags == 0:
            return "no errors detected"

        msg = f"<b>Error on {frame_counter=} </b><br><br>"

        flags = "".join([
            f"– {name}<br>"
            for idx, name in enumerate(self.error_flag_names)
            if bit_set(error_flags, idx)
        ])

        return msg + flags


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DPU Image Display")

        self.setStatusBar(QStatusBar(self))
        self.status = self.statusBar()

        self.image = None
        self.register_map = None
        self.data_puller = None
        self.data_monitor = None
        self.setup = GlobalState.setup

        try:
            self.ccd_bin_to_id = self.setup.camera.fee.ccd_numbering.CCD_BIN_TO_ID
        except AttributeError:
            raise SetupError("No entry in the setup for camera.fee.ccd_numbering.CCD_BIN_TO_ID")

        try:
            self.ccd_bin_to_idx = self.setup.camera.fee.ccd_numbering.CCD_BIN_TO_IDX
        except AttributeError:
            raise SetupError("No entry in the setup for camera.fee.ccd_numbering.CCD_BIN_TO_IDX")

        try:
            self.sensor_sel = self.setup.camera.fee.sensor_sel.enum
        except AttributeError:
            raise SetupError("No entry in the setup for camera.fee.sensor_sel")

        self.threadpool = QThreadPool.globalInstance()

        self.counter = 0

        self.tabs = QTabWidget()

        # Use the following line to put a small border around the components of the TAB Widget
        # self.tabs.setStyleSheet('border: 1px solid green;')

        self.hk_box = NFEEHousekeepingWidget()
        self.ccd_box = NFEE4CCDWidget()
        self.register_box = RegisterWidget()

        mode_params = {
            'N-FEE Mode': QLabel('OFF'),
            'N-FEE Cycle Time': QLabel(""),
            'DUMP Mode': QLabel(""),
            'Internal Sync': QLabel(""),
            'External Sync': QLabel(""),
        }

        self.mode_params = ModeParameterWidget(mode_params)

        readout_params = {
            'Row Start': QLabel('0'),
            'Row End': QLabel("4509"),
            'Num Columns': QLabel("2295"),
            'Readout Order': QLabel(f"{[1, 2, 3, 4]}"),
            'CCD Side': QLabel(""),
            'Number of Cycles': QLabel(""),
        }

        self.readout_params = ReadoutParameterWidget(readout_params)

        status_params = {
            'Error Flags': {
                'led': LED(),
                'color': Indic.RED,
                'label': QLabel('0b000000000000'),
                'retain': True,
            },
        }

        self.status_params = StatusParameterWidget(status_params)

        self.tabs.addTab(self.ccd_box, "CCD Display")
        self.tabs.addTab(self.hk_box, "HK Packet")
        self.tabs.addTab(self.register_box, "Register Map")

        params_box = QHBoxLayout()

        params_box.addWidget(self.mode_params)
        params_box.addWidget(self.readout_params)
        params_box.addWidget(self.status_params)

        vbox = QVBoxLayout()
        vbox.setSpacing(0)  # limit the space between the views and the parameters
        vbox.addWidget(self.tabs, stretch=1)
        vbox.addLayout(params_box)

        w = QWidget()
        w.setLayout(vbox)
        self.setCentralWidget(w)

        self.show()

        self.start_pulling_data()
        self.start_monitoring()

    def closeEvent(self, event):
        LOGGER.info("Window closed, quiting....")
        self.data_puller.quit()
        self.data_monitor.quit()
        event.accept()

        all_threads_finished = self.threadpool.waitForDone(msecs=2000)
        if not all_threads_finished:
            LOGGER.warning("Not all threads were finished before the DPU GUI terminated.")

    def start_pulling_data(self):
        self.data_puller = worker = DataPuller(DPU_SETTINGS.HOSTNAME, DPU_SETTINGS.DATA_DISTRIBUTION_PORT)
        self.threadpool.start(worker)
        worker.signals.data.connect(self.puller_output)
        worker.signals.finished.connect(self.puller_complete)
        worker.signals.error.connect(self.puller_error)
        worker.signals.stalled.connect(self.puller_stalled)

    def start_monitoring(self):
        self.data_monitor = worker = DataMonitor(DPU_SETTINGS.HOSTNAME, DPU_SETTINGS.MONITORING_PORT)
        self.threadpool.start(worker)
        worker.signals.data.connect(self.monitor_output)
        worker.signals.finished.connect(self.monitor_complete)
        worker.signals.error.connect(self.monitor_error)

    @pyqtSlot(int, bytes)
    def monitor_output(self, sync_id, data):
        LOGGER.info(f"Data Monitor: sync_id = {MessageIdentifier(sync_id).name}, {data = }")
        if sync_id == MessageIdentifier.SYNC_ERROR_FLAGS:
            params = {
                'Error Flags': data
            }
            self.status_params.update_params(params)

    @pyqtSlot()
    def monitor_complete(self):
        LOGGER.info("Data Monitor thread complete!")
        # zmq.Context().destroy(linger=0)

    @pyqtSlot(str)
    def monitor_error(self, t):
        LOGGER.warning(f"Data Monitor ERROR: {t}")

    @pyqtSlot(int, bytes)
    def puller_output(self, sync_id, data):
        # LOGGER.info(f"Data Puller: sync_id = {MessageIdentifier(sync_id).name}")  # Generates a lot of output!
        if sync_id == MessageIdentifier.SYNC_TIMECODE:
            timecode, timestamp = data
            # LOGGER.info(f"TIMECODE: {timecode=}, {timestamp=}")
        if sync_id == MessageIdentifier.SYNC_HK_PACKET:
            hk_packet, timestamp = data
            if self.tabs.currentWidget() is self.hk_box:
                with contextlib.suppress(KeyError):
                    self.hk_box.update_fields(hk_packet)
            # LOGGER.info(f"HK_PACKET: {hk_packet.type.frame_number=}, {timestamp=}")
            if hk_packet.type.frame_number == 0:
                pass
                # self.ccd_box.clear_image_data()
            if self.register_map is not None:
                # nr_lines = self.register_map["v_end"] - self.register_map["v_start"] + 1
                # nr_columns = self.register_map["h_end"] + 1
                # self.image = ImageCreator(nr_lines=nr_lines, nr_columns=nr_columns)
                self.image = ImageCreatorFullSize(
                    v_start=self.register_map["v_start"],
                    v_end=self.register_map["v_end"],
                    h_end=self.register_map["h_end"],
                )
                self.register_box.update(self.register_map)
        if sync_id == MessageIdentifier.SYNC_DATA_PACKET:
            data_packet, timestamp = data
            # LOGGER.info(f"DATA_PACKET: {data_packet.type.ccd_number=}, {timestamp=}")
            self.mark_ccd_widget(data_packet.type.ccd_number)
            if self.image is not None:
                self.image.add_data(data_packet)
                if data_packet.type.last_packet:
                    self.ccd_box.show_ccd_image(
                        self.ccd_bin_to_id[data_packet.type.ccd_number],
                        data_packet.type.ccd_side,
                        self.image.get_image(data_packet.type.ccd_side)
                    )

        if sync_id == MessageIdentifier.N_FEE_REGISTER_MAP:
            self.register_map = reg = RegisterMap('N-FEE', memory_map=data)
            # LOGGER.info(f"REGISTER_MAP: {reg['ccd_mode_config']=}")
            is_dump_mode = bool(not reg["digitise_en"] and reg["DG_en"] and reg["ccd_mode_config"] == n_fee_mode.FULL_IMAGE_MODE)

            params = {
                'N-FEE Mode': n_fee_mode(reg["ccd_mode_config"]).name,
                'N-FEE Cycle Time': "25.0s" if not reg["sync_sel"] else f"{reg['int_sync_period']/1000}s",
                'DUMP Mode': is_dump_mode,
                'Internal Sync': "True" if reg["sync_sel"] else "False",
                'External Sync': "False" if reg["sync_sel"] else "True",
            }
            self.mode_params.update_params(params)
            readout_order = reg["ccd_readout_order"]
            readout_order = convert_ccd_order_value(readout_order)
            params = {
                'Row Start': reg["v_start"],
                'Row End': reg["v_end"],
                'Num Columns': reg["h_end"] + 1,
                'Readout Order': readout_order,
                'CCD Side': self.sensor_sel(reg['sensor_sel']).name,
            }
            self.readout_params.update_params(params)
            if is_dump_mode:
                self.ccd_box.unmark()
        if sync_id == MessageIdentifier.NUM_CYCLES:
            # LOGGER.info(f"NUMBER OF CYCLES: {data}")
            self.readout_params.update_par('Number of Cycles', max(0, data))

    @pyqtSlot()
    def puller_complete(self):
        LOGGER.info("Data Puller thread complete!")
        # zmq.Context().destroy(linger=0)

    @pyqtSlot(str)
    def puller_error(self, t):
        LOGGER.warning(f"Data Puller ERROR: {t}")

    @pyqtSlot(bool)
    def puller_stalled(self, flag: bool):
        params = {
            'N-FEE Mode': 'CONNECTION LOST',
            'N-FEE Cycle Time': "",
            'DUMP Mode': "",
            'Internal Sync': "",
            'External Sync': "",
        }
        self.mode_params.update_params(params)

    def mark_ccd_widget(self, ccd_number: int):
        self.ccd_box.mark(self.ccd_bin_to_idx[ccd_number])


class RegisterWidget(QWidget):
    """ Widget to display the FEE register map."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.register_model = RegisterTableModel(RegisterMap())
        self.table_view = QTableView(self)
        self.table_view.setModel(self.register_model)
        self.table_view.resizeColumnsToContents()
        self.table_view.clicked.connect(self.on_cell_clicked)
        layout = QVBoxLayout(self)
        layout.addWidget(self.table_view)

    def update(self, register_map: RegisterMap):
        """ Update the register map.

        Args:
            - register_map: Register map to display.
        """

        self.register_model.setRegisterMap(register_map)
        self.register_model.layoutChanged.emit()

        self.table_view.resizeColumnsToContents()
        self.repaint()

    def on_cell_clicked(self, index: QModelIndex, *args, **kwargs):
        self.register_model.toggleDisplayRole(index)


def main():

    lock_file = QLockFile(str(Path("~/dpu_ui.app.lock").expanduser()))

    app_logo = get_resource(":/icons/logo-dpu.svg")

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(app_logo)))

    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    if lock_file.tryLock(100):

        process_status = ProcessStatus()

        timer_thread = threading.Thread(target=do_every, args=(10, process_status.update))
        timer_thread.daemon = True
        timer_thread.start()

        start_http_server(GUI_SETTINGS.METRICS_PORT)

        window = MainWindow()
        window.show()
        return app.exec()

    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The DPU GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()


if __name__ == '__main__':
    sys.exit(main())
