#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 16:54:25 2020

@author: pierre
"""

import os


import numpy as np

#import pandas

# egse
#from egse.coordinates.referenceFrame import ReferenceFrame
from egse.coordinates.cslmodel import CSLReferenceFrameModel
from egse.state import GlobalState, Setup
from scripts.laser_tracker_to_dict import laser_tracker_to_dict

# Hexapod
#from egse.hexapod.symetrie.puna import PunaController
from egse.hexapod.symetrie.puna import PunaSimulator
#from egse.hexapod.symetrie.puna import HexapodError

#from egse.coordinates.point import Points

from egse.coordinates import ref_model_to_dict, dict_to_ref_model

from camtest import list_setups, load_setup

from camtest.core import submit_setup

# submit_setup

from scripts.avoidance import is_avoidance_ok


def printm(matrix,rounding=2):
    import numpy as np
    print(np.round(matrix,rounding))
    
"""
def check_positions(out, expected, rel=0.0001, abs=0.0001):
    assert len(out) == len(expected)
    for idx, element in enumerate(out):
        assert element == approx(expected[idx], rel=rel, abs=abs)
"""

def positions_match(hexapod,hexsim,atol=0.0001,rtol=0.0001):
    return np.allclose(hexapod.get_user_positions(), hexsim.get_user_positions(), atol=atol, rtol=rtol)

confdir = os.getenv("PLATO_CONF_DATA_LOCATION")


################################################################################

list_setups()

setupnr = 9

setup = load_setup(setupnr)


#===================== Ingest model from xls file =============================



filexls = "/Users/pierre/plato/csl_refFrames.xls"


refFrames = laser_tracker_to_dict(filexls)

print(refFrames)

dict_model = dict_to_ref_model(refFrames)

csl_model = CSLReferenceFrameModel(refFrames)

transformation = csl_model.get_frame("hexusr").getActiveTransformationTo(csl_model.get_frame("hexobj"))
csl_model.add_frame(name="hexobusr", transformation=transformation, ref="hexusr")

# create hex_iso ?

## Add the links
csl_model.add_link("hexplt","hexobj")
csl_model.add_link("hexobj","hexobusr")
csl_model.add_link("hexmec","hexusr")

# fpa links ?


#=============================== POSITION 2 ===================================

# Run csl_model up to the definition of HEX_OBUSR  (egse/scripts)

## Instantiate a hexapod simulator

#hexsim = PunaSimulator(hex_mec=hexmec0, hex_plt=hexplt0, hex_obj=hexobj0, hex_usr=hexusr0, hex_obusr=hexobusr0)





# 1. Save setup before going to retracted position == save FPA_SEN position
"""
csl_list = [master0, gliso0, glrot0, glfix0, hexmec0,hexplt0, fpaaln0, fpasen0, \
            hexobj0,fpamec0,toumec0,toualn0,marialn0,touopt0,cammec0,toul60, \
            hexusr0,hexobusr0]

csl_dict = ref_model_to_dict(csl_list)
    
#setup.csl_model =  csl_dict


csl_model = CSLReferenceFrameModel(csl_dict)
"""


csl_dict =  csl_model.serialize()

setup.csl_model =  csl_dict



#newsetupfile = confdir+f"setup_{setupnr}_cslmodel.yaml"

#setup.to_yaml_file(newsetupfile)

setup = submit_setup(setup, "STM - FPA in place")


# 2. Goto retracted position

# 2a. simulation

hexsim.goto_retracted_position()

# 2b. hardware

execute(hexapod_puna_goto_retracted_position,wait=True)

# 2c. Check that model still coincides with new HW position
#     MAKE SURE HEX IS NOT A SIMULATOR...

print(f"Hexapod & Model match: {positions_match(hex,hexsim)}")

# 3. Save setup in retracted position

# 3a. Save full model, for the record
    
csl_dict = ref_model_to_dict(csl_model)
    
setup.csl_model =  csl_dict


# 3b. Save partial model, to be restored after the egse_sleep --> exclude glfix and glrot
csl_model_to_restore = [master0, gliso0, hexmec0,hexplt0, fpaaln0, fpasen0, \
            hexobj0,fpamec0,toumec0,toualn0,marialn0,touopt0,cammec0,toul60, \
            hexusr0,hexobusr0]

csl_dict = ref_model_to_dict(csl_model_to_restore)
    
setup.csl_model_to_restore =  csl_dict

setup = submit_setup(setup, "STM - Retracted")



#=============== EGSE SLEEP --> POSITION 1 -->  WAKEUP ========================

#=============================== POSITION 1 ===================================

list_setups()

# 1. Restore the retracted setup

setup = load_setup(TODO)  #   "STM - Retracted"

#setreup = Setup.from_yaml_file(newsetupfile)

# 2. Extract the csl_model from the setup  --  select the retracted setup, without 

csl_dict = setup.csl_model_to_restore

csl_model = dict_to_ref_model(csl_dict)

# 3. Instantiate hexapod model

hexsim = PunaSimulator(hex_mec=csl_model["hexmec0"],hex_plt=csl_model["hexplt0"],hex_obj=csl_model["hexobj0"],hex_usr=csl_model["hexusr0"],hex_obusr=csl_model["hexobusr0"])


# 4. Read model with FPA_SEN in position

newsetupfile = confdir + "TODO.yaml"

# TODO : REPLACE NEXT LINE BY get_setup(setup_id)
setup_high = Setup.from_yaml_file(newsetupfile) #    "STM - FPA in place"


# 5. Extract model with FPA high

csl_dict_high = setup_high.csl_model

csl_model_high = dict_to_ref_model(csl_dict_high)


# 6.  Extract FPA_SEN position to be restored

vtrans, vrot = csl_model_high["fpasen0"].getActiveTranslationRotationVectorsFrom(csl_model_high["hexmec0"])


# 7. Command the hexapod to that same location

hexsim.move_absolute(*vtrans,*vrot)

avoidance_respected = is_avoidance_ok(csl_model["hexusr0"], csl_model["hexobj0"], setup=None, verbose=True)

print(f"Avoidance OK after movement : {avoidance_respected}")
    
if avoidance_respected:

    execute(hexapod_puna_move_absolute_user,*vtrans,*vrot,wait=True)

else:
    
    print("Call your local EGSE manager")


