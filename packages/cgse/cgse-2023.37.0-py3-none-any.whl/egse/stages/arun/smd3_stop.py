from egse.stages.arun.smd3 import Smd3Controller, Smd3Proxy
import logging

logger = logging.getLogger("smd3_stopper")

if __name__ == "__main__":

    try:
        smd3 = Smd3Proxy()
        logger.info("Stopping through proxy")
    except:
        smd3 = Smd3Controller()
        logger.info("Stopping through controller")
    finally:
        smd3.emergency_stop()

