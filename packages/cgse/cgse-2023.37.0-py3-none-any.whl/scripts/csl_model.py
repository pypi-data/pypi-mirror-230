#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 17:09:04 2019

@author: pierre
"""

"""
MGSE MODEL wrt Coordinate Systems

Two models are necessary, representing the same MGSE, but on diff. bases
* model M (for Mec)
          - based on GL_FIX as a master
          - filled progressively during the mechanical alignment of the MGSE
          - never used to represent any actual movement
          - only used to gather information, and then it is transfered to model A

* model A (for Alignment, or Active)
          - based on HEX_MEC as a master
          - filled in one go from a model M once it's complete
          - used for the entire optical alignment

"""


import sys
#sys.path.append("/Users/pierre/plato/plato-common-egse/src")
sys.path


import numpy as np

# egse
from egse.coordinates.referenceFrame import ReferenceFrame
from egse.state import GlobalState

# Hexapod
from egse.hexapod.symetrie.puna import PunaController
from egse.hexapod.symetrie.puna import PunaSimulator
from egse.hexapod.symetrie.puna import HexapodError

from egse.coordinates.point import Points

def printm(matrix,rounding=2):
    import numpy as np
    print(np.round(matrix,rounding))


################################################################################

# PREDEFINED CONSTANTS    
# Rotation - identity
rdef = np.identity(3)
# Translation - null
tdef = np.array([0,0,0])
# Zoom - unit
zdef = np.array([1,1,1])
# Shear
sdef = np.array([0,0,0])

pi4 = np.pi/4.
I   = np.identity(4)

# Rotation around static axis, and around x, y and z in that order
rot_config = "sxyz"

try:
   hex = PunaController()
   hex.connect()
except HexapodError:
   hex = PunaSimulator()
   

print(f"Hexapod is a simulator: {hex.is_simulator()}")


degrees=True

################################################################################
# MODEL M : mechanical alignment of the MGSE
################################################################################

## TODO : READ translations and rotations FROM CALIBRATION FILE
testtr  = np.array([-2,-2,-2])
testrot = np.array([-3,-4,-5])


"""
## WORKING WITH GL_FIX = master until the end of the alignment.

# Master
master0 = ReferenceFrame.createMaster()

# GL_FIX = Identity
glfix0 = ReferenceFrame(transformation=np.identity(4), ref=master0,name="glfix0", rot_config=rot_config)
glfix0.addLink(master0)#,transformation=np.identity(4))

#print(glfix in masterM.linkedTo)

# GL_ROT --> GL_FIX  --  no link
glrot0 = ReferenceFrame(transformation=np.identity(4), ref=glfix0,name="glrot0", rot_config=rot_config)

# GL_ISO --> GL_ROT
tr_gliso  = testtr
rot_gliso = testrot
gliso0 = ReferenceFrame.fromTranslationRotation(tr_gliso,rot_gliso,rot_config=rot_config, ref=glrot0,name="gliso0",degrees=degrees)
gliso0.addLink(glrot0)#,transformation=gliso.transformation)
"""



# Master
master0fix = ReferenceFrame.createMaster()

##################
# REFERENCE FRAMES   ##  A. MGSE ALIGNMENT : GL_FIX as a master
##################

# GL_FIX = Identity
glfix0fix = ReferenceFrame(transformation=np.identity(4), ref=master0fix, name="glfix0fix", rot_config=rot_config)
glfix0fix.addLink(master0fix)

#print(glfix in masterM.linkedTo)

# GL_ROT --> GL_FIX  --  no link
glrot0fix = ReferenceFrame(transformation=np.identity(4), ref=glfix0fix, name="glrot0fix", rot_config=rot_config)

# GL_ISO --> GL_ROT
tr_gliso  = testtr
rot_gliso = testrot
gliso0fix = ReferenceFrame.fromTranslationRotation(tr_gliso,rot_gliso,rot_config=rot_config, ref=glrot0fix, name="gliso0fix",degrees=degrees)
gliso0fix.addLink(glrot0fix)


##################
# CHANGE OF REFERENCE --> GL_ISO BECOMES THE MASTER
##################

# Master
master0 = ReferenceFrame.createMaster()

gliso0 = ReferenceFrame(transformation=np.identity(4), ref=master0, name="gliso0", rot_config=rot_config)
gliso0.addLink(master0)


# GL_ROT --> GL_ISO
transformation = glrot0fix.getActiveTransformationFrom(gliso0fix)
glrot0 = ReferenceFrame(transformation=transformation,ref=gliso0, name="glrot0", rot_config=rot_config)
glrot0.addLink(gliso0)


# GL_FIX
transformation = glfix0fix.getActiveTransformationFrom(glrot0fix)
glfix0 = ReferenceFrame(transformation=transformation,ref=glrot0, name="glfix0", rot_config=rot_config)


##################
# PROCEED DEFINING THE MODEL. GL_ISO IS NOW THE MASTER
##################

# HEX_IS0 --> GL_ISO
tr_hexiso  = testtr
rot_hexiso = testrot
hexiso0 = ReferenceFrame.fromTranslationRotation(tr_hexiso,rot_hexiso,rot_config=rot_config, ref=gliso0,name="hexiso0",degrees=degrees)
hexiso0.addLink(gliso0)

# HEX_MEC --> HEX_ISO
hexmec0 = ReferenceFrame(transformation=np.identity(4), ref=hexiso0, name="hexmec0", rot_config=rot_config)
hexmec0.addLink(hexiso0)


# HEX_PLT --> HEX_MEC -- no link
tr_hexplt  = testtr
rot_hexplt = testrot
hexplt0 = ReferenceFrame(transformation=np.identity(4), ref=hexmec0, name="hexplt0", rot_config=rot_config)

# FPA_ALN --> GL_ISO -- no link
tr_fpaaln  = testtr
rot_fpaaln = testrot
fpaaln0 = ReferenceFrame.fromTranslationRotation(tr_fpaaln,rot_fpaaln,rot_config=rot_config, ref=gliso0, name="fpaaln0",degrees=degrees)

# FPA_SEN --> FPA_ALN
tr_fpasen  = testtr
rot_fpasen = testrot
fpasen0 = ReferenceFrame.fromTranslationRotation(tr_fpasen,rot_fpasen,rot_config=rot_config, ref=fpaaln0, name="fpasen0",degrees=degrees)
fpasen0.addLink(fpaaln0)

# HEX_OBJ --> FPA_SEN
transformation = fpasen0.getActiveTransformationFrom(hexplt0)
hexobj0 = ReferenceFrame(transformation=transformation,ref=hexplt0, name="hexobj0", rot_config=rot_config)
hexobj0.addLink(fpasen0)

# FPA_MEC --> FPA_ALN
tr_fpamec  = testtr
rot_fpamec = testrot
fpamec0 = ReferenceFrame.fromTranslationRotation(tr_fpamec,rot_fpamec,rot_config=rot_config, ref=fpaaln0, name="fpamec0",degrees=degrees)
fpamec0.addLink(fpaaln0)

# THE FOLLOWING ARE FOR CSL PURPOSE : TOU_ALN, TOU_OPT, CAM_MEC, MARI_ALN, CAM_BOR
# MARI_ALN wrt TOU_ALN and CAM_BOR wrt TOU_ALN are deliverables from CSL to the TH and the CM resp.
# The order in which we get the absolute location of these systems is TBD, cos it may differ
# from the order in which they are derived, because some may only positioned in orientation 
# to start with. TBD.

# Originally TOU_ALN only measured in orientation, no abs. location wrt GL_ISO
# Changed later on : will be provided wrt TOU_MEC 
# in order to be able to locate CAM_BOR (deliverable) and express MARI_ALN (deliverable)

# TOU_MEC --> GL_ISO
tr_toumec  = testtr
rot_toumec = testrot
toumec0 = ReferenceFrame.fromTranslationRotation(tr_toumec,rot_toumec,rot_config=rot_config, ref=gliso0, name="toumec0",degrees=degrees)
toumec0.addLink(gliso0)


# TOU_ALN --> TOU_MEC  --> here or in B.
tr_toualn  = testtr
rot_toualn = testrot
toualn0 = ReferenceFrame.fromTranslationRotation(tr_toualn,rot_toualn,rot_config=rot_config, ref=toumec0, name="toualn0",degrees=degrees)
toualn0.addLink(toumec0)

# MARI_ALN --> TOU_ALN --> here or in B.
tr_marialn  = testtr
rot_marialn = testrot
marialn0 = ReferenceFrame.fromTranslationRotation(tr_marialn,rot_marialn,rot_config=rot_config, ref=toualn0, name="marialn0",degrees=degrees)
marialn0.addLink(toualn0)

# TOU_OPT --> TOU_ALN -- optional
tr_touopt  = testtr
rot_touopt = testrot
touopt0 = ReferenceFrame.fromTranslationRotation(tr_touopt,rot_touopt,rot_config=rot_config, ref=toualn0, name="touopt0",degrees=degrees)
touopt0.addLink(toualn0)

# CAM_MEC --> TOU_ALN -- optional
tr_cammec  = testtr
rot_cammec = testrot
cammec0 = ReferenceFrame.fromTranslationRotation(tr_cammec,rot_cammec,rot_config=rot_config, ref=toualn0, name="cammec0",degrees=degrees)
cammec0.addLink(toualn0)


# Note we establish the full model and then transfer it to another master (hexmec)
# In reality a number of frames could be established directly in the final master:
# fpasen, fpamec, toul6, hexusr
# In practice they will certainly be communicated at this stage -> more logical this way

# TOU_L6 --> TOU_MEC
tr_toul6  = testtr
rot_toul6 = testrot
toul60 = ReferenceFrame.fromTranslationRotation(tr_toul6,rot_toul6,rot_config=rot_config, ref=toumec0, name="toul60",degrees=degrees)
toul60.addLink(toumec0)

# HEX_USR
# USR, defined in MEC --> first define a virtual frame in TOU_L6, then redefine it in HEX_MEC
tr_hexusr  = [0,0,-1.65]
rot_hexusr = [0,0,0]
hexusrtou = ReferenceFrame.fromTranslationRotation(tr_hexusr,rot_hexusr,rot_config=rot_config, ref=toul60, name="hexusrtou",degrees=degrees)
transformation = hexusrtou.getActiveTransformationFrom(hexmec0)
hexusr0 = ReferenceFrame(transformation=transformation,ref=hexmec0, name="hexusr0", rot_config=rot_config)
hexusr0.addLink(hexmec0)

del hexusrtou

# HEX_OBUSR
transformation = hexusr0.getActiveTransformationTo(hexobj0)
hexobusr0 = ReferenceFrame(transformation=transformation,rot_config=rot_config, ref=hexusr0, name="hexobusr0")
hexobusr0.addLink(hexobj0)

"""
# At this stage, hexapod movements could intervene to recenter the FPA wrt TOU

# This should be delayed as long as hexusr (L6S2) and hexobj (FPA_SEN) 
# haven't been properly defined, the avoidance volume can't be checked

# From this point on it's doable though (use is_avoidance_ok)

"""

##################
# REFERENCE FRAMES   ##  B. ALIGNMENT : TRANSFER MASTER to HEX_MEC & MODEL SIMPLIFICATION
##################

master = ReferenceFrame.createMaster()

# HEX_MEC
hexmec = ReferenceFrame(transformation=np.identity(4), ref=master, name="hexmec", rot_config=rot_config)
hexmec.addLink(master)

# HEX_PLT
transformation = hexplt0.getActiveTransformationFrom(hexmec0)
hexplt = ReferenceFrame(transformation=transformation,ref=hexmec, name="hexplt", rot_config=rot_config)

# HEX_OBJ
transformation = hexobj0.getActiveTransformationFrom(hexplt0)
hexobj = ReferenceFrame(transformation=transformation,ref=hexplt, name="hexobj", rot_config=rot_config)
hexobj.addLink(hexplt)

# FPA_MEC
transformation = fpamec0.getActiveTransformationFrom(hexobj0)
fpamec = ReferenceFrame(transformation=transformation,ref=hexobj, name="fpamec", rot_config=rot_config)
fpamec.addLink(hexobj)

# TOU_MEC
transformation = toumec0.getActiveTransformationFrom(hexmec0)
toumec = ReferenceFrame(transformation=transformation,ref=hexmec, name="toumec", rot_config=rot_config)
toumec.addLink(hexmec)

# HEX_USR
transformation = hexusr0.getActiveTransformationFrom(hexmec0)
hexusr = ReferenceFrame(transformation=transformation,ref=hexmec, name="hexusr", rot_config=rot_config)
hexusr.addLink(hexmec)

# CHANGE HEX_USR DEFINITION IN THE HEXAPOD CONTROLLER

# HEX_OBUSR
transformation = hexobj0.getActiveTransformationFrom(hexusr0)
hexobusr = ReferenceFrame(transformation=transformation,ref=hexusr, name="hexobusr", rot_config=rot_config)
hexobusr.addLink(hexobj)

# Deliverables : MARI_ALN & CAM_BOR --> unnecessary for the alignment
# but easier to represent them and get them for free in the end
# TOU_ALN  --> TOU_MEC
transformation = toualn0.getActiveTransformationFrom(toumec0)
toualn = ReferenceFrame(transformation=transformation,ref=toumec, name="toualn", rot_config=rot_config)
toualn.addLink(toumec)

# MARI_ALN --> TOU_ALN
transformation = marialn0.getActiveTransformationFrom(toualn0)
marialn = ReferenceFrame(transformation=transformation,ref=toualn, name="marialn", rot_config=rot_config)
marialn.addLink(toualn)

######
# CAM_BOR is only established after the alignment. This is a "placeholder"
# CAM_BOR is // TOU_OPT with its origin == that of FPA_SEN
# 0. get TOU_OPT (fixed wrt TOU_ALN)
# 1. Define CAM_BOR == TOU_OPT with CAM_BOR.ref = TOU_ALN
# 2. Determine the translation vector from TOU_OPT.origin to FPA_SEN.origin (HEX_OBJ.origin)
# 3. Apply that translation to CAM_BOR. It is now properly defined
# 4. Deliverables : its translation-rotation vectors wrt TOU_ALN

#0. 
# TOU_OPT  --> TOU_ALN
transformation = touopt0.getActiveTransformationFrom(toualn0)
touopt = ReferenceFrame(transformation=transformation,ref=toualn, name="touopt", rot_config=rot_config)
touopt.addLink(toualn)

# 1.
transformation = touopt.getActiveTransformationFrom(toualn)
cambor = ReferenceFrame(transformation=transformation,ref=toualn, name="cambor", rot_config=rot_config)

# 2. & 3.
translation = hexobj.getOrigin().expressIn(touopt)[:3]
rotation = [0.,0.,0.]
cambor.applyTranslationRotation(translation,rotation,rot_config=rot_config,degrees=degrees)

# 4.
translation,rotation = cambor.getActiveTranslationRotationVectorsFrom(toualn)



csl_model = [master,hexmec,hexplt,hexobj,hexusr,hexobusr,fpamec,toumec,toualn,touopt,marialn,cambor]




##################
# AVOIDANCE VOLUME
##################

"""
# NECESSARY FIELDS IN THE SETUP

setup.camera.fpa.avoidance.clearance_xy    # Horizontal clearance around L6
setup.camera.fpa.avoidance.clearance_z     # Vertical uncertainty on teh CCD location
setup.camera_fpa.avoidance.vertices_nb     # nb of points to represent the avoidance volume above the FPA
setup.camera_fpa.avoidance.vertices_radius # radius of the circle to represend the avoidance volume above the FPA

"""



setup = GlobalState.setup

"""
A. HORIZONTAL AVOIDANCE
  Ensure that the center of L6, materialised by HEX_USR (incl. z-direction security wrt TOU_L6)
  stays within a given radius of the origin of FPA_SEN
"""

# Clearance = the tolerance in every horizontal direction (3 mm; PLATO-KUL-PL-ICD-0001 v1.2)
clearance_xy = setup.camera.fpa.avoidance.clearance_xy

# l6xy = the projection of the origin of HEX_USR on the X-Y plane of FPA_SEN
l6xy = hexusr.getOrigin().expressIn(hexobj)[:2]


# !! This is a verification of the current situation --> need to replace by a simulation of the forthcoming movement in the building block
assert((l6xy[0]**2.+l6xy[1]**2.)< clearance_xy*clearance_xy)


"""
B. VERTICAL AVOIDANCE
   Ensure that the CCD never hits L6.
   The definition of HEX_USR includes a tolerance below L6 (1.65 mm)
   We include a tolerance above FPA_SEN here (0.3 mm)
   We define a collection of points to act at the vertices of the avoidance volume above the FPA
"""

# Clearance = vertical uncertainty on the CCD location (0.3 mm; PLATO-KUL-PL-ICD-0001 v1.2)
clearance_z = setup.camera.fpa.avoidance.clearance_z

# Vertices = Points representing the vertices of the avoidance volume above the FPA (60)
vertices_nb     = setup.camera.fpa.avoidance.vertices_nb
# All vertices are on a circle of radius 'vertices_radius' (100 mm)
vertices_radius = setup.camera.fpa.avoidance.vertices_radius

angles = np.linspace(0,np.pi * 2,vertices_nb,endpoint=False)
vertices_x = np.cos(angles) * vertices_radius
vertices_y = np.sin(angles) * vertices_radius
vertices_z = np.ones_like(angles) * clearance_z

# The collection of Points defining the avoidance volume around FPA_SEN
vert_obj = Points(coordinates=np.array([vertices_x,vertices_y,vertices_z]),ref=hexobj,name="vertices")

# Their coordinates in HEX_USR
# NB: vert_obj is a Points, vert_usr is an array
vert_usr = vert_obj.expressIn(hexusr)


# !! Same as above : this is verifying the current situation, not the one after a planned movement
# Verify that all vertices ("protecting" FPA_SEN) are below the x-y plane of HEX_USR ("protecting" L6)
assert(np.all(vert_usr[2,:] < 0.))




