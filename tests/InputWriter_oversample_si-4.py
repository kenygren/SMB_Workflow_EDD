# --------- import dependecies ----------
import sys
sys.path.append('../')  # Add the parent directory to the Python path

import numpy as np
import InputWriterUtil as iwrite

# ---------- name input textfile -----------

base_dir = ''
filename_suffix = 'OutputForSpec_dscan_oversamp_s4-1.txt'
f = base_dir+filename_suffix

# ---------- generate reference points ----------

##########################################
##### This section is user-defined #######
##### See reference examples #############
##########################################

ome = 0.387
Xcp = -38.2487
Ycp = -2.52131
rsampZ = -258.103
omecorr = 0

dx = 2
dz = 2
dy = 200

BoundX = [ -2.5, 2.5]
BoundZ = [-2.5, 2.5]
BoundY = [-2, 2]

# Determine the data pts on the edge:
x = np.linspace(BoundX[0], BoundX[1], dx)
z = np.linspace(BoundZ[0], BoundZ[1], dz)

zz, xx = np.meshgrid(z, x)



X = xx.flatten('F')
Y = X.copy() * 0
Z = zz.flatten('F')

W = X.copy()*0
Wcorr = X.copy()*0

XYZ1 = np.vstack( (X.flatten('F'), Y.flatten('F'), 1 * Z.flatten('F')) )

XYZWs  = np.vstack( (XYZ1[0] + Xcp, XYZ1[1] + Ycp, 1 * XYZ1[2] + rsampZ , W + ome, Wcorr + omecorr)).T

########################################

lab_ref_points_1 = XYZWs

# ---------- EDD input configuration dictionary (one per dataset) -----------

config_dataset_1 = {
    'dataset_ID': 2,
    'configuration_no': 2,

    'horz_slit': 0.05,
    'vert_slit': 0.05,
    'detector_slits': 0.05,

    'scantype': 6,

    'axis1': 'y',
    'start1': -2,
    'end1': 2,
    'numframes1': 200,

    #'offbias': 'center',

    'dwelltime': 30
}


# ---------- write text array  -----------

datasets_for_inputfile = [config_dataset_1] #write in priority order
lab_ref_points = [lab_ref_points_1] #match with above priority order

iwrite.combine_and_write_datasets(datasets_for_inputfile, lab_ref_points, f)

