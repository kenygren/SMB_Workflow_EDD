#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

# from hexrd_extras import core_fem as fem
#import PowderFittingTools as pwd

motor_speed = 3937.01 #hardcoded motor speed for rsampX, rsampY, rsampZ

###################
#primary function: 
###################

def combine_and_write_datasets(datasets_for_inputfile, lab_ref_points, f, ome, omeoff): 
    optimized_scan_params_summary, optimized_dwelltime_summary = update_scan_params(datasets_for_inputfile)
    datasets_for_writer = tuple_dataset_values(datasets_for_inputfile,lab_ref_points, optimized_dwelltime_summary, optimized_scan_params_summary, f, ome = ome, omeoff = omeoff)
    write_OuputForSpec2024_with_append(datasets_for_writer)

    return

###################
#remap motor to integer index
###################

def get_axis_number(axis):
    axis_mapping = {'x': 1, 'y': 2, 'z': 3, 'w': 4}
    return axis_mapping.get(axis, None)

###################
#optimize scan parameter functions 
###################

def calculate_updated_distance_from_num_points(desired_numpts, desired_distance, motor_speed):
    intervals = desired_numpts-1
    # Calculate starting effective stepsize
    stepsize = desired_distance / intervals
    #calculate total steps required 
    total_steps_required = stepsize * motor_speed
    # Round the total steps to the nearest integer
    nearest_integer_steps = np.round(total_steps_required)
    #newstepsize
    newstepsize = nearest_integer_steps / motor_speed 
    # Calculate the updated distance based on the rounded steps
    updated_distance = intervals * newstepsize
    return updated_distance

def update_dwelltime(updated_start, updated_stop, numpts, desired_dwelltime, motor_speed):
    updated_distance = calc_distance(updated_start,updated_stop)
    #calculate speed for desired dwell time with previously optimized distance and number of points
    speed = ((updated_distance * motor_speed) / (desired_dwelltime * numpts))
    #find closest even integer for speed
    even_int_speed = round_to_nearest_even(speed)
    #update dwelltime to compenstate for changes in integer speed
    updated_dwelltime = ((updated_distance * motor_speed) / (even_int_speed * numpts))
    safe_dwelltime = np.floor(updated_dwelltime * 1000) / 1000
    return safe_dwelltime

def round_to_nearest_even(number):
    # Round the number to the nearest integer
    rounded_number = np.round(number)
    # Check if the rounded number is odd
    if rounded_number % 2 != 0:
        # If odd, adjust to the nearest even integer
        if number > rounded_number:
            rounded_number += 1
        else:
            rounded_number -= 1
    return rounded_number

def update_start_end(start, end, offset, whereoffset = 'center'): 
    if whereoffset == 'center':
        center = abs(start)+abs(end)
        updatedstart = start - (offset/2)
        updatedend = end + (offset/2)
    elif whereoffset == 'fix_end':
        updatedstart = start - offset
        updatedend = end
    elif whereoffset == 'fix_start':
        updatedend = end + offset
        updatedstart = start
    return updatedstart, updatedend

def calc_distance(start,stop):
    distance = abs(start) + abs(stop)
    return distance


###################
#scantype parameter writers 
###################

def ScanType_0():
    empty = 0
    return empty

def ScanType_1(axis, start, stop, numframes, offsetbias = 'center'):
    axisint = get_axis_number(axis)
    distance = calc_distance(start,stop)
    updateddistance = calculate_updated_distance_from_num_points(numframes, distance, motor_speed)
    updatedstart, updatedstop = update_start_end(start, stop, updateddistance - distance, whereoffset=offsetbias)
    scanlist = (1, axisint, updatedstart, updatedstop, numframes)
    return scanlist

def ScanType_2(axis1, start1, stop1, numframes1, axis2, start2, stop2, numframes2, offsetbias = 'center'):
    axisint1 = get_axis_number(axis1)
    axisint2 = get_axis_number(axis2)
    distance1 = calc_distance(start1,stop1)
    distance2 = calc_distance(start2,stop2)
    updateddistance1 = calculate_updated_distance_from_num_points(numframes1, distance1, motor_speed)
    updatedstart1, updatedstop1 = update_start_end(start1, stop1, updateddistance1 - distance1, whereoffset=offsetbias)
    updateddistance2 = calculate_updated_distance_from_num_points(numframes2, distance2, motor_speed)
    updatedstart2, updatedstop2 = update_start_end(start2, stop2, updateddistance2 - distance2, whereoffset=offsetbias)
    scanlist = (2, axisint1, updatedstart1, updatedstop1, numframes1, axisint2, updatedstart2, updatedstop2, numframes2)
    return scanlist

def ScanType_3(axis1, start1, stop1, numframes1, axis2, start2, stop2, numframes2, offsetbias = 'center'):
    scanlist2 = ScanType_2(axis1, start1, stop1, numframes1, axis2, start2, stop2, numframes2, offsetbias)
    scanlist = (3,) + scanlist2[1:]
    return scanlist

def ScanType_4(axis, start, stop, numframes, offsetbias = 'center'):
    axisint = get_axis_number(axis)
    distance = calc_distance(start,stop)
    updateddistance = calculate_updated_distance_from_num_points(numframes, distance, motor_speed)
    updatedstart, updatedstop = update_start_end(start, stop, updateddistance - distance, whereoffset=offsetbias)
    scanlist = (4, axisint, updatedstart, updatedstop, numframes)
    return scanlist

def ScanType_5(axis1, start1, stop1, numframes1, axis2, start2, stop2, numframes2, flyaxis, offsetbias = 'center'):
    scanlist2 = ScanType_2(axis1, start1, stop1, numframes1, axis2, start2, stop2, numframes2, offsetbias)
    scanlist = (5,) + scanlist2[1:] + (get_axis_number(flyaxis),)
    return scanlist

def ScanType_6(axis, start, stop, numframes, flyaxis, offsetbias = 'center'):
    axisint = get_axis_number(axis)
    distance = calc_distance(start,stop)
    updateddistance = calculate_updated_distance_from_num_points(numframes, distance, motor_speed)
    updatedstart, updatedstop = update_start_end(start, stop, updateddistance - distance, whereoffset=offsetbias)
    scanlist = (6, axisint, updatedstart, updatedstop, numframes)
    return scanlist

###################
#updatescanparams for input datasets from configuration
###################

def update_scan_params(datasets_for_inputfile):
    optimized_scan_params_summary = []
    optimized_dwelltime_summary = []
    for dataset in datasets_for_inputfile:
        if dataset['scantype'] == 0:
            optimized_scan_params = ScanType_0()
            optimized_dwelltime = dataset['dwelltime']
        else: 
            if dataset['scantype'] == 1:
                optimized_scan_params = ScanType_1(dataset['axis1'], dataset['start1'], dataset['end1'], dataset['numframes1'], dataset['offbias'])
            elif dataset['scantype'] == 2:
                optimized_scan_params = ScanType_2(dataset['axis1'], dataset['start1'], dataset['end1'], dataset['numframes1'],dataset['axis2'], dataset['start2'], dataset['end2'], dataset['numframes2'], dataset['offbias'])
            elif dataset['scantype'] == 3:
                optimized_scan_params = ScanType_3(dataset['axis1'], dataset['start1'], dataset['end1'], dataset['numframes1'],dataset['axis2'], dataset['start2'], dataset['end2'], dataset['numframes2'], dataset['offbias'])
            elif dataset['scantype'] == 4:
                optimized_scan_params = ScanType_4(dataset['axis1'], dataset['start1'], dataset['end1'], dataset['numframes1'], dataset['offbias'])
            elif dataset['scantype'] == 5:
                optimized_scan_params = ScanType_5(dataset['axis1'], dataset['start1'], dataset['end1'], dataset['numframes1'],dataset['axis2'], dataset['start2'], dataset['end2'], dataset['numframes2'], dataset['flyaxis'], dataset['offbias'] )
            elif dataset['scantype'] == 6:
                optimized_scan_params = ScanType_6(dataset['axis1'], dataset['start1'], dataset['end1'], dataset['numframes1'], dataset['offbias'])

            ctime_input = optimized_scan_params[2:5] + (dataset['dwelltime'],motor_speed,)
            optimized_dwelltime = update_dwelltime(*ctime_input)

        optimized_scan_params_summary.append(optimized_scan_params)
        optimized_dwelltime_summary.append(optimized_dwelltime)  
    return optimized_scan_params_summary, optimized_dwelltime_summary


###################
#input textfile writer
###################

def tuple_dataset_values(datasets_for_inputfile, lab_ref_points, optimized_dwelltime_summary, optimized_scan_params_summary, f, ome = 0, omeoff = 0, IntStart = 1):
    dataset_for_writer = []
    for idx in range(0,len(datasets_for_inputfile)):
        dataset = datasets_for_inputfile[idx]
        dwelltime = optimized_dwelltime_summary[idx]
        scan_params = optimized_scan_params_summary[idx]
        values = (f, IntStart, dataset['dataset_ID'], dataset['configuration_no'], lab_ref_points[idx], ome, omeoff, dwelltime, dataset['horz_slit'], dataset['vert_slit'], dataset['detector_slits'], scan_params)
        dataset_for_writer.append(values) 

    return dataset_for_writer

def combine_data_input(f, IntStart, DataNo, Config,  XYZ, sq, offset, CtTime, bw, bh, rsgap_size,  Scan=0):
    appended_scans = []
    ### Vectors from scalars ###
    if np.isscalar(sq):
        sq = np.ones(XYZ.shape[0]) * sq
        
    if np.isscalar(offset):
        offset = np.ones(XYZ.shape[0]) * offset
    
    if np.isscalar(CtTime):
        CtTime = np.ones(XYZ.shape[0]) * CtTime
        
    if np.isscalar(bw):
        bw = np.ones(XYZ.shape[0]) * bw
        
    if np.isscalar(bh):
        bh = np.ones(XYZ.shape[0]) * bh
    
    if np.isscalar(rsgap_size):
        rsgap_size = np.ones(XYZ.shape[0]) * rsgap_size
    
    ### Default Scan
    if Scan == 0:
        scan_string = '%d \n'
        scan_info   = (0,)
    else:
        if isinstance(Scan, tuple):
        
            if Scan[0] == 1:
                # no string in input. for axis0: 1=x; 2=y; 3=z; 4=ome
                scan_string = '%d %d %f %f %d \n'
                scan_info = Scan
                
            if Scan[0] == 2:
                # no string in input. for axis0 and axis1: 1=x; 2=y; 3=z; 4=ome
                scan_string = '%d %d %f %f %d %s %f %f %d \n'
                scan_info = Scan
            if Scan[0] == 3:
                # no string in input. for axis0 and axis1: 1=x; 2=y; 3=z; 4=ome
                scan_string = '%d %s %f %f %d %s %f %f %d \n'
                scan_info = Scan
                
            if (Scan[0] == 4) | (Scan[0] == 6):
                # no string in input. for axis0: 1=x; 2=y; 3=z; 4=ome
                scan_string = '%d %d %f %f %d \n'
                scan_info = Scan
            
            if (Scan[0] == 5):
                # no string in input. for axis0 and axis1: 1=x; 2=y; 3=z; 4=ome
                scan_string = '%d %d %f %f %d %d %f %f %d %d \n'
                scan_info = Scan
        else:
            raise RuntimeError('Input Scan format is incorrect.')
    
    
    # 
    for ii in range(XYZ.shape[0]):
        
        core_string = '%d %d %d %f %f %f %f %f %f %f %f %f '
        core_info   = ((ii+IntStart), DataNo, Config, XYZ[ii,0], XYZ[ii,1], XYZ[ii,2], sq[ii], offset[ii], CtTime[ii], bw[ii], bh[ii], rsgap_size[ii])
        
        info_combined = ((core_string + scan_string) % (core_info + scan_info))
        appended_scans.append(info_combined)
    
    
    return appended_scans

def write_OuputForSpec2024_with_append(_to_write):
    #all_appended_scans = []
    for kk in range(0,len(_to_write)):
        single_dataset_values = _to_write[kk]
        f = single_dataset_values[0]
        appended_scans= combine_data_input(*single_dataset_values)
        #all_appended_scans.append(appended_scans)
        # File Writing 
        if kk == 0: 
            file1 = open(f, "w")
            for jj in range(len(appended_scans)):
                    file1.write(appended_scans[jj])
            file1.close()
        else:
            file1 = open(f, "a")
            for jj in range(len(appended_scans)):
                    file1.write(appended_scans[jj])
            file1.close()
    
    return 'Done'

def print_optimized_value_changes_start_end(dataset_no, targeted_value_start, targeted_value_end, actual_value_start, actual_value_end):
    print ("For Dataset %d, The TARGETED start and end values were [%d, %d]" % (dataset_no, targeted_value_start,targeted_value_end))
    print ("For Dataset %d, The OPTIMIZED start and end values are [%d, %d]" % (dataset_no, actual_value_start,actual_value_end))
    return

def print_optimized_dwell_time(targeted_dwelltime, actual_dwelltime):
    print ("For Datset %d, The TARGETED dwelltime was %d" % (dataset_no, targeted_dwelltime))
    print ("For Datset %d, The OPTIMIZED dwelltime is %d" % (dataset_no, actual_dwelltime))
    return
    
def print_no_change(dataset_no):
    print ("For Dataset %d, ScanType not flyscan - all TARGET values used as is" % (dataset_no))
    return


##BUILDING CLASS:### Not used yet

class ID_config: 
    def __init__(self, scan_no, dataset_no, configuration_no):
        self.scan_no = scan_no
        self.dataset_ID = dataset_ID
        self.configuration_no = configuration_no

class reference_position: 
    def __init__(self, labx, laby, labz, ome_ref, ome_corr):
        self.labx = labx
        self.laby = laby
        self.labz = labz
        self.ome_ref = ome_ref
        self.ome_corr = ome_corr

class edd_config: 
    def __init__(self, scan_no, dataset_no, configuration_no):
        self.horz_slit = horiz_slit
        self.vert_slit = vert_slit
        self.detector_slits = detector_slits
        self.atten = atten

"""
class scan_parameters:
    def __init__(self, axis1, start1, stop1, numframes1, axis2, start2, stop2, numframes2, offsetbias, dwelltime):
        self.scantype = scantype
        self.axis1 = axis1
        self.start1 = start1
        self.stop1 = stop1
        self.numframes1 = numframes1
        self.axis2 = axis2
        self.start2 = start2
        self.stop2 = stop2
        self.numframes2 = numframes2
        self.offsetbias = offsetbias
        self.ctime = dwelltime
"""

class scan_parameters:
    def __init__(self, config):
        self.scantype = config['scantype']
        self.axis1 = config['axis1']
        self.start1 = config['start1']
        self.stop1 = config['stop1']
        self.numframes1 = config['numframes1']
        self.axis2 = config['axis2']
        self.start2 = config['start2']
        self.stop2 = config['stop2']
        self.numframes2 = config['numframes2']
        self.offsetbias = config['offsetbias']
        self.ctime = config['dwelltime']

