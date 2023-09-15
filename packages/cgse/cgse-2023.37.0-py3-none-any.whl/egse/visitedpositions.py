"""
This module provides a GUI to show the visited positions (i.e. the positions at which 
the source was put during testing) on the focal plane.

To start the GUI, start (i)python and type the following commands:

    $ from egse import visitedpositions
    $ view = visitedpositions.start_visited_positions_gui()

Then you can add the visited locations as follows:

    * in focal-plane coordinates (x_fp, y_fp) [mm]:
        $ view.visit_focal_plane_position(x_fp, y_fp)

    * in CCD coordinates (row, column) [pixel] on a given CCD:
        $ view.visit_ccd_position(row, column, ccd_code)

    * in field angles (theta, phi) [degrees]:
        $ view.visit_field_angles(theta, phi)

At each of these locations, a red dot will appear on the plot.  You can 
switch between coordinate system (used in the plot) with the combobox
below the plot window (focal-plane coordinates, pixel coordinates, and
field angles).
"""
import pickle
import threading
from pathlib import Path

import sys
import zmq
from PyQt5.QtCore import QLockFile
from PyQt5.QtGui import (QFont, QIcon)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFrame, QVBoxLayout, QStatusBar, QMessageBox)

from egse.coordinates import ccd_to_focal_plane_coordinates, angles_to_focal_plane_coordinates, \
    focal_plane_coordinates_to_angles
from egse.gui.buttons import ToolTouchButton
from egse.gui.focalplane import FocalPlaneWidgetWithVisitedPositions
from egse.resource import get_resource
from egse.settings import Settings
from egse.zmq_ser import bind_address, connect_address

FONT = QFont("Helvetica", 18)

SETTINGS = Settings.load("Visited Positions UI")


class VisitedPositionsUIController:

    def __init__(self, view):
        """ Create a controller for the visited-positions GUI.

        Args:
            - view: Visited-positions GUI.
        """

        super(VisitedPositionsUIController, self).__init__()

        self.view = view

        thread = threading.Thread(target=self.listen)
        thread.daemon = True
        thread.start()

    def listen(self):
        """ Listen on the PULL socket for visited positions.

        If a visited position is received over the PULL socket, a red dot is placed at that position in the GUI.
        """

        context = zmq.Context.instance()
        socket = context.socket(zmq.PULL)

        socket.bind(self.get_bind_address)

        while True:

            pickle_string = socket.recv()
            data = pickle.loads(pickle_string)

            if isinstance(data, dict):

                if "theta" in data and "phi" in data:
                    self.visit_field_angles(data)

            elif data == "clear":
                self.clear()

    def visit_field_angles(self, data):
        """ Add a red dot at the given position on the focal-plane plot.

        Args:
            - data: Dictionary with the following entries:
                - theta: Gnomonic distance to the optical axis [degrees]
                - phi: In-field angle [degrees]
        """

        theta = data["theta"]
        phi = data["phi"]

        self.view.visit_field_angles(theta, phi)

    def clear(self):
        """ Clear all visited positions from the focal-plane plot."""

        self.view.clear_visited_positions()

    @property
    def get_bind_address(self):
        """ Returns bind address for the PULL socket.

        Returns: Bind address for the PULL socket.
        """

        return bind_address(SETTINGS.PROTOCOL, SETTINGS.PORT,)


class VisitedPositionsUIView(QMainWindow):

    def __init__(self):
        """ Open a window and initialise the GUI.

        The focal plane is shown, together with a blue circle indicating the size of the field-of-view, and a red dots
        indicating the positions that were visited so far.  Below this plot, you can find a combobox to switch between
        coordinate systems (focal-plane coordinates, pixel coordinates, and field angles).
        """

        super().__init__()

        self.setGeometry(300, 300, 1500, 1000)
        self.setWindowTitle("Visited-Positions GUI")

        self.init_ui()

        self.thread = None

        self.num_points = 0

    def init_ui(self):
        """ Initialisation of the GUI.

        The focal plane is shown, together with a blue circle indicating
        the size of the field-of-view, and a red dots indicating the positions that were visited so far.
        Below this plot, you can find a combobox to switch between coordinate systems (focal-plane coordinates,
        pixel coordinates, and field angles).
        """

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        # Statusbar

        self.setStatusBar(QStatusBar(self))
        self.status = self.statusBar()

        # Toolbar

        self.create_toolbar()

        # Central widget

        vbox_right = QVBoxLayout()

        vbox_right.addWidget(self.create_focal_plane_widget())

        app_frame.setLayout(vbox_right)

        self.setCentralWidget(app_frame)

    #########
    # Toolbar
    #########

    def create_toolbar(self):
        """ Create toolbar.

        Currently doesn't do anything.
        """
        self.clear_button = ToolTouchButton(
            name="clear_visited_positions",
            width=25, height=25,
            status_tip="Clear the visited positions",
            selected=get_resource(":/icons/sponge.svg"),
        )
        self.clear_button.clicked.connect(self.clear_visited_positions)

        # image_location = os.environ["PLATO_COMMON_EGSE_PATH"] + \
        #     "/src/egse/images/"

        # self.undo_pix = QPixmap(
        #     image_location + "undo.png").scaledToHeight(30, 1)
        #
        # self.undo_icon = QLabel()
        # self.undo_icon.setPixmap(self.undo_pix)
        #
        # # TODO Assign action to this button
        #
        # # Putting everything in place
        #
        self.toolbar = self.addToolBar('MainToolbar')
        self.toolbar.addWidget(self.clear_button)

        return self.toolbar

    ####################
    # Focal-plane widget
    ####################

    def create_focal_plane_widget(self):
        """ Create widget showing the position of the source in the focal plane.
        """

        self.focal_plane = FocalPlaneWidgetWithVisitedPositions()
        return self.focal_plane

    ###################
    # Visit position(s)
    ###################

    def visit_field_angles(self, theta, phi):
        """ Add a red dot at the given position on the focal-plane plot.

        Args:
            - theta: Angular distance from the optical axis [degrees].
            - phi: In-field angle [degrees].
        """

        # Conversion from field angles to focal-plane coordinates

        x_fp, y_fp = angles_to_focal_plane_coordinates(theta, phi)

        self.visit_focal_plane_position(x_fp, y_fp)

    def visit_focal_plane_position(self, x_fp, y_fp):
        """ Add a red dot at the given position on the focal-plan plot.

        Args:
            - x_fp: Focal-plane x-coordinate [mm].
            - y_fp: Focal-plane y-coordinate [mm].
        """

        self.focal_plane.visit_position(x_fp, y_fp)

        self.num_points += 1

    def visit_ccd_position(self, row, column, ccd_code):
        """ Add a red dot at the given position on the focal-plane plot.

        Args:
            - row: Row coordinate [pixels].
            - column: Column coordinate [pixels].
            - ccd_code: Code of the CCD [1, 2, 3, 4].
        """

        # Conversion from CCD coordinates to focal-plane coordinates

        x_fp, y_fp = ccd_to_focal_plane_coordinates(row, column, ccd_code)
        
        self.visit_focal_plane_position(x_fp, y_fp)

    ##########
    # Clearing
    ##########

    def clear_visited_positions(self):
        """ Clear all visited positions."""

        self.focal_plane.clear_visited_positions()

###########
# Start GUI
###########


def start_visited_positions_gui():
    """ Start the GUI showing the focal plane with the visited positions.
    You can add extra visited locations as follows (assuming "view" is the name of the GUI instance)

        * in focal-plane coordinates (x_fp, y_fp) [mm]:
            $ view.visit_focal_plane_position(x_fp, y_fp)

        * in pixel coordinates (row, column) [pixel] on a given CCD:
            $ view.visit_ccd_position(row, column, ccd_code)

        * in field angles (theta, phi) [degrees]:
            $ view.visit_field_angles(theta, phi)
    """

    app = QApplication([])

    view = VisitedPositionsUIView()

    view.show()

    return view


def _send_data(data):
    """ Send the given data to the visited-positions UI.

    Args:
        - data: Data to send to the visited-positions UI.
    """

    context = zmq.Context.instance()
    socket = context.socket(zmq.PUSH)

    protocol = SETTINGS.PROTOCOL
    hostname = SETTINGS.HOSTNAME
    port = SETTINGS.PORT

    socket.connect(connect_address(protocol, hostname, port))

    pickle_string = pickle.dumps(data)

    socket.send(pickle_string)
    socket.close()


def clear_visited_positions():
    """ Clear the visited positions from the visited-positions UI."""

    data = "clear"
    _send_data(data)


def visit_field_angles(theta, phi):
    """ Show the given position in the visited-positions GUI.

    Args:
        - theta: Angular distance from the optical axis [degrees].
        - phi: Angle from the x-axis of the focal plane (i.e. in-field angle) [degrees].
    """

    data = {"theta": theta, "phi": phi}
    _send_data(data)


def visit_focal_plane_position(x_fp, y_fp):
    """ Show the given position in the visited-positions GUI.

    Args:
        - x_fp: Focal-plane x-coordinate [mm].
        - y_fp: Focal-plan y-coordinate [mm].
    """

    # Convert to field angles

    theta, phi = focal_plane_coordinates_to_angles(x_fp, y_fp)
    visit_field_angles(theta, phi)


def visit_ccd_position(row, column, ccd_code):
    """ Show the given position in the visited positions GUI.

    Args:
        - row: Row coordinate [pixels].
        - column: Column coordinate [pixels].
        - ccd_code: Code of the CCD for which the pixel coordinates are given.
    """

    # Convert to focal-plane coordinates

    x_fp, y_fp = ccd_to_focal_plane_coordinates(row, column, ccd_code)
    visit_focal_plane_position(x_fp, y_fp)


def main():
    """ Main method to launch the Process Manager GUI."""

    lock_file = QLockFile(str(Path("~/visited_positions_ui.app.lock").expanduser()))

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(get_resource(":/icons/radar.svg"))))

    if lock_file.tryLock(100):
        # Check whether the Process Manager CS is running
        # (show a warning in a pop-up window if it's not)

        view = VisitedPositionsUIView()
        controller = VisitedPositionsUIController(view)

        view.show()

        return app.exec_()
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The Visited-Positions GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()


if __name__ == '__main__':
    sys.exit(main())
