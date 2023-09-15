import logging

from prometheus_client import Gauge

from egse.control import ControlServer
from egse.protocol import CommandProtocol
from egse.settings import Settings
# from egse.fdir.fdir_manager import FdirManagerProxy

from egse.ups.apc.apc import APCController
from egse.ups.apc.apc import APCInterface
from egse.ups.apc.apc import APCSimulator
from egse.ups.apc.apc import APCCommand
from egse.system import format_datetime
from egse.zmq_ser import bind_address

logger = logging.getLogger(__name__)

COMMAND_SETTINGS = Settings.load(filename='apc.yaml')

class APCProtocol(CommandProtocol):
    def __init__(self, control_server:ControlServer):
        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.apc = APCSimulator()
        else:
            self.apc = APCController()

        self.load_commands(COMMAND_SETTINGS.Commands, APCCommand, APCInterface)

        self.build_device_method_lookup_table(self.apc)
        
        self.gauge_linev     = Gauge('GSRON_UPS_LINEV', '')
        self.gauge_loadpct     = Gauge('GSRON_UPS_LOADPCT', '')
        self.gauge_bcharge     = Gauge('GSRON_UPS_BCHARGE', '')
        self.gauge_timeleft     = Gauge('GSRON_UPS_TIMELEFT', '')
        self.gauge_mbattchg     = Gauge('GSRON_UPS_MBATTCHG', '')
        self.gauge_mintimel     = Gauge('GSRON_UPS_MINTIMEL', '')
        self.gauge_maxtime     = Gauge('GSRON_UPS_MAXTIME', '')
        self.gauge_maxlinev     = Gauge('GSRON_UPS_MAXLINEV', '')
        self.gauge_minlinev     = Gauge('GSRON_UPS_MINLINEV', '')
        self.gauge_outputv     = Gauge('GSRON_UPS_OUTPUTV', '')
        self.gauge_dlowbatt     = Gauge('GSRON_UPS_DLOWBATT', '')
        self.gauge_lotrans     = Gauge('GSRON_UPS_LOTRANS', '')
        self.gauge_hitrans     = Gauge('GSRON_UPS_HITRANS', '')
        self.gauge_itemp     = Gauge('GSRON_UPS_ITEMP', '')
        self.gauge_alarmdel     = Gauge('GSRON_UPS_ALARMDEL', '')
        self.gauge_battv     = Gauge('GSRON_UPS_BATTV', '')
        self.gauge_linefreq     = Gauge('GSRON_UPS_LINEFREQ', '')
        self.gauge_lastxfer     = Gauge('GSRON_UPS_LASTXFER', '')
        self.gauge_numxfers     = Gauge('GSRON_UPS_NUMXFERS', '')
        self.gauge_tonbatt     = Gauge('GSRON_UPS_TONBATT', '')
        self.gauge_cumonbatt     = Gauge('GSRON_UPS_CUMONBATT', '')
        self.gauge_xoffbatt     = Gauge('GSRON_UPS_XOFFBATT', '')
        self.gauge_statflag     = Gauge('GSRON_UPS_STATFLAG', '')
        self.gauge_onbatt       = Gauge('GSRON_UPS_ONBATT', '')


    def get_bind_address(self):
        return bind_address(self.control_server.get_communication_protocol(),
                            self.control_server.get_commanding_port())

    def get_status(self):
        return super().get_status()

    def get_housekeeping(self) -> dict:

        hk_dict = {'timestamp': format_datetime()}

        try:
            dct = self.apc.get_status_dict()
            hk_dict[f'GSRON_UPS_LINEV'] = dct['LINEV']
            hk_dict[f'GSRON_UPS_LOADPCT'] = dct['LOADPCT']
            hk_dict[f'GSRON_UPS_BCHARGE'] = dct['BCHARGE']
            hk_dict[f'GSRON_UPS_TIMELEFT'] = dct['TIMELEFT']
            hk_dict[f'GSRON_UPS_MBATTCHG'] = dct['MBATTCHG']
            hk_dict[f'GSRON_UPS_MINTIMEL'] = dct['MINTIMEL']
            hk_dict[f'GSRON_UPS_MAXTIME'] = dct['MAXTIME']
            hk_dict[f'GSRON_UPS_MAXLINEV'] = dct['MAXLINEV']
            hk_dict[f'GSRON_UPS_MINLINEV'] = dct['MINLINEV']
            hk_dict[f'GSRON_UPS_OUTPUTV'] = dct['OUTPUTV']
            hk_dict[f'GSRON_UPS_DLOWBATT'] = dct['DLOWBATT']
            hk_dict[f'GSRON_UPS_LOTRANS'] = dct['LOTRANS']
            hk_dict[f'GSRON_UPS_HITRANS'] = dct['HITRANS']
            hk_dict[f'GSRON_UPS_ITEMP'] = dct['ITEMP']
            hk_dict[f'GSRON_UPS_ALARMDEL'] = dct['ALARMDEL']
            hk_dict[f'GSRON_UPS_BATTV'] = dct['BATTV']
            hk_dict[f'GSRON_UPS_LINEFREQ'] = dct['LINEFREQ']
            hk_dict[f'GSRON_UPS_NUMXFERS'] = dct['NUMXFERS']
            hk_dict[f'GSRON_UPS_TONBATT'] = dct['TONBATT']
            hk_dict[f'GSRON_UPS_CUMONBATT'] = dct['CUMONBATT']
            hk_dict[f'GSRON_UPS_STATFLAG'] = int(dct['STATFLAG'], 16)
            hk_dict[f'GSRON_UPS_ONBATT']   = 'ONBATT' in dct['STATUS']

        except Exception as exc:
            logger.exception("failed to get HK: %s", exc)

            return hk_dict
        
        self.gauge_linev.set(hk_dict[f'GSRON_UPS_LINEV'])
        self.gauge_loadpct.set(hk_dict[f'GSRON_UPS_LOADPCT'])
        self.gauge_bcharge.set(hk_dict[f'GSRON_UPS_BCHARGE'])
        self.gauge_timeleft.set(hk_dict[f'GSRON_UPS_TIMELEFT'])
        self.gauge_mbattchg.set(hk_dict[f'GSRON_UPS_MBATTCHG'])
        self.gauge_mintimel.set(hk_dict[f'GSRON_UPS_MINTIMEL'])
        self.gauge_maxtime.set(hk_dict[f'GSRON_UPS_MAXTIME'])
        self.gauge_maxlinev.set(hk_dict[f'GSRON_UPS_MAXLINEV'])
        self.gauge_minlinev.set(hk_dict[f'GSRON_UPS_MINLINEV'])
        self.gauge_outputv.set(hk_dict[f'GSRON_UPS_OUTPUTV'])
        self.gauge_dlowbatt.set(hk_dict[f'GSRON_UPS_DLOWBATT'])
        self.gauge_lotrans.set(hk_dict[f'GSRON_UPS_LOTRANS'])
        self.gauge_hitrans.set(hk_dict[f'GSRON_UPS_HITRANS'])
        self.gauge_itemp.set(hk_dict[f'GSRON_UPS_ITEMP'])
        self.gauge_alarmdel.set(hk_dict[f'GSRON_UPS_ALARMDEL'])
        self.gauge_battv.set(hk_dict[f'GSRON_UPS_BATTV'])
        self.gauge_linefreq.set(hk_dict[f'GSRON_UPS_LINEFREQ'])
        self.gauge_numxfers.set(hk_dict[f'GSRON_UPS_NUMXFERS'])
        self.gauge_tonbatt.set(hk_dict[f'GSRON_UPS_TONBATT'])
        self.gauge_cumonbatt.set(hk_dict[f'GSRON_UPS_CUMONBATT'])
        self.gauge_statflag.set(hk_dict[f'GSRON_UPS_STATFLAG'])
        self.gauge_onbatt.set(hk_dict[f'GSRON_UPS_ONBATT'])

        return hk_dict
