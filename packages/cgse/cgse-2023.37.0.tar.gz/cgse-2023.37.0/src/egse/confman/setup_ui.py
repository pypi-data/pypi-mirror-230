import logging
from pathlib import Path

import sys
from PyQt5.QtCore import Qt, QLockFile
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QAction, QListWidget, QMessageBox
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtWidgets import QVBoxLayout
from rich.console import Console

from egse.config import find_file
from egse.config import get_common_egse_root
from egse.confman import ConfigurationManagerProxy
from egse.control import Failure
from egse.gui import show_warning_message, VLine, show_info_message
from egse.resource import get_resource
from egse.settings import Settings
from egse.system import replace_environment_variable

logging.basicConfig(level=logging.INFO, format=Settings.LOG_FORMAT_FULL)

LOGGER = logging.getLogger(__name__)

SITE = Settings.load("SITE")["ID"]


class SetupUIView(QMainWindow):

    def __init__(self):
        """ Initialisation of the GUI to inspect the available setups.

        The components are placed in the window:
            - on the left-hand side: filtering of the setups + list with the setups that meet the conditions from the
              filter;
            - right-hand side: tabs with setup that were opened for visual inspection.
        """

        super().__init__()

        self.setGeometry(300, 300, 1200, 1000)

        cm_ctrl_settings = Settings.load("Configuration Manager Control Server")
        location = replace_environment_variable(cm_ctrl_settings.FILE_STORAGE_LOCATION)
        self._data_conf_location = Path(location) if location else get_common_egse_root()

        self.setWindowTitle(f"Available Setups ({self._data_conf_location})")

        # Build up the GUI

        self.toolbar = self.addToolBar("MainToolbar")

        self.filter = QLineEdit()
        self.filter_list = QListWidget()
        self.tabbed_widget = QTabWidget()

        self.init_ui()

        # Keep track of which setups have been opened in a tab

        self.open_tabs = []

    def resizeEvent(self, event):
        """ Re-sizing of the main window.

        Args:
            - event: Re-size event.
        """

        QMainWindow.resizeEvent(self, event)
        self.filter_list.setMinimumSize(self.width() / 2 - 50, self.height() - 200)

    def init_ui(self):
        """ Put the components in the GUI window.

        The GUI comprises the following components:
            - on the left-hand side: filtering of the setups + list with the setups that meet the conditions from the
              filter;
            - right-hand side: tabs with setup that were opened for visual inspection.
        """

        # Creating the content

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        self.create_toolbar()
        self.create_statusbar()

        # Left-hand side: filtering + drop-down menu

        lhs_layout = QVBoxLayout()
        lhs_frame = QFrame()

        filter_widget = self.make_filter_widget()
        self.update_list()

        lhs_layout.addWidget(filter_widget)
        lhs_layout.addWidget(self.filter_list)

        lhs_layout.addStretch()
        lhs_frame.setLayout(lhs_layout)

        # Right-hand side: tabs

        self.make_tabbed_widget()

        # Put everything together

        layout = QHBoxLayout()
        splitter = QSplitter(Qt.Horizontal)

        splitter.addWidget(lhs_frame)
        splitter.addWidget(self.tabbed_widget)
        splitter.setSizes([500, 1000])

        layout.addWidget(splitter)
        app_frame.setLayout(layout)

        self.setCentralWidget(app_frame)

    def create_toolbar(self):
        """ Configure the toolbar.

        The toolbar comprises a single button that allows you to load the setup that is shown in the active tab.
        """

        load_setup_pix = QPixmap(str(find_file("load.png", in_dir="images")))
        load_setup_icon = QIcon()
        load_setup_icon.addPixmap(load_setup_pix, QIcon.Normal, QIcon.On)

        load_setup_action = QAction(load_setup_icon, "Load the current setup", self)
        load_setup_action.setStatusTip("Load setup shown in the active tab.")
        load_setup_action.setCheckable(False)
        load_setup_action.triggered.connect(self.load_setup)

        self.toolbar.addAction(load_setup_action)

        return self.toolbar

    def create_statusbar(self):
        """ Create a status bar.

        Returns: Status bar.
        """

        self.statusBar().setStyleSheet("border: 0; background-color: #FFF8DC;")
        self.statusBar().setStyleSheet("QStatusBar::item {border: none;}")
        self.statusBar().addPermanentWidget(VLine())

    def load_setup(self):
        """Load the setup that is shown in the active tab. """

        current_widget = self.tabbed_widget.currentWidget()

        if current_widget is None:

            description = "No setup selected."
            info_text = "You can view setup files by selecting them in the list.  They will be opened in " \
                        + "individual tabs on the right-hand side.  \n\nTo be able to load a specific setup, bring " \
                        + "the corresponding tab into focus."

            show_warning_message(description, info_text=info_text)

        else:

            site, setup_id = current_widget.accessibleName().split(" ")

            if site == SITE:

                try:

                    with ConfigurationManagerProxy() as cm:

                        load_result = cm.load_setup(int(setup_id))

                        if isinstance(load_result, Failure):

                            description = f"Setup {setup_id} could not be loaded for {site}"
                            info_text = load_result.message

                            show_warning_message(description, info_text=info_text)

                        else:

                            description = f"Loaded setup {setup_id} for {site}"
                            show_info_message(description)

                except ConnectionError:

                    description = "Connection with Configuration Manager was lost."
                    info_text = "Check the status of the core services (and re-start when necessary)"
                    show_warning_message(description, info_text=info_text)

            else:

                description = "Wrong site ID."
                info_text = f"The site ID mentioned in the setup file ({site}) does not match the site you are at " \
                            + "f({SITE}), according to the settings file.  Therefore, loading this setup was prevented."
                show_warning_message(description, info_text=info_text)

    def make_filter_widget(self):
        """ Make widget where the available setups can be filtered:

        This widgets consists of the following elements:
            - text field in which the filter can be specified: when the return key is pressed, the filter is applied
              (i.e. all tabs are closed and the drop-down menu is updated);
            - search button: when this is pressed, the filter is applied (i.e. all tabs are closed and the list is
              updated);
            - clear button: when this is pressed, the filter is cleared (i.e. all tabs are closed and the list is
              updated).
        """

        layout = QHBoxLayout()

        widget = QGroupBox("Filter", self)

        # Text field for the filter

        self.filter.returnPressed.connect(self.apply_filter)
        self.filter.setStatusTip("Filtering of available setups, e.g. " +
                                 "site_id=\"CSL\", gse.hexapod.ID=2, camera.model=\"STM\".")
        layout.addWidget(self.filter)

        # Search button

        search_icon = QIcon(str(find_file("search.png", in_dir="images")))
        search_button = QPushButton()
        search_button.setIcon(search_icon)
        search_button.setStatusTip("Apply filter (alternatively hit return key in the text field).")
        search_button.clicked.connect(self.apply_filter)

        layout.addWidget(search_button)

        # Clear button

        clear_icon = QIcon(str(find_file("cross.svg", in_dir="images")))
        clear_button = QPushButton()
        clear_button.setIcon(clear_icon)
        clear_button.setStatusTip("Clear filter.")
        clear_button.clicked.connect(self.clear_filter)

        layout.addWidget(clear_button)

        widget.setLayout(layout)

        # Make the drop-down menu listen to selections

        self.filter_list.currentTextChanged.connect(self.view_setup)
        self.filter_list.setStatusTip(f"All available setups in {self._data_conf_location} "
                                      f"that meet the filter condition(s).")

        return widget

    def make_tabbed_widget(self):

        self.tabbed_widget.setTabsClosable(True)
        self.tabbed_widget.tabCloseRequested.connect(self.close_tab)
        self.tabbed_widget.setMovable(False)
        self.tabbed_widget.setDocumentMode(True)
        self.tabbed_widget.setElideMode(Qt.ElideRight)
        self.tabbed_widget.setUsesScrollButtons(True)

        # Make sure it is clear which tab is currently selected

        self.tabbed_widget.setStyleSheet(
            """QTabBar::tab:selected{background: gray}""")

    def close_tab(self, current_index):
        """ Close the tab with the given index. """

        current_widget = self.tabbed_widget.widget(current_index)

        # Remember that the tab has been closed

        self.open_tabs.remove(current_widget.accessibleName())

        current_widget.deleteLater()
        self.tabbed_widget.removeTab(current_index)

    def clear_filter(self):
        """ Clear the filter.

        The following actions are taken:
            - the text field with the filter is cleared;
            - the list needs to be updated (it should show all available setups again);
            - the tabs are cleared.
        """

        # Clear filter

        self.filter.setText("")
        self.filter.repaint()

        # Clear + re-build combobox

        self.filter_list.clear()
        self.update_list()
        self.filter_list.repaint()

        # Clear tabs

        self.clear_tabs()

    def clear_tabs(self):
        """ Clear the tabs.

        Clear the tabs on the right-hand side and clear the list of setups for which a tab was opened already.
        """

        self.tabbed_widget.clear()

        # Remember that all tabs were closed

        self.open_tabs.clear()

    def apply_filter(self):
        """ Apply the filter.

        The following actions are taken:
            - the list needs to be updated (it should only contain the setups that pass the filtering);
            - the tabs are closed.
        """

        # Clear + re-build combobox

        self.filter_list.clear()
        self.update_list()

        # Clear tabs

        self.clear_tabs()

    def update_list(self):

        self.filter_list.addItem(None)

        try:

            filter_dict = self.get_filter_dict()

            try:

                with ConfigurationManagerProxy() as cm:

                    setup_overview = cm.list_setups(**filter_dict)

                    for setup_id, setup_site, description, cam_id in setup_overview:
                        self.filter_list.addItem(f"{setup_site} {setup_id} {cam_id} – {description}")

            except ConnectionError:

                description = "Connection with Configuration Manager was lost."
                info_text = "Check the status of the core services (and re-start when necessary)"
                show_warning_message(description, info_text=info_text)

        except ValueError:

            description = "Invalid filter text"

            into_text = (
                "When using multiple filtering conditions, they should be comma-separated. \n"
                "Individual filtering conditions should follow the pattern key = value, where `key` should "
                "match the dot notation from the setup file (e.g. gse.hexapod.ID = 2)."
            )

            show_warning_message(description, into_text)

    def get_filter_dict(self):
        """ Convert the content of the filter text field to a dictionary.
        """

        filter_text = self.filter.text()
        filter_text = ''.join(filter_text.split())  # Get rid of any blanks

        # No filter was applied
        # Return an empty dictionary

        if filter_text == "":

            return {}

        else:

            # Split by search term (comma-separated)

            filter_dict = dict(e.split('=') for e in filter_text.split(', '))

            for key, value in filter_dict.items():

                try:

                    # Integer should be integers (not strings)

                    filter_dict[key] = int(value)

                except ValueError:

                    # Get rid of the quotes

                    filter_dict[key] = value[1:-1]

                # Allow for dot-navigation

                key.replace(".", "__")

            return filter_dict

    def view_setup(self, value: str):
        """ Show the setup that was selected in the drop-down menu, in a tab.

        Args:
            - value: Selected value from the drop-down menu, which contains the site and setup identifier.
        """

        if value != "":

            site, setup_id, _ = value.split(" ", 2)

            # Tab already open

            if (site + " " + setup_id) in self.open_tabs:

                return
            
            self.open_setup_tab(setup_id, site)

    def open_setup_tab(self, setup_id, setup_site):
        """ Show the setup file with the given filename in a tab.

        Args:
            - filename: Filename of the setup to show in a tab.
        """

        setup_tab = QGroupBox()
        layout = QVBoxLayout()
        setup_tab.setLayout(layout)

        # Setup

        setup_text = QTextBrowser()

        with ConfigurationManagerProxy() as cm:
            setup = cm.get_setup(setup_id=int(setup_id))

        console = Console(width=120, force_terminal=False, force_jupyter=False)
        with console.capture() as capture:
            console.print(setup)
        text = capture.get()
        setup_text.setText(text)

        # setup_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # setup_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        layout.addWidget(setup_text)

        tab_name = setup_site + " " + setup_id
        setup_tab.setAccessibleName(tab_name)
        # setup_tab.setStatusTip(f"Setup for {filename}.")
        self.tabbed_widget.addTab(setup_tab, tab_name)

        # Bring the new tab into focus

        self.tabbed_widget.setCurrentIndex(self.tabbed_widget.count() - 1)

        # Remember that a tab was opened for this setup

        self.open_tabs.append(tab_name)


# class SetupUIModel:
#
#     def __init__(self):
#         """ Initialisation of the Process Manager UI model."""
#
#         try:
#
#             self.configuration_manager = ConfigurationManagerProxy()
#
#         except ConnectionError:
#
#             self.configuration_manager = None
#
#     def is_connected(self):
#         """ Checks whether the Process Manager Control Server is active.
#
#         Checks whether a connection to the Process Manager Control Server has been established.
#
#         Returns:
#             - True if a connection to the Process Manager Control Server has been established; False otherwise.
#         """
#
#         return self.configuration_manager.ping() and self.configuration_manager.is_cs_connected()
#
#
# class SetupUIController:
#
#     def __init__(self, model: SetupUIModel,
#                  view: SetupUIView):
#         """ Initialisation of the Controller for the Process Manager GUI.
#         Args:
#             - model: Process Manager UI model.
#             - view: Process Manager UI view.
#         """
#
#         self.model = model
#         self.view = view
#
#
#
#     def update(self, changed_object):
#         """ Define button press actions for the toolbar.
#         Define which actions should be taken when which button (in the toolbar)
#         is pressed in the Process Manager GUI.  The following button are
#         available:
#             - starting all device Control Servers in the current setup;
#             - shutting down all device Control Servers in the current setup;
#             - showing pop-up window with an explanation about the process
#               status.
#         """
#
#         pass
#
#     def do(self):
#         pass
#

def main():
    """ Main method to launch the Setup GUI."""
    lock_file = QLockFile(str(Path("~/setup_ui.app.lock").expanduser()))

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(get_resource(":/icons/settings.svg"))))

    if lock_file.tryLock(100):
        # Check whether the Process Manager CS is running
        # (show a warning in a pop-up window if it's not)

        view = SetupUIView()

        view.show()

        return app.exec_()
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The setup GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()


if __name__ == '__main__':
    sys.exit(main())
