import matplotlib
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtWidgets import QSizePolicy, QGroupBox, QGridLayout, QLabel, QMainWindow, QFrame, QVBoxLayout, \
    QHBoxLayout, QPushButton
from math import radians, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from egse.config import find_file
from egse.resource import get_resource
from egse.settings import Settings
from egse.setup import get_setup
from egse.state import GlobalState

FONT = QFont("Helvetica", 18)

FOV_SETTINGS = Settings.load("Field-Of-View")
DEGREE_SYMBOL_PLOT = "$^\circ$"
DEGREE_SYMBOL_LABEL = f"\u00B0"

######################################
# Widgets for the scan mirror assembly
######################################


class HelpButton(QPushButton):
    """ Help button for the mechanisms widget."""

    def __init__(self):

        super(HelpButton, self).__init__()

        help_icon = QIcon(str(get_resource(":/icons/info.svg")))

        self.setIcon(help_icon)
        self.setMaximumSize(50, 50)
        self.setIconSize(QSize(30, 30))
        self.setStyleSheet("border: none;")


class ExplanationWindow(QMainWindow):

    def __init__(self, title, filename):
        """ Initialisation of a window with more explanation about the mechanisms.

        Args:
            - title: Window title.
            - filename: Full path to the image to display.
        """

        super(ExplanationWindow, self).__init__()

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        self.setWindowTitle(title)

        self.layout = QVBoxLayout()

        label = QLabel()
        pixmap = QPixmap(filename)
        label.setPixmap(pixmap)

        self.layout.addWidget(label)

        app_frame.setLayout(self.layout)

        self.setCentralWidget(app_frame)


class ScanMirrorAssembly(FigureCanvas):
    """ Display of the Scan Mirror Assembly

    FigureCanvas showing the distance of the scan mirror (along the translation stage) from the optical axis and the
    orientation of the scan mirror (small rotation stage).
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        self.figure = Figure(dpi=dpi)
        self.ax = self.figure.add_subplot(111, aspect='equal')

        FigureCanvas.__init__(self, self.figure)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        setup = GlobalState.setup
        self.offset_alpha = setup.gse.stages.calibration.offset_alpha
        self.offset_delta_x = setup.gse.stages.calibration.offset_delta_x

        self.plot(0, 0)

    def plot(self, angle, distance):
        """ Plot the position and orientation angle of the scan mirror w.r.t. the optical axis.

        Args:
            - distance: Distance (along the translation stage) between the scan mirror and the optical axis [mm].
            - angle: Orientation angle of the scan mirror [degrees].
        """

        cmd_angle = angle
        total_angle = cmd_angle + self.offset_alpha + 45

        cmd_distance = distance
        total_angle = distance

        # Light path (from collimator to SMA)

        self.ax.annotate("towards collimator", (-80, 20), color='k', fontsize=10, ha='center', va='center')
        self.ax.arrow(0, 0, -80, 0, fc='gray', ec='gray', lw=1,
                      head_width=6, head_length=10,
                      length_includes_head=True, clip_on=False)

        # Optical axis

        self.ax.plot([0.0, 0.0], [-55, 40], "k", linewidth=1)
        self.ax.annotate("optical axis", (0, 50), color='k', fontsize=10, ha='center', va='center')

        # Scan mirror

        self.mirror_thickness = 1
        self.mirror_length = 50

        ts = self.ax.transData
        coords = [distance, 0]  # Rotate around this point
        tr = matplotlib.transforms.Affine2D().rotate_deg_around(coords[0], coords[1], total_angle - 90)
        t = tr + ts
        self.scan_mirror = matplotlib.patches.Rectangle(
            (distance - self.mirror_length / 2, 0), self.mirror_length, self.mirror_thickness, color="k", transform=t)
        self.ax.add_patch(self.scan_mirror)

        self.arrow_right = matplotlib.patches.FancyArrow(
            -30, -50, 30, 0, length_includes_head=True, head_width=6, head_length=10, color="k")
        self.ax.add_patch(self.arrow_right)
        self.arrow_left = matplotlib.patches.FancyArrow(
            distance + 30, -50, -30, 0, length_includes_head=True, head_width=6, head_length=10, color="k")
        self.ax.add_patch(self.arrow_left)

        self.distance_annotation = self.ax.annotate(
            "$\Delta x$", (distance / 2, -65), color='k', fontsize=10, ha='center', va='center')
        self.angle_annotation = self.ax.annotate(
            u"\u03B1", (distance + 10, 20), color='k', fontsize=10, ha='center', va='center')

        self.ax.plot([distance, distance], [-55, 40], "--", color="gray", linewidth=1)

        # Axes

        self.ax.set_xlim([-110, 200])
        self.ax.set_ylim([-70, 60])

        self.ax.axis("off")

        self.draw()

    def update_plot(self, cmd_distance, angle):
        """
        Update the orientation of the scan mirror, and the distance (along the
        translation stage) between the scan mirror and the optical axis.

        :param distance: Distance (along the translation stage) between the scan mirror
                         and the optical axis [mm].

        :param angle: Orientation angle of the scan mirror [degrees].
        """

        cmd_angle = angle
        total_angle = cmd_angle + self.offset_alpha + 45

        total_distance = cmd_distance + self.offset_delta_x

        self.angle_annotation.remove()
        self.distance_annotation.remove()

        self.scan_mirror.remove()
        self.arrow_right.remove()
        self.arrow_left.remove()

        del self.ax.lines[-1]

        # Scan mirror

        ts = self.ax.transData
        coords = [total_distance, 0]  # Rotate around this point
        tr = matplotlib.transforms.Affine2D().rotate_deg_around(coords[0], coords[1], total_angle - 90)
        t = tr + ts
        self.scan_mirror = matplotlib.patches.Rectangle((total_distance - self.mirror_length / 2, 0),
                                                        self.mirror_length, self.mirror_thickness, color="k",
                                                        transform=t)
        self.ax.add_patch(self.scan_mirror)

        self.arrow_right = matplotlib.patches.FancyArrow(-30, -50, 30, 0, length_includes_head=True, head_width=6,
                                                         head_length=10, color="k")
        self.ax.add_patch(self.arrow_right)
        # self.arrow_left = matplotlib.patches.FancyArrow(
        #     distance + 30, -50, -30, 0, length_includes_head=True, head_width=6, head_length=10, color="k")
        self.arrow_left = matplotlib.patches.FancyArrow(total_distance + 30, -50, -30, 0, length_includes_head=True,
                                                        head_width=6, head_length=10, color="k")
        self.ax.add_patch(self.arrow_left)

        distance_text = f"$\Delta x$ = {cmd_distance:.2f} mm + {self.offset_delta_x} mm \n   = {total_distance:.2f} mm"
        self.distance_annotation = self.ax.annotate(distance_text, (cmd_distance / 2, -70), color='k', fontsize=10,
                                                    ha='center', va='center')

        angle_text = u"\u03B1" + f" = {cmd_angle:.2f}{DEGREE_SYMBOL_PLOT} + {self.offset_alpha}{DEGREE_SYMBOL_PLOT} " \
                                 f"+ 45{DEGREE_SYMBOL_PLOT} \n   = {total_angle:.2f}{DEGREE_SYMBOL_PLOT}"
        self.angle_annotation = self.ax.annotate(angle_text, (cmd_distance + 10, 20), color='k', fontsize=10, ha='left',
                                                 va='center')

        self.ax.plot([cmd_distance, cmd_distance], [-55, 40], "--", color="gray", linewidth=1)

        self.draw()


class ScanMirrorAssemblyWidget(QGroupBox):

    def __init__(self):
        """
        Initialisation of a plot showing the distance of the scan mirror (along the translation stage)
        from the optical axis and the orientation of the scan mirror (small rotation stage).
        """

        super(ScanMirrorAssemblyWidget, self).__init__("Scan Mirror Assembly")

        self.setStatusTip(
            "Current configuration of the scan mirror assembly (i.e. small rotation stage and translation stage)")
        self.setFont(FONT)

        setup = get_setup()
        self.offset_delta_x = setup.gse.stages.calibration.offset_delta_x
        self.offset_alpha = setup.gse.stages.calibration.offset_alpha

        self.explanation_window = ExplanationWindow("Configuration of the Scan Mirror Assembly",
                                                    str(find_file("sma.png", in_dir="images")))
        self.cmd_angle_text_explanation = QLabel()
        self.explanation_window.layout.addWidget(self.cmd_angle_text_explanation)
        self.explanation_window.layout.addWidget(QLabel(f"offset_alpha: {self.offset_alpha}{DEGREE_SYMBOL_LABEL} "
                                                        f"(see setup)"))
        self.total_angle_text_explanation = QLabel()
        self.explanation_window.layout.addWidget(self.total_angle_text_explanation)
        self.cmd_distance_text_explanation = QLabel()
        self.explanation_window.layout.addWidget(self.cmd_distance_text_explanation)
        self.explanation_window.layout.addWidget(QLabel(f"offset_delta_x: {self.offset_delta_x} mm (see setup)"))
        self.total_distance_text_explanation = QLabel()
        self.explanation_window.layout.addWidget(self.total_distance_text_explanation)

        layout = QVBoxLayout()

        self.sma = ScanMirrorAssembly()
        layout.addWidget(self.sma)

        self.cmd_angle_text = QLabel()
        self.cmd_distance_text = QLabel()

        labels_layout = QVBoxLayout()
        labels_layout.addWidget(self.cmd_angle_text)
        labels_layout.addWidget(self.cmd_distance_text)

        info_layout = QHBoxLayout()
        info_layout.addLayout(labels_layout)

        help_button = HelpButton()
        help_button.clicked.connect(self.explanation_window.show)

        info_layout.addWidget(help_button)
        layout.addLayout(info_layout)

        self.setLayout(layout)

    def update_plot(self, distance, angle):
        """
        Update the orientation of the scan mirror, and the distance (along the
        translation stage) between the scan mirror and the optical axis.

        :param distance: Distance (along the translation stage) between the scan mirror
                         and the optical axis [mm].

        :param angle: Orientation angle of the scan mirror [degrees].
        """

        self.sma.update_plot(-distance, angle)

        self.cmd_angle_text.setText(f"Commanded position for the small rotation stage: {angle:.2f}{DEGREE_SYMBOL_LABEL}")
        self.cmd_distance_text.setText(f"Commanded position for the translation stage: {distance:.2f}mm")

        self.cmd_angle_text_explanation.setText(f"Commanded position for the small rotation stage: {angle:.2f}{DEGREE_SYMBOL_LABEL}")
        self.total_angle_text_explanation.setText(f"Angle \u03B1 shown: {(angle + self.offset_alpha + 45):.2f}{DEGREE_SYMBOL_LABEL}")
        self.cmd_distance_text_explanation.setText(f"Commanded position for the translation stage: {distance:.2f} mm")
        self.total_distance_text_explanation.setText(f"Distance \u0394x shown: {(-distance + self.offset_delta_x):.2f} mm")

####################################
# Widgets for the big rotation stage
####################################


class BigRotationStage(FigureCanvas):
    """
    FigureCanvas showing the orientation of the big rotation stage.
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        self.figure = Figure(dpi=dpi)
        self.ax = self.figure.add_subplot(
            111, aspect='equal', projection="polar")

        FigureCanvas.__init__(self, self.figure)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.circle = plt.Circle(
            (0, 0), FOV_SETTINGS.RADIUS_DEGREES, color='b', fill=False, label="FOV", linewidth=1)
        self.plot()

    def plot(self, angle=45):
        """
        Plot the GL_FIX axes in black and the GL_ROT axes in red.

        :angle: Rotation angle of GL_ROT w.r.t. GL_FIX [degrees]. A positive angle
                corresponds to a counterclockwise rotation.
        """

        self.ax.arrow(0, 0, 0, 1, fc='k', ec='k', lw=1, head_width=.09,
                      head_length=.15, overhang=0.01, length_includes_head=True, clip_on=False)
        self.ax.arrow(pi / 2, 0, 0, 1, fc='k', ec='k', lw=1, head_width=.09,
                      head_length=.15, overhang=0.01, length_includes_head=True, clip_on=False)

        self.ax.set_rlim([0, 1])

        self.ax.plot([0], [0], "k", label="GL_FIX")
        self.ax.plot([0], [0], "r", label="GL_ROT")

        # Axes

        self.x_axis_gl_rot = self.ax.arrow(radians(angle), 0, 0, 1, fc='r', ec='r', lw=1, head_width=.09,
                                           head_length=.15, overhang=0.01, length_includes_head=True, clip_on=False)
        self.y_axis_gl_rot = self.ax.arrow(radians(angle + 90), 0, 0, 1, fc='r', ec='r', lw=1, head_width=.09,
                                           head_length=.15, overhang=0.01, length_includes_head=True, clip_on=False)

        self.ax.get_yaxis().set_visible(False)

        tick = [self.ax.get_rmax(), self.ax.get_rmax() * 0.97]
        for t in np.deg2rad(np.arange(0, 360, 5)):
            self.ax.plot([t, t], tick, lw=0.72, color="k")

        # Legend

        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        self.ax.legend(loc='center left', bbox_to_anchor=(1.2, 0.5))

        self.draw()

    def update_plot(self, angle):
        """
        Update the orientation of GL_ROT.

        :angle: Rotation angle of GL_ROT w.r.t. GL_FIX [degrees]. A positive angle
                corresponds to a counterclockwise rotation.
        """

        self.x_axis_gl_rot.remove()
        self.y_axis_gl_rot.remove()

        self.x_axis_gl_rot = self.ax.arrow(radians(angle), 0, 0, 1, fc='r', ec='r', lw=1, head_width=.09,
                                           head_length=.15, overhang=0.01, length_includes_head=True, clip_on=False)
        self.y_axis_gl_rot = self.ax.arrow(radians(angle + 90), 0, 0, 1, fc='r', ec='r', lw=1, head_width=.09,
                                           head_length=.15, overhang=0.01, length_includes_head=True, clip_on=False)

        self.draw()


class BigRotationStageWidget(QGroupBox):

    def __init__(self):
        """
        Initialisation of a plot showing the orientation of GL_ROT w.r.t.
        GL_FIX, based on the orientation of the big rotation stage.  Below the
        plot you can find the value of the rotation angle.
        """

        super(BigRotationStageWidget, self).__init__("Big Rotation Stage")

        self.setStatusTip(
            "Current configuration of the big rotation stage (visualised as the rotation of GL_ROT w.r.t. GL_FIX)")
        self.setFont(FONT)

        setup = get_setup()
        self.offset_phi = setup.gse.stages.calibration.offset_phi

        self.explanation_window = ExplanationWindow("Configuration of the big rotation stage",
                                                    str(find_file("big-rotation-stage.png", in_dir="images")))
        self.cmd_angle_text_explanation = QLabel()
        self.explanation_window.layout.addWidget(self.cmd_angle_text_explanation)
        self.explanation_window.layout.addWidget(QLabel(f"offset_phi: {self.offset_phi}{DEGREE_SYMBOL_LABEL} (see setup)"))
        self.total_angle_text_explanation = QLabel()
        self.explanation_window.layout.addWidget(self.total_angle_text_explanation)

        layout = QVBoxLayout()

        self.big_rotation_stage = BigRotationStage()
        layout.addWidget(self.big_rotation_stage)

        self.angle_big_rotation_stage_text = QLabel()

        info_layout = QHBoxLayout()

        help_button = HelpButton()
        help_button.clicked.connect(self.explanation_window.show)

        info_layout.addWidget(self.angle_big_rotation_stage_text)
        info_layout.addWidget(help_button)
        layout.addLayout(info_layout)

        self.setLayout(layout)

    def update_plot(self, angle):
        """
        Update the orientation of GL_ROT.

        :angle: Rotation angle of GL_ROT w.r.t. GL_FIX [degrees]. A positive angle
                corresponds to a counterclockwise rotation.
        """
        self.big_rotation_stage.update_plot(angle)

    def update(self, angle):
        """
        Update the shown configuration of the big rotation stage.
        """

        self.big_rotation_stage.update_plot(angle)

        self.angle_big_rotation_stage_text.setText(f"Commanded position for the big rotation stage: {angle:.2f}{DEGREE_SYMBOL_LABEL}")

        self.cmd_angle_text_explanation.setText(f"Commanded position for the big rotation stage: {angle:.2f}{DEGREE_SYMBOL_LABEL}")
        self.total_angle_text_explanation.setText(f"Angle shown in red: {(-angle + self.offset_phi):.2f}{DEGREE_SYMBOL_LABEL}")


################################
# Widgets for the focus position
################################


class FocusPosition(FigureCanvas):
    """
    FigureCanvas showing the focus position as the distance between L6S2 and FPA_SEN.
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """
        Initialisation of a plot showing L6 and FPA_SEN.
        """

        self.figure = Figure(dpi=dpi)
        self.ax = self.figure.add_subplot(111, aspect='equal')

        FigureCanvas.__init__(self, self.figure)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.plot()

    def plot(self, focus_position=0):
        """
        Plot a cyan trapezium representing L6 and a black rectangle representing the
        focal plane.  An arrow is drawn, next to which the distance between the two will
        be shown.
        """

        # L6

        self.l6_width = 120
        self.l6_thickness = 20

        points = [[-self.l6_width / 2, 0], [self.l6_width / 2, 0], [self.l6_width / 2 -
                                                                    5, self.l6_thickness],
                  [-self.l6_width / 2 + 5, self.l6_thickness], [-60, 0]]
        polygon = plt.Polygon(points, color="cyan")
        self.ax.add_patch(polygon)
        self.ax.annotate("L6", (0, 10), color='k',
                         fontsize=12, va='center', ha='center')

        self.ax.plot([self.l6_width / 2, self.l6_width / 2 + 20],
                     [0, 0], "--", color="gray", linewidth=1)
        self.ax.plot([self.l6_width / 2, self.l6_width / 2 + 20],
                     [-focus_position, -focus_position], "--", color="gray", linewidth=1)

        # FPA_SEN

        self.fpa_sen_size = 120
        self.fpa_sen_thickness = 1

        self.fpa_sen = patches.Rectangle(
            (-self.fpa_sen_size / 2, focus_position), 2 * self.fpa_sen_size / 2, -self.fpa_sen_thickness, color="k")
        self.ax.add_patch(self.fpa_sen)

        # Focus position

        self.arrow_down = matplotlib.patches.FancyArrow(
            self.l6_width / 2 + 10, 15, 0, -15, length_includes_head=True, head_width=3, head_length=5, color="k")
        self.ax.add_patch(self.arrow_down)
        self.arrow_up = matplotlib.patches.FancyArrow(
            self.l6_width / 2 + 10, -focus_position - 15, 0, 15, length_includes_head=True, head_width=3, head_length=5,
            color="k")
        self.ax.add_patch(self.arrow_up)

        self.focus_position_annotation = self.ax.annotate(
            "$\Delta$ z", (self.l6_width / 2 + 30, -focus_position / 2), color='k', fontsize=10, va='center')

        # Axes

        self.ax.set_xlim([-70, 150])
        self.ax.set_ylim([-40, 40])

        self.ax.axis("off")

        self.draw()

    def update_plot(self, focus_position):
        """
        Update the distance between L6S2 and FPA_SEN.

        :focus_position: Distance between L6S2 and FPA_SEN to display [mm].
        """

        del self.ax.lines[-1]

        self.fpa_sen.remove()
        self.arrow_down.remove()
        self.arrow_up.remove()
        self.focus_position_annotation.remove()

        self.fpa_sen = patches.Rectangle(
            (-self.fpa_sen_size / 2, -focus_position), 2 * self.fpa_sen_size / 2, -self.fpa_sen_thickness, color="k")
        self.ax.add_patch(self.fpa_sen)

        self.arrow_down = matplotlib.patches.FancyArrow(
            self.l6_width / 2 + 10, 15, 0, -15, length_includes_head=True, head_width=3, head_length=5, color="k")
        self.ax.add_patch(self.arrow_down)
        self.arrow_up = matplotlib.patches.FancyArrow(
            self.l6_width / 2 + 10, -focus_position - 15, 0, 15, length_includes_head=True, head_width=3, head_length=5,
            color="k")
        self.ax.add_patch(self.arrow_up)

        self.ax.plot([self.l6_width / 2, self.l6_width / 2 + 20],
                     [-focus_position, -focus_position], "--", color="gray", linewidth=1)

        self.focus_position_annotation = self.ax.annotate("$\Delta$ z = {:.2f} mm".format(
            focus_position), (self.l6_width / 2 + 30, -focus_position / 2), color='k', fontsize=10, va='center')

        self.draw()


class FocusPositionWidget(QGroupBox):

    def __init__(self):
        """ Initialisation of a plot showing L6 and FPA_SEN."""

        super(FocusPositionWidget, self).__init__("Focus Position")

        self.setStatusTip("Current focus position, as commanded via the hexapod")
        self.setFont(FONT)

        layout = QGridLayout()

        self.focus_position = FocusPosition()
        layout.addWidget(self.focus_position)
        self.setLayout(layout)

    def update_plot(self, focus_position):
        """
        Update the distance between L6S2 and FPA_SEN.

        :focus_position: Distance between L6S2 and FPA_SEN to display [mm].
        """

        self.focus_position.update_plot(focus_position)
