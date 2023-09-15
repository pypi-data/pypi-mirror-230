import os
import re
import tempfile

from egse.storage import _construct_filename
from egse.obsid import ObservationIdentifier
from egse.system import format_datetime


def test_construct_filename():

    today = format_datetime("today")
    with tempfile.TemporaryDirectory() as temp_dir:

        os.environ["PLATO_DATA_STORAGE_LOCATION"] = temp_dir

        assert re.match(
            f'{temp_dir}/obs/00023_KUL/00023_KUL_SPW_HK_{today}' + r'_\d{6}.txt',
            str(_construct_filename("SPW_HK", "txt", ObservationIdentifier("KUL", 42, 23))),
        )

        assert re.match(
            f'{temp_dir}/obs/00023_KUL_achel/00023_KUL_SPW_HK_{today}' + r'_\d{6}.txt',
            str(_construct_filename("SPW_HK", "txt", ObservationIdentifier("KUL", 42, 23), camera_name="achel")),
        )

        site_id = "INTA"
        assert re.match(
            f"{temp_dir}/daily/{today}/{today}_{site_id}_SPW_HK.txt",
            str(_construct_filename("SPW_HK", "txt", site_id=site_id)),
        )

        assert re.match(
            f"{temp_dir}/daily/{today}/{today}_{site_id}_SPW_HK_00001.txt",
            str(_construct_filename("SPW_HK", "txt", site_id=site_id, use_counter=True)),
        )
