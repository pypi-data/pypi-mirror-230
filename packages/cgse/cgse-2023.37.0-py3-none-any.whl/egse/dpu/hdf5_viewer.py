"""
A simple GUI application to visualise the content of an HDF5 file that contains N-FEE SpceWire data.
"""
# The original attempt was to use the TreeModel dynamically, but that didn't work and I finally
# found the reason in this StackOverflow topic:
#
# https://stackoverflow.com/questions/22713374/
#
# My solution to this problem was to save the internal_pointers in a set() because then they would
# not be duplicated, but that didn't work out. I then saved them in a list, this version was
# working, but very slow and the _internal_pointers grow indefinitely. My next try was to use a
# dictionary and create / retrieve the internal pointers. That work fine and is already faster, but
# it is not an elegant solution.
#
# The current implementation is based on the Simple Tree Model Example from the Qt documentation:
#
# https://doc.qt.io/qt-5/qtwidgets-itemviews-simpletreemodel-example.html#treemodel-class-definition
#
# The model in the example builds a complete fixed tree structure from the input data. I tried to
# optimize that by updating the tree structure whenever the user chooses to expand the nodes in
# the tree. The trick I used is to define a new role ExpandableRole and assign that role to Groups.
#
# Although I really want to stick to PEP8 for naming methods, functions and variable, I also wanted
# to stick to the Qt naming convention. For classes and methods that are in the realm of Qt I stick
# to their convention, this is the case for TreeModel, all other naming follows PEP8.
#
# TODO: data and headerData shall return a QVariant object. Is this needed for Python?

import logging
import sys
from pathlib import Path
from typing import Optional
from typing import Tuple

import h5py
import numpy as np
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QRunnable
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal as QSignal
from PyQt5.QtCore import pyqtSlot as QSlot
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QProgressBar
from rich.console import Console

from egse.dpu.ccd_ui import ImageCreatorFullSize
from egse.dpu.hdf5_model import HDF5Item
from egse.dpu.hdf5_model import HDF5Model
from egse.dpu.hdf5_model import RegisterTableModel
from egse.dpu.hdf5_ui import AttributesModel
from egse.dpu.hdf5_ui import DataPacketHeaderModel
from egse.dpu.hdf5_ui import DatasetPropertiesModel
from egse.dpu.hdf5_ui import FilePropertiesModel
from egse.dpu.hdf5_ui import GroupPropertiesModel
from egse.dpu.hdf5_ui import MainWindowGUI
from egse.dpu.hdf5_ui import PropertiesModel
from egse.exceptions import InternalError
from egse.fee.nfee import HousekeepingData
from egse.reg import RegisterMap
from egse.setup import SetupError
from egse.spw import DataPacket
from egse.spw import HousekeepingPacket
from egse.spw import SpaceWirePacket
from egse.state import GlobalState

MODULE_LOGGER = logging.getLogger(__name__)


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    * progress (int): progress complete,from 0-100
    * finished (no data): the worker is finished
    * result (object): the result from the Worker run() method, e.g.
        * a 2D Numpy array with the image data
    * error (tuple): exception type, value, traceback.format_exc()
    """

    progress = QSignal(int)
    result = QSignal(tuple)
    finished = QSignal()
    error = QSignal(tuple)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handle worker thread setup, signals
    and wrap-up.
    """

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback for signals to the kwargs, that way the function
        # has access to the signals of the worker. The signature of the
        # function needs to take args and kwargs into account.

        kwargs["signals"] = self.signals

    @QSlot()
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
        except (Exception, ) as exc:
            exc_type, value, tb = sys.exc_info()
            self.signals.error.emit((exc_type, value, tb))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class MainWindow(QMainWindow, MainWindowGUI):
    def __init__(self):
        super().__init__()

        self.n_fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

        # Setup the complete GUI

        self.setup_gui(self)

        # Add triggers / signals to the different views

        self.tree_view.clicked.connect(self.on_clicked)
        self.table_view.clicked.connect(self.on_cell_clicked)

        self.open_doc_action.triggered.connect(self.on_open_doc_clicked)

        self.reg_model = RegisterTableModel(RegisterMap())

        if len(sys.argv) > 0:
            filename = sys.argv[-1]
            self.load_hdf5_file(Path(filename))

        self.thread_pool = QThreadPool()

        self.counter = 0

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)

    def on_open_doc_clicked(self, *args, **kwargs):

        filename = QFileDialog.getOpenFileName(
            self, "Open a HDF5 file", filter="HDF5 Files (*.hdf5 *.h5)")
        filename = Path(filename[0])

        self.load_hdf5_file(filename)

    def load_hdf5_file(self, filename: Path):
        if filename.exists():
            try:
                hdf_file = h5py.File(filename, mode='r', locking=False)
                h5_model = HDF5Model(hdf_file)
            except OSError:
                self.status_bar.showMessage(f"OSError: could not open file {filename.name}", 5000)
                return

            self.tree_view.setModel(h5_model)
            self.tree_view.expanded.connect(h5_model.update_model_data)

            self.properties.setModel(FilePropertiesModel(hdf_file))

    def on_cell_clicked(self, index: QModelIndex, *args, **kwargs):
        self.proxy_model.sourceModel().toggleDisplayRole(index)

    def on_clicked(self, index: QModelIndex, *args, **kwargs):
        item: HDF5Item = index.internalPointer()
        hdf_item = item.get_item()

        self.packet_header.setModel(None)

        if len(hdf_item.attrs):
            self.attributes.setModel(AttributesModel(hdf_item))
        else:
            self.attributes.setModel(None)

        if isinstance(hdf_item, h5py.Group):
            self.properties.setModel(GroupPropertiesModel(hdf_item))
        elif isinstance(hdf_item, h5py.Dataset):
            self.properties.setModel(DatasetPropertiesModel(hdf_item))
        else:
            self.properties.setModel(PropertiesModel())

        if isinstance(hdf_item, h5py.Dataset):
            if "register" in hdf_item.name:
                reg_map = RegisterMap("N-FEE", memory_map=hdf_item[()])
                self.reg_model.setRegisterMap(reg_map)
                self.proxy_model.setSourceModel(self.reg_model)
                self.data_view.setCurrentWidget(self.table_box)
                self.table_view.resizeColumnsToContents()
                self.proxy_model.layoutChanged.emit()
            elif "hk_data" in hdf_item.name:
                packet = HousekeepingData(hdf_item[()])
                self.display_hk_data_text(packet)
            elif "hk" in hdf_item.name:
                packet = HousekeepingPacket(hdf_item[()])
                self.display_hk_packet_view(packet)
            elif "timecode" in hdf_item.name:
                data = hdf_item[()]
                self.text_box.setText(str(data))
                self.data_view.setCurrentWidget(self.text_box)
            else:
                data = hdf_item[()]
                if DataPacket.is_data_packet(data):
                    self.packet_header.setModel(DataPacketHeaderModel(DataPacket(data)))
                    self.packet_header.resizeColumnsToContents()
                self.text_box.setText(ndarray_to_str(data))
                self.data_view.setCurrentWidget(self.text_box)
        elif isinstance(hdf_item, h5py.Group):
            if "data" in hdf_item:
                self.handle_image_data(hdf_item)

    def display_hk_data_text(self, hk_data: HousekeepingData):

        console = Console(width=120, force_terminal=False, force_jupyter=False)
        with console.capture() as capture:
            console.print(hk_data)
        text = capture.get()
        self.text_box.setText(text)
        self.data_view.setCurrentWidget(self.text_box)

    def display_hk_packet_view(self, packet: HousekeepingPacket):
        hk_data = HousekeepingData(packet.data)

        fields = self.hk_box.spw_status.fields
        for par in fields:
            fields[par].setText(f"{hk_data[par]:8d}")

        fields = self.hk_box.tou_sense.fields
        for par in fields:
            x = f"TOU_SENSE_{par}"
            fields[par].setText(f"{hk_data[x]}")

        fields = self.hk_box.n_fee_voltages.fields
        for par in fields:
            fields[par].setText(f"{hk_data[par]:8d}")

        fields = self.hk_box.n_fee_temperatures.fields
        for par in fields:
            fields[par].setText(f"{hk_data[par]:8d}")

        fields = self.hk_box.ccd_voltages.fields
        for par in fields:
            fields[par].setText(f"{hk_data[par]:8d}")

        self.hk_box.spw_leds.update_leds(hk_data["spw_status"])

        self.hk_box.error_flags.update_flags(hk_data["error_flags"])

        self.data_view.setCurrentWidget(self.hk_box)

    def display_hk_packet_text(self, packet: HousekeepingPacket):
        hk_data = HousekeepingData(packet.data)

        console = Console(width=120, force_terminal=False, force_jupyter=False)
        with console.capture() as capture:
            console.print(hk_data)
        text = capture.get()
        self.text_box.setText(text)
        self.data_view.setCurrentWidget(self.text_box)

    def handle_image_data(self, hdf_item: h5py.Group):
        if "timecode" not in hdf_item:
            return None

        data_item = hdf_item["data"]

        if "v_start" not in data_item.attrs:
            reg_map = find_current_register_map(hdf_item)
            if not reg_map:
                return

            v_start = reg_map["v_start"]
            v_end = reg_map["v_end"]
            h_end = reg_map["h_end"]

        else:
            v_start = data_item.attrs["v_start"]
            v_end = data_item.attrs["v_end"]
            h_end = data_item.attrs["h_end"]

        # Create the Worker, any other args, kwargs are passed to the run function

        worker = Worker(
            create_image, data_item, v_start, v_end, h_end
        )
        worker.signals.result.connect(self.show_image_data)
        worker.signals.finished.connect(self.worker_finished)
        worker.signals.progress.connect(self.update_progress)

        # Execute the Worker run() method

        self.thread_pool.start(worker)

        self.timer.start()

        self.progress_label = QLabel(f"Generating image[{v_start}, {v_end}]")
        self.timer_label = QLabel("0s")
        self.progress = QProgressBar()
        self.status_bar.addWidget(self.progress_label)
        self.status_bar.addWidget(self.progress)
        self.status_bar.addWidget(self.timer_label)

    def recurring_timer(self):
        self.counter += 1
        self.timer_label.setText(f"{self.counter}s")

    def worker_finished(self):
        self.status_bar.removeWidget(self.progress)
        self.status_bar.removeWidget(self.progress_label)
        self.status_bar.removeWidget(self.timer_label)
        self.status_bar.show()
        self.timer.stop()
        self.counter = 0

    def update_progress(self, progress):
        self.progress.setValue(progress)

    def show_image_data(self, data: Tuple):
        ccd_nr, image_left, image_right = data
        # MODULE_LOGGER.info(f"{ccd_nr=}, {image_e.shape=}, {image_f.shape}")
        self.graph_box.ccd_number = ccd_nr
        if image_left is not None and sum(image_left.shape) > 0:
            self.graph_box.show_image_data(self.n_fee_side.LEFT_SIDE, image_left)
            self.data_view.setCurrentWidget(self.graph_box)
        if image_right is not None and sum(image_right.shape) > 0:
            self.graph_box.show_image_data(self.n_fee_side.RIGHT_SIDE, image_right)
            self.data_view.setCurrentWidget(self.graph_box)


def ndarray_to_str(data: np.ndarray):

    if not isinstance(data, np.ndarray):
        return str(data)

    packet: DataPacket = SpaceWirePacket.create_packet(data)
    data = packet.data_as_ndarray
    data_as_bytes = packet.data

    t = data.dtype
    w = data.shape[0]

    sdata = f"{w=} {t=}\n"
    sdata += f"{packet.type=!s}\n"

    # Represent the bytes object data, i.e. the original data coming from the SpaceWire

    sdata += "data_as_bytes:   "
    sdata += ", ".join(f"{data_as_bytes[ix]:08b} {data_as_bytes[ix+1]:08b}" for ix in range(0, 66, 2))
    sdata += " ... "
    sdata += ", ".join(f"{data_as_bytes[ix]:08b} {data_as_bytes[ix+1]:08b}" for ix in range((w-40)*2, w*2, 2))
    sdata += "\n"

    # Represent the numpy array, first as integers, seconds as binary strings

    sdata += "data_as_ndarray: "
    sdata += ", ".join(f"{data[ix]:d}" for ix in range(33))
    sdata += " ... "
    sdata += ", ".join(f"{data[ix]:d}" for ix in range(w - 40, w))
    sdata += "\n"

    sdata += "data_as_ndarray: "
    sdata += ", ".join(f"{data[ix] >> 8 & 0b11111111:08b} {data[ix] & 0b11111111:08b}" for ix in range(33))
    sdata += " ... "
    sdata += ", ".join(f"{data[ix] >> 8 & 0b11111111:08b} {data[ix] & 0b11111111:08b}" for ix in range(w - 40, w))
    sdata += "\n"

    return sdata


# @profile(sort_by='cumulative', lines_to_print=10, strip_dirs=True)
def create_image(hdf_item: h5py.Group, v_start: int, v_end: int, h_end: int,
                 signals: WorkerSignals):

    n_fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

    # MODULE_LOGGER.info(f"Creating image: {v_start=}, {v_end=}")

    nr_lines = v_end - v_start + 1
    nr_columns = h_end + 1

    image = ImageCreatorFullSize(v_start, v_end, h_end)

    ccd_nr = None
    lines_count = 0
    data_group = hdf_item
    nr_data = len(data_group)

    # If v_end is larger than 4509 it means we have parallel overscan data

    last_packet = [2, 2] if v_end > 4509 else [1, 1]

    for data_count in sorted(data_group, key=int):
        data = data_group[data_count][()]

        if not isinstance(data, np.ndarray):
            raise InternalError('HDF5 data group should only contain numpy arrays.')

        data_packet = SpaceWirePacket.create_packet(data)
        data = data_packet.data_as_ndarray

        image.add_data(data_packet)

        signals.progress.emit(int(data_count) * 100 // nr_data)

    # MODULE_LOGGER.info(f"{lines_count=}, {nr_lines=}")
    # MODULE_LOGGER.info(f"{image_e.shape=}, {image_f.shape=}")
    # MODULE_LOGGER.info(f"{last_packet=}")

    image_left = image.get_image(n_fee_side.LEFT_SIDE).astype(float)
    image_right = image.get_image(n_fee_side.RIGHT_SIDE).astype(float)

    try:
        image_left[image_left == 0] = np.nan
        image_right[image_right == 0] = np.nan
    except (Exception, ) as exc:
        MODULE_LOGGER.error(exc)

    # MODULE_LOGGER.info(f"{image_e.shape=}, {image_f.shape=}")

    if nr_data:
        try:
            data_packet = SpaceWirePacket.create_packet(data_group["0"][()])
            ccd_nr = data_packet.header.type_as_object.ccd_number  # N-FEE CCD number [0-3]
            # MODULE_LOGGER.info(f"before {ccd_nr=}")
            try:
                ccd_nr = GlobalState.setup.camera.fee.ccd_numbering.CCD_BIN_TO_ID[ccd_nr]
            except AttributeError:
                raise SetupError("No entry in the setup for camera.fee.ccd_numbering.CCD_BIN_TO_ID")
            # MODULE_LOGGER.info(f"after  {ccd_nr=}")
        except (Exception, ) as exc:
            MODULE_LOGGER.error(exc)

    # MODULE_LOGGER.info(f"Return: {ccd_nr=}, {image_e.shape=}, {image_f.shape=}")

    return ccd_nr, image_left, image_right


def find_current_register_map(hdf_item: h5py.Group) -> Optional[RegisterMap]:
    # The current register map is the one with the valid values for the current data.
    # Current means, for the hdf_item that was passed into this function
    # The algorithm is not fail safe yet, what we would actually need is attributes
    # to the readout group: v_start, v_end, h_end
    parent = hdf_item.parent
    parent_path = Path(parent.name)

    if "register" in parent:
        path = str(parent_path / "register")
        reg_map = RegisterMap("N-FEE", memory_map=hdf_item[path][()])
        return reg_map

    try:
        name = Path(hdf_item.name).name
        readout_count = count = int(name)
    except ValueError:
        MODULE_LOGGER.warning(
            f"Corrupt HDF5 file? Expected readout count as group name, got {hdf_item.name}.")
        return None

    MODULE_LOGGER.info(f"Processing readout count {count}.")

    # Search for the last readout containing a register map

    while True:
        count -= 1
        name = str(count)
        if name not in parent:
            break
        item = parent[name]
        if "register" in item and "data" not in item:
            MODULE_LOGGER.info(f"Found register in {name}.")
            path = str(parent_path / name / "register")
            reg_map = RegisterMap("N-FEE", memory_map=hdf_item[path][()])
            return reg_map

    return None


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    rc = app.exec()

    return rc


if __name__ == "__main__":

    sys.exit(main())
