import time
from logging import warning

import pytest

from egse.process import SubProcess
from egse.process import is_process_running
from egse.system import wait_until


@pytest.fixture(scope="module")
def setup_camera_access():
    """
    This fixture starts the N-FEE simulator and the DPU Control Server.

    An
    On Setup, both processes are started, on TearDown both processes are shut down.

    Yields:
        A tuple containing the feesim, dpu_cs SubProcess objects.

    """
    if is_process_running(items=["dpu_cs"]):
        pytest.xfail("DPU CS is already running")

    if is_process_running(items=["feesim"]):
        pytest.xfail("FEESIM is already running")

    feesim = SubProcess("N-FEE Simulator", ["feesim", "start"], ["--zeromq"])
    feesim.execute()

    if wait_until(is_process_running, ["feesim"], interval=1.0, timeout=5.0):
        raise RuntimeError("Couldn't start the N-FEE Simulator within the given time of 5s.")

    dpu_cs = SubProcess("DPU Control Server", ["dpu_cs", "start"], ["--zeromq"])
    dpu_cs.execute()

    if wait_until(is_process_running, ["dpu_cs"], interval=1.0, timeout=5.0):
        raise RuntimeError("Couldn't start the DPU Control Server within the given time of 5s.")

    time.sleep(5.0)  # give the processes time to initialize

    yield feesim, dpu_cs

    dpu_cs_stop = SubProcess("DPU Control Server", ["dpu_cs", "stop"])
    dpu_cs_stop.execute()

    if wait_until(is_process_running, ["dpu_cs", "start"], interval=1.0, timeout=5.0):
        warning("Couldn't stop the DPU Control Server within the given time of 5s. Quiting...")
        dpu_cs.quit()

    feesim.quit()
