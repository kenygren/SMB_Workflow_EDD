
import numpy as np
import InputWriterUtil as iwrite

####################################################################################################################################
##### DETERMINE REFERENCE POINTS FOR EACH SCAN #####
# """
# in flyscan of flymesh, numer of points of the "slow" axis (fly_axis0_npts) has to be greater than 1
# """

#sample 1 of the si-samples

base_dir = ''
filename_suffix = 'OutputForSpec_0216_s1-3.txt'
f = base_dir+filename_suffix

ome = 0.210
labx_ref = -4.69168
laby_ref = 12.099
labz_ref = -270.684
omeoff = 0 

ome = 0.210003
Xcp = -4.69168
Ycp = 12.09873
rsampZ = -270.684

dx = 28
dz = 20
dy = 3

ddx = 5
ddz = 5

DataNo, Config = 0, 1

# %% ######################################################################
####################### AM Ni Resonance Samples ###########################
######################### Sample E81 (t=4mm)  #############################

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

# %% ######################################################################
####################### AM Ni Resonance Samples ###########################
######################### Sample E81 (t=4mm)  #############################

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

XYZ1 = np.vstack( (X.flatten('F'), Y.flatten('F'), 1 * Z.flatten('F')) )
XYZAll  = np.vstack( (XYZ1[0] + sampXcp, XYZ1[1] + sampYcp, 1 * XYZ1[2] + rsampZ ) ).T

lab_ref_points_1 = XYZAll

####################################################################################################################################
##### PROVIDE CONFIGURATIONS FOR EACH SCAN #####

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

datasets_for_inputfile = [config_dataset_1] #write in priority order
lab_ref_points = [lab_ref_points_1] #match with above priority order

iwrite.combine_and_write_datasets(datasets_for_inputfile, lab_ref_points, f, ome, omeoff)