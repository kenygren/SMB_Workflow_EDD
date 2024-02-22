# --------- import dependecies ----------
import sys
sys.path.append('../')  # Add the parent directory to the Python path

import numpy as np
import InputWriterUtil as iwrite

# ---------- name input textfile -----------

base_dir = ''
filename_suffix = 'OutputForSpec_test_s1-1.txt'
f = base_dir+filename_suffix

# ---------- generate reference points ----------

##########################################
##### This section is user-defined #######
##### See reference examples #############
##########################################

ome = 0.210003
Xcp = -4.69168
Ycp = 12.09873
rsampZ = -270.684
omecorr = 0

dx = 28
dz = 20
dy = 3

ddx = 5
ddz = 5

DataNo, Config = 0, 1

##### Beam size #####
OffsetX = 0
OffsetZ = 0

##### Size of the plate #####
r1 = 1/2 * 24
r2 = 1/2 * 24  #  (1.2 * 0.5)

### If you find the edge of the plate, convert
### Center of the Sample
sampXcp = Xcp - 0
sampYcp = Ycp - r2
rsampZ  = rsampZ  +r1

#BoundZ = [-r1 + OffsetZ, r1-OffsetZ]
BoundX = [-0.35, 0.21]

#BoundX = [-r2+OffsetX, r2 - OffsetX]
BoundY = [-5, 5]

# Determine the data pts on the edge:
x = np.linspace(BoundX[0], BoundX[1], dx)
y = np.linspace(BoundY[0], BoundY[1], dy)
print( x )
print( 'AverageZ', np.mean(y) )
xx, yy = np.meshgrid(x, y)

##### For plotting #####

Xb = [ -r2, r2, r2, -r2, -r2 ]
Yb = [ r1, r1, -r1, -r1, r1 ]

ah = np.linspace(0, 360, 360)
XpH = r1 * np.cos( np.deg2rad( ah ) )
YpH = r1 * np.sin( np.deg2rad( ah ) )

X = xx.flatten('F')
Z = X.copy() * 0
Y = yy.flatten('F')

W = X.copy()*0
Wcorr = X.copy()*0

XYZ1 = np.vstack( (X.flatten('F'), Y.flatten('F'), 1 * Z.flatten('F')) )

XYZWs  = np.vstack( (XYZ1[0] + sampXcp, XYZ1[1] + sampYcp, 1 * XYZ1[2] + rsampZ , W + ome, Wcorr + omecorr)).T
XYZWs_2 = XYZWs[23:28]

########################################

lab_ref_points_1 = XYZWs
lab_ref_points_2 = XYZWs_2

# ---------- EDD input configuration dictionary (one per dataset) -----------

config_dataset_1 = {
    'dataset_ID': 1,
    'configuration_no': 1,

    'horz_slit': 0.05,
    'vert_slit': 0.05,
    'detector_slits': 0.05,

    'scantype': 1,

    'axis1': 'z',
    'start1': -5,
    'end1': 5,
    'numframes1': 18,

    'offbias': 'fix_end',

    'dwelltime': 15
}

config_dataset_2 = {
    'dataset_ID': 6,
    'configuration_no': 3,

    'horz_slit': 0.08,
    'vert_slit': 0.08,
    'detector_slits': 0.08,

    'scantype': 4,

    'axis1': 'z',
    'start1': -1,
    'end1': 1,
    'numframes1': 5,

    'offbias': 'center',

    'dwelltime': 12
}

# ---------- write text array  -----------

datasets_for_inputfile = [config_dataset_1, config_dataset_2] #write in priority order
lab_ref_points = [lab_ref_points_1, lab_ref_points_2] #match with above priority order

iwrite.combine_and_write_datasets(datasets_for_inputfile, lab_ref_points, f)

