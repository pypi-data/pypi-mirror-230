"""
This module provides all the code to generate the main GUI and the GUI components
used by the HDF5 Viewer.
"""
import logging
from pathlib import Path

import h5py
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QTableView
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from egse.bits import humanize_bytes
from egse.dpu.ccd_ui import NFEECCDWidget
from egse.dpu.hk_ui import NFEEHousekeepingWidget
from egse.resource import get_resource
from egse.spw import DataPacket

MODULE_LOGGER = logging.getLogger(__name__)


class MainWindowGUI:
    def setup_gui(self, main_window: QMainWindow):
        """
        Creates the widgets in the main window.

        This method creates the following widgets that are accessible from the main window:

        * tree_view (QTreeView): visualises a tree structure view of the HDF5 file
        * table_view (QTableView): visualise a table
        * data_view (QStackedLayout): a widget that contains different views
        * graph_box (QtGraph ImageView): visualise a CCD image
        * status_bar (QStatusBar): the status bar of the main window

        Args:
            main_window (QMainWindow): the main window of the application
        """
        main_window.setWindowTitle("N-FEE Data Inspector")
        main_window.setObjectName("main_window")
        main_window.resize(1400, 800)

        splitter = QSplitter()
        splitter.setContentsMargins(0, 0, 0, 0)

        self.data_box = QSplitter(Qt.Vertical, splitter)
        self.data_box.setMinimumWidth(300)
        self.data_box.setContentsMargins(5, 5, 5, 5)

        self.tree_view = QTreeView(self.data_box)

        self.details_view = QTabWidget(self.data_box)
        self.details_view.setTabsClosable(False)
        self.details_view.setMovable(False)
        self.details_view.setDocumentMode(True)
        self.details_view.setElideMode(Qt.ElideRight)
        self.details_view.setUsesScrollButtons(True)

        self.properties = QTableView()
        self.attributes = QTableView()
        self.packet_header = QTableView()

        self.details_view.addTab(self.properties, "Properties")
        self.details_view.addTab(self.attributes, "Attributes")
        self.details_view.addTab(self.packet_header, "Packet Header")

        self.text_box: QTextEdit = QTextEdit()
        self.text_box.setReadOnly(True)
        self.text_box.setFont(QFont("Courier New"))
        self.text_box.setLineWrapMode(QTextEdit.NoWrap)

        self.table_view = QTableView()

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterKeyColumn(-1)  # Search all columns
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self.table_view.setModel(self.proxy_model)

        self.searchbar = QLineEdit()

        # You can choose the type of search by connecting to a different slot here.
        # see https://doc.qt.io/qt-5/qsortfilterproxymodel.html#public-slots

        self.searchbar.textChanged.connect(self.proxy_model.setFilterRegExp)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 10, 10, 0)

        layout.addWidget(self.searchbar)
        layout.addWidget(self.table_view)

        self.table_box = QWidget()
        self.table_box.setLayout(layout)

        self.hk_box = NFEEHousekeepingWidget()

        self.graph_box = NFEECCDWidget(ccd_number=None, maximize=False)

        self.data_view: QStackedWidget = QStackedWidget(splitter)
        self.data_view.addWidget(self.text_box)
        self.data_view.addWidget(self.table_box)
        self.data_view.addWidget(self.hk_box)
        self.data_view.addWidget(self.graph_box)
        self.data_view.setCurrentIndex(0)

        scroll = QScrollArea()
        scroll.setObjectName("scroll")
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(True)

        main_window.setCentralWidget(splitter)

        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(36, 36))
        main_window.addToolBar(toolbar)

        self.open_doc_action = QAction(QIcon(str(get_resource(":/icons/open-document-hdf5.png"))),
                                       "Open HDF5 file...", main_window)
        self.open_doc_action.setStatusTip("Open a new HDF5 file...")
        toolbar.addAction(self.open_doc_action)

        self.status_bar = QStatusBar(main_window)
        main_window.setStatusBar(self.status_bar)


class PropertiesModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._header = ["Name", "Value"]
        self._data = []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data[index.row()][index.column()]
            try:
                return str(value)
            except (Exception,) as exc:
                return str(exc)

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._header[section])

            if orientation == Qt.Vertical:
                return None


class FilePropertiesModel(PropertiesModel):
    def __init__(self, data: h5py.File):
        """
        Args:
            data: h5py.File
        """
        super().__init__()
        self._data = [
            ["Name", data.name],
            ["Path", data.filename],
            ["Size", humanize_bytes(Path(data.filename).stat().st_size, precision=0)]
        ]


class GroupPropertiesModel(PropertiesModel):
    def __init__(self, data: h5py.Group):
        """
        Args:
            data: h5py.Group
        """
        super().__init__()
        self._data = [
            ["Name", data.name],
            ["Id", data.id],
            ["Nr. items", len(data.items())],
        ]


class DatasetPropertiesModel(PropertiesModel):
    def __init__(self, data: h5py.Dataset):
        """
        Args:
            data: h5py.Dataset
        """
        super().__init__()
        self._data = [
            ["Name", data.name],
            ["Id", data.id],
            ["Shape", data.shape],
            ["Type", data.dtype],
            ["Chunks", data.chunks],
            ["Nr. dimensions", data.ndim],
            ["Size", humanize_bytes(data.size)],
            ["Nr. bytes", humanize_bytes(data.nbytes)]
        ]


class AttributesModel(QAbstractTableModel):
    def __init__(self, data):
        """
        Args:
            data: h5py.File
        """
        super().__init__()
        h5_file: h5py.File = data
        self._header = ["Name", "Value"]
        self._data = [[k, str(v)] for k, v in data.attrs.items()]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._header[section])

            if orientation == Qt.Vertical:
                return None


class DataPacketHeaderModel(QAbstractTableModel):
    def __init__(self, data: DataPacket):
        """
        Args:
            data (DataPacket): SpaceWire data packet
        """
        super().__init__()
        self._header = ["Name", "Value"]
        packet_header = data.header
        self._data = [[k, str(v)] for k, v in packet_header.as_dict().items()]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._header[section])

            if orientation == Qt.Vertical:
                return None
