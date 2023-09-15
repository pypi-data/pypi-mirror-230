import pickle
import threading
from enum import Enum
from pathlib import Path

import sys
import zmq
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QLockFile
from PyQt5.QtGui import QCloseEvent, QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox

from egse.gui import QHLine
from egse.gui.buttons import ToggleButton
from egse.process import SubProcess
from egse.resource import get_resource
from egse.settings import Settings
from egse.zmq_ser import connect_address

CTRL_SETTINGS = Settings.load("FITS Generator Control Server")


class FitsgenStatus(str, Enum):

    DOWN = "inactive"
    IDLE = "idle"
    PROCESSING = "processing"


class FilenamesMonitoringWorker(QObject):
    """ Worker for monitoring the HDF5 and FITS files being handled by the FITS generation"""

    # The worker will send a two signals:
    # A dictionary with
    #   - "hdf5": HDF5 filename currently being processed
    #   - "fits": FITS filename currently being created
    # The status of the FITS generation process:
    #   - down: The FITS generation process is inactive
    #   - idle: The FITS generation process is waiting for an HDF5 file to come in
    #   - processing: The FITS generation process is processing data
    # The last obsid (being) processed

    filenames_signal = pyqtSignal(dict)
    status_signal = pyqtSignal(FitsgenStatus)
    last_processed_obsid_signal = pyqtSignal(str)

    def __init__(self):
        """ Initialisation of a monitoring worker for the FITS generation.

        This monitoring worker will listen on the monitoring port of the FITS generation process.
        """

        super(FilenamesMonitoringWorker, self).__init__()

        # When new monitorig information comes in, these variables will contain the previous values for the filenames
        # (HDF5 and FITS) and status of the FITS generation process.  Once we have checked whether changes have occurred
        # since the last time monitoring information was received, these values will be overwritten by the new ones.

        self.hdf5_filename = None
        self.fits_filename = None
        self.fitsgen_status = None
        self.last_processed_obsid = None

        self.active = False

        self.monitoring_socket = None
        self.monitoring_timeout = 0.5  # [s]
        self.commanding_address = None
        self.is_socket_connected = False

        self.connect_socket()

    def connect_socket(self):
        """ Create a socket and connect to the monitoring port."""

        try:

            # Ctrl settings:
            #   - transport protocol
            #   - hostname
            #   - monitoring port (to ask for process information)

            transport = CTRL_SETTINGS.PROTOCOL
            hostname = CTRL_SETTINGS.HOSTNAME
            monitoring_port = CTRL_SETTINGS.MONITORING_PORT

            # Create a socket and connect to the monitoring port

            monitoring_address = connect_address(transport, hostname, monitoring_port)
            self.monitoring_socket = zmq.Context().socket(zmq.SUB)
            self.monitoring_socket.connect(monitoring_address)
            self.monitoring_socket.setsockopt_string(zmq.SUBSCRIBE, "")

            self.is_socket_connected = True

        except AttributeError as exc:
            print(exc)
            self.is_socket_connected = False

    def stop(self):
        """ Stop the monitoring worker.

        The monitoring socket is disconnected from the monitoring port and is then closed immediately.
        """

        self.is_socket_connected = False
        self.monitoring_socket.close()

    def start_process(self):
        """ Start listening on the monitoring port."""

        self.run()

    @pyqtSlot()
    def run(self):
        """ Keep on listening on the monitoring port of the FITS generation process."""

        self.active = True

        while self.is_socket_connected and self.active:

            try:

                socket_list, _, _ = zmq.select([self.monitoring_socket], [], [], timeout=5)

                # Monitoring information was received (before timeout)

                if self.monitoring_socket in socket_list:

                    pickle_string = self.monitoring_socket.recv()
                    monitoring_info = pickle.loads(pickle_string)

                    current_hdf5_filename = monitoring_info["hdf5"]
                    current_fits_filename = monitoring_info["fits"]
                    current_last_processed_obsid = monitoring_info["last obsid (being) processed"]

                    if current_hdf5_filename != self.hdf5_filename or current_fits_filename != self.fits_filename:

                        self.hdf5_filename = current_hdf5_filename
                        self.fits_filename = current_fits_filename

                        self.filenames_signal.emit(monitoring_info)

                    current_fitsgen_status = (FitsgenStatus.PROCESSING if current_hdf5_filename
                                              else FitsgenStatus.IDLE)

                    if self.fitsgen_status != current_fitsgen_status:
                        self.fitsgen_status = current_fitsgen_status
                        self.status_signal.emit(current_fitsgen_status)

                    if self.last_processed_obsid != current_last_processed_obsid:
                        self.last_processed_obsid = current_last_processed_obsid
                        self.last_processed_obsid_signal.emit(current_last_processed_obsid)

                # Timeout occurred

                else:
                    self.fitsgen_status = FitsgenStatus.DOWN
                    self.status_signal.emit(FitsgenStatus.DOWN)

            except zmq.ZMQError:
                pass


class FitsgenUIView(QMainWindow):

    def __init__(self):
        """ Open a window and initialise the GUI.

        The following information is shown:
            - Status of the FITS generation process;
            - Name of the HDF5 file currently being processed;
            - Name of the FITS file currently being created.
        """

        super().__init__()

        self.setGeometry(300, 300, 500, 100)
        self.setWindowTitle("FITS generation UI")

        self.init_ui()

        self.filenames_monitoring_thread = QThread(self)
        self.filenames_monitoring_worker = FilenamesMonitoringWorker()
        self.filenames_monitoring_worker.moveToThread(self.filenames_monitoring_thread)
        self.filenames_monitoring_worker.filenames_signal.connect(self.on_filenames_change_signal)
        self.filenames_monitoring_worker.status_signal.connect(self.on_status_change_signal)
        self.filenames_monitoring_worker.last_processed_obsid_signal.connect(self.on_last_processed_obsid_change_signal)
        self.filenames_monitoring_thread.started.connect(self.filenames_monitoring_worker.start_process)
        self.filenames_monitoring_thread.start()

    def init_ui(self):

        # Creating the content

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        # self.create_toolbar()
        # self.create_statusbar()

        layout = QHBoxLayout()

        keyword_layout = QVBoxLayout()
        value_layout = QVBoxLayout()

        # Status

        self.inactive_pix = QPixmap()
        self.inactive_pix.load(str(get_resource(":/icons/led-red.svg"), ))
        self.inactive_pix = self.inactive_pix.scaledToWidth(20)
        self.inactive_tooltip = "FITS generation process is inactive"

        self.idle_pix = QPixmap()
        self.idle_pix.load(str(get_resource(":/icons/busy.svg"),))
        self.idle_pix = self.idle_pix.scaledToWidth(20)
        self.idle_tooltip = "Waiting for HDF5 files"

        self.processing_pix = QPixmap()
        self.processing_pix.load(str(get_resource(":/images/process-status.png"),))
        self.processing_pix = self.processing_pix.scaledToWidth(20)
        self.processing_tooltip = "Processing HDF5 files"

        self.status_pix = {
            FitsgenStatus.DOWN: self.inactive_pix,
            FitsgenStatus.IDLE: self.idle_pix,
            FitsgenStatus.PROCESSING: self.processing_pix
        }

        self.status_tooltip = {
            FitsgenStatus.DOWN: self.inactive_tooltip,
            FitsgenStatus.IDLE: self.idle_tooltip,
            FitsgenStatus.PROCESSING: self.processing_tooltip
        }

        self.status_icon = QLabel()
        self.status_icon.setPixmap(self.inactive_pix)
        self.status_icon.setStatusTip(self.inactive_tooltip)

        # Filenames

        self.hdf5_filename = QLabel("None")
        self.fits_filename = QLabel("None")

        # Last obsid (being) processed

        self.last_processed_obsid = QLabel("None")
        self.last_processed_obsid.setStatusTip("Do not remove this obsid, nor more recent ones!")

        keyword_layout.addWidget(QLabel("Status:"))
        keyword_layout.addWidget(QHLine())
        keyword_layout.addWidget(QLabel("HDF5 file currently being processed:"))
        keyword_layout.addWidget(QLabel("FITS file currently being created:"))
        keyword_layout.addWidget(QHLine())
        keyword_layout.addWidget(QLabel("Last obsid that was/is being processed:"))

        value_layout.addWidget(self.status_icon)
        value_layout.addWidget(QHLine())
        value_layout.addWidget(self.hdf5_filename)
        value_layout.addWidget(self.fits_filename)
        value_layout.addWidget(QHLine())
        value_layout.addWidget(self.last_processed_obsid)

        layout.addLayout(keyword_layout)
        layout.addLayout(value_layout)

        app_frame.setLayout(layout)

        self.setCentralWidget(app_frame)

        self.create_toolbar()
        self.create_statusbar()

    def create_toolbar(self):
        """ Create the toolbar.

        Buttons with the following functionality are foreseen:
            - Start/stop all EGSE device Control Servers in one go;
            - Start/stop all AEU Control Servers in one go:
            - Start/stop the FITS generation;
            - Start/stop the generation of FOV HK;
            - Start/stop the generation of N-FEE HK.
        """

        start_fitsgen_button = ToggleButton(name="Start the FITS generation process.",
                                            status_tip="Start the FITS generation process.",
                                            selected=get_resource(":/icons/fitsgen-start.svg"),
                                            not_selected=get_resource(":/icons/fitsgen-start.svg")
                                            )
        start_fitsgen_button.clicked.connect(self.start_fitsgen)

        stop_fitsgen_button = ToggleButton(name="Stop the FITS generation process.",
                                           status_tip="Stop the FITS generation process.",
                                           selected=get_resource(":/icons/fitsgen-stop.svg"),
                                           not_selected=get_resource(":/icons/fitsgen-stop.svg")
                                           )
        stop_fitsgen_button.clicked.connect(self.stop_fitsgen)

        self.toolbar = self.addToolBar("MainToolbar")
        self.toolbar.addWidget(start_fitsgen_button)
        self.toolbar.addWidget(stop_fitsgen_button)

        return self.toolbar

    def create_statusbar(self):
        """ Create the status bar."""

        self.statusBar().setStyleSheet("border: 0; background-color: #FFF8DC;")
        self.statusBar().setStyleSheet("QStatusBar::item {border: none;}")
        # self.statusBar().addPermanentWidget(VLine())

    def start_fitsgen(self):

        thread = threading.Thread(target=self._start_fitsgen)
        thread.daemon = True
        thread.start()

    def _start_fitsgen(self):

        fg = SubProcess("MyApp", [sys.executable, "-m", "egse.dpu.fitsgen", "start"])
        fg.execute(detach_from_parent=True)

    def stop_fitsgen(self):

        thread = threading.Thread(target=self._stop_fitsgen)
        thread.daemon = True
        thread.start()

    def _stop_fitsgen(self):

        fg = SubProcess("MyApp", [sys.executable, "-m", "egse.dpu.fitsgen", "stop"])
        fg.execute(detach_from_parent=True)

    def on_filenames_change_signal(self, filenames: dict):
        """ Update the UI if the filenames change.

        Args:
              - filenames: Dictionary with the HDF5 filename ("hdf5") and FITS filename ("fits")
        """

        self.hdf5_filename.setText(str(filenames.get("hdf5")) or "None")
        self.fits_filename.setText(str(filenames.get("fits")) or "None")

    def on_status_change_signal(self, status: FitsgenStatus):
        """ Update the UI when the status of the FITS generation process changes."""

        self.status_icon.setPixmap(self.status_pix.get(status))
        self.status_icon.show()
        self.status_icon.setStatusTip(self.status_tooltip.get(status))

        if status != FitsgenStatus.PROCESSING:
            self.hdf5_filename.setText("None")
            self.fits_filename.setText("None")

    def on_last_processed_obsid_change_signal(self, last_processed_obsid: str):

        if last_processed_obsid:
            self.last_processed_obsid.setText(last_processed_obsid)
        else:
            self.last_processed_obsid.setText("None")

    def closeEvent(self, close_event: QCloseEvent) -> None:
        """ Make sure that all threads are stopped when the GUI is closed.

        Args:
            - close_event: Close event received when the GUI is closed.
        """

        self.filenames_monitoring_worker.active = False

        self.filenames_monitoring_thread.quit()
        self.filenames_monitoring_thread.terminate()

        self.filenames_monitoring_thread.wait()

        
def main():
    """ Main method to launch the Process Manager GUI."""

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(get_resource(":/icons/fitsgen.svg"))))

    lock_file = QLockFile(str(Path("~/fitgen_ui.app.lock").expanduser()))

    if lock_file.tryLock(100):
        view = FitsgenUIView()
        view.show()

        return app.exec_()
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The FITS generation GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()

if __name__ == '__main__':
    sys.exit(main())
