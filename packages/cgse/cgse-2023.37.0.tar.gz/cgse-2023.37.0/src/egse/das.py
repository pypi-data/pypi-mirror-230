"""
The Data Acquisition System (DAS) is a small application that performs measurements on
different devices.

For the Keithley DAQ6510, the DAS reads the configuration for the Keithley DAQ6510 from the
Configuration Manager and then configures the device. When no Configuration Manager is
available, the DAS can also be started with a filename to read the configuration from. The file
should have the YAML format.

```
Setup:
    DAQ6510:
        Sensors:
            Temperature:
                TRANSDUCER: FRTD
                "RTD:FOUR": PT100
                UNIT: KELVIN
```

The Data Acquisition System can be started as follows:

```
$ das
Usage: das.py [OPTIONS] COMMAND [ARGS]...

Options:
  --verbose  print out more info to the terminal.
  --debug    set the logging output to DEBUG mode.
  --help     Show this message and exit.

Commands:
  daq6510  Run the Data Acquisition System for the DAQ6510.
  tcs      Run the Data Acquisition System for the TCS EGSE.
  cdaq     Run the Data Acquisition System for the CDAQ EGSE
```

"""
import logging
import multiprocessing
from datetime import timezone

import itertools
import rich

from egse.hk import read_conversion_dict, convert_hk_names
from egse.state import GlobalState

import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List

import click
import invoke
from prometheus_client import Gauge
from prometheus_client import start_http_server

from egse.control import Failure
from egse.settings import Settings
from egse.setup import Setup
from egse.storage import StorageProxy
from egse.storage import is_storage_manager_active
from egse.storage.persistence import CSV
from egse.system import SignalCatcher
from egse.system import flatten_dict
from egse.tcs.tcs import TCSProxy
from egse.tcs.tcs import is_tcs_cs_active
from egse.tempcontrol.keithley.daq6510 import DAQ6510Proxy
from egse.tempcontrol.keithley.daq6510 import count_number_of_channels
from egse.tempcontrol.keithley.daq6510 import get_channel_names
from egse.tempcontrol.keithley.daq6510_cs import is_daq6510_cs_active
from egse.tempcontrol.srs.ptc10 import ptc10Proxy
from egse.tempcontrol.srs.ptc10_cs import is_ptc10_cs_active
from egse.aeu.aeu import CRIOProxy, OperatingMode
from egse.aeu.aeu import is_aeu_cs_active

from egse.powermeter.ni.cdaq9184 import cdaq9184Proxy
from egse.powermeter.ni.cdaq9184_cs import is_cdaq9184_cs_active

from egse.ni.alarms.cdaq9375 import cdaq9375Proxy
from egse.ni.alarms.cdaq9375_cs import is_cdaq9375_cs_active

from egse.metrics import define_metrics
from egse.synoptics import SynopticsManagerProxy

from egse.system import format_datetime

LOGGER = logging.getLogger(__name__)

DAS = Settings.load("Data Acquisition System")


def load_setup_from_input_file(input_file: str):
    """Loads a Setup YAML file from disk."""
    input_file = Path(input_file).resolve()

    if not input_file.exists():
        click.echo(f"ERROR: Input file ({input_file}) doesn't exists.")
        return None

    return Setup.from_yaml_file(input_file)


def load_setup_from_configuration_manager():
    """Loads a Setup YAML file from the Configuration Manager."""

    return GlobalState.setup


class Config:
    def __init__(self):
        self.verbose = False
        self.debug = False


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option("--verbose", is_flag=True, help="print out more info to the terminal.")
@click.option("--debug", is_flag=True, help="set the logging output to DEBUG mode.")
@pass_config
def cli(config, verbose, debug):
    config.verbose = verbose
    config.debug = debug


@cli.command()
@click.option(
    "--count", default=None, help="how many samples should be taken for each measurement"
)
@click.option(
    "--interval", default=None, help="what is the time interval between scans [seconds]"
)
@click.option(
    "--delay", default=None, help="what is the time delay between measurements [seconds]"
)
@click.option(
    "--channel-list",
    default=None,
    help='a channel_list as understood by the device, e.g. "(@101:105)"',
)
@click.option(
    "--background/--no-background", "-bg/-no-bg", default=False,
    help="start the data acquisition in the background"
)
@click.argument("input_file", type=str, required=False)
@pass_config
def daq6510(config, count, interval, delay, channel_list, background: bool, input_file: str):
    """
    Run the Data Acquisition System for the DAQ6510.

    INPUT_FILE: YAML file containing the Setup for the DAQ6510 [optional]

    Note: When this command runs in the background, send an INTERRUPT SIGNAL with the kill command
    to terminate. Never send a KILL SIGNAL (9) because then the process will not properly be
    unregistered from the storage manager.

    $ kill -INT <PID>

    """

    hk_conversion_table = read_conversion_dict("DAS-DAQ6510", use_site=True)
    column_names = list(hk_conversion_table.values())

    if background:
        cmd = "das daq6510"
        cmd += f" --count {count}"
        cmd += f" --interval {interval}"
        cmd += f" --delay {delay}"
        cmd += f" --channel-list '{channel_list}'" if channel_list else ""
        cmd += f" {input_file}" if input_file else ""
        LOGGER.info(f"Invoking background command: {cmd}")
        invoke.run(cmd, disown=True)
        return

    multiprocessing.current_process().name = "das-daq6510"

    if config.debug:
        logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)

    if not is_daq6510_cs_active():
        LOGGER.error("The DAQ6510 Control Server is not running, start the 'daq6510_cs' command "
                     "before running the data acquisition.")
        return

    if not is_storage_manager_active():
        LOGGER.error("The storage manager is not running, start the core services "
                     "before running the data acquisition.")
        return

    if input_file:
        setup = load_setup_from_input_file(input_file)
    else:
        setup = load_setup_from_configuration_manager()

    if setup is None:
        LOGGER.error("ERROR: Could not load setup.")
        sys.exit(1)

    if config.verbose:
        LOGGER.info(setup)

    if "DAQ6510" not in setup.gse:
        LOGGER.error("ERROR: no DAQ6510 entry in the loaded Setup.")
        sys.exit(1)

    if not channel_list:
        channel_list = setup.gse.DAQ6510.channels

    if not count:
        count = setup.gse.DAQ6510.route.scan.COUNT.SCAN

    if not interval:
        interval = setup.gse.DAQ6510.route.scan.INTERVAL

    if not delay:
        delay = setup.gse.DAQ6510.route.delay

    count, interval, delay = int(count), int(interval), int(delay)

    channel_count = count_number_of_channels(channel_list)
    channel_names = get_channel_names(channel_list)

    DAQ_METRICS = {}
    for channel in channel_names:
        metrics_name = hk_conversion_table[channel]
        DAQ_METRICS[metrics_name] = Gauge(f"{metrics_name}",
                                          f"The current measure for the sensor connected to channel {channel} "
                                          f"({metrics_name}) on the DAQ6510")

    start_http_server(DAS.METRICS_PORT_DAQ6510)

    # Initialize some variables that will be used for registration to the Storage Manager

    origin = "DAS-DAQ6510"
    persistence_class = CSV
    prep = {
        "mode": "a",
        "ending": "\n",
        "column_names": ["timestamp", *column_names],
    }

    killer = SignalCatcher()

    with DAQ6510Proxy() as daq, StorageProxy() as storage:
        daq.reset()

        dt = datetime.now(tz=timezone.utc)
        daq.set_time(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        LOGGER.info(f"DAQ6510 date and time set: {daq.get_time()}")

        storage.register({"origin": origin, "persistence_class": persistence_class, "prep": prep})

        storage.save({"origin": origin, "data": f"# columns: {column_names}"})

        for sensor in setup.gse.DAQ6510.sensors:
            for function in setup.gse.DAQ6510.sensors[sensor]:
                sense = {
                    function.upper(): [
                        (key, value)
                        for key, value in flatten_dict(
                            setup.gse.DAQ6510.sensors[sensor][function]
                        ).items()
                        if key != "channels"
                    ]
                }
                function_channel_list = setup.gse.DAQ6510.sensors[sensor][function].channels
                if config.verbose:
                    LOGGER.info(f"{sense=}")
                    LOGGER.info(f"{function_channel_list=}")
                daq.configure_sensors(channel_list=function_channel_list, sense=sense)

        LOGGER.info(f"global: {channel_list=}, {channel_count=}")

        daq.setup_measurements(channel_list=channel_list)

        while True:
            try:
                response = daq.perform_measurement(
                    channel_list=channel_list, count=count, interval=interval
                )

                if killer.term_signal_received:
                    break

                if not response:
                    LOGGER.warning("Received an empty response from the DAQ6510, "
                                   "check the connection with the device.")
                    LOGGER.warning(f"Response: {response=}")
                    time.sleep(1.0)
                    continue

                if isinstance(response, Failure):
                    LOGGER.warning(f"Received a Failure from the DAQ6510 Control Server:")
                    LOGGER.warning(f"Response: {response}")
                    time.sleep(1.0)
                    continue

                # Process and save the response

                # LOGGER.debug(f"{response=}")

                dts = response[0][1].strip()
                dt = datetime.strptime(dts[:-3], "%m/%d/%Y %H:%M:%S.%f")
                datetime_string = format_datetime(dt.replace(tzinfo=timezone.utc))

                data = {hk_conversion_table[measure[0]]: float(measure[2]) for measure in response}

                data.update({"timestamp": datetime_string})

                # FIXME: we probably need to do something with the units...

                units = [measure[3] for measure in response]

                # LOGGER.debug(f"{data=}")

                storage.save({"origin": origin, "data": data})

                # Now extract channels from the response to update the metrics

                for channel in [measure[0] for measure in response]:
                    metrics_name = hk_conversion_table[channel]
                    DAQ_METRICS[metrics_name].set(data[metrics_name])

                # wait for the next measurement to be done (delay)

                time.sleep(delay)

            except KeyboardInterrupt:
                LOGGER.debug("Interrupt received, terminating...")
                break
            except Exception as exc:
                LOGGER.warning(f"DAS Exception: {exc}", exc_info=True)
                LOGGER.warning("Got a corrupt response from the DAQ6510. "
                               "Check log messages for 'DAS Exception'.")
                time.sleep(1.0)
                continue

        storage.unregister({"origin": origin})

# todo: start PTC10 automatically when when its CS starts. In click options below? background?
# todo: add disable_heater_error
@cli.command()
@click.option(
    "--background/--no-background", "-bg/-no-bg", default=False,
    help="start the data acquisition in the background"
)
@click.option(
    "--user_regulation", default=None, help="activate ptc10 regulation with the given parameter as temperature setpoint (float)"
)
# todo: voir pour option auto_regulation is_fkag=True valeur par défaut
@click.option(
    "--auto_regulation", is_flag=True, default=None, help="if this option is given, activate ptc10 regulation with survival mode (i.e. with T_min_NOP as temperature setpoint)"
)
@click.argument("input_file", type=str, required=False)
@pass_config
def ptc10(config, user_regulation: float, auto_regulation: int, background: bool, input_file: str):
    """
    Run the Data Acquisition System for the DAQ6510.

    INPUT_FILE: YAML file containing the Setup for the DAQ6510 [optional]

    Note: When this command runs in the background, send an INTERRUPT SIGNAL with the kill command
    to terminate. Never send a KILL SIGNAL (9) because then the process will not properly be
    unregistered from the storage manager.

    $ kill -INT <PID>

    """

    if background:
        cmd = "das ptc10"
        cmd += f" --user_regulation {user_regulation}"
        cmd += f" --auto_regulation {auto_regulation}"
        cmd += f" {input_file}" if input_file else ""
        LOGGER.info(f"Invoking background command: {cmd}")
        invoke.run(cmd, disown=True)
        return

    multiprocessing.current_process().name = "das-ptc10"

    if config.debug:
        logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)

    if not is_ptc10_cs_active():
        LOGGER.error("The PTC10 Control Server is not running, start the 'ptc10_cs' command "
                     "before running the data acquisition.")
        return

    if not is_storage_manager_active():
        LOGGER.error("The storage manager is not running, start the core services "
                     "before running the data acquisition.")
        return

    if input_file:
        setup = load_setup_from_input_file(input_file)
    else:
        setup = load_setup_from_configuration_manager()

    if setup is None:
        LOGGER.error("ERROR: Could not load setup.")
        sys.exit(1)

    if config.verbose:
        LOGGER.info(setup)

    if "PTC10" not in setup.gse:
        LOGGER.error("ERROR: no PTC10 entry in the loaded Setup.")
        sys.exit(1)

    channel_names = list(setup.gse.PTC10.channel_names.values()) # defined in config file

    # Creation of list HK_names used to store HK.
    site_id = setup.site_id # Name of the TH

    HK_names = ["G" + site_id + "_" + sensor_name for sensor_name in channel_names[:4]]
    units = ["ampere", "watt", "volt"]
    for unit in units:
        HK_names.extend(["G" + site_id + "_" + name + "_" + unit for name in channel_names[-3:]])
    HK_names.insert(0, HK_names.pop(2))  # I move GIAS_TTS_BiP_01 at the beginning of the list HK_names.
    # HK_names is ['GIAS_TTS_BiP_01', 'GIAS_TRP2', 'GIAS_TRP3', 'GIAS_TRP4', 'GIAS_H1_ampere', 'GIAS_H2_ampere', 'GIAS_H3_ampere', 'GIAS_H1_watt', 'GIAS_H2_watt', 'GIAS_H3_watt', 'GIAS_H1_volt', 'GIAS_H2_volt', 'GIAS_H3_volt']

    # Creation of Prometheus METRICS in a dictionnary from TM dictionnary
    PTC_METRICS = define_metrics("DAS-PTC10")

    if not list(PTC_METRICS.keys()) == HK_names: # Check if names in setup file (used for HK names) and names defined in TM dictionary for metrics names are same
        LOGGER.error("The names of HK defined in the current setup file " + setup.get_id() + " are not the same than those in TM dictionary for metrics")

    start_http_server(DAS.METRICS_PORT_PTC10)

    # Initialize some variables that will be used for registration to the Storage Manager

    origin = "DAS-PTC10"
    persistence_class = CSV
    prep = {
        "mode": "a",
        "ending": "\n",
        "header": "PTC10 First Connection Tests",
        "column_names": ["timestamp", *PTC_METRICS],
    }

    killer = SignalCatcher()

    with ptc10Proxy() as ptc, StorageProxy() as storage:

        storage.register({"origin": origin, "persistence_class": persistence_class, "prep": prep})

        # Renaming the names of channels in PTC10 device with names defined in the setup file
        old_channel_names = ptc.get_names()  # old_channel_names is a tuple of 2 lists with the names of inputs (4 sensors)
                                             # in the first list and the names of outputs (3 heaters) in the second list
        old_channel_names = old_channel_names[0] + old_channel_names[1]  # Now old_channel_names is a long list of 7 elements (4 inputs/sensors
                                                                         # and 3 outputs/heaters)
        for old_name, new_name in zip(old_channel_names, channel_names):
            ptc.set_name(old_name,new_name)

        # Setting the input for each heater
        for output_ch, input in zip([1, 2, 3], setup.gse.PTC10.heater_input):
            new_input = setup.gse.PTC10.heater_input[input]
            ptc.set_heater_input(output_ch, new_input)

        # Configure units before limits (because configuring units modifies limits)
        ptc.output_unit(setup.gse.PTC10.heater_unit)

        # Setting limits
        low_limit = setup.gse.PTC10.heater_limit.low
        high_limit = setup.gse.PTC10.heater_limit.high
        for output_ch in [1, 2, 3]:
            ptc.output_limit(output_ch, low_limit, high_limit)

        # Setting PID coefficients
        i = 0
        for pid in setup.gse.PTC10.PID:
            PID_list = list(setup.gse.PTC10.PID[pid].values())
            i += 1
            ptc.set_PID(input_ch=i, output_ch=i, PID=PID_list)

        # Setting the resistance of the heater in Ohm (manually measured with ohmmeter and written in the setup file)
        R = setup.gse.PTC10.heater_Ohm

        # Time update from egse server
        ptc.update_time()
        is_on_time = True

        while True:
            try:

# Update time of PTC10 every first of the month to avoid a time lag after several days and a time desynchronisation.
                day = time.gmtime()[2]
                if day >= 2:
                    is_on_time = False
                if day == 1 and not is_on_time:
                    ptc.update_time()
                    is_on_time = True

                if user_regulation and auto_regulation:
                    LOGGER.warning("Only 1 option is expected (user_regulation OR auto_regulation) but both were given.\nTerminating... ")
                    break

                if user_regulation: # If user_regulation is given, then run the function set_stable() with "user_regulation" as temperature setpoint
                    try:
                        ptc.set_stable(float(user_regulation))
                    except ValueError:
                        LOGGER.warning("ValueError: user_regulation must be a number.\nTerminating...")
                        break
                if auto_regulation: # If auto_regulation is given, then run the function set_survival() (i.e. with T_min_NOP as temperature setpoint)
                    ptc.set_survival()

                # Acquirement of PTC10 time for HK and PTC10 values (temperatures and heaters)
                try:
                    response = [ptc.get_time()] + ptc.read_temperature() + ptc.read_heater()[0]
                # Sometimes randomly PTC10 doesn't return the time and there is a Failure, so to avoid
                # a bad type in the column timestamp, if there is a Failure, HK are not saved for this
                # time and the code go back at the top of the while loop thanks to exceptions.
                except TypeError:
                    LOGGER.warning("TYPE ERROR")
                    continue
                except ValueError:
                    LOGGER.warning("VALUE ERROR")
                    continue

                if killer.term_signal_received:
                    break

                if not response:
                    LOGGER.warning("Received an empty response from the PTC10, "
                                   "check the connection with the device.")
                    LOGGER.warning(f"Response: {response=}")
                    time.sleep(1.0)
                    continue

                if isinstance(response, Failure):
                    LOGGER.warning(f"Received a Failure from the PTC10 Control Server:")
                    LOGGER.warning(f"Response: {response}")
                    time.sleep(1.0)
                    continue

                # Process and save the response

                response.insert(1, response.pop(3)) # I move the value of TTS_BiP_01 at the beginning of the list response.

                # Calculation of power : P = RI²
                for i in [5, 6, 7]:
                    response.append(R * response[i]**2)

                # Calculation of voltage : U = RI
                for i in [5, 6, 7]:
                    response.append(R * response[i])

                hk_dict = {"timestamp": response[0]}
                hk_dict.update({k: v for k, v in zip(HK_names, response[1:])})

                LOGGER.debug(f"{response=}")

                LOGGER.debug(hk_dict)

                # Saving HK with PTC10 time as timestamp
                storage.save({"origin": origin, "data": hk_dict})

                # Now set the values in the metrics
                hk_dict.pop("timestamp")
                for key, value in hk_dict.items():
                    PTC_METRICS[key].set(value)


            except KeyboardInterrupt:
                LOGGER.debug("Interrupt received, terminating...")
                break
            except Exception as exc:
                LOGGER.warning(f"DAS Exception: {exc}", exc_info=True)
                LOGGER.warning("Got a corrupt response from the PTC10. "
                               "Check log messages for 'DAS Exception'.")
                time.sleep(1.0)
                continue

        ptc.disable_all()
        storage.unregister({"origin": origin})


@cli.command()
@click.option(
    "--use-all-hk", is_flag=True,
    help=("Use get_all_housekeeping() method to read telemetry from the TCS EGSE. "
          "The device must not be in remote control mode for this.")
)
@click.option(
    "--interval", default=10, help="what is the time delay between measurements [seconds]"
)
@click.option(
    "--background/--no-background", "-bg/-no-bg", default=False,
    help="start the data acquisition in the background"
)
@pass_config
def tcs(config, use_all_hk, interval, background):
    """
    Run the Data Acquisition System for the TCS EGSE.

    Note: When this command runs in the background, send an INTERRUPT SIGNAL with the kill command
    to terminate. Never send a KILL SIGNAL (9) because then the process will not properly be
    unregistered from the storage manager.

    $ kill -INT <PID>

    """

    rich.print(
        "[red]WARNING[/red]: This function of the DAS has been deprecated and is replaced by the "
        "TCSTelemetry process which is automatically started by the tcs_cs. The `das tcs` will be "
        "removed shortly.")

    return

    if background:
        cmd = "das tcs"
        cmd += " --use-all-hk" if use_all_hk else ""
        cmd += f" --interval {interval}"
        LOGGER.info(f"Invoking background command: {cmd}")
        invoke.run(cmd, disown=True)
        return

    multiprocessing.current_process().name = "das-tcs"

    if config.debug:
        logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)

    start_http_server(DAS.METRICS_PORT_TCS)

    if not is_tcs_cs_active():
        LOGGER.error("The TCS Control Server is not running, start the 'tcs_cs' command "
                     "before running the data acquisition.")
        return

    if not is_storage_manager_active():
        LOGGER.error("The storage manager is not running, start the core services "
                     "before running the data acquisition.")
        return

    killer = SignalCatcher()

    with TCSProxy() as tcs_proxy, StorageProxy() as storage:

        # Not all HK parameters are always sent with the periodic telemetry, so we
        # use the know parameters names. Since we further on pass the values as a dictionary
        # to the storage, values which are not in `names` are silently ignored.

        names = patterns.keys()

        # For each of the names, create also a timestamp column for that name

        columns = list(itertools.chain.from_iterable((x + '_ts', x) for x in names))

        # Initialize some variables that will be used for registration to the Storage Manager
        # Use the names in the header of the CSV file as column names.

        origin = "DAS-TCS"
        persistence_class = CSV
        prep = {
            "mode": "a",
            "ending": "\n",
            "header": "TCS EGSE First Connection Tests",
            "column_names": columns,
        }

        storage.register({"origin": origin, "persistence_class": persistence_class, "prep": prep})

        while True:
            try:
                data = tcs_proxy.get_all_housekeeping() if use_all_hk else tcs_proxy.get_data()
                if killer.term_signal_received:
                    break

                if isinstance(data, Failure):
                    LOGGER.warning(f"Received a Failure from the TCS EGSE Control Server:")
                    LOGGER.warning(f"Response: {data}")
                    time.sleep(1.0)
                    continue

                LOGGER.debug(f"received {len(data or [])} data items")

                if data is None:
                    continue

                data = process_data(data)
                storage.save({"origin": origin, "data": data})

                time.sleep(interval)

            except KeyboardInterrupt:
                LOGGER.debug("Interrupt received, terminating...")
                break

        storage.unregister({"origin": origin})


TCS_AMBIENT_RTD = Gauge(
    "tcs_ambient_rtd", "The current ambient temperature on the TCS EGSE"
)
TCS_INTERNAL_RTD = Gauge(
    "tcs_internal_rtd", "The current internal temperature off the TCS EGSE"
)
TCS_FEE_RTD_1 = Gauge(
    "tcs_fee_rtd_1", "The TRP22 sensor for control channel 1"
)
TCS_FEE_RTD_2 = Gauge(
    "tcs_fee_rtd_2", "The TRP22 sensor for control channel 2"
)
TCS_FEE_RTD_3 = Gauge(
    "tcs_fee_rtd_3", "The TRP22 sensor for control channel 3"
)
TCS_TOU_RTD_1 = Gauge(
    "tcs_tou_rtd_1", "The TRP1 sensor for control channel 1"
)
TCS_TOU_RTD_2 = Gauge(
    "tcs_tou_rtd_2", "The TRP1 sensor for control channel 2"
)
TCS_TOU_RTD_3 = Gauge(
    "tcs_tou_rtd_3", "The TRP1 sensor for control channel 3"
)
TCS_CH1_IOUT = Gauge(
    "tcs_ch1_iout", "channel 1 iout"
)
TCS_CH1_POUT = Gauge(
    "tcs_ch1_pout", "channel 1 pout"
)
TCS_CH1_VOUT = Gauge(
    "tcs_ch1_vout", "channel 1 pout"
)
TCS_CH2_IOUT = Gauge(
    "tcs_ch2_iout", "channel 2 iout"
)
TCS_CH2_POUT = Gauge(
    "tcs_ch2_pout", "channel 2 pout"
)
TCS_CH2_VOUT = Gauge(
    "tcs_ch2_vout", "channel 2 pout"
)


def process_data(data: List) -> dict:
    """
    Process the output of the `get_data()` and the `get_all_housekeeping()` commands. Telemetry
    parameters can occur multiple times, only the last entry is retained.

    This function also updates the metrics that are requested by Prometheus.

    Args:
        data: the data as returned by get_data() and get_all_housekeeping().

    Returns:
        an up-to-date dictionary with the parameter values and their timestamps.
    """

    processed_data = {}

    # Create a proper dictionary with the last updated telemetry values.
    # We expect 3 entries: name, date, and value

    for item in data:

        if len(item) == 3:
            value = extract_value(item[0], item[2])
            processed_data.update({f"{item[0]}_ts": item[1], item[0]: value})
        else:
            click.echo("WARNING: incorrect format in data response from TCS EGSE.")

    # Fill in the metrics that will be monitored by Prometheus

    for name, metric in (
            ("ambient_rtd", TCS_AMBIENT_RTD),
            ("internal_rtd", TCS_INTERNAL_RTD),
            ("fee_rtd_1", TCS_FEE_RTD_1),
            ("fee_rtd_2", TCS_FEE_RTD_2),
            ("fee_rtd_3", TCS_FEE_RTD_3),
            ("tou_rtd_1", TCS_TOU_RTD_1),
            ("tou_rtd_2", TCS_TOU_RTD_2),
            ("tou_rtd_3", TCS_TOU_RTD_3),
            ("ch1_iout", TCS_CH1_IOUT),
            ("ch1_pout", TCS_CH1_POUT),
            ("ch1_vout", TCS_CH1_VOUT),
            ("ch2_iout", TCS_CH2_IOUT),
            ("ch2_pout", TCS_CH2_POUT),
            ("ch2_vout", TCS_CH2_VOUT),
    ):
        if name in processed_data:
            metric.set(processed_data[name])

    return processed_data


# Define different regex patterns, e.g. for temperature, time, power, etc.

temperature_pattern = re.compile(r'(.*) ºC')
seconds_pattern = re.compile(r'(.*) s')
milliseconds_pattern = re.compile(r'(.*) ms')
current_pattern = re.compile(r'(.*) A \[(.*) Apk\]')
voltage_pattern = re.compile(r'(.*) V')
voltage_peak_pattern = re.compile(r'(.*) V \[(.*) Vpk\]')
power_pattern = re.compile(r'(.*) mW \[(.*) mWavg\]')
storage_pattern = re.compile(r'\[(.*)\]')
match_all_pattern = re.compile(r'(.*)')

# Assign parsing patterns to each of the parameters that need specific parsing.

patterns = {
    'ambient_rtd': temperature_pattern,
    'ch1_clkheater_period': milliseconds_pattern,
    'ch1_clkheater_ticks': seconds_pattern,
    'ch1_iout': current_pattern,
    'ch1_pid_proctime': seconds_pattern,
    'ch1_pid_sp': temperature_pattern,
    'ch1_pid_ts': seconds_pattern,
    'ch1_pout': power_pattern,
    'ch1_pwm_ontime': milliseconds_pattern,
    'ch1_pwm_proctime': seconds_pattern,
    'ch1_tav': temperature_pattern,
    'ch1_vdc': voltage_pattern,
    'ch1_vout': voltage_peak_pattern,
    'ch2_clkheater_period': milliseconds_pattern,
    'ch2_clkheater_ticks': seconds_pattern,
    'ch2_iout': current_pattern,
    'ch2_pid_proctime': seconds_pattern,
    'ch2_pid_sp': temperature_pattern,
    'ch2_pid_ts': seconds_pattern,
    'ch2_pout': power_pattern,
    'ch2_pwm_ontime': milliseconds_pattern,
    'ch2_pwm_proctime': seconds_pattern,
    'ch2_tav': temperature_pattern,
    'ch2_vdc': voltage_pattern,
    'ch2_vout': voltage_peak_pattern,
    'fee_rtd_1': temperature_pattern,
    'fee_rtd_2': temperature_pattern,
    'fee_rtd_3': temperature_pattern,
    'fee_rtd_tav': temperature_pattern,
    'internal_rtd': temperature_pattern,
    'ni9401_external_clkheater_period': seconds_pattern,
    'ni9401_external_clkheater_timeout': seconds_pattern,
    'psu_vdc': voltage_pattern,
    'spare_rtd_1': temperature_pattern,
    'spare_rtd_2': temperature_pattern,
    'spare_rtd_3': temperature_pattern,
    'spare_rtd_tav': temperature_pattern,
    'storage_mmi': storage_pattern,
    'storage_realtime': storage_pattern,
    'tou_rtd_1': temperature_pattern,
    'tou_rtd_2': temperature_pattern,
    'tou_rtd_3': temperature_pattern,
    'tou_rtd_tav': temperature_pattern,
}


def extract_value(key, value):
    """
    Extract the actual value from the string containing the value and unit plus potential
    additional info. Parsing is done with dedicated regular expressions per parameter, e.g.
    parsing a temperature takes the 'ºC' into account when extracting the actual value.

    Args:
        key (str): name of the parameter
        value (str): the value as returned by the TCS EGSE
    """

    if key not in patterns:
        return value

    match = patterns[key].search(value)
    if match is not None:
        value = match.group(1)
    return value

@cli.command()
@click.option(
    "--use-all-hk", is_flag=True,
    help=("Use get_all_housekeeping() method to read telemetry from the CDAQ. "
          "The device must not be in remote control mode for this.")
)
@click.option(
    "--interval", default=1, help="what is the time delay between measurements [seconds]"
)
@click.option(
    "--background/--no-background", "-bg/-no-bg", default=False,
    help="start the data acquisition in the background"
)
@pass_config
def cdaq(config, use_all_hk, interval, background):
    """
    Run the Data Acquisition System for the CDAQ.

    INPUT_FILE: YAML file containing the Setup for the CDAQ [optional]

    Note: When this command runs in the background, send an INTERRUPT SIGNAL with the kill command
    to terminate. Never send a KILL SIGNAL (9) because then the process will not properly be
    unregistered from the storage manager.

    $ kill -INT <PID>

    """

    if background:
        cmd = "das cdaq-photo"
        cmd += " --use-all-hk" if use_all_hk else ""
        cmd += f" --interval {interval}"
        LOGGER.info(f"Invoking background command: {cmd}")
        invoke.run(cmd, disown=True)
        return

    multiprocessing.current_process().name = "das-cdaq-photodiodes"

    if config.debug:
        logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)

    if not is_cdaq9184_cs_active():
        LOGGER.error("The cdaq Control Server is not running, start the 'cdaq_cs' command "
                     "before running the data acquisition.")
        return

    if not is_storage_manager_active():
        LOGGER.error("The storage manager is not running, start the core services "
                     "before running the data acquisition.")
        return

    metrics_cdaq = define_metrics("DAS-CDAQ-PHOTODIODES")
    hk_names = ["GIAS_OGSE2_PHOTOD_1", "GIAS_OGSE2_PHOTOD_2", "GIAS_OGSE2_TAMPLI_1", "GIAS_OGSE2_TAMPLI_2",
                "GIAS_OGSE2_TSPHERE", "GIAS_OGSE2_GAMPLI_1", "GIAS_OGSE2_GAMPLI_2"]


    # The unit for photodiodes is V, for temperatures is °C and without unit for gains

    start_http_server(DAS.METRICS_PORT_CDAQ)

    # Initialize some variables that will be used for registration to the Storage Manager

    origin = "DAS-CDAQ-PHOTODIODES"
    persistence_class = CSV
    prep = {
        "mode": "a",
        "ending": "\n",
        "header": "CDAQ First Connection Tests",
        "column_names": ["timestamp", *metrics_cdaq],
    }

    killer = SignalCatcher()

    with cdaq9184Proxy() as cdaq, StorageProxy() as storage:

        # Use the names in the header of the CSV file as column names.

        storage.register({"origin": origin, "persistence_class": persistence_class, "prep": prep})

        while True:
            try:
                response = cdaq.read_values()

                if killer.term_signal_received:
                    break
                if not response:
                    LOGGER.warning("Received an empty response from the CDAQ, "
                       "check the connection with the device.")
                    LOGGER.warning(f"Response: {response=}")
                    time.sleep(1.0)
                    continue
                if isinstance(response, Failure):
                    LOGGER.warning(f"Received a Failure from the CDAQ Control Server:")
                    LOGGER.warning(f"Response: {response}")
                    time.sleep(1.0)
                    continue

                reformatted_response = reformat_cdaq_values(response)
                values = reformatted_response[2:]
                hk_dict = {key: value for key, value in zip(hk_names, values)}
                timestamp = format_datetime(datetime.strptime(reformatted_response[0] + '-' + reformatted_response[1], "%y/%m/%d-%H:%M:%S.%f"))
                data = [timestamp] + values
                storage.save({"origin": origin, "data": data})


                for key, value in hk_dict.items():
                    metrics_cdaq[key].set(value)

                # time.sleep(interval)

            except KeyboardInterrupt:
                LOGGER.debug("Interrupt received, terminating...")
                break

            except Exception as exc:
                LOGGER.warning(f"DAS Exception: {exc}", exc_info=True)
                LOGGER.warning("Got a corrupt response from the CDAQ. "
                               "Check log messages for 'DAS Exception'.")
                time.sleep(1.0)
                continue

        storage.unregister({"origin": origin})


def reformat_cdaq_values(data_to_be_reformatted: list) -> list:
    data = data_to_be_reformatted
    if len(data) != 35:
        LOGGER.error(f"Data received from Labview has not the expected length ({len(data)} but expected 35).")
    else:
        # The next elements (see the names in the headers) are not wanted so I delete them:
        # 1) Filtre_Roue_1, Filtre_Roue_2, Shutter, FEMTO_1_BIAS, FEMTO_2_BIAS, FEMTO_1_Input_Current,
        # FEMTO_2_Input_Current (the 7 last elements)
        # 2) Temp_4 to Temp_8 (elements from index 16 to 25)
        # 3) FEMTO_1_OVERLOAD and FEMTO_2_OVERLOAD (elements at indexes 4, 5, 8 and 9)

        # 1)
        del data[-7:]
        # 2)
        del data[16:26]
        # 3)
        for i in [9, 8, 5, 4]:
            del data[i]

        # Only mean is wanted, not deviation. So I delete all deviation elements
        # which are at indexes [3, 5, 7, 9, 11 ( = list(range(3, 12, 2)) )
        for index_to_delete in sorted(list(range(3, 12, 2)), reverse=True):  # I delete in the reverse order
            del data[index_to_delete]

        # The 2 first elements of data are date as str type. I leave them as str type. I convert the other elements of
        # data (which are relevant values) from str to float.
        data = data[:2] + [float(value) for value in data[2:]]

        return data


@cli.command()
@click.option(
    "--background/--no-background", "-bg/-no-bg", default=False,
    help="start the data acquisition in the background"
)
@pass_config
def cdaq_alarms(config, background):
    """
    Run the Data Acquisition System for the CDAQ alarms (CDAQ9375).

    INPUT_FILE: YAML file containing the Setup for the CDAQ [optional]

    Note: When this command runs in the background, send an INTERRUPT SIGNAL with the kill command
    to terminate. Never send a KILL SIGNAL (9) because then the process will not properly be
    unregistered from the storage manager.

    $ kill -INT <PID>

    """

    if background:
        cmd = "das cdaq-alarms"
        LOGGER.info(f"Invoking background command: {cmd}")
        invoke.run(cmd, disown=True)
        return

    multiprocessing.current_process().name = "das-cdaq-alarms"

    if config.debug:
        logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)

    if not is_cdaq9375_cs_active():
        LOGGER.error("The cdaq9375 Control Server is not running, start the 'cdaq9375_cs' command "
                     "before running the data acquisition.")
        return

    if not is_tcs_cs_active():
        LOGGER.error("The TCS Control Server is not running, start the 'tcs_cs' command "
                     "before running the data acquisition.")
        return

    if not is_aeu_cs_active(name="CRIO", timeout=1):
        LOGGER.error("The AEU Control Server is not running, start the 'aeu_cs' command "
                     "before running the data acquisition.")
        return

    if not is_storage_manager_active():
        LOGGER.error("The storage manager is not running, start the core services "
                     "before running the data acquisition.")
        return


    setup = load_setup_from_configuration_manager()

    metrics_cdaq_alarms = define_metrics("DAS-CDAQ-ALARMS")

    start_http_server(DAS.METRICS_PORT_CDAQ_ALARMS)

    # Initialize some variables that will be used for registration to the Storage Manager

    origin = "DAS-CDAQ-ALARMS"
    persistence_class = CSV
    prep = {
        "mode": "a",
        "ending": "\n",
        "header": "CDAQ-ALARMS First Connection Tests",
        "column_names": ["timestamp", *metrics_cdaq_alarms],
    }

    killer = SignalCatcher()

    with cdaq9375Proxy() as cdaq, StorageProxy() as storage, TCSProxy() as tcs_proxy, CRIOProxy() as aeu_crio:

        # Use the names in the header of the CSV file as column names.

        storage.register({"origin": origin, "persistence_class": persistence_class, "prep": prep})

        alarms_temperature = setup.gse.CDAQ_alarms.alarms_temperature

        trp1_min_op = alarms_temperature.trp1_min_op
        trp1_max_op = alarms_temperature.trp1_max_op
        trp1_min_nop = alarms_temperature.trp1_min_nop
        trp1_max_nop = alarms_temperature.trp1_max_nop
        trp22_min_op = alarms_temperature.trp22_min_op
        trp22_max_op = alarms_temperature.trp22_max_op
        trp22_min_nop = alarms_temperature.trp22_min_nop
        trp22_max_nop = alarms_temperature.trp22_max_nop

        alarm_exp1 = False # Low Temp NOP
        alarm_exp2 = False # High Temp NOP
        alarm_exp3 = False # low/High Temp OP
        alarm_exp4 = False # UPS alarm (UPS_Arrakis_alarm_summary or UPS_Ix_alarm_summary)
        while True:
            try:
                response = cdaq.get_tvac_and_ups_state()

                if killer.term_signal_received:
                    break
                if not response:
                    LOGGER.warning("Received an empty response from the CDAQ9375, "
                       "check the connection with the device.")
                    LOGGER.warning(f"Response: {response=}")
                    time.sleep(1.0)
                    continue
                if isinstance(response, Failure):
                    LOGGER.warning(f"Received a Failure from the CDAQ9375 Control Server:")
                    LOGGER.warning(f"Response: {response}")
                    time.sleep(1.0)
                    continue

                # EXP4
                if any([response["UPS_Ix_alarm_summary"], response["UPS_Ix_power_supply_absence"],
                        response["UPS_Arrakis_alarm_summary"], response["UPS_Arrakis_power_supply_absence"]]):
                    alarm_exp4 = True
                else:
                    alarm_exp4 = False

                try:
                    trp1_avg = tcs_proxy.get_housekeeping_value("tou_rtd_tav").value

                    if not trp1_avg:
                        LOGGER.warning("Received an empty response from the TCS, "
                                       "check the connection with the device.")
                        LOGGER.warning(f"Response: {trp1_avg=}")
                        time.sleep(1.0)
                        continue
                    if isinstance(trp1_avg, Failure):
                        LOGGER.warning(f"Received a Failure from the TCS EGSE Control Server:")
                        LOGGER.warning(f"Response: {trp1_avg}")
                        time.sleep(1.0)
                        continue

                    trp1_avg = float(trp1_avg)

                except ValueError:
                    LOGGER.warning(f"TRP1 Value Error in cdaq alarms: trp1_avg should be a number, got {trp1_avg}."
                                   f"\nTerminating...")
                    if trp1_avg == "tbd":
                        LOGGER.warning("Got TBD for TRP1_AVG.\nCheck if the task is well running.\nTerminating...")
                    break

                try:
                    trp22_avg = tcs_proxy.get_housekeeping_value("fee_rtd_tav").value

                    if not trp22_avg:
                        LOGGER.warning("Received an empty response from the TCS, "
                                       "check the connection with the device.")
                        LOGGER.warning(f"Response: {trp22_avg=}")
                        time.sleep(1.0)
                        continue
                    if isinstance(trp22_avg, Failure):
                        LOGGER.warning(f"Received a Failure from the TCS EGSE Control Server:")
                        LOGGER.warning(f"Response: {trp22_avg}")
                        time.sleep(1.0)
                        continue

                    trp22_avg = float(trp22_avg)

                except ValueError:
                    LOGGER.warning(f"TRP22_AVG ValueError: trp22_avg should be a number, got {trp22_avg}."
                                   f"\nTerminating...")
                    if trp22_avg == "tbd":
                        LOGGER.warning("Got TBD for TRP22_AVG.\nCheck if the task is well running.\nTerminating...")
                    break


                aeu_standby = aeu_crio.get_operating_mode() == OperatingMode.STANDBY  # True means aeu is in standby mode

                if aeu_standby:
                    alarm_exp3 = False
                    # EXP1
                    if trp1_avg < trp1_min_nop or trp22_avg < trp22_min_nop:
                        alarm_exp1 = True
                    else:
                        alarm_exp1 = False

                    # EXP2
                    if trp1_avg > trp1_max_nop or trp22_avg > trp22_max_nop:
                        alarm_exp2 = True
                    else:
                        alarm_exp2 = False

                # EXP3
                else:
                    if any([trp1_avg < trp1_min_op, trp1_avg > trp1_max_op,
                            trp22_avg < trp22_min_op, trp22_avg > trp22_max_op]):
                        alarm_exp3 = True
                    else:
                        alarm_exp3 = False

                alarm_exp_dict = {"alarm_EXP1": int(alarm_exp1),
                                  "alarm_EXP2": int(alarm_exp2),
                                  "alarm_EXP3": int(alarm_exp3),
                                  "alarm_EXP4": int(alarm_exp4)}
                response.update(alarm_exp_dict)
                hk_conversion_table = read_conversion_dict("DAS-CDAQ-ALARMS")
                hk_dict = convert_hk_names(response, hk_conversion_table)
                storage.save({"origin": origin, "data": hk_dict})

                hk_dict.pop("timestamp")
                for key, value in hk_dict.items():
                    metrics_cdaq_alarms[key].set(value)

                cdaq.send_egse_state_to_tvac(alarm_exp1, alarm_exp2, alarm_exp3, alarm_exp4)


            except KeyboardInterrupt:
                LOGGER.debug("Interrupt received, terminating...")
                break

            except Exception as exc:
                LOGGER.warning(f"DAS Exception: {exc}", exc_info=True)
                LOGGER.warning("Got a corrupt hk_dict from the CDAQ. "
                               "Check log messages for 'DAS Exception'.")
                time.sleep(1.0)
                continue

        storage.unregister({"origin": origin})

if __name__ == "__main__":
    cli()
