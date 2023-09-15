import datetime
import logging
import os
import sys
import tempfile
import time
from pathlib import Path

import pytest

from egse.obsid import ObservationIdentifier
from egse.obsid import TEST_LAB
from egse.process import SubProcess
from egse.process import is_process_running
from egse.storage import AlreadyRegisteredError
from egse.storage import StorageProxy
from egse.storage.persistence import CSV
from egse.system import format_datetime
from egse.system import wait_until

logger = logging.getLogger(__name__)

#################################################################################
# BE AWARE that this test uses the StorageProxy to connect and QUIT THE SERVER. #
# If you have a Storage Manager running when you run this test, this server     #
# will be terminated by this test!                                              #
#################################################################################


SITE_ID = "CSL1"


@pytest.fixture(scope="module")
def setup_storage():

    with tempfile.TemporaryDirectory() as temp_dir:

        data_location = f"{temp_dir}/data/{SITE_ID}"

        Path(data_location, "obs").mkdir(mode=0o755, parents=True)
        Path(data_location, "daily").mkdir(mode=0o755, parents=True)
        os.environ["PLATO_DATA_STORAGE_LOCATION"] = f"{temp_dir}/data/"  # data_location

        storage_cs = SubProcess(
            "storage_cs",
            [sys.executable, '-m', 'egse.storage.storage_cs', "start"]
        )
        storage_cs.execute()

        if wait_until(is_process_running, ["storage_cs"], interval=1.0, timeout=5.0):
            raise RuntimeError("Couldn't start the Process Control Server within the given time of 5s.")

        time.sleep(5.0)  # give the processes time to initialize

        yield storage_cs

        storage_cs.quit()


def test_storage_location(setup_storage):

    storage_proxy = StorageProxy(hostname="localhost")
    assert storage_proxy.ping()

    path = storage_proxy.get_storage_location()

    assert Path(path, "daily").exists()
    assert Path(path, "obs").exists()
    assert path.endswith(SITE_ID)


def test_storage(setup_storage):
    """Test the Storage server."""

    obsid = ObservationIdentifier(SITE_ID, 2, 1234)
    reg_name = "HK-Hexapod"
    camera_name = "Cornet"

    storage_proxy = StorageProxy(hostname="localhost")
    assert storage_proxy.ping()

    service_proxy = storage_proxy.get_service_proxy()
    assert service_proxy.ping()

    assert "start_observation" in storage_proxy.get_commands()

    header = ["Timestamp", "Origin"]
    header.extend([hex(x) for x in range(10)])

    storage_proxy.register(
        {"origin": reg_name, "persistence_class": CSV, "prep": {"header": header, "mode": "w"}}
    )

    assert reg_name in storage_proxy.get_registry_names()

    for filename in storage_proxy.get_filenames(item={"origin": reg_name}):
        assert f"daily/{format_datetime('today')}/" in str(filename)

    # save some data outside an observation

    storage_proxy.save({"origin": reg_name, "data": "# no real data...starting an observation"})

    # Now start an observation, data shall be saved in a separate file

    storage_proxy.start_observation(obsid=obsid, camera_name=camera_name)

    # Test if filenames contain obsid and camera name when observation is running

    assert any(f"{obsid.create_id(order=TEST_LAB)}_{camera_name.lower()}" in str(x)
               for x in storage_proxy.get_filenames(item={"origin": reg_name}))

    for idx in range(3):
        data = [datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y%m%d %H%M%S"), reg_name]
        data.extend([x * idx + 1000 for x in range(10)])
        storage_proxy.save({"origin": reg_name, "data": data})

    storage_proxy.end_observation(obsid)

    storage_proxy.save({"origin": reg_name, "data": "# no real data...ended the observation"})

    storage_proxy.disconnect_cs()

    return_code = service_proxy.quit_server()
    logger.info(f"Storage Control Server quit message: {return_code}")

    service_proxy.disconnect_cs()


def test_registry():

    from egse.storage import Registry

    reg = Registry()

    assert len(reg) == 0

    reg.register("one", 1)
    reg.register("two", 2)

    assert len(reg) == 2

    assert "one" in reg
    assert "zero" not in reg

    with pytest.raises(ValueError):
        _ = 1 in reg  # item names in reg shall be of type str

    reg.unregister("two")

    assert len(reg) == 1
    assert "two" not in reg

    with pytest.raises(KeyError):
        reg.unregister("two")

    with pytest.raises(AlreadyRegisteredError):
        reg.register("one", "uno")
