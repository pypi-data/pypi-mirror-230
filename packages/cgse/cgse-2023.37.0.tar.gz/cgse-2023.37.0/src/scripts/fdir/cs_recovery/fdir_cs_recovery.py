import logging
import importlib

from argparse import ArgumentParser

from egse.procman import ProcessManagerProxy
from egse.control import is_control_server_active
from egse.zmq_ser import connect_address
from egse.setup   import get_setup, Setup
from egse.settings import Settings


logger = logging.getLogger(__name__)
logging.basicConfig()

parser = ArgumentParser()
parser.add_argument('cs_name', help='Name of the CS in the config')
args = parser.parse_args()

SETUP = get_setup()
SETUP = SETUP['gse']

devices = {}
devices = Setup.find_devices(SETUP, devices=devices)

cs_name = args.cs_name

for key, value in devices.items():
    if cs_name in key:
        proxy = value[0]
        args  = value[1]
        module_name = proxy[7:].rsplit(".", 1)[0]
        
        module = importlib.import_module(module_name)
        
        ctrl_settings = module.CTRL_SETTINGS
        transport = ctrl_settings.PROTOCOL
        hostname = ctrl_settings.HOSTNAME
        if module_name == "egse.aeu.aeu" or "egse.tempcontrol.agilent.agilent3497" in module_name:
            name = key.split(" ")[1].upper()
            commanding_port = ctrl_settings[name]["COMMANDING_PORT"]
        else:
            commanding_port = ctrl_settings.COMMANDING_PORT           

if is_control_server_active(connect_address(transport,
                                            hostname,
                                            commanding_port)):
    logger.info("False positive: CS seems to be online")
else:
    try:
        with ProcessManagerProxy() as procman:
            procman.start_cs(cs_name, False)
            
    except Exception as e:
        logger.error(f"Could not start {args.cs_name}")
     
        
        logger.info(f"finished {__name__}")
        