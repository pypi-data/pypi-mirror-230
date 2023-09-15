from egse.control import ControlServer
from egse.protocol import CommandProtocol
from egse.settings import Settings

from prometheus_client import Gauge

from egse.lampcontrol.beaglebone.beaglebone import BeagleboneController
from egse.lampcontrol.beaglebone.beaglebone import BeagleboneInterface
from egse.lampcontrol.beaglebone.beaglebone import BeagleboneSimulator
from egse.lampcontrol.beaglebone.beaglebone_devif import BeagleboneCommand
from egse.synoptics import SynopticsManagerProxy
from egse.system import format_datetime
from egse.zmq_ser import bind_address

COMMAND_SETTINGS = Settings.load(filename='beaglebone.yaml')
SITE_ID = Settings.load("SITE").ID

gauge_lamp_on = Gauge("GSRON_LAMP_LAMP_ON", "")
gauge_laser_on = Gauge("GSRON_LAMP_LASER_ON", "")
gauge_lamp_module_fault = Gauge("GSRON_LAMP_MODULE_FAULT", "")
gauge_controller_fault = Gauge("GSRON_LAMP_CTRL_FAULT", "")


class BeagleboneProtocol(CommandProtocol):
    def __init__(self, control_server:ControlServer):
        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.beaglebone = BeagleboneSimulator()
        else:
            self.beaglebone = BeagleboneController()

        self.load_commands(COMMAND_SETTINGS.Commands, BeagleboneCommand, BeagleboneInterface)

        self.build_device_method_lookup_table(self.beaglebone)

        self.synoptics = SynopticsManagerProxy()

    def get_bind_address(self):
        return bind_address(self.control_server.get_communication_protocol(),
                            self.control_server.get_commanding_port())

    def get_status(self):
        status_dict = super().get_status()
        status_dict['lamp_status'] = {
            'lamp_state' : self.beaglebone.get_lamp_on(),
            'laser_state' : self.beaglebone.get_laser_on(),
            'module_fault' : self.beaglebone.get_lamp_module_fault(),
            'controller_fault' : self.beaglebone.get_controller_fault()
        }
        return status_dict

    def get_housekeeping(self) -> dict:

        hk_dict = dict()
        hk_dict['timestamp'] = format_datetime()

        hk_dict['GSRON_LAMP_LAMP_ON'] = self.beaglebone.get_lamp_on()
        hk_dict['GSRON_LAMP_LASER_ON'] = self.beaglebone.get_laser_on()

        # Send the HK acquired so far to the Synoptics Manager
        self.synoptics.store_th_synoptics(hk_dict)

        hk_dict['GSRON_LAMP_MODULE_FAULT'] = self.beaglebone.get_lamp_module_fault()
        hk_dict['GSRON_LAMP_CTRL_FAULT'] = self.beaglebone.get_controller_fault()

        gauge_lamp_on.set(hk_dict['GSRON_LAMP_LAMP_ON'])
        gauge_laser_on.set(hk_dict['GSRON_LAMP_LASER_ON'])
        gauge_lamp_module_fault.set(hk_dict['GSRON_LAMP_MODULE_FAULT'])
        gauge_controller_fault.set(hk_dict['GSRON_LAMP_CTRL_FAULT'])

        return hk_dict
