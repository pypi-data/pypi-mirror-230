import logging
import multiprocessing
import sys

import click
import zmq

from prometheus_client  import start_http_server

from egse.settings      import Settings
from egse.control       import ControlServer, is_control_server_active
from egse.system        import replace_environment_variable
from egse.alert         import AlertManagerProtocol, AlertManagerProxy
from egse.zmq_ser       import connect_address

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("Alert Manager Control Server")

class AlertManagerControlServer(ControlServer):
    """
    The Alert Manager Control Server handles all Common-EGSE Alerts and notification.
    """
    def __init__(self, phase):
        """ Initialisation of a new Control Server for Alert Management

        The initialisation of this Control Server consists of the following
        steps:

            - Define the device protocol;
            - Bind the command socket to the device protocol (to listen for
              commands);
            - Add the device protocol to the poller, to be able to listen for
              commands on different sockets in one thread.
        """
        
        super().__init__()

        # Protocol used for commanding
        
        self.device_protocol = AlertManagerProtocol(self, phase)
        
        # Bind to a socket to listen for commands
        
        self.logger.debug(f"Binding ZeroMQ socket to {self.device_protocol.get_bind_address()}")
        self.device_protocol.bind(self.dev_ctrl_cmd_sock)

        # Listen on different sockets in the same threads -> poller
        
        self.poller.register(self.dev_ctrl_cmd_sock, zmq.POLLIN)


    def get_communication_protocol(self):
        """Returns the communication protocol, as defined in the settings.

        Returns:
            - Communication protocol, as defined in the settings.
        """
        return CTRL_SETTINGS.PROTOCOL

    def get_commanding_port(self):
        """Returns the commanding port number.

        The commanding port is the port on which the Controller listens for
        commands, using the REQ-REP (ZeroMQ) socket pattern.  Its number is
        read from the settings file.

        Returns:
            - Number of the port on which the Controller listens for commands.
        """
        return CTRL_SETTINGS.COMMANDING_PORT

    def get_service_port(self):
        """Returns the service port number.

        The service port is the port on which the Controller listens for
        configuration and administration, using the PUB-SUB (ZeroMQ) socket
        pattern.  Its number is read from the settings file.

        Returns:
            - Number of the port on which the Controller listens for
              configuration and administration.
        """
        return CTRL_SETTINGS.SERVICE_PORT

    def get_monitoring_port(self):
        """Returns the monitoring port number.

        The monitoring port is the port on which the Controller sends periodic
        information on the device, using the PUB-SUB (ZeroMQ) socket
        pattern.  Its number is read from the settings file.

        Returns:
            - Number of the port on which the Controller sends periodic status
              information on the device.
        """
        return CTRL_SETTINGS.MONITORING_PORT

    def get_storage_mnemonic(self):
        """Returns the storage mnemonic for the Controller.

        The storage mnemonic is used in the filename of the housekeeping of
        the Controller (as using by the Storage).  If this is not defined in
        the settings file, "PM" will be used instead.

        Returns:
            - Storage mnemonic for the Controller.
        """
        try:
            
            # As defined in the settings file
            
            return CTRL_SETTINGS.STORAGE_MNEMONIC
        except AttributeError:
            
            # Default
            
            return "AM"

    def before_serve(self):
        """ Start the Prometheus server """
        start_http_server(CTRL_SETTINGS.METRICS_PORT)
        
    def after_serve(self):
        """ Stop all running alert threads """
        self.device_protocol.controller.stop_all_alerts()
        self.device_protocol.controller.stop_all_cs_monitors()


@click.group()
def cli():
    pass

@cli.command()
@click.argument('phase', type=click.Choice(['none', 'warm', 'transition', 'cold'], case_sensitive=False), default='none')
def start(phase):
    """ Start the Alert Manager """
    multiprocessing.current_process().name = "alertman_cs"

    # Check if prerequisites are fulfilled
    try:
        check_prerequisites()
    except RuntimeError as exc:
        print(exc)
        logger.error(exc)
        return 0

    try:
        control_server = AlertManagerControlServer(phase)
        control_server.serve()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    except SystemExit as exit_code:
        print("System Exit with code {}.".format(exit_code))
        sys.exit(exit_code)
    except Exception:
        import traceback

        traceback.print_exc(file=sys.stdout)

    return 0

@cli.command()
def stop():
    """Sends a 'quit_server' command to the Alert Manager"""
    with AlertManagerProxy() as am:
        sp = am.get_service_proxy()
        sp.quit_server()

@cli.command()    
def status():
    """ Print the status of the Alert Manager Control Server"""
    import rich
    
    rich.print("Alert Manager")
    
    protocol = CTRL_SETTINGS.PROTOCOL
    hostname = CTRL_SETTINGS.HOSTNAME
    port     = CTRL_SETTINGS.COMMANDING_PORT
    
    endpoint = connect_address(protocol, hostname, port)
    
    if is_control_server_active(endpoint):
        rich.print(f"   Status: [green]active")
        
        with AlertManagerProxy() as am:
            rich.print(f"   Hostname: {am.get_ip_address()}")
            rich.print(f"   Monitoring port: {am.get_monitoring_port()}")
            rich.print(f"   Commanding port: {am.get_commanding_port()}")
            rich.print(f"   Service port: {am.get_service_port()}")
            phase = am.current_phase()
            alerts = am.alert_status(None)
            if alerts:
                num = len(alerts)
                active = 0
                triggered = 0
                for alert in alerts.values():
                    if alert['active']:
                        active += 1
                    if alert['triggered']:
                        triggered += 1
                rich.print(f"   Phase: [bright_cyan]{phase.upper()}")
                rich.print(f"   Running (Active/Total): [red]{active}[white]/[green]{num}")
                rich.print(f"   Triggered:  [red]{triggered}[white]/[green]{num}")
            rich.print(f"   Email server: {replace_environment_variable(CTRL_SETTINGS.EMAIL_SERVER)}")
            rich.print(f"   Bot address: {replace_environment_variable(CTRL_SETTINGS.EMAIL_SENDER)}")
            rich.print(f"   CS recipients: {replace_environment_variable(CTRL_SETTINGS.EMAIL_CS_RECIPIENTS)}")
            rich.print(f"   Warning recipients: {replace_environment_variable(CTRL_SETTINGS.EMAIL_WARNING_RECIPIENTS)}")
    else:
        rich.print(f"   Status: [red]Inactive")
    

def check_prerequisites():
    """ Checks whether the required environment variables have been set. """
    sender = replace_environment_variable(CTRL_SETTINGS.EMAIL_SENDER)
    server = replace_environment_variable(CTRL_SETTINGS.EMAIL_SERVER)
    warning_recip = replace_environment_variable(CTRL_SETTINGS.EMAIL_WARNING_RECIPIENTS)
    cs_recip = replace_environment_variable(CTRL_SETTINGS.EMAIL_CS_RECIPIENTS)
    
    if not (sender and server and warning_recip and cs_recip):
        raise RuntimeError(
            "The environment variables referenced in the Settings.yaml file for the "
            "'EMAIL_SENDER', 'EMAIL_SERVER', 'EMAIL_WARNING_RECIPIENTS', 'EMAIL_CS_RECIPIENTS'"
            "of the Alert Manager control server does not exist, please set the "
            "Environment variables."
        )

    logger.debug(f"Alert sender: {sender}")
    logger.debug(f"Alert server: {server}")
    logger.debug(f"Warning recipients: {warning_recip}")
    logger.debug(f"Cs recipients: {cs_recip}")

if __name__ == "__main__":
    sys.exit(cli())
