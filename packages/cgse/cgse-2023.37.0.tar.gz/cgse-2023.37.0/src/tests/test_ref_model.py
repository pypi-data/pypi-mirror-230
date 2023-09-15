import logging

import numpy as np

from egse.coordinates import ReferenceFrame
from egse.coordinates import dict_to_ref_model
from egse.coordinates import ref_model_to_dict

LOGGER = logging.getLogger()


def test_proper_ref_model():
    rot_config = "sxyz"
    master = ReferenceFrame.createMaster()

    a_ref = ReferenceFrame(transformation=np.identity(4), ref=master, name="a_ref",
                           rot_config=rot_config)
    a_ref.addLink(master)

    b_ref = ReferenceFrame(transformation=np.identity(4), ref=a_ref, name="b_ref",
                           rot_config=rot_config)

    c_ref = ReferenceFrame.fromTranslationRotation(
        [-2, -2, -2], [-3, -4, -5], rot_config=rot_config, ref=b_ref, name="c_ref"
    )
    c_ref.addLink(b_ref)
    c_ref.addLink(a_ref)

    d_ref = ReferenceFrame(transformation=np.identity(4), ref=c_ref, name="d_ref",
                           rot_config=rot_config)

    model_list = [a_ref, b_ref, c_ref, d_ref, master]

    csl_model = ref_model_to_dict(model_list)
    LOGGER.info(csl_model.pretty_str())

    LOGGER.info(csl_model["a_ref"])
    LOGGER.info(csl_model.a_ref)

    ref_model = dict_to_ref_model(csl_model)

    LOGGER.info(ref_model.pretty_str())

    LOGGER.info(ref_model["a_ref"])
    LOGGER.info(ref_model.a_ref)

    LOGGER.info(ref_model.a_ref.find_master())

    # the model has no master

    no_master_list = [a_ref, b_ref, c_ref, d_ref]

    # check if there is any reference frame for which the master is not in the model

    x = [ref.find_master() in no_master_list for ref in no_master_list]
    LOGGER.warning(x)

    # find any reference frame that refers to another reference frame not inside the model

    x = [ref for ref in no_master_list if ref.ref not in no_master_list]
    LOGGER.warning(x)

    # the model is missing a reference frame

    missing_ref_model = [master, b_ref, d_ref]

    x = [ref for ref in missing_ref_model if ref.ref not in missing_ref_model]
    LOGGER.warning(x)
