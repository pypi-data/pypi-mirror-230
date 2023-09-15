import logging

from egse.control import ControlServer
from egse.protocol import CommandProtocol
from egse.settings import Settings
# from egse.fdir.fdir_manager import FdirManagerProxy

from prometheus_client import Gauge

from egse.vacuum.beaglebone.beaglebone import BeagleboneController
from egse.vacuum.beaglebone.beaglebone import BeagleboneInterface
from egse.vacuum.beaglebone.beaglebone import BeagleboneSimulator
from egse.vacuum.beaglebone.beaglebone_devif import BeagleboneCommand
from egse.system import format_datetime
from egse.zmq_ser import bind_address

logger = logging.getLogger(__name__)

COMMAND_SETTINGS = Settings.load(filename='beaglebone.yaml')

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
        
        self.gauge_rmt_mv011_fb = Gauge('GSRON_VALVE_RMT_MV011', '')
        self.gauge_rmt_mv021_fb = Gauge('GSRON_VALVE_RMT_MV012', '')
        self.gauge_rmt_mv031_fb = Gauge('GSRON_VALVE_RMT_MV013', '')
        self.gauge_rmt_mv041_fb = Gauge('GSRON_VALVE_RMT_MV014', '')
        self.gauge_rmt_mv012_fb = Gauge('GSRON_VALVE_RMT_MV021', '')
        self.gauge_rmt_mv022_fb = Gauge('GSRON_VALVE_RMT_MV022', '')
        self.gauge_rmt_mv032_fb = Gauge('GSRON_VALVE_RMT_MV023', '')
        self.gauge_rmt_mv042_fb = Gauge('GSRON_VALVE_RMT_MV024', '')
        self.gauge_rmt_mv002_fb = Gauge('GSRON_VALVE_RMT_MV002', '')
        self.gauge_rmt_mv001_fb = Gauge('GSRON_VALVE_RMT_MV001', '')

        self.gauge_oc_mv011_fb = Gauge('GSRON_VALVE_OC_MV011', '')
        self.gauge_oc_mv021_fb = Gauge('GSRON_VALVE_OC_MV012', '')
        self.gauge_oc_mv031_fb = Gauge('GSRON_VALVE_OC_MV013', '')
        self.gauge_oc_mv041_fb = Gauge('GSRON_VALVE_OC_MV014', '')
        self.gauge_oc_mv012_fb = Gauge('GSRON_VALVE_OC_MV021', '')
        self.gauge_oc_mv022_fb = Gauge('GSRON_VALVE_OC_MV022', '')
        self.gauge_oc_mv032_fb = Gauge('GSRON_VALVE_OC_MV023', '')
        self.gauge_oc_mv042_fb = Gauge('GSRON_VALVE_OC_MV024', '')
        self.gauge_oc_mv002_fb = Gauge('GSRON_VALVE_OC_MV002', '')

        self.gauge_open_mv001_fb = Gauge('GSRON_VALVE_OPEN_MV001', '')
        self.gauge_close_mv001_fb = Gauge('GSRON_VALVE_CLOSE_MV001', '')
        self.gauge_intrlck_door_fb = Gauge('GSRON_VALVE_INTERLOCK_DOOR', '')
        
        self.cache = {'feedback' : {},
                      'remote'   : {}}


    def get_bind_address(self):
        return bind_address(self.control_server.get_communication_protocol(),
                            self.control_server.get_commanding_port())

    def get_status(self):
        status_info = super().get_status()
        try:
            remote = {
                f'GSRON_VALVE_RMT_MV011': self.beaglebone.get_valve('LN2_SHROUD_RMT'),
                f'GSRON_VALVE_RMT_MV012': self.beaglebone.get_valve('LN2_TEB-FEE_RMT'),
                f'GSRON_VALVE_RMT_MV013': self.beaglebone.get_valve('LN2_TEB-TOU_RMT'),
                f'GSRON_VALVE_RMT_MV014': self.beaglebone.get_valve('LN2_TRAP_RMT'),
                f'GSRON_VALVE_RMT_MV021': self.beaglebone.get_valve('N2_SHROUD_RMT'),
                f'GSRON_VALVE_RMT_MV022': self.beaglebone.get_valve('N2_TEB-FEE_RMT'),
                f'GSRON_VALVE_RMT_MV023': self.beaglebone.get_valve('N2_TEB-TOU_RMT'),
                f'GSRON_VALVE_RMT_MV024': self.beaglebone.get_valve('N2_TRAP_RMT'),
                f'GSRON_VALVE_RMT_MV002': self.beaglebone.get_valve('VENT_VALVE_RMT'),
                f'GSRON_VALVE_RMT_MV001': self.beaglebone.get_valve('GATE_VALVE_RMT')
            }

            feedback = {
                f'GSRON_VALVE_OC_MV011': self.beaglebone.get_valve('LN2_SHROUD_FB'),
                f'GSRON_VALVE_OC_MV012': self.beaglebone.get_valve('LN2_TEB-FEE_FB'),
                f'GSRON_VALVE_OC_MV013': self.beaglebone.get_valve('LN2_TEB-TOU_FB'),
                f'GSRON_VALVE_OC_MV014': self.beaglebone.get_valve('LN2_TRAP_FB'),
                f'GSRON_VALVE_OC_MV021': self.beaglebone.get_valve('N2_SHROUD_FB'),
                f'GSRON_VALVE_OC_MV022': self.beaglebone.get_valve('N2_TEB-FEE_FB'),
                f'GSRON_VALVE_OC_MV023': self.beaglebone.get_valve('N2_TEB-TOU_FB'),
                f'GSRON_VALVE_OC_MV024': self.beaglebone.get_valve('N2_TRAP_FB'),
                f'GSRON_VALVE_OC_MV002': self.beaglebone.get_valve('VENT_VALVE_FB'),
                f'GSRON_VALVE_OPEN_MV001': self.beaglebone.get_valve('GATE_OPEN_FB'),
                f'GSRON_VALVE_CLOSE_MV001': self.beaglebone.get_valve('GATE_CLOSE_FB'),
                f'GSRON_VALVE_INTERLOCK_DOOR': self.beaglebone.get_valve('INTRLCK_DOOR_FB')
            }
            
            
            # Remember state, even in manual mode
            if feedback != self.cache['feedback']:
                for key, value in feedback.items():
                    code = key.split('_')[-1]

                    if 'DOOR' in key:
                        continue
                    elif 'MV001' in key:
                        if not remote[f'GSRON_VALVE_RMT_{code}']:
                            if 'OPEN' in key:
                                if value:
                                    self.beaglebone.set_valve(code, False)
                                else:
                                    self.beaglebone.set_valve(code, True)
                            if 'CLOSE' in key:
                                if value:
                                    self.beaglebone.set_valve(code, True)
                                else:
                                    self.beaglebone.set_valve(code, False)
                    else:
                        if not remote[f'GSRON_VALVE_RMT_{code}']:
                            self.beaglebone.set_valve(code, value)
                        
            self.cache['feedback'] = feedback
            self.cache['remote']   = remote
            
            status_info['Remote']   = remote
            status_info['Feedback'] = feedback

        except Exception as exc:
            logger.info("Status omitted")
            raise exc 
        return status_info


    def get_housekeeping(self) -> dict:
        hk_dict = {'timestamp': format_datetime()}
        try:
            hk_dict = {
                'timestamp': format_datetime(),
                f'GSRON_VALVE_RMT_MV011'     : self.cache['remote']['GSRON_VALVE_RMT_MV011'],
                f'GSRON_VALVE_RMT_MV012'     : self.cache['remote']['GSRON_VALVE_RMT_MV012'],
                f'GSRON_VALVE_RMT_MV013'     : self.cache['remote']['GSRON_VALVE_RMT_MV013'],
                f'GSRON_VALVE_RMT_MV014'     : self.cache['remote']['GSRON_VALVE_RMT_MV014'],
                f'GSRON_VALVE_RMT_MV021'     : self.cache['remote']['GSRON_VALVE_RMT_MV021'],
                f'GSRON_VALVE_RMT_MV022'     : self.cache['remote']['GSRON_VALVE_RMT_MV022'],
                f'GSRON_VALVE_RMT_MV023'     : self.cache['remote']['GSRON_VALVE_RMT_MV023'],
                f'GSRON_VALVE_RMT_MV024'     : self.cache['remote']['GSRON_VALVE_RMT_MV024'],
                f'GSRON_VALVE_RMT_MV002'     : self.cache['remote']['GSRON_VALVE_RMT_MV002'],
                f'GSRON_VALVE_RMT_MV001'     : self.cache['remote']['GSRON_VALVE_RMT_MV001'],
                f'GSRON_VALVE_OC_MV011'      : self.cache['feedback']['GSRON_VALVE_OC_MV011'],
                f'GSRON_VALVE_OC_MV012'      : self.cache['feedback']['GSRON_VALVE_OC_MV012'],
                f'GSRON_VALVE_OC_MV013'      : self.cache['feedback']['GSRON_VALVE_OC_MV013'],
                f'GSRON_VALVE_OC_MV014'      : self.cache['feedback']['GSRON_VALVE_OC_MV014'],
                f'GSRON_VALVE_OC_MV021'      : self.cache['feedback']['GSRON_VALVE_OC_MV021'],
                f'GSRON_VALVE_OC_MV022'      : self.cache['feedback']['GSRON_VALVE_OC_MV022'],
                f'GSRON_VALVE_OC_MV023'      : self.cache['feedback']['GSRON_VALVE_OC_MV023'],
                f'GSRON_VALVE_OC_MV024'      : self.cache['feedback']['GSRON_VALVE_OC_MV024'],
                f'GSRON_VALVE_OC_MV002'      : self.cache['feedback']['GSRON_VALVE_OC_MV002'],
                f'GSRON_VALVE_OPEN_MV001'    : self.cache['feedback']['GSRON_VALVE_OPEN_MV001'],
                f'GSRON_VALVE_CLOSE_MV001'   : self.cache['feedback']['GSRON_VALVE_CLOSE_MV001'],
                f'GSRON_VALVE_INTERLOCK_DOOR': self.cache['feedback']['GSRON_VALVE_INTERLOCK_DOOR']
            }
        except Exception as exc:
            logger.warning(f'failed to get HK ({exc})')

            return hk_dict

        self.gauge_rmt_mv011_fb.set(hk_dict[f'GSRON_VALVE_RMT_MV011'])
        self.gauge_rmt_mv021_fb.set(hk_dict[f'GSRON_VALVE_RMT_MV012'])
        self.gauge_rmt_mv031_fb.set(hk_dict[f'GSRON_VALVE_RMT_MV013'])
        self.gauge_rmt_mv041_fb.set(hk_dict[f'GSRON_VALVE_RMT_MV014'])
        self.gauge_rmt_mv012_fb.set(hk_dict[f'GSRON_VALVE_RMT_MV021'])
        self.gauge_rmt_mv022_fb.set(hk_dict[f'GSRON_VALVE_RMT_MV022'])
        self.gauge_rmt_mv032_fb.set(hk_dict[f'GSRON_VALVE_RMT_MV023'])
        self.gauge_rmt_mv042_fb.set(hk_dict[f'GSRON_VALVE_RMT_MV024'])
        self.gauge_rmt_mv002_fb.set(hk_dict[f'GSRON_VALVE_RMT_MV002'])
        self.gauge_rmt_mv001_fb.set(hk_dict[f'GSRON_VALVE_RMT_MV001'])

        self.gauge_oc_mv011_fb.set(hk_dict[f'GSRON_VALVE_OC_MV011'])
        self.gauge_oc_mv021_fb.set(hk_dict[f'GSRON_VALVE_OC_MV012'])
        self.gauge_oc_mv031_fb.set(hk_dict[f'GSRON_VALVE_OC_MV013'])
        self.gauge_oc_mv041_fb.set(hk_dict[f'GSRON_VALVE_OC_MV014'])
        self.gauge_oc_mv012_fb.set(hk_dict[f'GSRON_VALVE_OC_MV012'])
        self.gauge_oc_mv022_fb.set(hk_dict[f'GSRON_VALVE_OC_MV022'])
        self.gauge_oc_mv032_fb.set(hk_dict[f'GSRON_VALVE_OC_MV023'])
        self.gauge_oc_mv042_fb.set(hk_dict[f'GSRON_VALVE_OC_MV024'])
        self.gauge_oc_mv002_fb.set(hk_dict[f'GSRON_VALVE_OC_MV002'])

        self.gauge_open_mv001_fb.set(hk_dict[f'GSRON_VALVE_OPEN_MV001'])
        self.gauge_close_mv001_fb.set(hk_dict[f'GSRON_VALVE_CLOSE_MV001'])
        self.gauge_intrlck_door_fb.set(hk_dict[f'GSRON_VALVE_INTERLOCK_DOOR'])

        return hk_dict
