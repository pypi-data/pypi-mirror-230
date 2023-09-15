import logging

from rich import print

from egse.synoptics import SynopticsManagerProxy


def test_store_common_synoptics():

    hk_name = "NFEE_T_CCD1"

    logging.warning("Make sure the Synoptics Manager is running...")

    with SynopticsManagerProxy() as syn_proxy:
        syn_proxy.store_common_synoptics(
            {
                "timestamp": "2021-11-30 14:01",
                hk_name: 42.24,
            }
        )

    logging.warning(
        "Check in de browser if there is a value for the synoptic "
        "parameter 'GSYN_CCD1' [localhost:6207]"
    )
