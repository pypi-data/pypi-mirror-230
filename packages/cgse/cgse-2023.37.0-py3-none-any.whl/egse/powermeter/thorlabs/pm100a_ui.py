"""
A Graphical User Interface for monitoring the Thorlabs PM100A Power Meter used during IAS TVAC.

.. todo:: put code in the __main__ section into a main() function, so this GUI
          can be called from another Python process/script.
"""
import argparse
import logging
import sys
from pathlib import Path

import pyqtgraph as pg
from PyQt5 import QtGui
from PyQt5.QtCore import QDateTime, QTimer, Qt, QLockFile
from PyQt5.QtGui import QFont, QIcon, QPalette, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
                             QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QMainWindow, QPushButton,
                             QSpinBox, QTextEdit, QToolButton, QVBoxLayout, QMessageBox)

from egse.gui.stripchart import StripChart
from egse.observer import Observable
from egse.observer import Observer
from egse.powermeter.thorlabs.pm100a import ThorlabsPM100Controller, ThorlabsPM100Proxy, ThorlabsPM100Simulator
from egse.resource import get_resource

from egse.settings import Settings
from egse.state import UnknownStateError
from egse.gui import show_warning_message
from prometheus_client import Gauge, Summary
from prometheus_client import start_http_server
from egse.process import ProcessStatus
import threading
from egse.system import do_every
from egse.config import find_file

MODULE_LOGGER = logging.getLogger(__name__)

SETTINGS = Settings.load("Thorlabs PM100 Controller")
FONT = QFont("Helvetica", 18)

GUI_SETTINGS = Settings.load("PM100A GUI")

class ThorlabsUIView(QMainWindow, Observable):
    def __init__(self):
        super().__init__()

        # Define those variables that we will need/use in different methods

        self.measure = None
        self.clear_action = None
        self.reconnect_action = None
        self.toolbar = None

        self.stripchart = None

        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle("Thorlabs Controller")

        self.init_gui()

    def createToolbar(self):
        image_location = Path(__file__).resolve().parent.parent.parent / "images"

        # The Reconnect action is used to reconnect the device or control server

        connected_pix = QPixmap(str(image_location / "connected-100.png"))
        disconnected_pix = QPixmap(str(image_location / "disconnected-100.png"))
        reconnect_icon = QIcon()
        reconnect_icon.addPixmap(connected_pix, QIcon.Normal, QIcon.On)
        reconnect_icon.addPixmap(disconnected_pix, QIcon.Normal, QIcon.Off)

        self.reconnect_action = QAction(reconnect_icon, "Reconnect", self)
        self.reconnect_action.setToolTip("Reconnect")
        self.reconnect_action.setCheckable(True)
        self.reconnect_action.triggered.connect(self.onClick)

        self.toolbar = self.addToolBar("MainToolbar")
        self.toolbar.addAction(self.reconnect_action)

        return self.toolbar

    def create_channel_group(self):

        group_box = QGroupBox("Thorlabs PM100A")

        # Create the label fields that display the current measure

        grid_show = QGridLayout()

        grid_show.addWidget(QLabel("PM100A "), 0, 0)

        self.measure = QLabel(self)
        self.measure.setAlignment(Qt.AlignRight)
        self.measure.setText("0.000")

        self.measure.setFont(QtGui.QFont(self.measure.font().family(), 24))

        grid_show.addWidget(self.measure, 0, 1)

        grid_show.addWidget(QLabel(" W"), 0, 2)

        grid_show.setColumnStretch(1, 10)

        # Create the edit text field for setting the position

        self.stripchart = StripChart(
            labels={"left": ("measure", "W"), "bottom": ("Time", "d hh:mm:ss")}
        )
        self.stripchart.setInterval(60 * 60 * 12)  # 12h of data
        self.stripchart.set_yrange(0, 40)

        vbox = QVBoxLayout()

        vbox.addLayout(grid_show)
        vbox.addStretch(1)
        vbox.addWidget(self.stripchart)

        group_box.setLayout(vbox)

        return group_box

    def update_stripchart(self, time, value):
        if value > 10:
            value = 0
        else:
            pass
        self.stripchart.update(time, value)

    def update_value_field(self, value):
        if value > 10:
            self.measure.setText("Set to Autorange")
        # TODO: add zeroing (equivalent to ZERO!) warning when values are negative
        else:
            self.measure.setText(f"{value:.3E}")

    def initialize_values(self, average, wavelength, beam, autorange, autozero):
        "gets the parameter values on powermeter start up"
        self.average_value.setValue(average)
        self.autorange.setChecked(autorange["auto"])
        self.range_value.setText(f"{autorange['range']:.3E}" + " W")
        self.zero_set.setChecked(bool(autozero["set"]))
        index = self.wavelength_value.findText(str(int(wavelength)) + " nm")
        self.wavelength_value.setCurrentIndex(index)
        self.beam_value.setValue(round(beam, 1))

    def init_gui(self):

        # Switch to using white background and black foreground for pyqtgraph stripcharts

        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")

        # The main frame in which all the other frames are located, the outer Application frame

        app_frame = QFrame()
        app_frame.setObjectName("AppFrame")

        # configuration frame located on the right of the main frame
        configuration_frame = QFrame()
        configuration_frame.setObjectName("ConfigurationFrame")

        vbox_right = QVBoxLayout()

        #  AVERAGE WIDGETS

        self.set_average = QGridLayout()
        self.average_value = QSpinBox()
        self.average_value.setMinimum(1)
        self.average_value.setValue(1)
        self.average_label = QLabel("Average Measurements:")

        self.average_value.valueChanged.connect(self.SetAverage)

        self.set_average.addWidget(self.average_label, 0, 0, 1, 1)
        self.set_average.addWidget(self.average_value, 0, 1, 1, 1)

        vbox_right.addLayout(self.set_average)

        #  POWER RANGE WIDGETS

        self.set_range = QHBoxLayout()

        self.range_up = QToolButton()
        self.range_up.setArrowType(Qt.LeftArrow)
        self.range_up.setObjectName("down")
        self.range_value = QLabel()
        self.range_down = QToolButton()
        self.range_down.setArrowType(Qt.RightArrow)
        self.range_down.setObjectName("up")
        self.autorange = QCheckBox("Autorange")
        self.autorange.setObjectName("auto")

        self.range_up.clicked.connect(self.SetRange)
        self.range_down.clicked.connect(self.SetRange)
        self.autorange.toggled.connect(self.SetRange)

        self.set_range.addWidget(self.range_up)
        self.set_range.addWidget(self.range_value)
        self.set_range.addWidget(self.range_down)

        self.set_range.addWidget(self.autorange)

        vbox_right.addLayout(self.set_range)

        #  CORRECTION WAVELENGTH WIDGETS

        self.correction_wavelength = QHBoxLayout()

        self.wavelength_value = QComboBox()
        self.wavelength_value.addItems(
            ["532 nm", "535 nm", "635 nm", "785 nm", "800 nm", "830 nm", "980 nm", "1060 nm"]
        )  # puedes acceder a los indices luego
        self.wavelength_value.currentIndexChanged.connect(self.wavelength_changed)

        self.correction_wavelength_label = QLabel("Set correction wavelength:")
        self.correction_wavelength_label.setBuddy(self.wavelength_value)

        self.correction_wavelength.addWidget(self.correction_wavelength_label)
        self.correction_wavelength.addWidget(self.wavelength_value)

        vbox_right.addLayout(self.correction_wavelength)

        #  CORRECTION BEAM DIAMETER WIDGETS

        self.correction_beam = QHBoxLayout()

        self.beam_value = QDoubleSpinBox()
        self.beam_value.setMinimum(0.1)
        self.beam_value.setMaximum(9.4)
        self.beam_value.setSingleStep(0.1)
        self.beam_value.valueChanged.connect(self.beam_changed)

        self.beam_label = QLabel("Set correction beam diameter (mm):")

        self.correction_beam.addWidget(self.beam_label)
        self.correction_beam.addWidget(self.beam_value)

        vbox_right.addLayout(self.correction_beam)

        #  AUTOZERO WIDGETS

        self.autozero = QHBoxLayout()
        self.zero_set = QCheckBox("Set Autozero")
        self.zero_set.setObjectName("zero")
        self.zero_set.toggled.connect(self.SetAutozero)

        self.autozero.addWidget(self.zero_set)

        vbox_right.addLayout(self.autozero)

        #  GET CONFIGURATION WIDGETS

        # TODO:
        #   remove Get configuration button after validation of the widget, format dictionary
        #   into string
        self.GetConfig = QVBoxLayout()
        self.ConfigButton = QPushButton("Get configuration")
        self.ConfigButton.clicked.connect(self.update_configuration)
        self.ConfigText = QTextEdit()
        self.ConfigText.setContentsMargins(5, 5, 5, 5)

        self.GetConfig.addWidget(self.ConfigButton)
        self.GetConfig.addWidget(self.ConfigText)

        vbox_right.addLayout(self.GetConfig)

        vbox_right.setAlignment(Qt.AlignTop)

        # -------- PUTTING ALL TOGETHER ---------

        configuration_frame.setLayout(vbox_right)

        hbox = QHBoxLayout()
        self.createToolbar()
        hbox.addWidget(self.create_channel_group())
        hbox.addWidget(configuration_frame)

        app_frame.setLayout(hbox)

        self.setCentralWidget(app_frame)

    def set_style(self):
        """
        Set the style for the thorlabsUI Widget when it is connected to a real
        powermeter Controller (hardware).

        This will override the styles that were defined in the styles.qss style file
        that was loaded for the Application.
        """
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.Light)
        self.setStyleSheet(
            """
            QGroupBox {
                border: 1px solid lightGray;
                border-radius: 0px;
                margin-top: 0px;
                padding-top: 10px;
            }
            QGroupBox::title {
                background-color: transparent;
                padding-top: 0px;
                padding-left: 0px;
            }
        """
        )

    def set_style_simulator(self):
        """
        Set the style for the thorlabsUI Widget when it is connected to a
        powermeter Simulator.

        This will override the styles that were defined in the styles.qss style file
        that was loaded for the Application.
        """
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.Dark)
        self.setStyleSheet(
            """
            QGroupBox {
                border: 1px solid lightGray;
                border-radius: 0px;
                margin-top: 0px;
                padding-top: 10px;
            }
            QGroupBox::title {
                background-color: transparent;
                padding-top: 0px;
                padding-left: 0px;
            }
        """
        )

    def onClick(self):

        sender = self.sender()
        MODULE_LOGGER.debug(f"sender.text() = {sender.text()}")
        MODULE_LOGGER.debug(f"sender.isChecked() = {sender.isChecked()}")
        self.notifyObservers(sender)

    def wavelength_changed(self, i):
        "gets the index"
        wavelength = [532, 535, 635, 785, 800, 830, 980, 1060]
        self.actionObservers({"set_wavelength": wavelength[i]})

    def beam_changed(self, v):
        "gets beam diameter to be set"
        diameter = round(v, 1)
        self.actionObservers({"set_diameter": diameter})

    def update_configuration(self):
        self.actionObservers({"get_configuration": None})

    def update_configuration_value(self, configuration):
        autorange = configuration["Power Range"]
        autorange = autorange["range"]
        self.range_value.setText(f"{autorange:.3E}" + " W")
        self.ConfigText.setText(str(configuration))

    def SetRange(self):
        print("action")
        sender = self.sender()
        _range = None
        print(sender.objectName())
        if sender.objectName() == "up":
            print("up")
            self.autorange.setChecked(False)
            _range = sender.objectName()
        elif sender.objectName() == "down":
            print("down")
            self.autorange.setChecked(False)
            _range = sender.objectName()
        elif sender.objectName() == "auto":
            pass
        else:
            print("Power range could not be modified")
        auto = bool(self.autorange.checkState())
        print(auto)
        self.actionObservers({"set_range": [_range, auto]})

    def SetAverage(self):
        print(self.average_value.value())
        self.actionObservers({"set_average": self.average_value.value()})

    def SetAutozero(self):
        autozero = bool(self.zero_set.checkState())
        print(autozero)
        self.actionObservers({"set_zero": bool(self.zero_set.checkState())})

    def set_connection_state(self, state):

        if state == "connected":
            self.reconnect_action.setChecked(True)
        elif state == "disconnected":
            self.reconnect_action.setChecked(False)
        else:
            raise UnknownStateError(
                f"Unknown State ({state}), expected 'connected' or 'disconnected'."
            )


class ThorlabsUIModel:
    def __init__(self, type_):
        self.type = type_

        if self.type == "proxy":
            self.tl = ThorlabsPM100Proxy()
        elif self.type == "direct":
            self.tl = ThorlabsPM100Controller()
        elif self.type == "simulator":
            self.tl = ThorlabsPM100Simulator()
        else:
            raise Exception(
                f"Unknown type of Thorlabs implementation passed into the model: {type}"
            )

        if self.tl is not None:
            MODULE_LOGGER.debug(f"ThorlabsController initialized as {self.tl.__class__.__name__}")

    def has_commands(self):
        if self.type == "proxy":
            return self.tl.has_commands()
        return True

    def load_commands(self):
        if self.type == "proxy":
            self.tl.load_commands()

    def is_simulator(self):
        return self.tl.is_simulator()

    def is_connected(self):
        if self.type == "proxy":
            return self.tl.is_cs_connected()
        else:
            return self.tl.is_connected()

    def get_value(self):
        value = self.tl.get_value()
        return float(value)

    def get_configuration(self):
        "gets the powermeter parameter configuration"
        configuration = self.tl.get_config()
        return configuration

    def get_autozero(self):
        return self.tl.get_autozero()

    def get_diameter(self):
        return self.tl.get_diameter()

    def set_wavelength(self, wavelength):
        self.tl.set_wavelength(wavelength)

    def set_range(self, range, auto):
        self.tl.set_range(range_action=range, auto=auto)

    def set_average(self, average):
        self.tl.set_average(average=average)

    def set_diameter(self, diameter):
        self.tl.set_diameter(diameter)

    def set_zero(self, autozero):
        print(autozero)
        self.tl.set_zero(autozero=autozero)

    def reconnect(self):
        # I need a better insight in what could be wrong and how to reconnect
        # This is probably also dependent on Proxy or other Hexapod implementation

        if self.type == "proxy":
            self.tl.reconnect_cs()
            return self.tl.is_cs_connected()
        else:
            self.tl.reconnect()
            return self.tl.is_connected()
            #MODULE_LOGGER.warning("Don't know how to re-connect {self.tl.__class__.__name__}.")
            #return_code = False
        return False #return_code

    def disconnect(self):
        self.tl.disconnect()


class ThorlabsUIController(Observer):
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.addObserver(self)

        self._metrics = {
            "execution_time": Summary('ui_update_execution_time_seconds',
                                      'Time spent updating the values in the GUI', ["type"]),
            "pm_out": Gauge("power_meter_value", "pm_output")
        }

        self.create_timer()

        if self.model.is_connected():
            self.initialize_values()  # initializes to the GUI parameters to the values read from
            # the powermeter power meter

            if self.model.is_simulator():
                self.view.set_style_simulator()
            else:
                self.view.set_style()

            self.view.set_connection_state("connected")
            self.start_timer()
        else:
            self.stop_timer()
            self.view.set_connection_state("disconnected")

    def create_timer(self):
        """Create a Timer that will update the States every second."""

        self.states_capture_timer = QTimer()
        # This is only needed when the Timer needs to run in another Thread
        # self.states_capture_timer.moveToThread(self)
        self.states_capture_timer.timeout.connect(self.update_values)
        self.states_capture_timer.setInterval(200)

        self.stripchart_timer = QTimer()
        self.stripchart_timer.timeout.connect(self.update_stripchart)
        self.stripchart_timer.setInterval(200)

    def start_timer(self):
        self.states_capture_timer.start()
        self.stripchart_timer.start()

    def stop_timer(self):
        self.states_capture_timer.stop()
        self.stripchart_timer.stop()

    def update_values(self):

        # This method should not be called when not connected, by design!
        value = self.model.get_value()
        self.view.update_value_field(value)

    def update_stripchart(self):

        with self._metrics["execution_time"].labels(type="stripcharts").time():
            value = self.model.get_value()
            self.view.update_stripchart(QDateTime.currentMSecsSinceEpoch(), value)
            self._metrics["pm_out"].set(value)

    def initialize_values(self):
        "initializes to the GUI parameters to the values read from the powermeter power meter"
        configuration = self.model.get_configuration()
        average = configuration["Measurement"]
        average = average["Average number"]

        wavelength = configuration["Correction Wavelength (nm)"]
        beam = configuration["Beam diameter (mm)"]

        autorange = configuration["Power Range"]

        autozero = configuration["Autozero correction"]

        self.view.initialize_values(average, wavelength, beam, autorange, autozero)

    def update(self, changed_object):

        text = changed_object.text()

        if text == "Reconnect":

            if changed_object.isChecked():
                MODULE_LOGGER.debug("Reconnecting the PM100 model.")
                if self.model.reconnect():
                    self.view.set_connection_state("connected")
                    if not self.model.has_commands():
                        self.model.load_commands()
                    self.start_timer()
                else:
                    self.view.reconnect_action.setChecked(False)
            else:
                MODULE_LOGGER.debug("Disconnecting the PM100 model.")
                self.stop_timer()
                self.model.disconnect()
                self.view.set_connection_state("disconnected")

            return

        if text == "ClearErrors":
            self.model.clearError()

        if text == "Reset":
            pass

    def do(self, actions):

        for action, value in actions.items():
            MODULE_LOGGER.debug(f"do {action} with {value}")
            if action == "set_wavelength":
                wavelength = value
                print(wavelength)
                MODULE_LOGGER.debug(f"do: set_wavelength({wavelength}:{type(wavelength)})")
                self.model.set_wavelength(wavelength)
                configuration = self.model.get_configuration()
                print(configuration)
                self.view.update_configuration_value(configuration)

            if action == "set_diameter":
                diameter = value
                print(diameter)
                MODULE_LOGGER.debug(f"do: set_diameter({diameter}:{type(diameter)})")
                self.model.set_diameter(diameter)
                configuration = self.model.get_configuration()
                print(configuration)
                self.view.update_configuration_value(configuration)

            if action == "set_range":
                _range, auto = value
                MODULE_LOGGER.debug(f"do: set_range({_range}:{type(_range)}, {auto}:{type(auto)})")
                self.model.set_range(_range, auto)
                configuration = self.model.get_configuration()
                print(configuration)
                self.view.update_configuration_value(configuration)

            if action == "get_configuration":
                configuration = self.model.get_configuration()
                self.view.update_configuration_value(configuration)

            if action == "set_average":
                average = value
                MODULE_LOGGER.debug(f"do: set_average({average}:{type(average)})")
                self.model.set_average(average)
                configuration = self.model.get_configuration()
                print(configuration)
                self.view.update_configuration_value(configuration)

            if action == "set_zero":
                autozero = value
                print(autozero)
                MODULE_LOGGER.debug(f"do: set_zero({autozero}:{type(autozero)})")
                self.model.set_zero(autozero)
                configuration = self.model.get_configuration()
                print(configuration)
                self.view.update_configuration_value(configuration)


def parse_arguments():
    """
    Prepare the arguments that are specific for this application.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type",
        dest="type",
        action="store",
        choices={"proxy", "simulator", "direct"},
        help="Specify the implementation you want to connect to.",
        default="proxy",
    )
    parser.add_argument(
        "--profile",
        default=False,
        action="store_true",
        help="Enable info logging messages with method profile information.",
    )
    args = parser.parse_args()
    return args


def main():
    lock_file = QLockFile(str(Path("~/pm100a_ui.app.lock").expanduser()))

    styles_location = find_file("styles.qss", in_dir="egse/gui")

    args = list(sys.argv)
    args[1:1] = ["-stylesheet", str(styles_location)]
    app = QApplication(args)
    app.setWindowIcon(QIcon(str(get_resource(":/icons/meter.svg"))))

    if lock_file.tryLock(100):
        process_status = ProcessStatus()

        timer_thread = threading.Thread(target=do_every, args=(10, process_status.update))
        timer_thread.daemon = True
        timer_thread.start()

        start_http_server(GUI_SETTINGS.METRICS_PORT)

        args = parse_arguments()

        if args.profile:
            Settings.set_profiling(True)

        if args.type == "proxy":
            proxy = ThorlabsPM100Proxy()
            if not proxy.ping():
                description = "Could not connect to Powermeter Control Server"
                info_text = (
                    "The GUI will start, but the connection button will show a disconnected state. "
                    "Please check if the Control Server is running and start the server if needed. "
                    "Otherwise, check if the correct HOSTNAME for the control server is set in the "
                    "Settings.yaml "
                    "configuration file."
                )

                show_warning_message(description, info_text)

        view = ThorlabsUIView()
        model = ThorlabsUIModel(args.type)
        controller = ThorlabsUIController(model, view)

        view.show()

        return app.exec_()
    else:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setWindowTitle("Error")
        error_message.setText("The PM100a GUI application is already running!")
        error_message.setStandardButtons(QMessageBox.Ok)

        return error_message.exec()


if __name__ == "__main__":
    sys.exit(main())
