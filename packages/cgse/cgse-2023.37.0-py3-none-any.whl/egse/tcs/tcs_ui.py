"""
A simple GUI which allows to inspect the TCS EGSE configuration and housekeeping.

The GUI window consists of a tabbed view with two tabs.

The Configuration tab shows the configuration at the time the GUI was started or the tab was
reloaded. The Housekeeping tab shows all the housekeeping values. Whenever a tabs is selected,
the content is refreshed.

!!! note
    If you want to use the Configuration tab or the Housekeeping tab, the TCS EGSE must be in
    Remote Control mode. Use the remote control button in the toolbar.

"""
import logging
import multiprocessing
from pathlib import Path

import sys
import warnings
from collections import namedtuple
from enum import Enum

multiprocessing.current_process().name = "tcs_ui"

from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer, QLockFile
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from rich.console import Console
from rich.table import Table

from egse.control import Failure
from egse.gui.buttons import ToggleButton
from egse.gui.buttons import TouchButton
from egse.observer import Observable
from egse.observer import Observer
from egse.resource import get_resource
from egse.tcs.tcs import TCSProxy
from egse.tcs.tcs import is_tcs_cs_active

MODULE_LOGGER = logging.getLogger(__name__)

CONFIGURATION_TAB = "Configuration"
HOUSEKEEPING_TAB = "Housekeeping"

ScrollableTextBox = namedtuple("ScrollableTextBox", ["scroll", "text_box"])


class Actions(Enum):
    REFRESH_TAB = "refresh-tab"
    CLEAR_POPUP = "clear-popup"


class TCSUIModel:
    def __init__(self):
        super().__init__()

        # FIXME: shall we do some checking for exceptions here?
        self.device = TCSProxy()

    def read_configuration(self) -> dict:
        return self.device.get_configuration()

    def read_all_housekeeping(self):
        return  self.device.get_all_housekeeping()


class TCSUIView(QMainWindow, Observable):

    def __init__(self):
        super().__init__()

        self.setGeometry(600, 100, 1000, 900)
        self.setWindowTitle('TCS EGSE Viewer')

        self.setStatusBar(QStatusBar(self))
        self.status = self.statusBar()

        # Instance variables defined and used in the create methods below

        self.cs_connection = None
        self.device_connection = None
        self.start_task_button = None
        self.remote_control_button = None
        self.reload_button = None
        self.clear_button = None
        self.toolbar = None

        self.text_tabs = {
            CONFIGURATION_TAB: self.create_scrollable_text_box(CONFIGURATION_TAB),
            HOUSEKEEPING_TAB: self.create_scrollable_text_box(HOUSEKEEPING_TAB)
        }

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(False)

        # self.tabs.currentChanged.connect(self.on_current_tab_changed)
        self.tabs.tabBarClicked.connect(self.on_current_tab_changed)

        self.tabs.addTab(self.text_tabs[CONFIGURATION_TAB].scroll, CONFIGURATION_TAB)
        self.tabs.addTab(self.text_tabs[HOUSEKEEPING_TAB].scroll, HOUSEKEEPING_TAB)

        self.setCentralWidget(self.tabs)

        self.create_toolbar()

    def create_toolbar(self):

        icon_width = icon_height = 42

        # Struct is used to add some fixed spacing between the icons

        strut = QWidget()
        strut.setFixedSize(5, 5)

        # spacer widget to help with aligning some buttons to the right

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # The Reconnect action is used to reconnect to the control server

        self.cs_connection = ToggleButton(
            name="CS-CONNECT",
            width=icon_width, height=icon_height,
            status_tip="connect-disconnect TCS EGSE control server.",
            selected=get_resource(":/icons/cs-connected.svg"),
            not_selected=get_resource(":/icons/cs-not-connected.svg"),
            disabled=get_resource(":/icons/cs-connected-disabled.svg")
        )
        self.cs_connection.clicked.connect(self.on_cs_connection_button_click)

        # The Reconnect action is used to reconnect the device

        self.device_connection = ToggleButton(
            name="DEVICE-CONNECT",
            width=icon_width, height=icon_height,
            status_tip="connect-disconnect the TCS EGSE device controller",
            selected=get_resource(":/icons/plugged.svg"),
            not_selected=get_resource(":/icons/unplugged.svg"),
            disabled=get_resource(":/icons/plugged-disabled.svg")
        )
        self.device_connection.clicked.connect(self.on_device_connection_button_click)

        with TCSProxy() as tcs:

            self.start_task_button = ToggleButton(
                name="START-TASK",
                width=icon_width, height=icon_height,
                status_tip="Start/stop task on the TCS EGSE.",
                selected=get_resource(":/icons/start-button.svg"),
                not_selected=get_resource(":/icons/stop-button.svg"),
                disabled=[
                    get_resource(":/icons/start-button-disabled.svg"),
                    get_resource(":/icons/stop-button-disabled.svg"),
                ]
            )
            self.start_task_button.clicked.connect(self.on_start_task_button_click)
            if isinstance(task_is_running := tcs.is_task_running(), Failure):
                self.start_task_button.disable()
            else:
                self.start_task_button.set_selected(not task_is_running)

            self.remote_control_button = ToggleButton(
                name="REMOTE-CONTROL",
                width=icon_width, height=icon_height,
                status_tip="(de-)Activate remote control on the TCS EGSE.",
                selected=get_resource(":/icons/remote-control-on.svg"),
                not_selected=get_resource(":/icons/remote-control-off.svg"),
            )
            self.remote_control_button.clicked.connect(self.on_remote_control_button_click)
            self.remote_control_button.set_selected(tcs.is_remote_operation_active())

        self.reload_button = TouchButton(
            name="RELOAD-TELEMETRY",
            width=32, height=32,
            status_tip="Reload the current view: Configuration or Housekeeping.",
            selected=get_resource(":/icons/repeat-blue.svg"),
        )
        self.reload_button.clicked.connect(self.on_reload_button_click)

        self.clear_button = TouchButton(
            name="CLEAR-MMI-ERROR",
            width=icon_width, height=icon_height,
            status_tip="Clear the red box error message on the MMI.",
            selected=get_resource(":/icons/cleaning.svg"),
        )
        self.clear_button.clicked.connect(self.on_clear_button_click)

        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.addWidget(self.device_connection)
        self.toolbar.addWidget(self.cs_connection)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.start_task_button)
        self.toolbar.addWidget(strut)
        self.toolbar.addWidget(self.remote_control_button)
        self.toolbar.addWidget(strut)
        self.toolbar.addWidget(self.reload_button)
        self.toolbar.addWidget(spacer)
        self.toolbar.addWidget(self.clear_button)

        self.toolbar.setStyleSheet("padding: 5px;")

        # self.toolbar.setStyleSheet("padding-top: 10px; "
        #                            "padding-bottom: 10px;")

        self.addToolBar(self.toolbar)

    def on_current_tab_changed(self, tab_nr):
        if tab_nr == -1:
            return
        tab_name = self.tabs.tabText(tab_nr)
        self.actionObservers({Actions.REFRESH_TAB: (tab_nr, tab_name)})

    def on_cs_connection_button_click(self):
        MODULE_LOGGER.info("Control Server connection button clicked, not yet implemented.")

    def on_device_connection_button_click(self):
        MODULE_LOGGER.info("Device connection button clicked, not yet implemented.")

    def on_clear_button_click(self):

        self.actionObservers({Actions.CLEAR_POPUP: None})

    def on_reload_button_click(self):
        """Update the view in the currently selected TAB."""

        tab_nr = self.tabs.currentIndex()
        tab_name = self.tabs.tabText(tab_nr)

        self.actionObservers({Actions.REFRESH_TAB: (tab_nr, tab_name)})

    def on_remote_control_button_click(self):

        if not is_tcs_cs_active():
            self.status.showMessage(
                "TCS EGSE Control Server is not active, check if the `tcs_cs` is running.",
                msecs=5000
            )
            return

        with TCSProxy() as tcs:
            if tcs.is_remote_operation_active():
                response = tcs.quit_remote_operation()
                self.remote_control_button.set_selected(False)
                self.start_task_button.disable()
            else:
                response = tcs.request_remote_operation()
                self.remote_control_button.set_selected(True)
                self.start_task_button.enable()

    def on_start_task_button_click(self):
        """Start / stop a task on the TCS EGSE.
        This is equivalent to pressing the Start/Stop button on the touch screen of the TCS EGSE.
        The device must be in remote control mode.
        """

        if not is_tcs_cs_active():
            self.status.showMessage(
                "TCS EGSE Control Server is not active, check if the `tcs_cs` is running.",
                msecs=5000
            )
            return

        with TCSProxy() as tcs:
            if not tcs.is_remote_operation_active():
                self.start_task_button.disable()
                self.status.showMessage(
                    "TCS EGSE is not in remote control mode, press the remote control button.",
                    msecs=5000
                )
                return

            if tcs.is_task_running():
                response = tcs.stop_task()
                # MODULE_LOGGER.info(f"stop_task: {response=}")
                self.start_task_button.set_selected(True)
            else:
                response = tcs.run_task()
                # MODULE_LOGGER.info(f"run_task: {response=}")
                self.start_task_button.set_selected(False)

    # TODO: should this function move into egse.gui?

    def create_scrollable_text_box(self, name: str) -> ScrollableTextBox:
        scroll = QScrollArea()
        scroll.setObjectName(name)
        widget = QWidget()
        vbox = QVBoxLayout()

        text_box: QTextEdit = QTextEdit()
        text_box.setReadOnly(True)
        monospaced_font = QFont("Courier New")
        monospaced_font.setStyleHint(QFont.Monospace)
        text_box.setFont(monospaced_font)
        text_box.setLineWrapMode(QTextEdit.NoWrap)
        vbox.addWidget(text_box)

        widget.setLayout(vbox)

        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        return ScrollableTextBox(scroll, text_box)

    def get_tab_nr(self, tab_name: str) -> int:
        """Find the index for the TAB with the given name."""
        for index in range(self.tabs.count()):
            if tab_name == self.tabs.tabText(index):
                return index

    def set_text_for_tab(self, tab_id: str, text: str, preserve_scroll: bool = True):
        """Set the text in the TAB with tab_id. The TAB is expected to be a ScrollableTextBox.

        Args:
            tab_id: the identification for the TAB. This is the name of the TAB.
            text: the replacement text to be shown in the TAB
            preserve_scroll: show the test from the start or preserve the current scroll position
        """

        widget: ScrollableTextBox = self.text_tabs[tab_id]
        text_box: QTextEdit = widget.text_box

        if preserve_scroll:
            vsb = text_box.verticalScrollBar()
            old_pos_ratio = vsb.value() / (vsb.maximum() or 1)

            text_box.setText(text)

            vsb.setValue(round(old_pos_ratio * vsb.maximum()))
        else:
            text_box.setText(text)


class TCSUIController(Observer):
    def __init__(self, model: TCSUIModel, view: TCSUIView):
        super().__init__()
        self._model = model
        self._view = view
        self._view.addObserver(self)

        self.hk_capture_timer = None
        self.remote_button_update_timer = None

        self.update_housekeeping_view()
        self.update_configuration_view()

        self.create_timer()

    def update(self, changed_object):
        pass

    def do(self, actions):

        for action, value in actions.items():
            # MODULE_LOGGER.info(f"Action requested: do {action} with {value=}")
            if action == Actions.REFRESH_TAB:
                self.do_refresh_tab(tab_nr=value[0], tab_name=value[1])
            elif action == Actions.CLEAR_POPUP:
                self.do_clear_popup()

    def do_refresh_tab(self, tab_nr: int, tab_name: str):
        if tab_name == CONFIGURATION_TAB:
            self.update_configuration_view()
            self.stop_timer()
        elif tab_name == HOUSEKEEPING_TAB:
            self.update_housekeeping_view()
            self.start_timer()
        else:
            warnings.warn(
                f"Unknown TAB name passed into the refresh method in the UI Controller {tab_name}.")

    def do_clear_popup(self):
        if not is_tcs_cs_active():
            return

        with TCSProxy() as tcs:
            if tcs.is_remote_operation_active():
                tcs.clear_popup()

        self._view.status.showMessage("Popup has been cleared on MMI.", 2000)

    def update_configuration_view(self):

        if not is_tcs_cs_active():
            self._view.set_text_for_tab(
                CONFIGURATION_TAB,
                "TCS EGSE Control Server is not active, check if the `tcs_cs` is running."
            )
            return

        tcs_conf = self._model.read_configuration()

        if isinstance(tcs_conf, Failure):
            self._view.set_text_for_tab(
                CONFIGURATION_TAB,
                "Could not retrieve the configuration of the TCS EGSE.\n"
                "Check if the TCS EGSE is in Remote Control mode."
            )
            return

        table = Table(title="Configuration Parameters")

        table.add_column("Name", justify="left", style="cyan", no_wrap=True)
        table.add_column("Value", justify="right", style="green")

        for name, value in sorted(tcs_conf.items()):
            table.add_row(name, value)

        console = Console(force_terminal=False, force_jupyter=False)
        with console.capture() as capture:
            console.print(table)
        text = capture.get()

        self._view.set_text_for_tab(CONFIGURATION_TAB, text, preserve_scroll=True)

    def update_housekeeping_view(self):

        if not is_tcs_cs_active():
            self._view.set_text_for_tab(
                HOUSEKEEPING_TAB,
                "TCS EGSE Control Server is not active, check if the `tcs_cs` is running."
            )
            return

        all_hk = self._model.read_all_housekeeping()

        if isinstance(all_hk, Failure):
            logging.warning(f"Communication error: {all_hk}")
            self._view.status.showMessage("Communication failure with TCS EGSE", 5000)
            self._view.set_text_for_tab(
                HOUSEKEEPING_TAB,
                "Could not retrieve housekeeping from the TCS EGSE.\n"
                "Check if the TCS EGSE is in Remote Control mode."
            )
            return

        table = Table(title="All Housekeeping parameters", width=120)

        table.add_column("Timestamp", justify="center", style="black", no_wrap=True)
        table.add_column("Name", justify="left", style="cyan", no_wrap=True)
        table.add_column("Value", justify="right", style="green", no_wrap=False)

        for hk_entry in all_hk:
            try:
                table.add_row(hk_entry[0], hk_entry[1], hk_entry[2])
            except IndexError:
                # FIXME: view should have a method for this
                self._view.status.showMessage('Incorrect format for housekeeping data', 2000)
                logging.warning(f"Incorrect format for housekeeping data: {hk_entry=}")

        console = Console(width=120, force_terminal=False, force_jupyter=False)
        with console.capture() as capture:
            console.print(table)
        text = capture.get()

        self._view.set_text_for_tab(HOUSEKEEPING_TAB, text, preserve_scroll=True)

    def update_state_of_buttons(self):

        if not is_tcs_cs_active():
            return

        with TCSProxy() as tcs:
            self._view.remote_control_button.set_selected(tcs.is_remote_operation_active())
            if tcs.is_remote_operation_active():
                task_is_running = tcs.is_task_running()
                if isinstance(task_is_running, Failure):
                    self._view.status.showMessage(task_is_running.message, 2000)
                    self._view.start_task_button.disable()
                else:
                    self._view.start_task_button.enable()
                    self._view.start_task_button.set_selected(not task_is_running)

    def create_timer(self):
        """Create a Timer that will update the Housekeeping every second."""

        self.hk_capture_timer = QTimer()

        self.hk_capture_timer.timeout.connect(self.update_housekeeping_view)
        self.hk_capture_timer.setInterval(10000)

        self.remote_button_update_timer = QTimer()
        self.remote_button_update_timer.timeout.connect(self.update_state_of_buttons)
        self.remote_button_update_timer.setInterval(500)  #
        self.remote_button_update_timer.start()

    def start_timer(self):
        self.hk_capture_timer.start()

    def stop_timer(self):
        self.hk_capture_timer.stop()


def main():

    if not is_tcs_cs_active():
        print("ERROR: TCS CS is not active, "
              "start the TCS control server before launching this GUI.")
        sys.exit(1)

    lock_file = QLockFile(str(Path("~/tcs_ui.app.lock").expanduser()))

    app_logo = get_resource(":/icons/logo-tcs.svg")

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(app_logo)))

    if lock_file.tryLock(100):

        view = TCSUIView()
        model = TCSUIModel()

        TCSUIController(model, view)

        view.show()

        return app.exec()
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The TCS GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()


if __name__ == '__main__':
    sys.exit(main())
