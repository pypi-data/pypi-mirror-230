import logging
import threading
import ssl
import time
import importlib
import yaml
import numpy as np
import zmq
import pickle
from   smtplib      import SMTP
from collections    import namedtuple

from egse.setup                 import load_setup
from egse.zmq_ser               import connect_address, bind_address
from egse.device                import DeviceInterface
from egse.command               import ClientServerCommand
from egse.proxy                 import Proxy
from egse.protocol              import CommandProtocol
from egse.decorators            import dynamic_interface
from egse.settings              import Settings
from egse.system                import replace_environment_variable, find_class
from egse.hk                    import get_housekeeping, HKError
from egse.system                import format_datetime, EPOCH_1958_1970
from egse.control               import ControlServer, is_control_server_active
from egse.alert.gsm.beaglebone  import BeagleboneProxy
from egse.fdir.fdir_manager     import FdirManagerProxy
from egse.procman               import ProcessManagerProxy

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("Alert Manager Control Server")
DEVICE_SETTINGS = Settings.load(filename='alertman.yaml')

CS_STATUS = ['Offline', 'Controller disconnected', 'Online']

LIMIT = 0
SETPOINT = 1
RATEOFCHANGE = 2
MASK = 3

class AlertException(BaseException):
    """
    Base class for all expcetion related to the Alerts
    """
    pass             



class AlertManagerCommand(ClientServerCommand):
    """
    Command (client-server) for process management.
    """
    pass



def load_alert_configuration(phase):
    """ Load the alert configuration for the configration file.
    
    Returns all the alerts defined in the given file. Uses defaults for missing fields.
    """
    AlertConfiguration = namedtuple('AlertConfiguration', ['name',
                                                           'metric',
                                                           'timeout',
                                                           'unit',
                                                           'actions',
                                                           'maximum_age',
                                                           'fdir_code',
                                                           'sample_rate',
                                                           'alert_type',
                                                           'limits'])
    
    try:
        configuration = load_setup().gse.alert_manager.configuration[phase]
    except AttributeError as ex:
        raise AlertException("Could not find a configuration for the {} phase in the setup".format(phase)) from ex 
    else:
        alerts = {}

        for name, config in configuration['alerts'].items():
            try:
                if   'operational_limit'    in config:
                    alert_type = LIMIT
                    
                    limits = {
                        'min' : config['operational_limit'].get('min', None),
                        'max' : config['operational_limit'].get('max', None)
                    }
                    
                elif 'rate_of_change'       in config:
                    alert_type = RATEOFCHANGE
                    
                    limits = {
                        'limit' : config['rate_of_change'].get('limit', None),
                        'time_window' : config['rate_of_change'].get('time_window', 60)
                    }
                
                    if limits['limit'] is None:
                        raise AlertException(\
                                    "Invalid configuration: No limit defined in the configuration")
                    
                elif 'mask'                 in config:
                    alert_type = MASK
                    limits = {'mask':  config['mask']}
                    
                elif 'setpoint'             in config:
                    alert_type = SETPOINT
                    
                    limits = {
                        'metric' : None,
                        'value'  : None,
                        'offset' : config['setpoint'].get('offset', 2)
                    }
                    
                    if 'setpoint' in config:
                        if 'sensor' not in config['setpoint'] and \
                        'value' not in config['setpoint']:
                            raise AlertException(\
                                "Invalid configuration: No metric or value defined in configuration")
                        elif 'sensor' in config['setpoint'] and \
                            'value' in config['setpoint']:
                            raise AlertException(\
                                "Invalid configuration: Can not have both a metric and value in configuration")
                        else:
                            if 'sensor' in config['setpoint']:
                                limits['metric'] = config['setpoint']['sensor']
                            if 'value' in config['setpoint']:
                                limits['value'] = config['setpoint']['value']       
                else:
                    raise AlertException("Invalid configuration: No alert type was defined in the configuration")
                
                alerts[name] = AlertConfiguration(
                    name,
                    config['sensor'],
                    config.get('timeout', 5),
                    config.get('unit', ''),
                    config.get('actions', []),
                    config.get('maxAge', 30),
                    config.get('fdir', ''),
                    config.get('sampleRate', 5),
                    alert_type,
                    limits
                )
                
            except Exception as ex:
                logger.warning("Could not create configuration for alert '%s' : %s" % (name, ex))
            
        return configuration, alerts



class Alert:
    """
    Alert class representing a single alert
    
    An alert has one main function self.update() which retrieves data from housekeeping and compares
    it to the limits defined in the configuration. The Alert Manager Controller runs this method in
    a thread. Sanity checks have been added to prevent false positives.
    """
    def __init__(self, configuration, notification_worker):
        """ Initialization of a new alert, to be used by the Alert Manager
        

        Args:
            configuration (_type_): _description_
            notification_worker (_type_): _description_
        """
        self.configuration          = configuration
        self.notification_worker    = notification_worker
        self.value                  = 0.0
        self.triggered              = False
        self.notified               = False
        self.active                 = False
        self.timed_out              = 0.0
        self.cycle_check            = False
        self.cycle_timeout          = 0.0
        self.lastTimestamp          = 0.0
        self.last_update            = 0.0
        self.thread                 = threading.Thread()
    
    def metric_is_available(self):
        """ Check whether a metric is available in the HK files """
        try:
            timestamp, _ = get_housekeeping(hk_name=self.configuration.metric)
            if time.time() - (float(timestamp) - EPOCH_1958_1970) > self.configuration.maximum_age:
                raise
        except:
            logger.warning(f"Alert '{self.configuration.name}' : " \
                           f"Metric: '{self.configuration.metric}' is currently unavailable." \
                            f"Please restart this alert when metric is available.")
            return False
        else:
            return True
    
    def daily_cycle_check(self):
        """ When a metric is not found in housekeeping, keeping trying for 60 seconds.
        This makes sure that alerts don't crash during the daily cycle of housekeeping files

        Returns:
            bool: Whether the file has cycled or not
        """
        try:
            _, _ = get_housekeeping(hk_name=self.configuration.metric)
        except HKError as ex:
            if not self.cycle_check:
                self.cycle_check = True
                self.cycle_timeout = time.time()
            
            if (time.time() - self.cycle_timeout) > 300:
                logger.info(f"Alert '{self.configuration.name}' : No daily file found after 5 minutes. Housekeeping is unavailable: {ex}")
                self.active = False
                self.triggered = False
                self.timed_out = 0.0
                
            return False
        else:
            logger.debug(f"Alert '{self.configuration.name}' : Daily file has been cycled")
            self.cycle_check = False
            return True

    
    def generate_alert_message(self):
        """ Generates the email body for the alert based on the alert type
        """
        body = ""
        
        fdir_code = self.configuration.fdir_code
        actions   = self.configuration.actions
        
        if self.configuration.alert_type == LIMIT:
            if self.configuration.limits['min'] != None and self.configuration.limits['max'] != None:
                body += f"- {self.configuration.name} exceeded its operational limits of {float(self.configuration.limits['min']):.3e} & {float(self.configuration.limits['max']):.3e}. Current value: {float(self.value):.3e}\n"
            elif self.configuration.limits['min'] != None:
                body += f"- {self.configuration.name} exceeded its operatinoal limits of {float(self.configuration.limits['min']):.3e}. Current value: {float(self.value):.3e}\n"
            elif self.configuration.limits['max'] != None:
                body += f"- {self.configuration.name} exceeded its operational limits of {float(self.configuration.limits['max']):.3e}. Current value: {float(self.value):.3e}\n"
        elif self.configuration.alert_type is SETPOINT:
            body += f"- {self.configuration.name} setpoint offset was larger than {float(self.configuration.limits['offset']):.3e}. Current value: {float(self.value):.3e}\n"
        elif self.configuration.alert_type is MASK:
            body += f"- {self.configuration.name} is {bool(self.value)}"
        elif self.configuration.alert_type is RATEOFCHANGE:
            body += f"- {self.configuration.name} has exceeded its RoC limit of {float(self.configuration.limits['limit']):.3e}. Current value: {float(self.value):.3e}\n"
        
        if fdir_code:
            body += f"\t- FDIR code: '{self.configuration.fdir_code}' was fired\n"
        
        if actions:
            body += f"\t- Corrective actions:\n"
            for action in actions:
                body += f"\t\t\t-   {action}\n"
        
        return body
    
    def trigger_alert(self):
        """ Send a notifcation and FDIR signal, also ensures that alerts are only triggered once
        """
        if not self.notified:
            self.triggered = True
            logger.critical(f"Alert '{self.configuration.name}' : triggered!")
            
            self.notification_worker.add_notification(0, self.generate_alert_message())
            
            self.signal_fdir()

            self.notified = True
    
    def clear_alert(self):
        """ Resets the alert after it being triggered
        """
        if self.triggered:
            logger.info(f"Alert '{self.configuration.name}' : Alert status has been reset.")
            self.triggered = False
            self.timed_out = 0.0
            self.notified  = False 
    
    def signal_fdir(self):
        """ Signal the FDIR manager, if a fidr code was configured
        """
        if self.configuration.fdir_code:
            try:
                logger.info(f"Signaled fdir: '{self.configuration.fdir_code}'")
                with FdirManagerProxy() as fdir:
                    fdir.signal_fdir(self.configuration.fdir_code, self.configuration.metric)
            except Exception as e:
                logger.critical(f"Alert '{self.configuration.name}' : Could not signal FDIR manager. {e}")
        else:
            logger.info(f"Alert '{self.configuration.name}' Does not have a configured FDIR code.")
    
    def get_housekeeping(self, metric, time_window=None):
        """ Retrieves housekeeping from the HK files. Checks whether the value actually exists,
            and if the age is still appropiate.
        """
        try:
            timestamps, values = get_housekeeping(hk_name=metric, time_window=time_window)
        except HKError:
            if self.daily_cycle_check():
                timestamps, values = get_housekeeping(hk_name=metric, time_window=time_window)
            else:
                raise AlertException(f"{self.configuration.name} : Daily file cycle is being checked")


        most_recent_timestamp = float(timestamps[-1]) if type(timestamps) == np.ndarray else timestamps

        self.lastTimestamp = most_recent_timestamp
        
        is_alive = time.time() - (most_recent_timestamp - EPOCH_1958_1970) > self.configuration.maximum_age
        value_exists = values[-1] if type(values) == np.ndarray else values

        if is_alive:
            self.active = False
            logger.critical(f"Alert '{self.configuration.name}' : Last housekeeping value was older than {self.configuration.maximum_age} seconds")
            raise Exception(f"Alert '{self.configuration.name}' : Last housekeeping value was older than {self.configuration.maximum_age} seconds")

        if not value_exists:
            logger.critical(f"Alert '{self.configuration.name}' : Housekeeping returned an emptry string as latest value")
            self.active = False
            raise Exception(f"Alert '{self.configuration.name}' : Housekeeping returned an emptry string as latest value")
            
        return timestamps, values
                
    def limit_check(self, value):
        """ Compares a given value to the configured upper and lower limits
        """ 
        min_triggered = False
        max_triggered = False
        
        self.value = value
        
        if self.configuration.limits['max']:
            if float(value) > self.configuration.limits['max']:
                self.timed_out = time.time() if self.timed_out == 0.0 else self.timed_out
                if (time.time() - self.timed_out) > self.configuration.timeout:
                    max_triggered = True

        if self.configuration.limits['min']:
            if float(value) < self.configuration.limits['min']:
                self.timed_out = time.time() if self.timed_out == 0.0 else self.timed_out
                if (time.time() - self.timed_out) > self.configuration.timeout:
                    min_triggered = True
                   
        if min_triggered or max_triggered:
            self.trigger_alert()
        else:
            self.clear_alert()

    def setpoint_check(self, value):
        """ Compares a given value to the configured setpoint (dynamic/static setpoint)
        """
        self.value = value
        
        if self.configuration.limits['metric']:
            try:
                _, sp_value = self.get_housekeeping(self.configuration.limits['metric'], None)
            except Exception as ex:
                logger.warning(ex, exc_info=True)
                self.active = False
                return
        
        else:
            sp_value = self.configuration.limits['value']
            
        if not (float(sp_value) - self.configuration.limits['offset']) <= float(value) <= (float(sp_value) + self.configuration.limits['offset']):
            self.timed_out = time.time() if self.timed_out == 0.0 else self.timed_out
            if (time.time() - self.timed_out) > self.configuration.timeout:
                self.trigger_alert()
        else:
            self.clear_alert()
        
      
    def rate_of_change_check(self, timestamps, values):
        """ Compares a given value to the configured rate-of-change setpoint
        """
        deltaY = float(values[-1]) - float(values[0])
        deltaX = float(timestamps[-1]) - float(timestamps[0])
        
        self.value = deltaY / deltaX
        
        if self.configuration.limits['limit'] < 0:
            if self.value < self.configuration.limits['limit']:
                self.timed_out = time.time() if self.timed_out == 0.0 else self.timed_out
                if (time.time() - self.timed_out) > self.configuration.timeout:
                    self.trigger_alert()
            else:
                self.clear_alert()
        else:
            if self.value > self.configuration.limits['limit']:
                self.timed_out = time.time() if self.timed_out == 0.0 else self.timed_out
                if (time.time() - self.timed_out) > self.configuration.timeout:
                    self.trigger_alert()
            else:
                self.clear_alert()
            
    
    def mask_check(self, value):
        """ Masks a bitmap and check the state of a single bit
        """
        self.value = value
        
        if (int(value) >> self.configuration.limits['mask']) & 0b1:
            self.timed_out = time.time() if self.timed_out == 0.0 else self.timed_out
            if (time() - self.timed_out) > self.configuration.maximum_age:
                self.trigger_alert()
        else:
            self.clear_alert()

    def update(self):
        """ Update current alert status
        """
        if self.active:
            if (time.time() - self.last_update) > self.configuration.sample_rate:
                try:
                    timestamps, values = self.get_housekeeping(self.configuration.metric,
                                                            self.configuration.limits.get('time_window', None))
                except Exception as ex:
                    logger.warning(ex)
                    self.active = False
                    return
                except AlertException as a_ex:
                    logger.warning(a_ex)
                    self.last_update = (time.time() + 10) # Increase delay before next check
                    return
                else:
                    self.cycle_check = False
                
                try:
                    if self.configuration.alert_type == LIMIT:
                        self.limit_check(values)
                    elif self.configuration.alert_type is SETPOINT:
                        self.setpoint_check(values)
                    elif self.configuration.alert_type is MASK:
                        self.mask_check(values)
                    elif self.configuration.alert_type is RATEOFCHANGE:
                        self.rate_of_change_check(timestamps, values)
                except Exception as ex:
                    logger.warning(ex)
                    raise AlertException(ex)
                
                self.last_update = time.time()
       
       
        
class ControlServerWorker:
    """ Worker to monitor all running control servers
    """
    def __init__(self, notifyer):
        self.pm_proxy = ProcessManagerProxy()
        self.devices  = self.pm_proxy.get_devices()
        self.notifyer = notifyer
        self.thread   = threading.Thread() 
        self.active   = False
        self.monitors = {}
        
        for process_name, process_info in self.devices.items():
            
            if ('alert' in process_name.lower())or ('fdir' in process_name.lower()):
                continue
            
            self.monitors[process_name] = {'name' : process_name,
                                           'type' : process_info[0],
                                           'type_as_type' : find_class(process_info[0][7:]),
                                           'device_args' : process_info[1],
                                           'socket' : None,
                                           'timeout' : 0.5,
                                           'connected' : False,
                                           'address' : None,
                                           'prev_status' : False}
        
        self.fdir_codes = {}
        
        self.connect_to_sockets() 

    
    def load_fdir_codes(self, configuration):
        if 'hardware' in configuration:
            self.fdir_codes =  configuration['hardware']
        else:
            self.fdir_codes = []
    
    def connect_to_sockets(self):
        """ Connect to commanding/monitoring socket of control servers
        """
        for monitor in self.monitors.values():
            try:
                module_name     = monitor['type'][7:].rsplit(".", 1)[0]
                module          = importlib.import_module(module_name)
                
                ctrl_settings   = module.CTRL_SETTINGS
                transport       = ctrl_settings.PROTOCOL
                hostname        = ctrl_settings.HOSTNAME
                
                if module_name == "egse.aeu.aeu" or "egse.tempcontrol.agilent.agilent3497" in module_name:
                    name = monitor['name'].split(" ")[1].upper()
                    
                    commanding_port = ctrl_settings[name]['COMMANDING_PORT']
                    monitoring_port = ctrl_settings[name]['MONITORING_PORT']
                else:
                    commanding_port = ctrl_settings.COMMANDING_PORT
                    monitoring_port = ctrl_settings.MONITORING_PORT
                 
                monitoring_address = connect_address(transport, hostname, monitoring_port)

                monitor['socket'] = zmq.Context().socket(zmq.SUB)
                monitor['socket'].connect(monitoring_address)
                monitor['socket'].setsockopt_string(zmq.SUBSCRIBE, "")
                
                monitor['address'] = connect_address(transport, hostname, commanding_port)
                monitor['connected'] = True                
                
            except AttributeError as attr_er:
                logger.exception(attr_er)
                monitor['connected'] = False
            
            # break
    
    def get_device_status(self, monitor):  
        """ Retreive the current status of a control server
        """
        status    = 0

        try:
            with find_class(monitor['type'])(*monitor['device_args']) as proxy:
                if isinstance(proxy, DeviceInterface):
                    try:
                        if proxy.is_connected():
                            # CS connected to controller
                            status = 2
                        else:
                            # CS not connected to controller
                            status = 1
                    except AttributeError:                        
                            status = 1
                    
                else:
                    status      = 2
                    
        except ConnectionError:
            pass
        
        return status
                    
    def start(self):
        """ Start Control server monitor worker
        """
        logger.info("Starting control server monitoring loop")
        
        if self.thread != None:
            if self.thread.is_alive():
                return
        
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        
        
    def stop(self):
        """ Stop Control server monitor worker
        """
        self.active = False
        if self.thread != None:
            if self.thread.is_alive():
                self.thread.join()
                return
        logger.info("Control server monitor has been stopped")
    
    def run(self):
        """ Control server monitoring loop
        """
        self.active = True
        
        while self.active:
            for monitor in self.monitors.values():
                if monitor['connected']:
                    status = 0
                    try:
                        socket_list, _, _ = zmq.select([monitor['socket']], [], [], timeout=monitor['timeout'])
                        
                        if monitor['socket'] in socket_list:
                            pickle_string   = monitor['socket'].recv()
                            monitoring_info = pickle.loads(pickle_string)

                            monitor['timeout'] = monitoring_info['delay'] / 1000 + 0.5 # [s]
                            
                            status = self.get_device_status(monitor)
                                
                    except zmq.ZMQError:
                        pass    

                    # Timeout occured
                    else:
                        if not is_control_server_active(endpoint=monitor['address'], timeout=30):
                            status = 0
                        else:
                            monitor['timeout'] += 0.5
                
                    if monitor['prev_status'] != status:
                        
                        if monitor['prev_status'] >= 1 and status == 0:
                            
                            msg = f"-  {monitor['name']} Contol Server has gone offline."
                            
                            self.notifyer.add_notification(-1, msg)
                            
                            logger.warning(f"{monitor['name']} has stopped. Signalling FDIR to attempt a restart")
                            
                            try:
                                with FdirManagerProxy() as fdir:
                                    fdir.signal_fdir('FDIR_CS_STOPPED', [monitor['name']])
                            except Exception as ex:
                                logger.critical(f"Could not send FDIR signal: {ex}")
                                
                        elif monitor['prev_status'] == 2 and status == 1:
                            
                            msg = f"-  {monitor['name']} Control Server has lost connection to the device controller"
                            
                            self.notifyer.add_notification(-1, msg)

                            if self.fdir_codes != {}:
                                if monitor['name'] in self.fdir_codes:
                                    fdir_code = self.fdir_codes[monitor['name']]
                                    try:
                                        with FdirManagerProxy() as fdir:
                                            fdir.signal_fdir(f"FDIR_{fdir_code['code']}_HW", [f"{fdir_code['arg']}"])
                                    except Exception as ex:
                                        logger.critical(f"Could not send FDIR signal: {ex}")
                            
                            logger.warning(f"{monitor['name']} has lost connection to the device. Signalling FDIR to recover")
                            
                        monitor['prev_status'] = status
                        
                logger.debug(f"{monitor['name']} Control Server status: {CS_STATUS[monitor['prev_status']]}")
            time.sleep(60)



class AlertNotificationWorker:
    """
    Worker for handling the pushing of notification
    """
    def __init__(self):
        self.sender     = replace_environment_variable(CTRL_SETTINGS.EMAIL_SENDER)
        self.recipients = replace_environment_variable(CTRL_SETTINGS.EMAIL_CS_RECIPIENTS)
        
        self._server    = replace_environment_variable(CTRL_SETTINGS.EMAIL_SERVER)
        self._port      = 25
        self._context   = ssl.create_default_context()
        
        self.gsm_module = BeagleboneProxy()
        
        self.alert_messages = []
        self.cs_messages    = []
        
        self.thread = threading.Thread()

    def notify(self):
        '''
        Threaded method that waits 30 seconds for new messages before pushing the notification 
        '''
        # Check if message buffer is empty
        n = len(self.alert_messages) + len(self.cs_messages)
        
        if n != 0:
            start_time = time.time()
            
            # Wait until no new messages are added to the buffer in the last 30 seconds
            while time.time() - start_time < 60:
                n2 = len(self.alert_messages) + len(self.cs_messages)
                
                if n2 is not n:
                    start_time = time.time()
                    n = n2
                time.sleep(1)
            
            self.send_mail()
            self.send_sms()
            
            self.clear_notifications()

    
    def add_notification(self, nType, msg: str):
        """
        Adds a message to the notification queue and start the threaded method, if it is not running
        """
        
        # Add notification to message buffer
        if nType in [LIMIT, SETPOINT, RATEOFCHANGE, MASK]:
            self.alert_messages.append(msg)
        else:
            self.cs_messages.append(msg)
        # See if notification thread has already been started 
        if not self.thread.is_alive():
            self.thread.__init__(target=self.notify, daemon=True)
            self.thread.start()
        
    def clear_notifications(self):
        """
        Clears the notification queue's
        """
        self.alert_messages = []
        self.cs_messages    = []

    def send_mail(self):
        """
        """
        message = """\
Subject: Plato Common-EGSE Notification

"""
        # message = """Subject: Plato Common-EGSE Notification"""
        if len(self.alert_messages) > 0:
            message += ''.join(self.alert_messages)
        
        if len(self.cs_messages) > 0:
            message += ''.join(self.cs_messages)
        
        message += "\n\nKind regards,\n" \
                "Your friendly PLATO notification bot\n\n" \
                "If I am not working as expected, please contact: s.n.gomashie@sron.nl"
        try:
            with SMTP(self._server, self._port) as server:
                server.sendmail(self.sender, self.recipients.split(','), message)
        except Exception as ex:
            logger.critical(f"Notification worker could not send an email: {ex}")
            
        logger.debug(f"Email send: {self.sender} {self.recipients}")

    def send_sms(self):
        self.gsm_module.set_alert(1)

class AlertManagerInterface:
    """
    Interface for dynamic loading of the command for Alert Management.
    """
    @dynamic_interface
    def load_configuration(self, phase = 'none'):
        """ Load a new phase into the alert manager. """
    
        raise NotImplementedError
        
    @dynamic_interface
    def status(self, name = None) -> dict:
        """ Returns the status of all configured alerts """
        
        raise NotImplementedError
        
    @dynamic_interface
    def stop_cs_monitor(self):
        """ Stops the control server monitor """
        
        raise NotImplementedError
    
    @dynamic_interface
    def start_cs_monitor(self):
        """ Starts the control server monitor """
        
        raise NotImplementedError
        
    @dynamic_interface
    def start_alert(self, name = None):
        """ Start the alert monitor """
        
        raise NotImplementedError
        
    @dynamic_interface
    def stop_alert(self, name = None):
        """ Stop the alert monitor """
        
        raise NotImplementedError
  
  
     
class AlertManagerController(AlertManagerInterface):
    
    """
    Controller for Alert Management
    """
    
    def __init__(self, phase='none'):
        """ Initialization for the Alert Manager Controller.

        Args:
            phase (str, optional): _description_. Defaults to 'none'.
        """
        self.phase                  = phase
        self.active                 = False
        self.alerts                 = {}
        self.notification_worker    = AlertNotificationWorker()
        self.control_server_worker  = ControlServerWorker(self.notification_worker)
        
        self.thread                 = threading.Thread()
        
        self.load_configuration(phase)
        self.control_server_worker.start()

    def load_configuration(self, phase = 'none'):
        """ Load a new phase into the alert manager. """
        if phase != 'none':
            self.stop_alert()
            
            try:
                self.configuration, alerts = load_alert_configuration(phase)
                self.alerts = self.initialize_alerts(alerts)
                
                self.control_server_worker.load_fdir_codes(self.configuration)
            except Exception as ex:
                logger.warning(f"Could not load {phase} phase: {ex}")
            else:
                self.phase = phase
        
        else:
            self.stop_alert()
            self.alerts = {}
            self.phase = phase

        logger.info(f"Alert manager has been configured for the {self.phase} phase")
    
    def initialize_alerts(self, alerts):
        """ Initialize the alerts
        """
        for key, configuration in alerts.items():
            try:
                alerts[key] = Alert(configuration, self.notification_worker)
            except Exception as ex:
                logger.warning(f"Could not create alert '{key}': {ex}")
        return alerts
    
    def status(self, name = None) -> dict:
        """ Returns the status of all configured alerts """
        status = {}
        if self.alerts:
            for key, alert in self.alerts.items():
                status[key] = {
                    'active'            : alert.active,
                    'triggered'         : alert.triggered,
                    'value'             : alert.value,
                    'lastTimestamp'         : alert.lastTimestamp
                }
            if name and (name in status):
                return  status[name]
            else:
                return status
        
    def stop_cs_monitor(self):
        """ Stops the control server monitor 
        """
        self.control_server_worker.stop()
    
    def start_cs_monitor(self):
        """ Starts the control server monitor 
        """
        self.control_server_worker.start()
    
    def start_alert(self, name = None):
        """ Start one or all alert monitors
        """
        if name != None:
            self.alerts[name].active = True
        else:
            for alert in self.alerts.values():
                alert.active = True
        
        if self.thread.is_alive():
            return

        logger.info(f"Starting alert monitor in {self.phase} phase")
    
        self.thread.__init__(target=self.run)
        self.thread.setDaemon(True)
        self.thread.start()
    
    def stop_alert(self, name = None):
        """ Stop one or all alert monitors
        """
        if name != None:
            self.alerts[name].active = False
        else:
            
            self.active = False
            for alert in self.alerts.values():
                alert.active = False
                
            if self.thread.is_alive():
                self.thread.join()
    
    def run(self):
        """ The alert monitoring loop
        """
        self.active = True

        while self.active:
            for alert in self.alerts.values():
                if alert.active:
                    try:
                        alert.update()
                    except Exception as ex:
                        logger.info(ex)
                time.sleep(0.1)
                    



class AlertManagerProxy(Proxy, AlertManagerInterface):
    """
    Proxy for Alert Management, used to connect to the Alert Manager
    Control Server and send commands remotely.
    """

    def __init__(
        self,
        protocol=CTRL_SETTINGS.PROTOCOL,
        hostname=CTRL_SETTINGS.HOSTNAME,
        port=CTRL_SETTINGS.COMMANDING_PORT,
    ):
        """Initialisation of a new Proxy for Alert Management.

        If no connection details (transport protocol, hostname, and port) are
        not provided, these are taken from the settings file.

        Args:
            - protocol: Transport protocol [default is taken from settings
                        file].
            - hostname: Location of the control server (IP address) [default
                        is taken from settings file].
            - port: TCP port on which the Control Server is listening for
                    commands [default is taken from settings file].
        """

        super().__init__(connect_address(protocol, hostname, port))



class AlertManagerProtocol(CommandProtocol):
    """
    Command Protocol for Alert Management.
    """
    def __init__(self, control_server: ControlServer, phase):
        """Initialisation of a new Protocol for Alert Management.

        The initialisation of this Protocol consists of the following steps:

            - create a Controller to which the given Control Server should send commands;
            - load the commands;
            - build a look-up table for the commands.

        Args:
            - control_server: Control Server via which commands should be sent
                              to the Controller.
        """

        super().__init__()

        # Control Server for Alert Management

        self.control_server = control_server

        # Create a new Controller for Alert Management

        self.controller = AlertManagerController(phase)

        # Load the commands (for commanding of the AM Controller) from the
        # YAML file into a dictionary, stored in the AM Protocol

        self.load_commands(
            DEVICE_SETTINGS.Commands, AlertManagerCommand, AlertManagerController
        )

        # Build a look-up table for the methods

        self.build_device_method_lookup_table(self.controller)


    def get_bind_address(self):
        """Returns the address to bind a socket to.

        This bind address is a properly formatted URL, based on the
        communication protocol and the commanding port.

        Returns:
            - Properly formatted URL to bind a socket to.
        """

        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )

    def get_status(self) -> dict:
        """Returns the status information for the Control Server.

        This status information is returned in the form of a dictionary that
        contains the following information about the Control Server for
        Alert Management:

            - timestamp (str): string representation of the current datetime;
            - PID (int): process ID for the Control Server;
            - Up (float): uptime of the Control Server [s];
            - UUID (uuid1): Universally Unique Identifier for the Control
                            Server;
            - RSS (int): 'Resident Set Size', this is the non-swapped physical
                         memory a process has used [byte];
            - USS (int): 'Unique Set Size', this is the memory which is unique
                         to a process [byte];
            - CPU User (float): time spent in user mode [s];
            - CPU System (float): time spent in kernel mode [s];
            - CPU count: number of CPU cores in use by the process;
            - CPU% (float): process CPU utilization as a percentage [%].
            - Alert Status (dict): The status of all active alerts
            - Alert Phase (int): The enumerate value of the current phase

        Returns:
            - Dictionary with status information for the Control Server for
              Alert Management.
        """

        status = super().get_status()

        status['alert_status'] = self.controller.status()
        status['phase']        = self.controller.phase
        
        return status

    def get_housekeeping(self) -> dict:
        """Returns the housekeeping data for the Control Server.

        This housekeeping data is returns in the form of a dictionary that
        contains the following information about the Control Server for
        Alert Management:

            - timestamp (str): string representation of the current datetime.

        Returns:
            - Dictionary with housekeeping data for the Control Server for
              Alert Management.
        """

        return {"timestamp": format_datetime()}

    def quit(self):
        self.controller.quit()
    
    
    
def main():
    
    dev = AlertManagerController()
    
if __name__ == "__main__":
    main()