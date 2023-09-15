"""
This module provides the View (V) in the MVC pattern of the FOV GUI application.
"""

import logging

from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QVBoxLayout

from egse.config import find_file
from egse.config import set_logger_levels
from egse.gui.focalplane import FocalPlaneWidgetWithSourcePosition
from egse.gui.mechanisms import BigRotationStageWidget
from egse.gui.mechanisms import FocusPositionWidget
from egse.gui.mechanisms import ScanMirrorAssemblyWidget
from egse.observer import Observable
from egse.settings import Settings
from egse.state import UnknownStateError

FOV_SETTINGS = Settings.load("Field-Of-View")

logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)
MODULE_LOGGER = logging.getLogger(__name__)

# Restrict the logging output for the following loggers.

# Note that, in production, the logging level for the different loggers can be changed with a
# service command `set_logging_level(logger_name, level)`.

logger_levels = [
    ("matplotlib", logging.WARNING),
    ("egse.config", logging.WARNING),
]

set_logger_levels(logger_levels)


FONT = QFont("Helvetica", 18)

COORDINATE_SYSTEMS = {
    "Focal plane": "Focal-plane coordinates [mm]",
    "Pixels": "Pixel coordinates",
    "Angles": "Angles"
}


class FOVUIView(QMainWindow, Observable):

    def __init__(self):

        """
        Open a window and initialiase the GUI.  The GUI is divided into two parts.  On the
        left there are three widgets, showing the current setting of the stages and the focus
        position.  On the right the focal plane is shown, together with a blue circle indicating
        the size of the field-of-view, and a red dot indicating the current position of the source.
        """

        super().__init__()

        self.setGeometry(300, 300, 1500, 1000)
        self.setWindowTitle("FOV Position GUI")

        self.init_ui()

    def init_ui(self):
        """ Initialisation of the GUI.

        The GUI is divided into two parts.  On the left there are three widgets, showing the current setting of the
        stages and the focus position. On the right the focal plane is shown, together with a blue circle indicating the
        size of the field-of-view, and a red dot indicating the current position of the source.
        """

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        # Toolbar

        self.create_toolbar()

        hbox = QHBoxLayout()

        # Mechanisms

        mechanisms_frame = QFrame()
        mechanisms_frame.setObjectName("Mechanisms")

        vbox_left = QGridLayout()
        vbox_left.addWidget(self.create_sma_widget())
        vbox_left.addWidget(self.create_big_rotation_stage_widget())
        vbox_left.addWidget(self.create_focus_position_widget())

        mechanisms_frame.setLayout(vbox_left)

        # FOV

        fpa_frame = QFrame()
        fpa_frame.setObjectName("FOV")

        vbox_right = QVBoxLayout()
        vbox_right.addWidget(self.create_focal_plane_widget())

        # Current source position

        self.source_position_text = QLabel()        # "Current source position"
        self.source_position_text.setFont(FONT)
        vbox_right.addWidget(self.source_position_text)

        self.source_position_angles_text = QLabel()        # (theta, phi)
        self.source_position_angles_text.setIndent(50)
        self.source_position_angles_text.setFont(FONT)
        self.source_position_angles_text.setToolTip(
            "Gnomonic distance to the optical axis " + u"\u03B8" + " = 90" + u"\u00B0" + " - 2" + u"\u03B1" +
            " and in-field angle " + u"\u03C6")
        vbox_right.addWidget(self.source_position_angles_text)

        self.source_position_pixels_text = QLabel()        # (row, column)
        self.source_position_pixels_text.setIndent(50)
        self.source_position_pixels_text.setFont(FONT)
        self.source_position_pixels_text.setToolTip(
            "Pixel coordinates on specified CCD")
        vbox_right.addWidget(self.source_position_pixels_text)

        self.source_position_mm_text = QLabel()            # (xFP, yFP)
        self.source_position_mm_text.setIndent(50)
        self.source_position_mm_text.setFont(FONT)
        self.source_position_mm_text.setToolTip("Focal-plane coordinates")
        vbox_right.addWidget(self.source_position_mm_text)

        fpa_frame.setLayout(vbox_right)

        # Putting everything in place

        hbox.addWidget(mechanisms_frame)
        hbox.addWidget(fpa_frame)

        app_frame.setLayout(hbox)

        self.setCentralWidget(app_frame)

    #########
    # Toolbar
    #########

    def create_toolbar(self):
        """ Create toolbar.

        Two buttons are foreseen: one for reconnect with the hexapod and one to the stages.
        """

        self.connected_pix = QPixmap(
            str(find_file("connected-100.png", in_dir="images"))).scaledToHeight(30, 1)
        self.disconnected_pix = QPixmap(
            str(find_file("disconnected-100.png", in_dir="images"))).scaledToHeight(30, 1)

        self.reconnect_icon_hexapod = QLabel()
        self.reconnect_icon_hexapod.setPixmap(self.connected_pix)

        self.reconnect_icon_stages = QLabel()
        self.reconnect_icon_stages.setPixmap(self.connected_pix)

        # Putting everything in place

        self.toolbar = self.addToolBar('MainToolbar')

        hexapod_label = QLabel("Hexapod")
        hexapod_label.setFont(FONT)
        self.toolbar.addWidget(hexapod_label)
        self.reconnect_icon_hexapod.setToolTip(
            "Connection status of the hexapod")
        self.toolbar.addWidget(self.reconnect_icon_hexapod)
        self.toolbar.addSeparator()

        stages_label = QLabel("Stages")
        stages_label.setFont(FONT)
        self.toolbar.addWidget(stages_label)
        self.reconnect_icon_stages.setToolTip(
            "Connection status of the stages")
        self.toolbar.addWidget(self.reconnect_icon_stages)
        self.toolbar.addSeparator()

        return self.toolbar

    #########
    # Widgets
    #########

    def create_sma_widget(self):
        """ Create widget showing the setting of the scan mirror assembly."""

        self.sma = ScanMirrorAssemblyWidget()
        return self.sma

    def create_big_rotation_stage_widget(self):
        """ Create widget showing the setting of the big rotation stage."""

        self.big_rotation_stage = BigRotationStageWidget()
        return self.big_rotation_stage

    def create_focus_position_widget(self):
        """ Create widget showing the focus position."""

        self.focus_position = FocusPositionWidget()
        return self.focus_position

    def create_focal_plane_widget(self):
        """ Create widget showing the position of the source in the focal plane."""

        self.focal_plane = FocalPlaneWidgetWithSourcePosition()
        return self.focal_plane

    ##########
    # Updating
    ##########

    def update_sma(self, distance, angle):
        """ Update the shown configuration of the scan mirror assembly.

        The orientation of the scan mirror must be changed, and the labels showing the distance from the scan
        mirror to the optical axis (along the translation stage) and the orientation angle of the scan mirror must be
        updated.

        :param distance: Distance between the scan mirror and the optical axis (along the translation stage) for the new
                         configuration of the scan mirror assembly [mm].

        :param angle: Orientation angle of the scan mirror [degrees].
        """

        self.sma.update_plot(distance, angle)

    def update_big_rotation_stage(self, angle):
        """ Update the shown configuration of the big rotation stage.

        The orientation of GL_ROT w.r.t. GL_FIX must be set to the given angle.

        :param angle: Rotation angle for the new configuration of the big rotation stage [degrees].
        """

        self.big_rotation_stage.update(angle)

    def update_focus_position(self, focus_position):
        """ Update the shown focus position.

        :param focus_position: New focus position [mm].
        """

        self.focus_position.update_plot(focus_position)

    def update_source_position(self, position):

        """ Update the position of the source in the focal plane to the given postion (x, y).

        The red dot must move on the focal plane (movement may not be visible) and the text label with the focal-plane
        coordinates must be updated.

        :param position: Dictionary with the following entries:

            - "angles": tuple with the field angles (theta, phi) [degrees];
            - "pixels": tuple with the pixel coordinates (row, column) [pixels] and CCD code;
            - "mm": tuple with the focal-plane coordinates (x, y) [mm].
        """

        (theta, phi) = position["angles"]
        (row, column, ccd_code) = position["pixels"]
        (x_fp, y_fp) = position["mm"]

        # Update the red dot in the plot

        self.focal_plane.update_source_position(x_fp, y_fp)

        # Update the text label

        if abs(x_fp) > FOV_SETTINGS.RADIUS_MM or abs(y_fp) > FOV_SETTINGS.RADIUS_MM:

            MODULE_LOGGER.debug("Current source position: outside FOV")
            self.source_position_text.setText(
                "Current source position: outside FOV")
            self.source_position_angles_text.setText("")
            self.source_position_pixels_text.setText("")
            self.source_position_mm_text.setText("")

        else:

            self.source_position_text.setText("Current source position:")
            self.source_position_angles_text.setText(
                u"\u2022" + "(" + u"\u03B8" + ", " + u"\u03C6" + ") [" + u"\u00B0" + "] = ({:.2f}, {:.2f})".format(theta, phi))

            if ccd_code is None:

                self.source_position_pixels_text.setText(
                    u"\u2022" + " source doesn't fall on any CCD")

            else:

                self.source_position_pixels_text.setText(
                    u"\u2022" + "(x<sub>CCD</sub>, y<sub>CCD</sub>) [pixels] = ({:.2f}, {:.2f}) on CCD ".format(column, row) + str(ccd_code))

            self.source_position_mm_text.setText(
                u"\u2022" + "(x<sub>FP</sub>, y<sub>FP</sub>) [mm] = ({:.2f}, {:.2f})".format(x_fp, y_fp))

    ##############
    # Connectivity
    ##############

    def set_connection_state_hexapod(self, state):
        """ Sets the connection state for the Symétrie Hexapod.

        :param state: Connectivity state to use for the Symétrie Hexapod.
        """

        if state == "connected":

            self.reconnect_icon_hexapod.setPixmap(self.connected_pix)

        elif state == "disconnected":

            self.reconnect_icon_hexapod.setPixmap(self.disconnected_pix)

        else:

            raise UnknownStateError(
                f"Unknown State ({state}) for the hexapod, expected 'connected' or 'disconnected'.")

    def set_connection_state_stages(self, state):
        """ Sets the connection state for the Huber stages.

        :param state: Connectivity state to use for the Huber stages.
        """

        if state == "connected":

            self.reconnect_icon_stages.setPixmap(self.connected_pix)

        elif state == "disconnected":

            self.reconnect_icon_stages.setPixmap(self.disconnected_pix)

        else:

            raise UnknownStateError(f"Unknown State ({state}) for the stages, expected 'connected' or 'disconnected'.")
