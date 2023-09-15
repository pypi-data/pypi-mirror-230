"""
This modules yields to widgets in which the focal plane is visualised.  The combobox
below the plot can be used to choose the coordinate system used in the plot: focal-plane
coordinates, pixel coordinates, and field angles.  A blue cirle denotes the edge of the
FOV.
"""
import logging
from math import atan
from math import degrees
from math import radians

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from egse.coordinates import ccd_to_focal_plane_coordinates
from egse.coordinates import focal_plane_coordinates_to_angles
from egse.gui.formatter import degree_formatter
from egse.settings import Settings
from egse.state import GlobalState

FONT = QFont("Helvetica", 18)

FOV_SETTINGS = Settings.load("Field-Of-View")
MODULE_LOGGER = logging.getLogger(__name__)

COORDINATE_SYSTEMS = {
    "Focal plane": "Focal-plane coordinates [mm]",
    "Pixels": "Pixel coordinates",
    "Angles": "Angles"
}

PIXEL_SIZE = CCD_SETTINGS = Settings.load("CCD").PIXEL_SIZE / 1000     # Pixel size [mm]
ZEROPOINT = Settings.load("CCD").ZEROPOINT          # CCD zeropoint (x, y) [mm]
NUM_ROWS = Settings.load("CCD").NUM_ROWS
NUM_COLUMNS = Settings.load("CCD").NUM_COLUMNS


class FocalPlane(FigureCanvas):

    """
    FigureCanvas showing the focal plane, with a blue circle indicating the field-of-view.
    The available coordinate systems are:
        - pixel coordinates [pixels],
        - focal-plane coordinates [mm],
        - and field angles [degrees].
    """

    def __init__(self, parent=None, dpi=100):

        """
        Initialisation of a plot of the focal plane, with a blue circle indicating the
        field-of-view.
        """
        self.fee_side = GlobalState.setup.camera.fee.ccd_sides.enum
        self.ccd_id = GlobalState.setup.camera.fee.ccd_numbering.CCD_ID

        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)

        FigureCanvas.__init__(self, self.figure)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def change_to_focal_plane_coordinates(self):

        """
        Preparation of the plot to show the source position in focal-plane coordinates:

            - clear the plot;
            - draw a blue circle, indicating the size of the field-of view;
            - configure the axes and grid lines;
            - draw the CCDs and their readout registers;
            - add the CCD codes.

        The draw() method should be called in the sub-classes.
        """

        self.coordinate_system = COORDINATE_SYSTEMS["Focal plane"]

        self.figure.delaxes(self.ax)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_aspect(1)

        # Circle indicating the size of the FOV [mm]

        self.circle = plt.Circle(
            (0, 0), FOV_SETTINGS.RADIUS_MM, color='b', fill=False, label="FOV", linewidth=1)
        self.ax.add_artist(self.circle)

        # Range

        limit = 85
        self.ax.set_xlim([-limit, limit])
        self.ax.set_ylim([-limit, limit])

        self.ax.set_xlabel("$x_{FP} [mm]$", fontsize=10)
        self.ax.xaxis.set_label_coords(1.085, 0.45)
        self.ax.set_ylabel("$y_{FP} [mm]$", fontsize=10, rotation=0)
        self.ax.yaxis.set_label_coords(0.47, 1.05)

        # Make sure the axes cross at the origin

        self.ax.axvline(x=0, color="k", linewidth=1)
        self.ax.axhline(y=0, color="k", linewidth=1)

        self.ax.spines['left'].set_position('center')
        self.ax.spines['bottom'].set_position('center')
        self.ax.spines['right'].set_color('none')
        self.ax.spines['top'].set_color('none')

        xmin, xmax = self.ax.get_xlim()
        ymin, ymax = self.ax.get_ylim()

        self.ax.arrow(xmin, 0, xmax-xmin+7, 0., fc='k', ec='k', lw=1,
                      head_width=3, head_length=5, overhang=0.3,
                      length_includes_head=True, clip_on=False)

        self.ax.arrow(0, ymin, 0., ymax-ymin+7, fc='k', ec='k', lw=1,
                      head_width=3, head_length=5, overhang=0.3,
                      length_includes_head=True, clip_on=False)

        # Readout registers

        self.ax.plot([-ZEROPOINT[0], ZEROPOINT[1]], [-ZEROPOINT[1], -
                                                     ZEROPOINT[1]], color="k", linewidth=3)   # Upper left CCD
        self.ax.plot([ZEROPOINT[1], ZEROPOINT[1]], [-ZEROPOINT[0],
                                                    ZEROPOINT[1]], color="k", linewidth=3)    # Lower left CCD
        self.ax.plot([ZEROPOINT[0], -ZEROPOINT[1]], [ZEROPOINT[1],
                                                     ZEROPOINT[1]], color="k", linewidth=3)   # Lower right CCD
        self.ax.plot([-ZEROPOINT[1], -ZEROPOINT[1]], [ZEROPOINT[0], -
                                                      ZEROPOINT[1]], color="k", linewidth=3)  # Upper right CCD

        # CCD middle

        self.ax.plot([ZEROPOINT[0] - NUM_COLUMNS / 2 * PIXEL_SIZE, ZEROPOINT[0] - NUM_COLUMNS / 2 * PIXEL_SIZE],
                     [-ZEROPOINT[0], ZEROPOINT[1]], color="k", linewidth=1,
                     linestyle="dotted")  # Upper left CCD
        self.ax.plot([-ZEROPOINT[1], ZEROPOINT[0]],
                     [ZEROPOINT[0] - NUM_COLUMNS / 2 * PIXEL_SIZE, ZEROPOINT[0] - NUM_COLUMNS / 2 * PIXEL_SIZE],
                     color="k", linewidth=1, linestyle="dotted")  # Lower left CCD
        self.ax.plot([-ZEROPOINT[0] + NUM_COLUMNS / 2 * PIXEL_SIZE, -ZEROPOINT[0] + NUM_COLUMNS / 2 * PIXEL_SIZE],
                     [-ZEROPOINT[1], ZEROPOINT[0]], color="k", linewidth=1,
                     linestyle="dotted")  # Lower right CCD
        self.ax.plot([-ZEROPOINT[0], ZEROPOINT[1]],
                     [-ZEROPOINT[0] + NUM_COLUMNS / 2 * PIXEL_SIZE, -ZEROPOINT[0] + NUM_COLUMNS / 2 * PIXEL_SIZE],
                     color="k", linewidth=1, linestyle="dotted")  # Upper right CCD

        # CCD codes

        self.ax.text(-80, 70, self.ccd_id[2])     # Upper left CCD
        self.ax.text(-80, -75, self.ccd_id[3])    # Lower left CCD
        self.ax.text(60, -75, self.ccd_id[0])     # Lower right CCD
        self.ax.text(60, 70, self.ccd_id[1])      # Upper right CCD

        self.ax.text(-30, 10, self.fee_side.LEFT_SIDE.name, rotation=180)       # Upper leftCCD, left side
        self.ax.text(-75, 10, self.fee_side.RIGHT_SIDE.name, rotation=180)      # Upper left CCD, right side
        self.ax.text(-20, -15, self.fee_side.LEFT_SIDE.name, rotation=-90)      # Lower left CCD, left side
        self.ax.text(-20, -75, self.fee_side.RIGHT_SIDE.name, rotation=-90)     # Lower left CCD, right side
        self.ax.text(10, -15, self.fee_side.LEFT_SIDE.name)                     # Lower right CCD, left side
        self.ax.text(50, -15, self.fee_side.RIGHT_SIDE.name)                    # Lower right CCD, right side
        self.ax.text(10, 10, self.fee_side.LEFT_SIDE.name, rotation=90)         # Upper right CCD, left side
        self.ax.text(10, 50, self.fee_side.RIGHT_SIDE.name, rotation=90)        # Upper right CCD, right side

        self.ax.plot([-ZEROPOINT[0], ZEROPOINT[1], ZEROPOINT[1], -ZEROPOINT[0], -ZEROPOINT[0]],
                     [ZEROPOINT[0], ZEROPOINT[0], -ZEROPOINT[1], -ZEROPOINT[1], ZEROPOINT[0]],
                     color="k", linewidth=1)  # Upper left CCD
        self.ax.plot([-ZEROPOINT[0], ZEROPOINT[1], ZEROPOINT[1], -ZEROPOINT[0], -ZEROPOINT[0]],
                     [-ZEROPOINT[0], - ZEROPOINT[0], ZEROPOINT[1], ZEROPOINT[1], -ZEROPOINT[0]],
                     color="k", linewidth=1)  # Lower left CCD
        self.ax.plot([-ZEROPOINT[1], ZEROPOINT[0], ZEROPOINT[0], -ZEROPOINT[1], -ZEROPOINT[1]],
                     [-ZEROPOINT[0], - ZEROPOINT[0], ZEROPOINT[1], ZEROPOINT[1], -ZEROPOINT[0]],
                     color="k", linewidth=1)  # Lower right CCD
        self.ax.plot([-ZEROPOINT[1], ZEROPOINT[0], ZEROPOINT[0], -ZEROPOINT[1], -ZEROPOINT[1]],
                     [ZEROPOINT[0], ZEROPOINT[0], -ZEROPOINT[1], -ZEROPOINT[1], ZEROPOINT[0]],
                     color="k", linewidth=1)  # Upper right CCD

        # Grid lines

        self.ax.grid(color="lightgray", linewidth=0.5)

        ticks = np.arange(-80, 90, 20)
        ticks = np.delete(ticks, 4)
        self.ax.set_xticks(ticks)
        self.ax.set_yticks(ticks)

    def change_to_pixel_coordinates(self):

        """
        Preparation of the plot to show the source position in pixel coordinates:

            - clear the plot;
            - draw a blue circle, indicating the size of the field-of view;
            - configure the axes and grid lines;
            - draw the CCDs and their readout registers;
            - add the CCD codes.

        The draw() method should be called in the sub-classes.
        """

        self.coordinate_system = COORDINATE_SYSTEMS["Pixels"]

        self.figure.delaxes(self.ax)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_aspect(1)

        # Circle indicating the size of the FOV [mm]

        self.circle = plt.Circle(
            (0, 0), FOV_SETTINGS.RADIUS_PIXELS, color='b', fill=False, label="FOV", linewidth=1)
        self.ax.add_artist(self.circle)

        # Range
        # If we do it like this, the circle will have the same size on screen when
        # switching between coordinate systems

        limit = 85 / PIXEL_SIZE
        self.ax.set_xlim([-limit, limit])
        self.ax.set_ylim([-limit, limit])

        self.ax.set_xlabel("$x_{CCD} [pixels]$", fontsize=10)
        self.ax.xaxis.set_label_coords(1.085, 0.45)
        self.ax.set_ylabel("$y_{CCD} [pixels]$", fontsize=10, rotation=0)
        self.ax.yaxis.set_label_coords(0.47, 1.05)

        # Make sure the axes cross at the origin

        self.ax.axvline(x=0, color="k", linewidth=1)
        self.ax.axhline(y=0, color="k", linewidth=1)

        self.ax.spines['left'].set_position('center')
        self.ax.spines['bottom'].set_position('center')
        self.ax.spines['right'].set_color('none')
        self.ax.spines['top'].set_color('none')

        xmin, xmax = self.ax.get_xlim()
        ymin, ymax = self.ax.get_ylim()

        self.ax.arrow(xmin, 0, xmax-xmin+7/PIXEL_SIZE, 0., fc='k', ec='k', lw=1,
                      head_width=3/PIXEL_SIZE, head_length=5/PIXEL_SIZE,
                      length_includes_head=True, clip_on=False)

        self.ax.arrow(0, ymin, 0., ymax-ymin+7/PIXEL_SIZE, fc='k', ec='k', lw=1,
                      head_width=3/PIXEL_SIZE, head_length=5/PIXEL_SIZE, overhang=0.3,
                      length_includes_head=True, clip_on=False)

        # Readout registers

        self.ax.plot([-ZEROPOINT[0] / PIXEL_SIZE, ZEROPOINT[1] / PIXEL_SIZE],
                     [-ZEROPOINT[1] / PIXEL_SIZE, -ZEROPOINT[1] / PIXEL_SIZE],
                     color="k", linewidth=3)  # Upper left CCD
        self.ax.plot([ZEROPOINT[1] / PIXEL_SIZE, ZEROPOINT[1] / PIXEL_SIZE],
                     [-ZEROPOINT[0] / PIXEL_SIZE, ZEROPOINT[1] / PIXEL_SIZE],
                     color="k", linewidth=3)    # Lower left CCD
        self.ax.plot([ZEROPOINT[0] / PIXEL_SIZE, -ZEROPOINT[1] / PIXEL_SIZE],
                     [ZEROPOINT[1] / PIXEL_SIZE, ZEROPOINT[1] / PIXEL_SIZE],
                     color="k", linewidth=3)    # Lower right CCD
        self.ax.plot([-ZEROPOINT[1] / PIXEL_SIZE, -ZEROPOINT[1] / PIXEL_SIZE],
                     [ZEROPOINT[0] / PIXEL_SIZE, -ZEROPOINT[1] / PIXEL_SIZE],
                     color="k", linewidth=3)  # Upper right CCD

        # CCD middle

        self.ax.plot([ZEROPOINT[0] / PIXEL_SIZE - NUM_COLUMNS / 2, ZEROPOINT[0] / PIXEL_SIZE - NUM_COLUMNS / 2],
                     [-ZEROPOINT[0] / PIXEL_SIZE, ZEROPOINT[1] / PIXEL_SIZE],
                     color="k", linewidth=1, linestyle="dotted")  # Upper left CCD
        self.ax.plot([-ZEROPOINT[1] / PIXEL_SIZE, ZEROPOINT[0] / PIXEL_SIZE],
                     [ZEROPOINT[0] / PIXEL_SIZE - NUM_COLUMNS / 2, ZEROPOINT[0] / PIXEL_SIZE - NUM_COLUMNS / 2],
                     color="k", linewidth=1, linestyle="dotted")  # Lower left CCD
        self.ax.plot([-ZEROPOINT[0] / PIXEL_SIZE + NUM_COLUMNS / 2, -ZEROPOINT[0] / PIXEL_SIZE + NUM_COLUMNS / 2],
                     [-ZEROPOINT[1] / PIXEL_SIZE, ZEROPOINT[0] / PIXEL_SIZE],
                     color="k", linewidth=1, linestyle="dotted")  # Lower right CCD
        self.ax.plot([-ZEROPOINT[0] / PIXEL_SIZE, ZEROPOINT[1] / PIXEL_SIZE],
                     [-ZEROPOINT[0] / PIXEL_SIZE + NUM_COLUMNS / 2, -ZEROPOINT[0] / PIXEL_SIZE + NUM_COLUMNS / 2],
                     color="k", linewidth=1, linestyle="dotted")  # Upper right CCD

        # CCD codes

        self.ax.text(-80 / PIXEL_SIZE, 70 / PIXEL_SIZE, self.ccd_id[2])     # Upper left CCD
        self.ax.text(-80 / PIXEL_SIZE, -75 / PIXEL_SIZE, self.ccd_id[3])    # Lower left CCD
        self.ax.text(60 / PIXEL_SIZE, -75 / PIXEL_SIZE, self.ccd_id[0])     # Lower right CCD
        self.ax.text(60 / PIXEL_SIZE, 70 / PIXEL_SIZE, self.ccd_id[1])      # Upper right CCD

        self.ax.text(-30 / PIXEL_SIZE, 10 / PIXEL_SIZE, self.fee_side.LEFT_SIDE.name, rotation=180)     # Upper left CCD, left side
        self.ax.text(-75 / PIXEL_SIZE, 10 / PIXEL_SIZE, self.fee_side.RIGHT_SIDE.name, rotation=180)    # Upper left CCD, right side
        self.ax.text(-20 / PIXEL_SIZE, -15 / PIXEL_SIZE, self.fee_side.LEFT_SIDE.name, rotation=-90)    # Lower left CCD, left side
        self.ax.text(-20 / PIXEL_SIZE, -75 / PIXEL_SIZE, self.fee_side.RIGHT_SIDE.name, rotation=-90)   # Lower left CCD, right side
        self.ax.text(10 / PIXEL_SIZE, -15 / PIXEL_SIZE, self.fee_side.LEFT_SIDE.name)   # Lower right CCD, left side
        self.ax.text(50 / PIXEL_SIZE, -15 / PIXEL_SIZE, self.fee_side.RIGHT_SIDE.name)  # Lower right CCD, right side
        self.ax.text(10 / PIXEL_SIZE, 10 / PIXEL_SIZE, self.fee_side.LEFT_SIDE.name, rotation=90)   # Upper right CCD, left side
        self.ax.text(10 / PIXEL_SIZE, 50 / PIXEL_SIZE, self.fee_side.RIGHT_SIDE.name, rotation=90)  # Upper right CCD, right side

        self.ax.plot([-ZEROPOINT[0] / PIXEL_SIZE, ZEROPOINT[1] / PIXEL_SIZE, ZEROPOINT[1] / PIXEL_SIZE, -ZEROPOINT[0] / PIXEL_SIZE, -ZEROPOINT[0] / PIXEL_SIZE],
                     [ZEROPOINT[0] / PIXEL_SIZE, ZEROPOINT[0] / PIXEL_SIZE, -ZEROPOINT[1] / PIXEL_SIZE, -ZEROPOINT[1] / PIXEL_SIZE, ZEROPOINT[0] / PIXEL_SIZE],
                     color="k", linewidth=1)  # Upper left CCD
        self.ax.plot([-ZEROPOINT[0] / PIXEL_SIZE, ZEROPOINT[1] / PIXEL_SIZE, ZEROPOINT[1] / PIXEL_SIZE, -ZEROPOINT[0] / PIXEL_SIZE, -ZEROPOINT[0] / PIXEL_SIZE],
                     [-ZEROPOINT[0] / PIXEL_SIZE, -ZEROPOINT[0] / PIXEL_SIZE, ZEROPOINT[1] / PIXEL_SIZE, ZEROPOINT[1] / PIXEL_SIZE, -ZEROPOINT[0] / PIXEL_SIZE],
                     color="k", linewidth=1)  # Lower left CCD
        self.ax.plot([-ZEROPOINT[1] / PIXEL_SIZE, ZEROPOINT[0] / PIXEL_SIZE, ZEROPOINT[0] / PIXEL_SIZE, -ZEROPOINT[1] / PIXEL_SIZE, -ZEROPOINT[1] / PIXEL_SIZE],
                     [-ZEROPOINT[0] / PIXEL_SIZE, -ZEROPOINT[0] / PIXEL_SIZE, ZEROPOINT[1] / PIXEL_SIZE, ZEROPOINT[1] / PIXEL_SIZE, -ZEROPOINT[0] / PIXEL_SIZE],
                     color="k", linewidth=1)  # Lower right CCD
        self.ax.plot([-ZEROPOINT[1] / PIXEL_SIZE, ZEROPOINT[0] / PIXEL_SIZE, ZEROPOINT[0] / PIXEL_SIZE, -ZEROPOINT[1] / PIXEL_SIZE, -ZEROPOINT[1] / PIXEL_SIZE],
                     [ZEROPOINT[0] / PIXEL_SIZE, ZEROPOINT[0] / PIXEL_SIZE, -ZEROPOINT[1] / PIXEL_SIZE, -ZEROPOINT[1] / PIXEL_SIZE, ZEROPOINT[0] / PIXEL_SIZE],
                     color="k", linewidth=1)  # Upper right CCD

        # Grid lines

        ticks = np.arange(-4000, 5000, 1000)
        ticks = np.delete(ticks, 4)
        self.ax.set_xticks(ticks)
        self.ax.set_yticks(ticks)
        self.ax.grid(color="lightgray", linewidth=0.5)

    def change_to_angle_coordinates(self):

        """
        Preparation of the plot to show the source position in angle coordinates:

            - clear the plot;
            - draw a blue circle, indicating the size of the field-of view;
            - configure the axes and grid lines;
            - draw the CCDs and their readout registers;
            - add the CCD codes.

        The draw() method should be called in the sub-classes.
        """

        self.coordinate_system = COORDINATE_SYSTEMS["Angles"]

        self.figure.delaxes(self.ax)
        self.ax = self.figure.add_subplot(111, projection="polar")
        self.ax.set_aspect(1)

        # Circle indicating the size of the FOV [mm]

        self.circle = plt.Circle(
            (0, 0), FOV_SETTINGS.RADIUS_DEGREES, color='b', fill=False, label="FOV", linewidth=1,
            transform=self.ax.transData._b)
        self.ax.add_artist(self.circle)

        # Range
        # If we do it like this, the circle will have the same size on screen when
        # switching between coordinate systems

        limit = degrees(atan(85 / FOV_SETTINGS.FOCAL_LENGTH))

        self.ax.set_rlim([0, limit])

        # CCD codes

        theta, phi = focal_plane_coordinates_to_angles(-30, 10)
        self.ax.text(radians(phi), theta, self.fee_side.LEFT_SIDE.name, rotation=180)      # Upper left CCD, left side
        theta, phi = focal_plane_coordinates_to_angles(-75, 10)
        self.ax.text(radians(phi), theta, self.fee_side.RIGHT_SIDE.name, rotation=180)     # Upper left CCD, right side
        theta, phi = focal_plane_coordinates_to_angles(-20, -15)
        self.ax.text(radians(phi), theta, self.fee_side.LEFT_SIDE.name, rotation=-90)      # Lower left CCD, left side
        theta, phi = focal_plane_coordinates_to_angles(-20, -75)
        self.ax.text(radians(phi), theta, self.fee_side.RIGHT_SIDE.name, rotation=-90)     # Lower left CCD, right side
        theta, phi = focal_plane_coordinates_to_angles(10, -15)
        self.ax.text(radians(phi), theta, self.fee_side.LEFT_SIDE.name)                    # Lower right CCD, left side
        theta, phi = focal_plane_coordinates_to_angles(50, -15)
        self.ax.text(radians(phi), theta, self.fee_side.RIGHT_SIDE.name)                   # Lower right CCD, right side
        theta, phi = focal_plane_coordinates_to_angles(10, 10)
        self.ax.text(radians(phi), theta, self.fee_side.LEFT_SIDE.name, rotation=90)       # Upper right CCD, left side
        theta, phi = focal_plane_coordinates_to_angles(10, 50)
        self.ax.text(radians(phi), theta, self.fee_side.RIGHT_SIDE.name, rotation=90)      # Upper right CCD, right side

        self.ax.text(radians(135), 22, self.ccd_id[2], ha="center")              # Upper left CCD
        self.ax.text(radians(-135), 22, self.ccd_id[3], ha="center", va="top")   # Lower left CCD
        self.ax.text(radians(-45), 22, self.ccd_id[0], ha="center", va="top")    # Lower right CCD
        self.ax.text(radians(45), 22, self.ccd_id[1], ha="center")               # Upper right CCD

        (theta1_ccd1, phi1_ccd1) = focal_plane_coordinates_to_angles(-ZEROPOINT[0], -ZEROPOINT[1])
        (theta2_ccd1, phi2_ccd1) = focal_plane_coordinates_to_angles(ZEROPOINT[1], -ZEROPOINT[1])
        (theta3_ccd1, phi3_ccd1) = focal_plane_coordinates_to_angles(ZEROPOINT[1], ZEROPOINT[0])
        (theta4_ccd1, phi4_ccd1) = focal_plane_coordinates_to_angles(-ZEROPOINT[0], ZEROPOINT[0])

        phi1_ccd1 = radians(phi1_ccd1)
        phi2_ccd1 = radians(phi2_ccd1)
        phi3_ccd1 = radians(phi3_ccd1)
        phi4_ccd1 = radians(phi4_ccd1)

        self.ax.plot([phi1_ccd1, phi2_ccd1], [theta1_ccd1, theta2_ccd1], color="k", linewidth=3)
        self.ax.plot([phi1_ccd1, phi2_ccd1, phi3_ccd1, phi4_ccd1, phi1_ccd1],
                     [theta1_ccd1, theta2_ccd1, theta3_ccd1, theta4_ccd1, theta1_ccd1], color="k", linewidth=1)

        (theta1_ccd2, phi1_ccd2) = focal_plane_coordinates_to_angles(ZEROPOINT[1], -ZEROPOINT[0])
        (theta2_ccd2, phi2_ccd2) = focal_plane_coordinates_to_angles(ZEROPOINT[1], ZEROPOINT[1])
        (theta3_ccd2, phi3_ccd2) = focal_plane_coordinates_to_angles(-ZEROPOINT[0], ZEROPOINT[1])
        (theta4_ccd2, phi4_ccd2) = focal_plane_coordinates_to_angles(-ZEROPOINT[0], -ZEROPOINT[0])

        phi1_ccd2 = radians(phi1_ccd2)
        phi2_ccd2 = radians(phi2_ccd2)
        phi3_ccd2 = radians(phi3_ccd2)
        phi4_ccd2 = radians(phi4_ccd2)

        self.ax.plot([phi1_ccd2, phi2_ccd2], [theta1_ccd2, theta2_ccd2], color="k", linewidth=3)
        self.ax.plot([phi1_ccd2, phi2_ccd2, phi3_ccd2, phi4_ccd2, phi1_ccd2],
                     [theta1_ccd2, theta2_ccd2, theta3_ccd2, theta4_ccd2, theta1_ccd2], color="k", linewidth=1)

        (theta1_ccd3, phi1_ccd3) = focal_plane_coordinates_to_angles(ZEROPOINT[0], ZEROPOINT[1])
        (theta2_ccd3, phi2_ccd3) = focal_plane_coordinates_to_angles(-ZEROPOINT[1], ZEROPOINT[1])
        (theta3_ccd3, phi3_ccd3) = focal_plane_coordinates_to_angles(-ZEROPOINT[1], -ZEROPOINT[0])
        (theta4_ccd3, phi4_ccd3) = focal_plane_coordinates_to_angles(ZEROPOINT[0], -ZEROPOINT[0])

        phi1_ccd3 = radians(phi1_ccd3)
        phi2_ccd3 = radians(phi2_ccd3)
        phi3_ccd3 = radians(phi3_ccd3)
        phi4_ccd3 = radians(phi4_ccd3)

        self.ax.plot([phi1_ccd3, phi2_ccd3], [theta1_ccd3, theta2_ccd3], color="k", linewidth=3)
        self.ax.plot([phi1_ccd3, phi2_ccd3, phi3_ccd3, phi4_ccd3, phi1_ccd3],
                     [theta1_ccd3, theta2_ccd3, theta3_ccd3, theta4_ccd3, theta1_ccd3], color="k", linewidth=1)

        (theta1_ccd4, phi1_ccd4) = focal_plane_coordinates_to_angles(-ZEROPOINT[1], ZEROPOINT[0])
        (theta2_ccd4, phi2_ccd4) = focal_plane_coordinates_to_angles(-ZEROPOINT[1], -ZEROPOINT[1])
        (theta3_ccd4, phi3_ccd4) = focal_plane_coordinates_to_angles(ZEROPOINT[0], -ZEROPOINT[1])
        (theta4_ccd4, phi4_ccd4) = focal_plane_coordinates_to_angles(ZEROPOINT[0], ZEROPOINT[0])

        phi1_ccd4 = radians(phi1_ccd4)
        phi2_ccd4 = radians(phi2_ccd4)
        phi3_ccd4 = radians(phi3_ccd4)
        phi4_ccd4 = radians(phi4_ccd4)

        self.ax.plot([phi1_ccd4, phi2_ccd4], [theta1_ccd4, theta2_ccd4], color="k", linewidth=3)
        self.ax.plot([phi1_ccd4, phi2_ccd4, phi3_ccd4, phi4_ccd4, phi1_ccd4],
                     [theta1_ccd4, theta2_ccd4, theta3_ccd4, theta4_ccd4, theta1_ccd4], color="k", linewidth=1)

        # CCD middle

        (theta1, phi1) = focal_plane_coordinates_to_angles((ZEROPOINT[1] - ZEROPOINT[0]) / 2, -ZEROPOINT[1])
        (theta2, phi2) = focal_plane_coordinates_to_angles((ZEROPOINT[1] - ZEROPOINT[0]) / 2, ZEROPOINT[0])
        phi1 = radians(phi1)
        phi2 = radians(phi2)
        self.ax.plot([phi1, phi2], [theta1, theta2], color="k", linewidth=1, linestyle="dotted")    # Upper left CCD

        (theta1, phi1) = focal_plane_coordinates_to_angles(ZEROPOINT[0], -(ZEROPOINT[1] - ZEROPOINT[0]) / 2)
        (theta2, phi2) = focal_plane_coordinates_to_angles(-ZEROPOINT[1], -(ZEROPOINT[1] - ZEROPOINT[0]) / 2)
        phi1 = radians(phi1)
        phi2 = radians(phi2)
        self.ax.plot([phi1, phi2], [theta1, theta2], color="k", linewidth=1, linestyle="dotted")    # Lower left CCD

        (theta1, phi1) = focal_plane_coordinates_to_angles(-(ZEROPOINT[1] - ZEROPOINT[0]) / 2, ZEROPOINT[1])
        (theta2, phi2) = focal_plane_coordinates_to_angles(-(ZEROPOINT[1] - ZEROPOINT[0]) / 2, -ZEROPOINT[0])
        phi1 = radians(phi1)
        phi2 = radians(phi2)
        self.ax.plot([phi1, phi2], [theta1, theta2], color="k", linewidth=1, linestyle="dotted")    # Lower right CCD

        (theta1, phi1) = focal_plane_coordinates_to_angles(-ZEROPOINT[0], (ZEROPOINT[1] - ZEROPOINT[0]) / 2)
        (theta2, phi2) = focal_plane_coordinates_to_angles(ZEROPOINT[1], (ZEROPOINT[1] - ZEROPOINT[0]) / 2)
        phi1 = radians(phi1)
        phi2 = radians(phi2)
        self.ax.plot([phi1, phi2], [theta1, theta2], color="k", linewidth=1, linestyle="dotted")    # Uoper right CCD

        # Grid lines

        tick = [self.ax.get_rmax(), self.ax.get_rmax() * 0.]
        for t in np.deg2rad(np.arange(0, 360, 15)):
            self.ax.plot([t, t], tick, lw=0.72, color="lightgray")

        tick = [self.ax.get_rmax(), self.ax.get_rmax() * 0.]
        for t in np.deg2rad(np.arange(0, 360, 45)):
            self.ax.plot([t, t], tick, lw=0.72, color="k")

        ticks = np.arange(2, 20, 2)
        self.ax.set_rticks(ticks)

        self.ax.yaxis.set_major_formatter(
            ticker.FuncFormatter(degree_formatter))


class FocalPlaneWithSubField(FocalPlane):

    """
    FigureCanvas showing the focal plane, with a blue circle indicating the field-of-view.
    The available coordinate systems are:
        - pixel coordinates [pixels],
        - focal-plane coordinates [mm],
        - and field angles [degrees].

    Possibility to draw the position of the sub-field on the focal plane.
    """

    def __init__(self):

        """
        Initialisation of a plot of the focal plane, with a blue circle indicating the
        field-of-view.
        """

        super(FocalPlaneWithSubField, self).__init__()

        self.subfield_is_drawn = False
        self.ccd_code = None
        self.zeropoint_row = None
        self.zeropoint_column = None
        self.num_rows = None
        self.num_columns = None

        self.change_to_pixel_coordinates()

    def set_subfield(self, ccd_code=None, zeropoint_row=None, zeropoint_column=None, num_rows=None, num_columns=None):

        """
        First-time drawing of the sub-field (in pixel coordinates).  All information is stored in
        variables and the sub-field is shown as a red rectangle on the focal plane.

        :param ccd_code: Code of the CCD on which the sub-field is located.

        :param zeropoint_row: Row coordinate of the origin of the sub-field in the CCD coordinate system
                              of the given CCD [pixels].

        :param zeropoint_column: Column coordinate of the origin of the sub-field in the CCD coordinate system
                                 of the given CCD [pixels].

        :param num_rows: Number of rows in the sub-field [pixels].

        :param num_columns: Number of columns in the sub-field [pixels].
        """

        self.ccd_code = ccd_code
        self.zeropoint_row = zeropoint_row
        self.zeropoint_column = zeropoint_column
        self.num_rows = num_rows
        self.num_columns = num_columns

        if self.coordinate_system == COORDINATE_SYSTEMS["Focal plane"]:
            self.change_to_focal_plane_coordinates
        elif self.coordinate_system == COORDINATE_SYSTEMS["Pixels"]:
            self.change_to_pixel_coordinates()
        elif self.coordinate_system == COORDINATE_SYSTEMS["Angles"]:
            self.change_to_angle_coordinates()

    def change_to_pixel_coordinates(self):

        """
        Preparation of the plot to show the source position in pixel coordinates:

            - clear the plot;
            - draw a blue circle, indicating the size of the field-of view;
            - configure the axes and grid lines;
            - draw the CCDs and their readout registers;
            - add the CCD codes;

        and re-draw the sub-field (if any).
        """

        super().change_to_pixel_coordinates()
        self.subfield_is_drawn = False

        self.update_subfield()

        self.draw()

    def change_to_focal_plane_coordinates(self):

        """
        Preparation of the plot to show the source position in focal-plane coordinates:

            - clear the plot;
            - draw a blue circle, indicating the size of the field-of view;
            - configure the axes and grid lines;
            - draw the CCDs and their readout registers;
            - add the CCD codes;

        and re-draw the sub-field (if any).
        """

        super().change_to_focal_plane_coordinates()
        self.subfield_is_drawn = False

        self.update_subfield()

        self.draw()

    def change_to_angle_coordinates(self):

        """
        Preparation of the plot to show the source position in angle coordinates:

            - clear the plot;
            - draw a blue circle, indicating the size of the field-of view;
            - configure the axes and grid lines;
            - draw the CCDs and their readout registers;
            - add the CCD codes;

        and re-draw the sub-field (if any).
        """

        super().change_to_angle_coordinates()
        self.subfield_is_drawn = False

        self.update_subfield()

        self.draw()

    def update_subfield(self):

        # Remove the sub-field (if needed)

        if self.subfield_is_drawn:

            del self.ax.lines[-1]
            self.subfield_is_drawn = False

        if self.ccd_code is None:
            self.draw()
            return

        # Draw the sub-field

        (x_fp_1, y_fp_1) = ccd_to_focal_plane_coordinates(
            self.zeropoint_row, self.zeropoint_column, self.ccd_code)
        (x_fp_2, y_fp_2) = ccd_to_focal_plane_coordinates(
            self.zeropoint_row + self.num_rows, self.zeropoint_column, self.ccd_code)
        (x_fp_3, y_fp_3) = ccd_to_focal_plane_coordinates(
            self.zeropoint_row + self.num_rows, self.zeropoint_column + self.num_columns, self.ccd_code)
        (x_fp_4, y_fp_4) = ccd_to_focal_plane_coordinates(
            self.zeropoint_row, self.zeropoint_column + self.num_columns, self.ccd_code)

        if self.coordinate_system == COORDINATE_SYSTEMS["Focal plane"]:

            self.ax.plot([x_fp_1, x_fp_2], [y_fp_1, y_fp_2], "r-")
            self.ax.plot([x_fp_2, x_fp_3], [y_fp_2, y_fp_3], "r-")
            self.ax.plot([x_fp_3, x_fp_4], [y_fp_3, y_fp_4], "r-")
            self.ax.plot([x_fp_4, x_fp_1], [y_fp_4, y_fp_1], "r-")

        elif self.coordinate_system == COORDINATE_SYSTEMS["Pixels"]:

            self.ax.plot([x_fp_1 / PIXEL_SIZE, x_fp_2 / PIXEL_SIZE], [y_fp_1 / PIXEL_SIZE, y_fp_2 / PIXEL_SIZE], "r-")
            self.ax.plot([x_fp_2 / PIXEL_SIZE, x_fp_3 / PIXEL_SIZE], [y_fp_2 / PIXEL_SIZE, y_fp_3 / PIXEL_SIZE], "r-")
            self.ax.plot([x_fp_3 / PIXEL_SIZE, x_fp_4 / PIXEL_SIZE], [y_fp_3 / PIXEL_SIZE, y_fp_4 / PIXEL_SIZE], "r-")
            self.ax.plot([x_fp_4 / PIXEL_SIZE, x_fp_1 / PIXEL_SIZE], [y_fp_4 / PIXEL_SIZE, y_fp_1 / PIXEL_SIZE], "r-")

        elif self.coordinate_system == COORDINATE_SYSTEMS["Angles"]:

            (theta1, phi1) = focal_plane_coordinates_to_angles(x_fp_1, y_fp_1)
            (theta2, phi2) = focal_plane_coordinates_to_angles(x_fp_2, y_fp_2)
            (theta3, phi3) = focal_plane_coordinates_to_angles(x_fp_3, y_fp_3)
            (theta4, phi4) = focal_plane_coordinates_to_angles(x_fp_4, y_fp_4)

            phi1 = radians(phi1)
            phi2 = radians(phi2)
            phi3 = radians(phi3)
            phi4 = radians(phi4)

            self.ax.plot([phi1, phi2], [theta1, theta2], "r-")
            self.ax.plot([phi2, phi3], [theta2, theta3], "r-")
            self.ax.plot([phi3, phi4], [theta3, theta4], "r-")
            self.ax.plot([phi4, phi1], [theta4, theta1], "r-")

        self.subfield_is_drawn = True

        self.draw()


class FocalPlaneWithSourcePosition(FocalPlane):

    """
    FigureCanvas showing the focal plane, with a blue circle indicating the field-of-view.
    The available coordinate systems are:
        - pixel coordinates [pixels],
        - focal-plane coordinates [mm],
        - and field angles [degrees].

    Possibility to draw the source position on the focal plane.
    """

    def __init__(self):

        """
        Initialisation of a plot of the focal plane, with a blue circle indicating the
        field-of-view.
        """

        super(FocalPlaneWithSourcePosition, self).__init__()

        self.source_position_is_drawn = False
        self.x_fp = None
        self.y_fp = None

        self.change_to_pixel_coordinates()

    def change_to_pixel_coordinates(self):

        """
        Preparation of the plot to show the source position in pixel coordinates:

            - clear the plot;
            - draw a blue circle, indicating the size of the field-of view;
            - configure the axes and grid lines;
            - draw the CCDs and their readout registers;
            - add the CCD codes;

        and re-draw the source position (if any).
        """

        super().change_to_pixel_coordinates()
        self.source_position_is_drawn = False

        self.update_source_position(self.x_fp, self.y_fp)

        self.draw()

    def change_to_focal_plane_coordinates(self):

        """
        Preparation of the plot to show the source position in focal-plane coordinates:

            - clear the plot;
            - draw a blue circle, indicating the size of the field-of view;
            - configure the axes and grid lines;
            - draw the CCDs and their readout registers;
            - add the CCD codes;

        and re-draw the source position (if any).
        """

        super().change_to_focal_plane_coordinates()
        self.source_position_is_drawn = False

        self.update_source_position(self.x_fp, self.y_fp)

        self.draw()

    def change_to_angle_coordinates(self):

        """
        Preparation of the plot to show the source position in angle coordinates:

            - clear the plot;
            - draw a blue circle, indicating the size of the field-of view;
            - configure the axes and grid lines;
            - draw the CCDs and their readout registers;
            - add the CCD codes;

        and re-draw the source position (if any).
        """

        super().change_to_angle_coordinates()
        self.source_position_is_drawn = False

        self.update_source_position(self.x_fp, self.y_fp)

        self.draw()

    def update_source_position(self, x_fp, y_fp):

        """
        Add a red dot at the position with the given focal-plane coordinates. In case
        a source position had been marked before, that red dot must be removed first.

        :param x_fp: Focal-plane x-coordinate of the new source position [mm].

        :param y_fp: Focal-plane y-coordinate of the new source position [mm].
        """

        # Remove the previously visited location (if needed)

        if self.source_position_is_drawn:

            del self.ax.lines[-1]
            self.source_position_is_drawn = False

        if (x_fp is None) or (y_fp is None):
            return

        # Outside the FOV

        if abs(x_fp) > FOV_SETTINGS.RADIUS_MM and abs(y_fp) > FOV_SETTINGS.RADIUS_MM:

            self.ax.plot([0], [0], color="white")

        # Put a red dot at the new source position

        if self.coordinate_system == COORDINATE_SYSTEMS["Focal plane"]:

            self.ax.plot([x_fp], [y_fp], "ro")

        elif self.coordinate_system == COORDINATE_SYSTEMS["Pixels"]:

            self.ax.plot([x_fp / PIXEL_SIZE], [y_fp / PIXEL_SIZE], "ro")

        elif self.coordinate_system == COORDINATE_SYSTEMS["Angles"]:

            (theta, phi) = focal_plane_coordinates_to_angles(x_fp, y_fp)

            self.ax.plot([radians(phi)], [theta], "ro")

        self.source_position_is_drawn = True
        self.x_fp = x_fp
        self.y_fp = y_fp

        self.draw()


class FocalPlaneWithVisitedPositions(FocalPlane):

    """
    FigureCanvas showing the focal plane, with a blue circle indicating the field-of-view.
    The available coordinate systems are:
        - pixel coordinates [pixels],
        - focal-plane coordinates [mm],
        - and field angles [degrees].

    Possibility to draw the visited positions of the sub-field on the focal plane.
    """

    def __init__(self):

        """
        Initialisation of a plot of the focal plane, with a blue circle indicating the
        field-of-view.
        """

        super(FocalPlaneWithVisitedPositions, self).__init__()

        self.visited_x_fp = np.array([])
        self.visited_y_fp = np.array([])

        self.change_to_pixel_coordinates()

    def change_to_pixel_coordinates(self):

        """
        Preparation of the plot to show the source position in pixel coordinates:

            - clear the plot;
            - draw a blue circle, indicating the size of the field-of view;
            - configure the axes and grid lines;
            - draw the CCDs and their readout registers;
            - add the CCD codes;

        and re-draw the visited positions (if any).
        """

        super().change_to_pixel_coordinates()

        # Re-draw the visited positions in the new coordinate system

        self.redraw_visited_positions()

        self.draw()

    def change_to_focal_plane_coordinates(self):

        """
        Preparation of the plot to show the source position in focal-plane coordinates:

            - clear the plot;
            - draw a blue circle, indicating the size of the field-of view;
            - configure the axes and grid lines;
            - draw the CCDs and their readout registers;
            - add the CCD codes;

        and re-draw the visited postiions (if any).
        """

        super().change_to_focal_plane_coordinates()

        # Re-draw the visited positions in the new coordinate system

        self.redraw_visited_positions()

        self.draw()

    def change_to_angle_coordinates(self):

        """
        Preparation of the plot to show the source position in angle coordinates:

            - clear the plot;
            - draw a blue circle, indicating the size of the field-of view;
            - configure the axes and grid lines;
            - draw the CCDs and their readout registers;
            - add the CCD codes;

        and re-draw the visited positions (if any).
        """

        super().change_to_angle_coordinates()

        # Re-draw the visited positions in the new coordinate system

        self.redraw_visited_positions()

        self.draw()

    def visit_position(self, x_fp, y_fp, redraw=False):

        """
        Add a red dot at the position with the given focal-plane coordinates. If you are not
        in re-drawing mode, keep track of this new position in the list of visited positions.

        :param x: Focal-plane x-coordinate of the new visited position [mm].

        :param y: Focal-plane y-coordinate of the new visited position [mm].

        :param redraw: If False, the given position should not be added to the list of visited
                       positions (as it is already in there); otherwise, the list of visited
                       positions must be expanded with the given position.
        """

        if len(self.visited_x_fp) > 0:

            self.ax.lines[-1].set_color("blue")

        # Outside the FOV

        if abs(x_fp) > FOV_SETTINGS.RADIUS_MM and abs(y_fp) > FOV_SETTINGS.RADIUS_MM:

            self.ax.plot([0], [0], color="white")

        # Put a red dot at the new source position

        if self.coordinate_system == COORDINATE_SYSTEMS["Focal plane"]:

            self.ax.plot([x_fp], [y_fp], "ro")

        elif self.coordinate_system == COORDINATE_SYSTEMS["Pixels"]:

            self.ax.plot([x_fp / PIXEL_SIZE], [y_fp / PIXEL_SIZE], "ro")

        elif self.coordinate_system == COORDINATE_SYSTEMS["Angles"]:

            (theta, phi) = focal_plane_coordinates_to_angles(x_fp, y_fp)

            self.ax.plot([radians(phi)], [theta], "ro")

        if not redraw:

            self.visited_x_fp = np.append(self.visited_x_fp, x_fp)
            self.visited_y_fp = np.append(self.visited_y_fp, y_fp)

        self.draw()

    def redraw_visited_positions(self):

        """
        Re-draw the visited positions in the current coordinate system.
        """

        for (x_fp, y_fp) in zip(self.visited_x_fp, self.visited_y_fp):
            self.visit_position(x_fp, y_fp, redraw=True)

    def clear_visited_positions(self):
        """ Clear all visited positions."""

        num_points = len(self.visited_x_fp)
        while num_points > 0:
            del self.ax.lines[-1]
            num_points -= 1

        self.visited_x_fp = np.array([])
        self.visited_y_fp = np.array([])

        self.draw()
############################################
# Focal plane + combobox (coordinate system)
############################################


class FocalPlaneWidget(QGroupBox):

    """
    Widget with a FigureCanvas (plot window) showing the focal plane, with a blue circle
    indicating the field-of-view.  Below the plot window, you can find a combobox to choose
    the coordinate system to use in the plot.  The available coordinate systems are:
        - pixel coordinates [pixels],
        - focal-plane coordinates [mm],
        - and field angles [degrees].
    """

    def __init__(self):

        """
        Initialisation of a plot of the focal plane, with a blue circle indicating the
        field-of-view.  Below the plot you can find a spinner to choose the coordinate
        system to be used in the plot.
        """

        super(FocalPlaneWidget, self).__init__("Focal Plane")

        self.setFont(FONT)

        layout = QGridLayout()

        # Focal plane

        self.focal_plane = self.get_focal_plane()

        # Combobox (coordinate system)

        coordinate_system_combobox = QComboBox(self)
        coordinate_system_combobox.setFont(FONT)
        coordinate_system_combobox.addItem(COORDINATE_SYSTEMS["Pixels"])
        coordinate_system_combobox.addItem(COORDINATE_SYSTEMS["Angles"])
        coordinate_system_combobox.addItem(COORDINATE_SYSTEMS["Focal plane"])
        coordinate_system_combobox.currentTextChanged.connect(self.update_coordinate_system)

        coordinate_label = QLabel("Coordinate system")
        coordinate_label.setFont(FONT)
        coordinate_label.setStatusTip("Coordinate system to use in the plot")

        # Putting everything together

        layout.addWidget(self.focal_plane)
        layout.addWidget(coordinate_label)
        layout.addWidget(coordinate_system_combobox)

        self.setLayout(layout)

    def update_coordinate_system(self, value):

        """
        Switch to the given coordinate system to use in the plot.  Currently implemented are
        focal-plane coordinates, pixel coordinates, and field angles.  This means that the plot
        needs to be cleared and re-built in the specified coordinate system.

        :param value: Name of the coordinate system to switch to.
        """

        # Focal-plane coordinates

        if value == COORDINATE_SYSTEMS["Focal plane"]:

            self.focal_plane.change_to_focal_plane_coordinates()

        # Field angles

        elif value == COORDINATE_SYSTEMS["Angles"]:

            self.focal_plane.change_to_angle_coordinates()

        # Pixel coordinates

        elif value == COORDINATE_SYSTEMS["Pixels"]:

            self.focal_plane.change_to_pixel_coordinates()

    def get_focal_plane(self):

        """
        Returns the widget with the focal plane only (so without the combobox to
        choose the coordinate system).

        :return: Widget with the focal plane only (so without the combobox to
                 choose the coordinate system).
        """

        return None

    def change_to_focal_plane_coordinates(self):

        """
        Preparation of the plot to show the source position in focal-plane coordinates:

            - clear the plot;
            - draw a blue circle, indicating the size of the field-of view;
            - configure the axes and grid lines;
            - draw the CCDs and their readout registers;
            - add the CCD codes.
        """

        self.focal_plane.change_to_focal_plane_coordinates()

    def change_to_pixel_coordinates(self):

        """
        Preparation of the plot to show the source position in pixel coordinates:

            - clear the plot;
            - draw a blue circle, indicating the size of the field-of view;
            - configure the axes and grid lines;
            - draw the CCDs and their readout registers;
            - add the CCD codes.
        """

        self.focal_plane.change_to_pixel_coordinates()

    def change_to_angle_coordinates(self):

        """
        Preparation of the plot to show the source position in angle coordinates:

            - clear the plot;
            - draw a blue circle, indicating the size of the field-of view;
            - configure the axes and grid lines;
            - draw the CCDs and their readout registers;
            - add the CCD codes.
        """

        self.focal_plane.change_to_angle_coordinates()

    def get_widget(self):

        """
        Returns the widget itself.

        :return: Widget itself.
        """

        return self


class FocalPlaneWidgetWithSubField(FocalPlaneWidget):

    """
    Widget with a FigureCanvas (plot window) showing the focal plane, with a blue circle
    indicating the field-of-view.  Below the plot window, you can find a combobox to choose
    the coordinate system to use in the plot.  The available coordinate systems are:
        - pixel coordinates [pixels],
        - focal-plane coordinates [mm],
        - and field angles [degrees].

    Possibility to draw the position of the sub-field on the focal plane.
    """

    def __init__(self, ccd_code=None, zeropoint_row=None, zeropoint_column=None, num_rows=None, num_columns=None):

        """
        Initialisation of a plot of the focal plane, with a blue circle indicating the
        field-of-view.  Below the plot you can find a spinner to choose the coordinate
        system to be used in the plot.

        In the plot window, the position of tbe sub-field will be plotted.

        :param ccd_code: Code of the CCD on which the sub-field is located.

        :param zeropoint_row: Row coordinate of the origin of the sub-field in the CCD coordinate system
                              of the given CCD [pixels].

        :param zeropoint_column: Column coordinate of the origin of the sub-field in the CCD coordinate system
                                 of the given CCD [pixels].

        :param num_rows: Number of rows in the sub-field [pixels].

        :param num_columns: Number of columns in the sub-field [pixels].
        """

        super(FocalPlaneWidgetWithSubField, self).__init__()

        self.setStatusTip(
            "Position of the sub-field on the focal plane, based on the FITS header")

        self.focal_plane.set_subfield(ccd_code=ccd_code, zeropoint_row=zeropoint_row,
                                      zeropoint_column=zeropoint_column, num_rows=num_rows, num_columns=num_columns)


    def get_focal_plane(self):

        """
        Returns the widget with the focal plane only (so without the combobox to
        choose the coordinate system).

        :return: Widget with the focal plane only (so without the combobox to
                 choose the coordinate system).
        """

        return FocalPlaneWithSubField()


class FocalPlaneWidgetWithSourcePosition(FocalPlaneWidget):

    """
    Widget with a FigureCanvas (plot window) showing the focal plane, with a blue circle
    indicating the field-of-view.  Below the plot window, you can find a combobox to choose
    the coordinate system to use in the plot.  The available coordinate systems are:
        - pixel coordinates [pixels],
        - focal-plane coordinates [mm],
        - and field angles [degrees].

    Possibility to draw the source position on the focal plane.
    """

    def __init__(self):

        """
        Initialisation of a plot of the focal plane, with a blue circle indicating the
        field-of-view.  Below the plot you can find a spinner to choose the coordinate
        system to be used in the plot.

        In the plot window, the position of tbe sub-field will be plotted.
        """

        super(FocalPlaneWidgetWithSourcePosition, self).__init__()

        self.setStatusTip(
            "Position of the source on the focal plane, based on the position of the mechanisms")

    def update_source_position(self, x_fp, y_fp):

        """
        Add a red dot at the position with the given focal-plane coordinates. In case
        a source position had been marked before, that red dot must be removed first.

        :param x_fp: Focal-plane x-coordinate of the new source position [mm].

        :param y_fp: Focal-plane y-coordinate of the new source position [mm].
        """

        self.focal_plane.update_source_position(x_fp, y_fp)

    def get_focal_plane(self):
        """
        Returns the widget with the focal plane only (so without the combobox to
        choose the coordinate system).

        :return: Widget with the focal plane only (so without the combobox to
                 choose the coordinate system).
        """

        return FocalPlaneWithSourcePosition()


class FocalPlaneWidgetWithVisitedPositions(FocalPlaneWidget):

    """
    Widget with a FigureCanvas (plot window) showing the focal plane, with a blue circle
    indicating the field-of-view.  Below the plot window, you can find a combobox to choose
    the coordinate system to use in the plot.  The available coordinate systems are:
        - pixel coordinates [pixels],
        - focal-plane coordinates [mm],
        - and field angles [degrees].

    Possibility to draw the visited positions on the focal plane.
    """

    def __init__(self):

        """
        Initialisation of a plot of the focal plane, with a blue circle indicating the
        field-of-view.  Below the plot you can find a spinner to choose the coordinate
        system to be used in the plot.

        In the plot window, the visited positions will be plotted.
        """

        super(FocalPlaneWidgetWithVisitedPositions, self).__init__()

        self.setToolTip("Visited positions")

    def visit_position(self, x_fp, y_fp):

        """
        Add a red dot at the position with the given focal-plane coordinates.

        :param x: Focal-plane x-coordinate of the new visited position [mm].

        :param y: Focal-plane y-coordinate of the new visited position [mm].
        """

        self.focal_plane.visit_position(x_fp, y_fp)

    def get_focal_plane(self):

        """
        Returns the widget with the focal plane only (so without the combobox to
        choose the coordinate system).

        :return: Widget with the focal plane only (so without the combobox to
                 choose the coordinate system).
        """

        return FocalPlaneWithVisitedPositions()

    def clear_visited_positions(self):
        """ Clear all visited positions."""

        self.focal_plane.clear_visited_positions()
