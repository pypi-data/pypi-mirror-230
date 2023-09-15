"""This module defines widgets that are common to the DPU GUI and the HDF5 GUI."""
import logging
from datetime import datetime
from typing import Optional

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtGui
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from numpy import unravel_index

from egse.gui.buttons import ToolTouchButton
from egse.resource import get_resource
from egse.spw import DataPacket
from egse.state import GlobalState

LOGGER = logging.getLogger(__name__)


class ImageCreator1:

    def __init__(self, nr_lines: int, nr_columns: int):
        self.nr_lines = nr_lines
        self.nr_columns = nr_columns
        self.image_E = np.empty((0,), dtype=np.uint16)
        self.image_F = np.empty((0,), dtype=np.uint16)

        self.n_fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

    def add_data(self, data_packet: DataPacket):
        if data_packet.type.ccd_side == self.n_fee_side.E_SIDE:
            self.image_E = np.concatenate((self.image_E, data_packet.data_as_ndarray))
        else:
            self.image_F = np.concatenate((self.image_F, data_packet.data_as_ndarray))

    def get_image(self, side: int):
        if side == self.n_fee_side.E_SIDE:
            return self.image_E.reshape(self.nr_lines, self.nr_columns).T
        else:
            return self.image_F.reshape(self.nr_lines, self.nr_columns).T


class ImageCreator:
    def __init__(self, nr_lines: int, nr_columns: int):
        self.nr_lines = nr_lines
        self.nr_columns = nr_columns
        self.index_E = self.index_F = 0
        self.image_E = np.empty((nr_lines * nr_columns,), dtype=np.uint16)
        self.image_F = np.empty((nr_lines * nr_columns,), dtype=np.uint16)

        self.n_fee_side = GlobalState.setup.camera.fee.ccd_sides.enum


    def add_data(self, data_packet: DataPacket):
        data = data_packet.data_as_ndarray
        data_length = len(data)
        if data_packet.type.ccd_side == self.n_fee_side.E_SIDE:
            self.image_E[self.index_E:self.index_E+data_length] = data
            self.index_E += data_length
        else:
            self.image_F[self.index_F:self.index_F+data_length] = data
            self.index_F += data_length

    def get_image(self, side: int):
        if side == self.n_fee_side.LEFT_SIDE:
            return self.image_E.reshape(self.nr_lines, self.nr_columns).T
        else:
            return np.fliplr(self.image_F.reshape(self.nr_lines, self.nr_columns)).T


class ImageCreatorFullSize:
    MAX_NR_LINES = 4540
    MAX_NR_COLUMNS = 2295

    def __init__(self, v_start: int, v_end: int, h_end: int):
        # LOGGER.debug(f"{v_start=}, {v_end=}, {h_end=}, {id(self)=}")

        self.n_fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

        self.nr_lines = v_end - v_start + 1
        self.nr_columns = h_end + 1
        self.index_left = self.index_right = v_start * self.MAX_NR_COLUMNS
        # self.image_E = np.empty((self.MAX_NR_LINES * self.MAX_NR_COLUMNS,), dtype=np.uint16)
        # self.image_F = np.empty((self.MAX_NR_LINES * self.MAX_NR_COLUMNS,), dtype=np.uint16)
        self.image_left = np.full((self.MAX_NR_LINES * self.MAX_NR_COLUMNS,), fill_value=np.nan, dtype=np.uint16)
        self.image_right = np.full((self.MAX_NR_LINES * self.MAX_NR_COLUMNS,), fill_value=np.nan, dtype=np.uint16)

    def add_data(self, data_packet: DataPacket):
        data = data_packet.data_as_ndarray
        data_length = len(data)
        if data_packet.type.ccd_side == self.n_fee_side.LEFT_SIDE:
            self.image_left[self.index_left:self.index_left + data_length] = data
            self.index_left += data_length
        else:
            self.image_right[self.index_right:self.index_right + data_length] = data
            self.index_right += data_length

    def get_image(self, side: int):
        if side == self.n_fee_side.LEFT_SIDE:
            return self.image_left.reshape(self.MAX_NR_LINES, self.MAX_NR_COLUMNS).T
        else:
            return np.fliplr(self.image_right.reshape(self.MAX_NR_LINES, self.MAX_NR_COLUMNS)).T


class CCDImageWidget(QWidget):
    def __init__(self, *args, axisItems=None, **kwargs):
        super().__init__(*args, **kwargs)

        vbox = QVBoxLayout()
        self.image_view = CCDImageView(view=pg.PlotItem(axisItems=axisItems))
        self.image_view.ui.histogram.gradient.loadPreset('viridis')
        self.label = QLabel()

        vbox.addWidget(self.label)
        vbox.addWidget(self.image_view)

        vbox.setSpacing(5)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

        self.mouse_hover_update = pg.SignalProxy(self.image_view.scene.sigMouseMoved, rateLimit=60,
                                                 slot=self.mouse_moved)

    def getImageItem(self):
        return self.image_view.getImageItem()

    def getView(self):
        return self.image_view.getView()

    def clearImage(self):
        self.image_view.clear()

    def setImage(self, image_data, *args, **kwargs):
        try:
            self.image_view.setImage(image_data, *args, **kwargs)
        except (Exception, ) as exc:
            # An Exception will be raised when all values are NaN, i.e. when no image was taken
            LOGGER.warning(exc)

    def mouse_moved(self, event):
        pos = event[0]  ## using signal proxy turns original arguments into a tuple
        viewbox = self.image_view.getView().getViewBox()
        if viewbox.sceneBoundingRect().contains(pos):
            mousePoint = viewbox.mapSceneToView(pos)
            x = int(mousePoint.x())
            y = int(mousePoint.y())
            image = self.image_view.image
            try:
                flux = image[x, y] if x >= 0 and y >= 0 else None
            except (IndexError, TypeError):
                flux = None
            self.label.setText(f"{x=}, {y=}, {flux=}")
        else:
            self.label.clear()


class CCDImageView(pg.ImageView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui.menuBtn.hide()
        self.ui.roiBtn.hide()
        #self.ui.histogram.hide()
        self.getView().getViewBox().invertY(False)

        # Mark the end of the serial pre-scan area

        line = pg.InfiniteLine((25, 0), pen={'color': 'r', 'width': 1})
        self.addItem(line)

        # Mark the start of the serial over-scan area

        line = pg.InfiniteLine((25+2255, 0), pen={'color': 'r', 'width': 1})
        self.addItem(line)

        # Mark the start of the parallel over-scan

        line = pg.InfiniteLine((0, 4510), angle=0, pen={'color': 'r', 'width': 1})
        self.addItem(line)

    def set_range_to_brightest_pixel(self, width: int = 50, height: int = 50):
        if self.image is None:
            return
        img = self.image
        try:
            max_value_idx = unravel_index(np.nanargmax(img), img.shape)
            x, y = max_value_idx
            x_offset, y_offset = width // 2, height // 2
            self.view.vb.setXRange(x - x_offset, x + x_offset, padding=0)
            self.view.vb.setYRange(y - y_offset, y + y_offset, padding=0)
        except ValueError as exc:
            LOGGER.warning(exc)


class OffsetAxis(pg.AxisItem):
    """This axis item changes the tick mark strings with an offset."""
    def __init__(self, offset: float = 0.0):
        super().__init__(orientation='left')
        self.offset = offset

    def tickStrings(self, values, scale, spacing):
        values = [value + self.offset for value in values]
        return super().tickStrings(values, scale, spacing)


class NFEECCDWidget(QWidget):
    sig_maximize = pyqtSignal(int)

    def __init__(self, ccd_number: Optional[int], maximize: bool = True, *args, **kwargs):
        """

        Args:
            ccd_number: the CCD number as displayed [1-4] (the CGSE CCD number)
            maximize: if True, the maximize button is shown
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.n_fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

        self._ccd_number = ccd_number  # CGSE CCD number [1-4]
        self.ccd_label = QLabel(f"CCD #{self._ccd_number}")

        self.graph_left: CCDImageWidget = CCDImageWidget(axisItems={'left': OffsetAxis()})
        self.graph_right: CCDImageWidget = CCDImageWidget(axisItems={'left': OffsetAxis()})

        vbox_left = QVBoxLayout()
        vbox_right = QVBoxLayout()

        vbox_left.addWidget(self.graph_left)
        vbox_right.addWidget(self.graph_right)

        # We used ToolTouchButtons because the buttons are not located in a QToolBar and
        # otherwise the alignment will be messed up.

        self.maximize = ToolTouchButton(
            name="EXPAND-IMAGE_VIEW",
            width=25, height=25,
            status_tip="show the CCD image in a separate screen",
            selected=get_resource(":/icons/maximize.svg"),
        )
        self.maximize.clicked.connect(self.maximize_view)

        self.cleaning = ToolTouchButton(
            name="CLEAN-IMAGE_VIEW",
            width=25, height=25,
            status_tip="clear the CCD image",
            selected=get_resource(":/icons/sponge.svg"),
        )
        self.cleaning.clicked.connect(self.clear_image_data)

        self.zoom = ToolTouchButton(
            name="ZOOM_TO_BRIGHTEST_PIXEL",
            width=25, height=25,
            status_tip="zoom to the brightest pixel in each half of the CCD",
            selected=get_resource(":/icons/zoom-to-pixel-dark.svg"),
        )
        self.zoom.clicked.connect(self.zoom_to_brightest_pixel)

        # spacer widget to help with aligning the icons to the right,
        # it's equivalent to a stretch ona layout

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Struct is used to add some fixed spacing between the icons

        strut = QWidget()
        strut.setFixedSize(5, 35)

        header_hbox = QHBoxLayout()
        header_hbox.addWidget(self.ccd_label)
        header_hbox.addStretch()
        header_hbox.addWidget(self.zoom)
        header_hbox.addWidget(strut)
        header_hbox.addWidget(self.cleaning)
        if maximize:
            header_hbox.addWidget(strut)
            header_hbox.addWidget(self.maximize)
        header_hbox.addWidget(strut)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox_left)
        hbox.addLayout(vbox_right)

        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)

        vbox = QVBoxLayout()

        vbox.addLayout(header_hbox)
        vbox.addLayout(hbox)

        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

    def mark(self):
        """Mark the CCD number label in read. This usually means that CCD is the active CCD."""
        self.ccd_label.setStyleSheet("color: red;")

    def unmark(self):
        """Unmark the CCD number label, i.e. no css style is applied."""
        self.ccd_label.setStyleSheet("")

    @property
    def ccd_number(self):
        """Returns the CGSE CCD number [1-4]."""
        return self._ccd_number

    @ccd_number.setter
    def ccd_number(self, value: Optional[int]):
        """Sets the CGSE CCD number [1-4]. """
        if value is None:
            return
        self._ccd_number = value  # CGSE CCD number [1-4]
        self.ccd_label.setText(f"CCD #{value}")

    def maximize_view(self):
        self.sig_maximize.emit(self._ccd_number)

    def clear_image_data(self):
        if self.graph_left.image_view.image is not None:
            self.graph_left.image_view.clear()
            self.graph_left.image_view.autoRange()

        if self.graph_right.image_view.image is not None:
            self.graph_right.image_view.clear()
            self.graph_right.image_view.autoRange()

    def zoom_to_brightest_pixel(self):
        self.graph_left.image_view.set_range_to_brightest_pixel()
        self.graph_right.image_view.set_range_to_brightest_pixel()

    def show_image_data(self, side: int, image: Optional[np.ndarray]):

        graph_box = self.graph_right if side == self.n_fee_side.RIGHT_SIDE else self.graph_left

        if image is not None:
            graph_box.setImage(image, autoRange=False, autoLevels=True, levelMode='mono')


class NFEE4CCDWidget(QWidget):
    def __init__(self):
        super().__init__()

        # CCD numbering here is CGSE CCD number [1-4]

        self.ccd_1 = NFEECCDWidget(1, parent=self)
        self.ccd_2 = NFEECCDWidget(2, parent=self)
        self.ccd_3 = NFEECCDWidget(3, parent=self)
        self.ccd_4 = NFEECCDWidget(4, parent=self)

        self.ccd_1.sig_maximize.connect(self.maximize_view)
        self.ccd_2.sig_maximize.connect(self.maximize_view)
        self.ccd_3.sig_maximize.connect(self.maximize_view)
        self.ccd_4.sig_maximize.connect(self.maximize_view)

        self.ccds = [self.ccd_1, self.ccd_2, self.ccd_3, self.ccd_4]

        self.n_fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

        grid_layout = QGridLayout()

        grid_layout.addWidget(self.ccd_1, 0, 0)
        grid_layout.addWidget(self.ccd_2, 1, 0)
        grid_layout.addWidget(self.ccd_4, 0, 1)
        grid_layout.addWidget(self.ccd_3, 1, 1)

        self.setLayout(grid_layout)

        self.image_data = [
            [None, None], [None, None], [None, None], [None, None],
        ]

    def mark(self, ccd_idx: int):
        """ Set the label of the given CCD to red, the others to black.

        This indicates that the given CCD is active and the others are inactive.

        Args:
            - ccd_idx: Index of the active CCD.
        """
        for ccd_widget in self.ccds:
            ccd_widget.unmark()
        self.ccds[ccd_idx].mark()

    def unmark(self):
        """ Set the CCD labels to black to indicate they are inactive."""
        for ccd_widget in self.ccds:
            ccd_widget.unmark()

    def maximize_view(self, ccd_number: int):
        """
        Creates a new CCD Widget for the given CCD number in a separate window.

        Args:
            ccd_number: CGSE CCD number [1-4]
        """
        widget = NFEECCDWidget(ccd_number, maximize=False)
        layout = QHBoxLayout()
        layout.addWidget(widget)

        ccd_idx = ccd_number - 1

        if self.image_data[ccd_idx][self.n_fee_side.E_SIDE] is not None:
            widget.show_image_data(self.n_fee_side.E_SIDE, self.image_data[ccd_idx][self.n_fee_side.E_SIDE])
        if self.image_data[ccd_idx][self.n_fee_side.F_SIDE] is not None:
            widget.show_image_data(self.n_fee_side.F_SIDE, self.image_data[ccd_idx][self.n_fee_side.F_SIDE])

        self.frame = QFrame()
        self.frame.resize(QSize(800, 600))
        self.frame.setLayout(layout)
        self.frame.show()

    def clear_image_data(self):
        for ccd in self.ccds:
            ccd.clear_image_data()

    def show_ccd_image(self, ccd_number: int, ccd_side: int, image: np.ndarray):
        """
        Show the image data in the CCDImageView.

        Args:
            ccd_number: the CGSE CCD number [1-4]
            ccd_side: 1 = left side, 0 = right side
            image: Numpy array with the CCD image data

        """
        # LOGGER.debug(f"{ccd_number=}, {CCD_BIN_TO_ID[ccd_number]}, {ccd_side=}")

        self.image_data[ccd_number-1][ccd_side] = image
        self.ccds[ccd_number-1].show_image_data(ccd_side, image)


class NFEEStateWidget(QWidget):
    def __init__(self):
        super().__init__()

        states = {
            "N-FEE MODE": "ON MODE",
            "N-FEE CYCLE TIME": 25.0,
            "DUMP MODE": True,
            "INTERNAL SYNC": False,
            "External SYNC": True,
            "row start": 0,
            "row end": 4509,
            "col end": 2295,
            "readout order": [1, 2, 3, 4],
            "ccd_side": "BOTH",
        }
        vbox = QVBoxLayout()

        for name, value in states.items():
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(name))
            hbox.addWidget(QLabel(value))


class NFEEStateTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

        # Row colors empty by default.
        self._row_colors = {}

    def data(self, index, role):
        if role == Qt.DecorationRole:
            value = self._data[index.row()][index.column()]
            if isinstance(value, bool):
                if value:
                    return QtGui.QIcon("tick.png")

                return QtGui.QIcon("cross.png")

        if role == Qt.DisplayRole:
            value = self._data[index.row()][index.column()]
            if isinstance(value, datetime):
                return value.strftime("%Y-%m-%d")

            return value

        if role == Qt.BackgroundRole:
            color = self._row_colors.get(index.row())  # returns None if not in.
            if color:
                return QtGui.QColor(color)

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def set_row_color(self, row, color):
        self._row_colors[row] = color
