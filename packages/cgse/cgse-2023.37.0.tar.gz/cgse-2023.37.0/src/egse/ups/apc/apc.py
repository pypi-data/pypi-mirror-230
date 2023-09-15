import logging
import socket
from collections import OrderedDict

from egse.decorators import dynamic_interface
from egse.device import DeviceInterface
from egse.proxy import Proxy
from egse.settings import Settings
from egse.zmq_ser import connect_address
from egse.command import ClientServerCommand

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("APC Control Server")
DEVICE_SETTINGS = Settings.load(filename='apc.yaml')

CMD_STATUS = "\x00\x06status".encode()
EOF = "  \n\x00\x00"
SEP = ":"
BUFFER_SIZE = 1024
ALL_UNITS = (
    "Minutes",
    "Seconds",
    "Percent",
    "Volts",
    "Watts",
    "Amps",
    "Hz",
    "C",
    "VA",
    "Percent Load Capacity"
)

class APCError(Exception):
    pass


class APCCommand(ClientServerCommand):
    def get_cmd_string(self, *args, **kwargs):
        out = super().get_cmd_string(*args, **kwargs)
        return out + '\n'

class APCInterface(DeviceInterface):
    """ APC base class."""

    @dynamic_interface
    def get_bcharge(self):
        """ Battery charge. """
        return NotImplemented

    @dynamic_interface
    def get_onbatt(self):
        """ On battery power. """
        return NotImplemented

    @dynamic_interface
    def get_timeleft(self):
        """ Timeleft when on battery. """
        return NotImplemented


class APCSimulator(APCInterface):
   """ APC simulator class. """

   def __init__(self):
       self._is_connected = True

   def is_connected(self):
       return self._is_connected

   def is_simulator(self):
       return True

   def connect(self):
       self._is_connected = True

   def disconnect(self):
       self._is_connected = False

   def reconnect(self):
       if self.is_connected():
           self.disconnect()
       self.connect()

   def get_bcharge(self):
       return 90.0

   def get_onbatt(self):
       return False

   def get_timeleft(self):
       return 1000.0


class APCController(APCInterface):

    def __init__(self):
        super().__init__()
        self._is_connected = True

    def is_simulator(self):
        return False

    def is_connected(self):
        return self._is_connected

    def connect(self):
        self._is_connected = True

    def disconnect(self):
        self._is_connected = False


    def reconnect(self):
        self._is_connected = True

    def get_linev(self):
        dct = self._parse(self._get(), True)
        return float(dct['LINEV'])
    
    def get_loadpct(self):
        dct = self._parse(self._get(), True)
        return float(dct['LOADPCT'])

    def get_bcharge(self):
        dct = self._parse(self._get(), True)
        return float(dct['BCHARGE'])

    def get_timeleft(self):
        dct = self._parse(self._get(), True)
        return float(dct['TIMELEFT'])

    def get_onbatt(self):
        dct = self._parse(self._get(), True)
        return 'ONBATT' in dct['STATUS']
    
    def get_mbattchg(self):
        dct = self._parse(self._get(), True)
        return float(dct['MBATTCHG'])
    
    def get_mintimel(self):
        dct = self._parse(self._get(), True)
        return float(dct['MINTIMEL'])
    
    def get_maxtime(self):
        dct = self._parse(self._get(), True)
        return float(dct['MAXTIME'])
    
    def get_maxlinev(self):
        dct = self._parse(self._get(), True)
        return float(dct['MAXLINEV'])
    
    def get_minlinev(self):
        dct = self._parse(self._get(), True)
        return float(dct['MINLINEV'])
    
    def get_outputv(self):
        dct = self._parse(self._get(), True)
        return float(dct['OUTPUTV'])

    def get_dlowbatt(self):
        dct = self._parse(self._get(), True)
        return float(dct['DLOWBATT'])

    def get_lotrans(self):
        dct = self._parse(self._get(), True)
        return float(dct['LOTRANS'])
    
    def get_hitrans(self):
        dct = self._parse(self._get(), True)
        return float(dct['HITRANS'])
    
    def get_itemp(self):
        dct = self._parse(self._get(), True)
        return float(dct['ITEMP'])
    
    def get_alarmdel(self):
        dct = self._parse(self._get(), True)
        return float(dct['ALARMDEL'])
    
    def get_status_dict(self):
        return self._parse(self._get(), True)

    def _get(self, host="localhost", port=3551, timeout=30):
        """
        Connect to the APCUPSd NIS and request its status.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.send(CMD_STATUS)
        buffr = ""
        while not buffr.endswith(EOF):
            buffr += sock.recv(BUFFER_SIZE).decode()
        sock.close()
        return buffr


    def _split(self, raw_status):
        """
        Split the output from get_status() into lines, removing the length and
        newline chars.
        """
        # Remove the EOF string, split status on the line endings (\x00), strip the
        # length byte and newline chars off the beginning and end respectively.
        return [x[1:-1] for x in raw_status[:-len(EOF)].split("\x00") if x]


    def _parse(self, raw_status, strip_units=False):
        """
        Split the output from get_status() into lines, clean it up and return it as
        an OrderedDict.
        """
        lines = self._split(raw_status)
        if strip_units:
            lines = self._strip_units_from_lines(lines)
        # Split each line on the SEP character, strip extraneous whitespace and
        # create an OrderedDict out of the keys/values.
        return OrderedDict([[x.strip() for x in x.split(SEP, 1)] for x in lines])


    def _strip_units_from_lines(self, lines):
        """
        Removes all units from the ends of the lines.
        """
        for line in lines:
            for unit in ALL_UNITS:
                if line.endswith(" %s" % unit):
                    line = line[:-1-len(unit)]
            yield line

class APCProxy(Proxy, APCInterface):
    def __init__(self, protocol=CTRL_SETTINGS.PROTOCOL,
                 hostname=CTRL_SETTINGS.HOSTNAME,
                 port=CTRL_SETTINGS.COMMANDING_PORT):
        super().__init__(connect_address(protocol, hostname, port))
