import logging

from egse.aeu.aeu import CRIOProxy
from egse.tcs.tcs import TCSProxy

LOGGER = logging.getLogger("egse.test.tcs")

while True:

    time.sleep(1.0)

    with TCSProxy() as tcs_proxy, CRIOProxy() as aeu_crio:

        try:
            trp1_avg = float(tcs_proxy.get_housekeeping_value("tou_rtd_tav").value)
        except ValueError:
            LOGGER.warning(f"TRP1 Value Error in cdaq alarms: trp1_avg should be a number, got {trp1_avg}."
                           f"\nTerminating...")
            if trp1_avg == "tbd":
                LOGGER.warning("Got TBD for TRP1_AVG.\nCheck if the task is well running.\nTerminating...")
            break
            trp22_avg = float(tcs_proxy.get_housekeeping_value("fee_rtd_tav").value)
        except ValueError:
            LOGGER.warning(f"TRP22_AVG ValueError: trp22_avg should be a number, got {trp22_avg}."
                           f"\nTerminating...")
            if trp22_avg == "tbd":
                LOGGER.warning("Got TBD for TRP22_AVG.\nCheck if the task is well running.\nTerminating...")
            break

        aeu_standby = aeu_crio.get_operating_mode() == OperatingMode.STANDBY  # True means aeu is in standby mode
