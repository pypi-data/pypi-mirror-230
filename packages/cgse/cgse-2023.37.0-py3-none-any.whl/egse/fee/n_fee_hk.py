import logging
import multiprocessing
import os
import pickle
import signal
from typing import List

import click
import invoke
import numpy as np
import rich
import sys
import time
import zmq
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QRunnable
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox
from prometheus_client import start_http_server

import egse.logger
from egse.fee.nfee import HousekeepingData
from egse.hk import convert_hk_names
from egse.hk import read_conversion_dict
from egse.metrics import define_metrics
from egse.settings import Settings
from egse.setup import NavigableDict, SetupError
from egse.state import GlobalState
from egse.storage import StorageProxy
from egse.storage import register_to_storage_manager
from egse.storage import unregister_from_storage_manager
from egse.storage.persistence import CSV
from egse.synoptics import SynopticsManagerProxy
from egse.system import get_host_ip
from egse.zmq import MessageIdentifier
from egse.zmq_ser import bind_address
from egse.zmq_ser import connect_address

LOGGER = logging.getLogger(__name__)

DPU_SETTINGS = Settings.load("DPU Processor")
CTRL_SETTINGS = Settings.load("N-FEE HK Control Server")

APP_NAME = "n_fee_hk"
ORIGIN = "N-FEE-HK"
TIMEOUT = 1  # timeout for polling the data distribution from the DPU CS

HK_TIMESTAMP_NAME = "timestamp"

KNOWN_KEYS_NOT_IN_METRICS = ['timestamp', 'timecode_ts']

class GeneratorSignals(QObject):
    finished = pyqtSignal()


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        'str' Exception string

    data
        'object' data returned from processing

    """

    finished = pyqtSignal()
    error = pyqtSignal(str)
    data = pyqtSignal(int, object)


class DataPuller(QRunnable):
    def __init__(self, hostname: str, port: int, timeout: int = TIMEOUT):
        super().__init__()
        self.signals = WorkerSignals()
        self.hostname = hostname
        self.port = port
        self.quit_request = False
        self.timeout = timeout

        context = zmq.Context.instance()

        self.receiver = context.socket(zmq.SUB)
        self.receiver.setsockopt_string(zmq.SUBSCRIBE, "")

        self.commander = context.socket(zmq.REP)

    @pyqtSlot()
    def run(self):
        ip_address = get_host_ip()
        receiver_endpoint = f"tcp://{self.hostname}:{self.port}"
        commander_endpoint = bind_address(CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.COMMANDING_PORT)
        self.receiver.connect(receiver_endpoint)
        self.commander.bind(commander_endpoint)

        poller = zmq.Poller()
        poller.register(self.receiver, zmq.POLLIN)
        poller.register(self.commander, zmq.POLLIN)

        while True:

            socket_list = dict(poller.poll(timeout=self.timeout))

            if self.quit_request:
                LOGGER.info('DataPuller quit requested.')
                break

            if self.receiver in socket_list:
                try:
                    sync_id, pickle_string = self.receiver.recv_multipart()
                    sync_id = int.from_bytes(sync_id, byteorder='big')
                    data = pickle.loads(pickle_string)
                    self.signals.data.emit(sync_id, data)
                except Exception as exc:
                    LOGGER.error("Exception caught!", exc_info=True)
                    self.signals.error.emit(str(exc))

            if self.commander in socket_list:
                pickle_string = self.commander.recv()
                command = pickle.loads(pickle_string)
                if command.lower() == "quit":
                    self.commander.send(pickle.dumps("ACK"))
                    LOGGER.info('DataPuller quit requested...')
                    break
                if command.lower() == "status":
                    LOGGER.info('DataPuller status requested...')
                    response = dict(
                        status="ACK",
                        host=ip_address,
                        listening_port=self.port,
                        command_port=CTRL_SETTINGS.COMMANDING_PORT,
                    )
                    self.commander.send(pickle.dumps(response))

        LOGGER.info("Cleaning up ZeroMQ sockets...")

        poller.unregister(self.commander)
        poller.unregister(self.receiver)

        self.receiver.disconnect(f"tcp://{self.hostname}:{self.port}")
        self.receiver.close(linger=0)
        self.commander.close(linger=0)

        self.signals.finished.emit()

    def quit(self):
        self.quit_request = True


class DataCollector:
    def __init__(self, keys: List):
        self._keys = keys

        # initialise the data dictionary

        self._data = {k: None for k in self._keys}

    def __getitem__(self, item):
        return self._data[item]

    def __contains__(self, item):
        return item in self._data

    def get(self, item):
        try:
            return self._data[item]
        except KeyError:
            return None

    def keys(self):
        return self._keys

    def values(self):
        return self._data.values()

    def update(self, data: dict):
        if x := set(data) - set(self._data):
            LOGGER.warning(
                f"New housekeeping found which was not previously in the N-FEE HK packet: {x}"
            )
        self._data.update(data)

    def clear(self):
        self._data = {k: None for k in self._keys}

    def as_dict(self):
        return self._data


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.hk_generator = HousekeepingGenerator()

        column_names = self.hk_generator.hk_names_mapping.values()
        register_to_storage_manager(ORIGIN, CSV, prep=dict(mode='a', column_names=list(column_names)))

        self.hk_generator.signals.finished.connect(self.close)
        self.hk_generator.run()

        LOGGER.info("Initialised MainWindow")

    def closeEvent(self, event: QCloseEvent) -> None:
        LOGGER.info(f"closeEvent called...{event=}")

        if self.hk_generator.data_puller:
            self.hk_generator.data_puller.quit()
        else:
            LOGGER.info("Data Puller was already terminated.")

        time.sleep(TIMEOUT)
        unregister_from_storage_manager(ORIGIN)
        LOGGER.info("AFTER UNREGISTER STORAGE")


class HousekeepingGenerator:

    def __init__(self):

        self.signals = GeneratorSignals()

        # Convert with info from HK info table
        # Append the new names

        self.data_puller = None
        self.threadpool = QThreadPool()

        # The hk_names_mapping is a dictionary that maps the original device telemetry parameter
        # names to the correct device names as defined in the CGSE. The keys in the mapping are
        # the original device name, the values are the CGSE corrected names

        self.hk_names_mapping = read_conversion_dict(ORIGIN, use_site=False)

        # Add the timestamp and timecode_ts to the names mapping
        self.hk_names_mapping.update({'timestamp': 'timestamp', 'timecode_ts': 'timecode_ts'})

        hk_header = self.hk_names_mapping.keys()

        # Read from the setup: sensor calibration data (as a NavigableDict)

        self.supply_voltage_calibration = GlobalState.setup.camera.fee.calibration.supply_voltages
        self.temperature_calibration = GlobalState.setup.camera.fee.calibration.temperatures

        self.current_data = DataCollector([HK_TIMESTAMP_NAME, *hk_header])

        self.hk_metrics = define_metrics(ORIGIN, dashboard='*')

    def run(self):
        self.start_pulling_data()

    def start_pulling_data(self):
        self.data_puller = worker = DataPuller(
            DPU_SETTINGS.HOSTNAME, DPU_SETTINGS.DATA_DISTRIBUTION_PORT
        )
        worker.signals.data.connect(self.worker_output)
        worker.signals.finished.connect(self.worker_complete)
        worker.signals.error.connect(self.worker_error)
        self.threadpool.start(worker)

    def update_metrics(self):

        for orig_name, metric_name in self.hk_names_mapping.items():
            # LOGGER.info(f"{orig_name=}, {metric_name=}")
            try:
                value = self.current_data.get(orig_name)
                if value is not None:
                    self.hk_metrics[metric_name].set(value)
                else:
                    self.hk_metrics[metric_name].set(float('nan'))
                    # LOGGER.debug(f"No current data available for {metric_name}.")
            except KeyError as exc:
                if metric_name not in KNOWN_KEYS_NOT_IN_METRICS:
                    LOGGER.warning(f"Unknown metric name: {orig_name=}, {metric_name=}")

    def send_hk_data_to_storage(self):

        # All saved data needs at least a timestamp

        if 'timestamp' not in self.current_data or self.current_data['timestamp'] is None:
            return

        # Translate the HK names (i.e. start using the correct prefix)
        # and append them to the rest of the HK

        # CHANGED: Remember self.hk_names_mapping shall contain both timestamp and timecode_ts.
        #          Be careful here, because the convert_hk_names() returns a new dict while the
        #          self.current_data is a DataCollector. So, don't catch the returned dict in the
        #          self.current_data.
        current_data = convert_hk_names(self.current_data.as_dict(), self.hk_names_mapping)

        # Calibration (supply voltages + temperatures)

        calibrated_supply_voltages = get_calibrated_supply_voltages(current_data, self.supply_voltage_calibration)
        current_data.update(calibrated_supply_voltages)

        calibrated_temperatures = get_calibrated_temperatures(current_data, self.temperature_calibration)
        current_data.update(calibrated_temperatures)

        with StorageProxy() as storage:

            rc = storage.save(
                {
                    "origin": ORIGIN,
                    "data": current_data
                }
            )
        if rc and not rc.successful:
            LOGGER.warning(f"Couldn't save HK data to the Storage manager: {rc}")

        # Store the calibrated temperatures as synoptics
        # (only when there's actually something there in the N-FEE HK)

        if len(calibrated_temperatures) > 0:

            calibrated_temperatures["timestamp"] = current_data[HK_TIMESTAMP_NAME]

            with SynopticsManagerProxy() as synoptics:
                synoptics.store_common_synoptics(calibrated_temperatures)

    def worker_output(self, sync_id, data):

        if sync_id == MessageIdentifier.SYNC_TIMECODE:
            self.current_data.clear()

            timecode, timestamp = data
            LOGGER.debug(f"Timecode: {timestamp=}, {timecode=}")

            self.current_data.update({"timecode": timecode, "timecode_ts": timestamp})

        if sync_id == MessageIdentifier.SYNC_HK_PACKET:
            hk_packet, timestamp = data
            LOGGER.debug(f"HK Packet: {timestamp=}, {hk_packet.type=!s}")

            hk_data = HousekeepingData(hk_packet.data)
            self._store_hk_data(hk_data, timestamp)

        if sync_id == MessageIdentifier.SYNC_HK_DATA:
            hk_data, timestamp = data
            LOGGER.debug(f"HK Data: {timestamp=}")

            self._store_hk_data(hk_data, timestamp)

        if sync_id == MessageIdentifier.NUM_CYCLES:
            LOGGER.debug(f"num_cycles: {max(0, data)}")
            self.current_data.update({'num_cycles': max(0, data)})

    def _store_hk_data(self, hk_data: HousekeepingData, timestamp: str):
        self.current_data.update({HK_TIMESTAMP_NAME: timestamp})

        for par_name in hk_data:
            self.current_data.update({par_name: hk_data[par_name]})

        self.send_hk_data_to_storage()
        self.update_metrics()

    def worker_complete(self):
        LOGGER.info("THREAD COMPLETE!")
        LOGGER.info(f"Number of threads running: {self.threadpool.activeThreadCount()}")
        self.data_puller = None
        self.signals.finished.emit()

    def worker_error(self, msg):
        LOGGER.warning(f"ERROR: {msg}")


def get_calibrated_supply_voltages(counts, supply_voltage_calibration):
    """ Calibrate the N-FEE supply voltages.

    The difference in naming between calibrated and uncalibrated housekeeping is the suffix "_RAW".

    The calibration consist of applying a linear function to the raw values.

    Args:
        - counts: Uncalibrated, raw data for all HK.
        - supply_voltage_calibration: Supply voltage calibration s read from the YAML file that was specified in the
                                      setup

    Returns: Dictionary with calibrated supply voltages [V].
    """

    supply_voltages = {}

    for cal_name in supply_voltage_calibration:

        raw_name = f"{cal_name}_RAW"
        cal = supply_voltage_calibration[cal_name]

        if counts[raw_name] is not None:

            supply_voltage = cal.gain * counts[raw_name] + cal.offset

            supply_voltages[cal_name] = supply_voltage

    return supply_voltages


def get_calibrated_temperatures(counts, sensor_calibration):
    """ Calibrate the N-FEE temperatures.

    The calibrated temperatures come from:

        - TOU TRP PT1000 sensors
        - CCD PT100/PT1000 sensors
        - PT1000 board sensors
        - ISL71590 board sensors

    The difference in naming between calibrated and uncalibrated temperatures is the suffix "_RAW".

    Args:
        - counts: Uncalibrated, raw data for all HK.
        - sensor_calibration: N-FEE temperature calibration as read from the YAML file that was specified in the setup

    Returns: Dictionary with calibrated temperatures [°C].
    """

    temperatures = {}

    for sensor_type in sensor_calibration:
        temperatures.update(get_calibrated_temperatures_for_type(counts, sensor_calibration, sensor_type))

    return temperatures


def get_calibrated_temperatures_for_type(counts, sensor_calibration, sensor_type) -> dict:
    """ Calibrate the N-FEE temperatures for the given sensor type.

    Args:
        - counts: Uncalibrated, raw data [ADU]
        - sensor_calibration: Calibration information for the given sensor type
        - sensor_calibration: N-FEE sensor calibration as read from the YAML file that was specified in the setup

    Returns: Dictionary with calibrated temperatures [°C] for the given sensor type.
    """

    cal = sensor_calibration[sensor_type]

    temperatures = {}

    for cal_name in cal.sensor_names:

        if cal_name.endswith("_AMB"):
            raw_name = f"{cal_name[:-4]}_RAW"
        else:
            raw_name = f"{cal_name}_RAW"

        if counts[raw_name] is not None:

            sensor_info = cal[cal_name] if cal_name in cal else cal

            try:
                temperature = counts_to_temperature(cal_name, counts[raw_name], sensor_info)

            except AttributeError as exc:
                raise SetupError(
                    "Not all TOU TRP PT1000 calibration information is available in the setup under "
                    "setup.camera.fee.calibration."
                ) from exc

            temperatures[cal_name] = temperature

    return temperatures


def counts_to_temperature(sensor_name: str, counts: float, sensor_info: NavigableDict):
    """ Convert the given counts for the given sensor to temperature.

    Args:
        - sensor_name: Sensor name
        - counts: Uncalibrated, raw data [ADU]
        - sensor_info: Calibration information for the given sensor (type)

    Returns: Calibrated temperature [°C] for the given sensor
    """

    # Conversion: temperature = counts * gain + offset

    if "counts_to_temperature_gain" in sensor_info and "counts_to_temperature_offset" in sensor_info:
        return counts * sensor_info.counts_to_temperature_gain + sensor_info.counts_to_temperature_offset

    # Conversion: counts -> resistance -> temperature

    resistance = counts_to_resistance(sensor_name, counts, sensor_info)
    return resistance_to_temperature(sensor_name, resistance, sensor_info)


def counts_to_resistance(sensor_name: str, counts: float, sensor_info: NavigableDict):
    """ Convert the given counts for the given sensor to resistance.

    Args:
        - sensor_name: Sensor name
        - counts: Uncalibrated, raw data [ADU]
        - sensor_info: Calibration information for the given sensor (type)

    Returns: Resistance [Ohm] for the given sensor.
    """

    # Offset (if any)

    counts_to_resistance_offset = sensor_info.counts_to_resistance_offset \
        if "counts_to_resistance_offset" in sensor_info \
        else 0

    # Conversion: counts -> voltage -> resistance

    if "counts_to_voltage_gain" in sensor_info and "voltage_to_resistance_gain" in sensor_info:
        return counts * sensor_info.counts_to_voltage_gain * sensor_info.voltage_to_resistance_gain \
               + counts_to_resistance_offset

    # Conversion: counts -> resistance

    elif "counts_to_resistance_gain" in sensor_info:
        return counts * sensor_info.counts_to_resistance_gain \
               + counts_to_resistance_offset

    raise SetupError(f"Setup does not contain info for conversion from counts to resistance for {sensor_name}")


def resistance_to_temperature(sensor_name: str, resistance: float, sensor_info: NavigableDict):
    """ Convert the given resistance for the given sensor to counts.

    Args:
        - sensor_name: Sensor name
        - resistance: Resistance [Ohm]
        - sensor_info: Calibration information for the given sensor (type)

    Returns: Temperature [°C] for the given sensor.
    """

    resistance_to_temperature_info = sensor_info.resistance_to_temperature

    # Series resistance (if any)

    if "series_resistance" in resistance_to_temperature_info:

        series_resistance = resistance_to_temperature_info.series_resistance
        if sensor_name in resistance_to_temperature_info:
            series_resistance = series_resistance[sensor_name]
        resistance -= series_resistance

    method: str = resistance_to_temperature_info.method

    if "divide_resistance_by" in resistance_to_temperature_info:
        resistance /= resistance_to_temperature_info.divide_resistance_by

    # Polynomial

    if method == "polynomial":

        # Coefficients given for conversion temperature -> resistance

        if "temperature_to_resistance_coefficients" in resistance_to_temperature_info:
            return solve_temperature(resistance_to_temperature_info.temperature_to_resistance_coefficients, resistance)

        # Coefficients given for conversion resistance -> temperature

        if "resistance_to_temperature_coefficients" in resistance_to_temperature_info:
            return np.polyval(resistance_to_temperature_info.resistance_to_temperature_coefficients, resistance)

    if method != "callendar_van_dusen":
        raise SetupError(f"Setup does not contain info for conversion from resistance to temperature for {sensor_name}")

    standard = resistance_to_temperature_info.standard
    ref_resistance = resistance_to_temperature_info.ref_resistance
    return callendar_van_dusen(resistance, ref_resistance, standard)


def solve_temperature(temperature_to_resistance_coefficients, resistance):
    """ Solve the temperature from the temperature -> resistance polynomial.

    For the given temperature -> resistance polynomial and the given resistance, we determine what the corresponding
    temperature is by:
        - Finding the roots of
            polynomial(temperature) = resistance
        - Discarding the roots with an imaginary component
        - Selecting the remaining root in the relevant temperature regime (here: [-200°C, 200°C])
    """

    temperature_to_resistance_poly = np.poly1d(temperature_to_resistance_coefficients)
    temperatures = (temperature_to_resistance_poly - resistance).roots

    for temperature in temperatures:
        if temperature.imag == 0 and -200 <= temperature <= 200:
            return temperature.real


def callendar_van_dusen(resistance, ref_resistance, standard):
    """ Solve the Callendar - van Dusen equation for temperature.

    Args:
        - resistance: Resistance [Ohm] for which to calculate the temperature
        - ref_resistance: Resistance [Ohm] for a temperature of 0°C

    Return: Temperature [°C] corresponding to the given resistance.
    """

    # Resistances higher than the reference resistance correspond to

    coefficients = GlobalState.setup.sensor_calibration.callendar_van_dusen[standard]

    # Positive temperatures

    if resistance >= ref_resistance:
        resistance_to_temperature_coefficients = [ref_resistance * coefficients.C,
                                                  -ref_resistance * 100 * coefficients.C,
                                                  ref_resistance * coefficients.B,
                                                  ref_resistance * coefficients.A, ref_resistance * 1]

    # Negative temperatures

    else:
        resistance_to_temperature_coefficients = [ref_resistance * coefficients.B,
                                                  ref_resistance * coefficients.A,
                                                  ref_resistance * 1]

    return solve_temperature(resistance_to_temperature_coefficients, resistance)



@click.group()
def cli():
    pass


@cli.command()
@click.option("--gui/--no-gui", default=False,
              help="start the N-FEE HK Process with graphics support [default=--no-gui].")
def start_bg(gui):
    """Start the N-FEE HK Processor in the background."""

    options = "--gui" if gui else "--no-gui"
    invoke.run(f"n_fee_hk start {options}", disown=True)


@cli.command()
@click.option("--gui/--no-gui", default=False,
              help="start the N-FEE HK Process with graphics support [default=--no-gui].")
def start(gui):
    """Start the N-FEE HK Processor."""

    multiprocessing.current_process().name = "n_fee_hk"

    start_http_server(CTRL_SETTINGS.METRICS_PORT)

    args = sys.argv
    if not gui:
        args.extend(["-platform", "offscreen"])

    LOGGER.info(f"{args=}")

    app = QApplication(args)

    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    window = MainWindow()
    window.show()

    def sigint_handler(*args):
        """Handler for the SIGINT signal."""
        LOGGER.info('Handling signal SIGINT...')
        if QApplication.platformName() == "offscreen":
            window.close()
            QApplication.quit()
        elif QMessageBox.question(
                None, '', "Are you sure you want to quit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
        ) == QMessageBox.Yes:
            window.close()
            QApplication.quit()

    signal.signal(signal.SIGINT, sigint_handler)

    # The following code is solely here to have the app react faster to CTRL-C in the terminal

    timer = QTimer()
    timer.start(500)  # interval in msec
    timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.

    try:
        rc = app.exec_()
    except KeyboardInterrupt:
        LOGGER.info(f"Keyboard interrupt accepted, terminating application {APP_NAME}")

    LOGGER.info("Destroying ZeroMQ context...")

    egse.logger.close_all_zmq_handlers()

    context = zmq.Context.instance()
    context.destroy(linger=0)


@cli.command()
def stop():
    """Stop the N-FEE HK Control Server."""

    response = send_request("quit")
    if response == "ACK":
        rich.print("Logger successfully terminated.")
    else:
        rich.print(f"[red] ERROR: {response}")


@cli.command()
def status():
    """Roll over the log file of the Logger Control Server."""

    rich.print("N-FEE HK Generator:")

    response = send_request("status")
    if response.get("status") == "ACK":
        rich.print("  Status: [green]active")
        rich.print(f"  Hostname: {response.get('host')}")
        rich.print(f"  Listening port: {response.get('listening_port')}")
        rich.print(f"  Commanding port: {response.get('command_port')}")
    else:
        rich.print("  Status: [red]not active")


TIMEOUT_RECV = 1.0  # seconds


def send_request(command_request: str):
    """Sends a request to the Logger Control Server and waits for a response."""
    ctx = zmq.Context.instance()
    endpoint = connect_address(
        CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT
    )
    socket = ctx.socket(zmq.REQ)
    socket.connect(endpoint)

    socket.send(pickle.dumps(command_request))
    rlist, _, _ = zmq.select([socket], [], [], timeout=TIMEOUT_RECV)
    if socket in rlist:
        response = socket.recv()
        response = pickle.loads(response)
    else:
        response = {"error": "Received from ZeroMQ socket timed out for N-FEE HK Control Server."}
    socket.close(linger=0)

    return response


if __name__ == '__main__':
    sys.exit(cli())
