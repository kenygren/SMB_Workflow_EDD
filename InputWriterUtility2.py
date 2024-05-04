#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

motor_x_speed = 3937.01 #hardcoded motor speed for rsampX, rsampY, rsampZ
motor_y_speed = 3937.01 #hardcoded motor speed for rsampX, rsampY, rsampZ
motor_z_speed = 3937.01 #hardcoded motor speed for rsampX, rsampY, rsampZ
motor_w_speed = 2000.0 #hardcoded motor speed for rsampX, rsampY, rsampZ
per_scan_overhead = 5 # 4 for scans themselves, added 1 for motor motions 

###################
#primary function: 
###################

def combine_and_write_datasets(datasets_for_inputfile, lab_ref_points, f): 
    optimized_scan_params_summary, optimized_dwelltime_summary = update_scan_params(datasets_for_inputfile)
    calculate_dataset_collectiontimes(datasets_for_inputfile, lab_ref_points, optimized_scan_params_summary, optimized_dwelltime_summary, per_scan_overhead)
    datasets_for_writer = tuple_dataset_values(datasets_for_inputfile,lab_ref_points, optimized_dwelltime_summary, optimized_scan_params_summary, f)
    write_OuputForSpec2024_with_append(datasets_for_writer)
    return


###################
#remap motor to integer index
###################

def get_axis_number(axis):
    axis_mapping = {'x': 1, 'y': 2, 'z': 3, 'w': 4}
    return axis_mapping.get(axis, None)

def get_motor_speed(axis):
    axis_mapping = {'x': motor_x_speed, 'y': motor_y_speed, 'z': motor_z_speed, 'w': motor_w_speed }
    return axis_mapping.get(axis, None)


###################
#Get Direction and Motor Based Parameters
###################

def get_relevant_beam_dimension(datasets_for_inputfile, axis): 
    for dataset in datasets_for_inputfile:
            if axis == 'x':
                relevant_beamsize = dataset['horz_slit']
            elif axis == 'z':
                relevant_beamsize = dataset['vert_slit']
            elif axis == 'y':
                relevant_beamsize = 0
            elif axis == 'w':
                relevant_beamsize = 0
    else:
        print("you've made a mistake")
    return relevant_beamsize


###################
#Calculate Scan illumination regions for x, z motion
###################

def calculate_scan_distance_from_desired_illumination_distance(beamsize, illumination_distance, scantype, stepsize):    
    if scantype == 'dscan':
        distance = illumination_distance - beamsize
    elif scantype == 'flyscan':
        distance = illumination_distance - beamsize - stepsize
    #distance = (input flight range) + (interval size) + (beam width)
    return distance

def calculate_illumination_distance_from_scan_distance(beamsize, scan_distance, scantype, stepsize): 
    if scantype == 'dscan':
        distance = scan_distance + beamsize
    elif scantype == 'flyscan':
        distance = scan_distance + beamsize + stepsize 
    return distance

###################
#Get Dataset Times
###################

def calculate_dataset_collectiontimes(datasets_for_inputfile, lab_ref_points, optimized_scan_params_summary, optimized_dwelltime_summary, per_scan_overhead):
    total_time = []
    for datasetidx in range(0,len(datasets_for_inputfile)):
        dataset = datasets_for_inputfile[datasetidx]
        optimized_scan_params = optimized_scan_params_summary[datasetidx]
        optimized_dwelltime = optimized_dwelltime_summary[datasetidx]
        num_scans = len(lab_ref_points[datasetidx])
        if dataset['scantype'] == 0 :
            dataset_time = (num_scans * (optimized_dwell + per_scan_overhead))
        elif dataset['scantype'] in [1, 4, 6 ]:
            dataset_time = (num_scans * per_scan_overhead) + (num_scans * optimized_scan_params[4] * optimized_dwelltime)  
            #optimized_scan_params[4] = numframes1 , optimized_scan_params[8] - numframes2 #will make more sense with class
        elif dataset['scantype'] in [2 , 3 , 5] : 
            dataset_time = (num_scans * per_scan_overhead) + (num_scans * ((optimized_scan_params[4] * optimized_dwelltime * optimized_scan_params[8])) + (optimized_scan_params[8] * per_scan_overhead))
        print("Dataset %d has %d scans and will take approximately %f hours to complete" % (dataset['dataset_ID'], num_scans, dataset_time/60/60))
        total_time.append(dataset_time)
    print("The entire inputfile array will take approx. %f hours to complete" % ((sum(total_time)/60/60)))
    return


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
    distance = abs(start-stop)
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
    motor_speed = get_motor_speed(axis)
    updateddistance = calculate_updated_distance_from_num_points(numframes, distance, motor_speed)
    updatedstart, updatedstop = update_start_end(start, stop, updateddistance - distance, whereoffset=offsetbias)
    scanlist = (1, axisint, updatedstart, updatedstop, numframes)
    return scanlist

def ScanType_2(axis1, start1, stop1, numframes1, axis2, start2, stop2, numframes2, offsetbias = 'center'):
    axisint1 = get_axis_number(axis1)
    axisint2 = get_axis_number(axis2)
    distance1 = calc_distance(start1,stop1)
    distance2 = calc_distance(start2,stop2)
    motor_speed1 = get_motor_speed(axis1)
    motor_speed2 = get_motor_speed(axis2)
    updateddistance1 = calculate_updated_distance_from_num_points(numframes1, distance1, motor_speed1)
    updatedstart1, updatedstop1 = update_start_end(start1, stop1, updateddistance1 - distance1, whereoffset=offsetbias)
    updateddistance2 = calculate_updated_distance_from_num_points(numframes2, distance2, motor_speed2)
    updatedstart2, updatedstop2 = update_start_end(start2, stop2, updateddistance2 - distance2, whereoffset=offsetbias)
    scanlist = (2, axisint1, updatedstart1, updatedstop1, numframes1, axisint2, updatedstart2, updatedstop2, numframes2)
    return scanlist

def ScanType_3(axis1, start1, stop1, numframes1, axis2, start2, stop2, numframes2, offsetbias = 'center'):
    scanlist2 = ScanType_2(axis1, start1, stop1, numframes1, axis2, start2, stop2, numframes2, offsetbias)
    scanlist = (3,) + scanlist2[1:]
    return scanlist

def ScanType_4(axis, start, stop, numframes, offsetbias = 'center'):
    scanlist1 = ScanType_1(axis, start, stop, numframes, offsetbias = 'center')
    scanlist = (4,) + scanlist1[1:]
    return scanlist

def ScanType_5(axis1, start1, stop1, numframes1, axis2, start2, stop2, numframes2, flyaxis, offsetbias = 'center'):
    scanlist2 = ScanType_2(axis1, start1, stop1, numframes1, axis2, start2, stop2, numframes2, offsetbias)
    scanlist = (5,) + scanlist2[1:] + (get_axis_number(flyaxis),)
    return scanlist

def ScanType_6(axis, start, stop, numframes): #offsetbias = 'center'):
    axisint = get_axis_number(axis)
    scanlist = (6, axisint, start, stop, numframes)
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
            print_no_change(dataset['dataset_ID'])
        elif dataset['scantype'] == 6:
            relevant_beamsize = get_relevant_beam_dimension(datasets_for_inputfile, dataset['axis1'])
            illumination_distance = calc_distance(dataset['start1'], dataset['end1'])
            stepsize = (illumination_distance - relevant_beamsize) / (dataset['numframes1'] - 1)
            scan_distance = calculate_scan_distance_from_desired_illumination_distance(relevant_beamsize, illumination_distance, 'dscan', stepsize)
            offset = scan_distance - illumination_distance
            scan_start1, scan_end1 = update_start_end(dataset['start1'],dataset['end1'], offset, whereoffset = 'center')

            optimized_scan_params = ScanType_6(dataset['axis1'], scan_start1, scan_end1, dataset['numframes1'])
            optimized_dwelltime = dataset['dwelltime']
            print_no_change(dataset['dataset_ID'])   
        else:
            if dataset['scantype'] == 1:
                relevant_beamsize = get_relevant_beam_dimension(datasets_for_inputfile, dataset['axis1'])
                illumination_distance = calc_distance(dataset['start1'], dataset['end1'])
                stepsize = (illumination_distance - relevant_beamsize) / (dataset['numframes1'] - 1)
                scan_distance = calculate_scan_distance_from_desired_illumination_distance(relevant_beamsize, illumination_distance, 'flyscan', stepsize)
                offset = scan_distance - illumination_distance
                scan_start1, scan_end1 = update_start_end(dataset['start1'],dataset['end1'], offset, whereoffset = 'center')
                
                optimized_scan_params = ScanType_1(dataset['axis1'], scan_start1, scan_end1, dataset['numframes1'], dataset['offbias'])

            elif dataset['scantype'] == 2:
                relevant_beamsize = get_relevant_beam_dimension(datasets_for_inputfile, dataset['axis1'])
                illumination_distance = calc_distance(dataset['start1'], dataset['end1'])
                stepsize = (illumination_distance - relevant_beamsize) / (dataset['numframes1'] - 1)
                scan_distance = calculate_scan_distance_from_desired_illumination_distance(relevant_beamsize, illumination_distance, 'flyscan', stepsize)
                offset = scan_distance - illumination_distance
                scan_start1, scan_end1 = update_start_end(dataset['start1'],dataset['end1'], offset, whereoffset = 'center')
                
                relevant_beamsize2 = get_relevant_beam_dimension(datasets_for_inputfile, dataset['axis2'])
                illumination_distance = calc_distance(dataset['start2'], dataset['end2'])
                stepsize = (illumination_distance - relevant_beamsize2) / (dataset['numframes2'] - 1)
                scan_distance = calculate_scan_distance_from_desired_illumination_distance(relevant_beamsize2, illumination_distance, 'dscan', stepsize)
                offset = scan_distance - illumination_distance
                scan_start2, scan_end2 = update_start_end(dataset['start2'],dataset['end2'], offset, whereoffset = 'center')

                optimized_scan_params = ScanType_2(dataset['axis1'], scan_start1, scan_end1, dataset['numframes1'],dataset['axis2'], scan_start2, scan_end2, dataset['numframes2'], dataset['offbias'])
            
            elif dataset['scantype'] == 3:
                relevant_beamsize = get_relevant_beam_dimension(datasets_for_inputfile, dataset['axis1'])
                illumination_distance = calc_distance(dataset['start1'], dataset['end1'])
                stepsize = (illumination_distance - relevant_beamsize) / (dataset['numframes1'] - 1)
                scan_distance = calculate_scan_distance_from_desired_illumination_distance(relevant_beamsize, illumination_distance, 'flyscan', stepsize)
                offset = scan_distance - illumination_distance
                scan_start1, scan_end1 = update_start_end(dataset['start1'],dataset['end1'], offset, whereoffset = 'center')
                
                relevant_beamsize2 = get_relevant_beam_dimension(datasets_for_inputfile, dataset['axis2'])
                illumination_distance = calc_distance(dataset['start2'], dataset['end2'])
                stepsize = (illumination_distance - relevant_beamsize2) / (dataset['numframes2'] - 1)
                scan_distance = calculate_scan_distance_from_desired_illumination_distance(relevant_beamsize2, illumination_distance, 'dscan', stepsize)
                offset = scan_distance - illumination_distance
                scan_start2, scan_end2 = update_start_end(dataset['start2'],dataset['end2'], offset, whereoffset = 'center')


                optimized_scan_params = ScanType_3(dataset['axis1'], scan_start1, scan_end1, dataset['numframes1'],dataset['axis2'], scan_start2, scan_end2, dataset['numframes2'], dataset['offbias'])
            
            elif dataset['scantype'] == 4:
                relevant_beamsize = get_relevant_beam_dimension(datasets_for_inputfile, dataset['axis1'])
                illumination_distance = calc_distance(dataset['start1'], dataset['end1'])
                stepsize = (illumination_distance - relevant_beamsize) / (dataset['numframes1'] - 1)
                scan_distance = calculate_scan_distance_from_desired_illumination_distance(relevant_beamsize, illumination_distance, 'flyscan', stepsize)
                offset = scan_distance - illumination_distance
                scan_start, scan_end = update_start_end(dataset['start1'],dataset['end1'], offset, whereoffset = 'center')

                optimized_scan_params = ScanType_4(dataset['axis1'], scan_start, scan_end, dataset['numframes1'], dataset['offbias'])

            elif dataset['scantype'] == 5:
                relevant_beamsize = get_relevant_beam_dimension(datasets_for_inputfile, dataset['axis1'])
                illumination_distance = calc_distance(dataset['start1'], dataset['end1'])
                stepsize = (illumination_distance - relevant_beamsize) / (dataset['numframes1'] - 1)
                scan_distance = calculate_scan_distance_from_desired_illumination_distance(relevant_beamsize, illumination_distance, 'flyscan', stepsize)
                offset = scan_distance - illumination_distance
                scan_start1, scan_end1 = update_start_end(dataset['start1'],dataset['end1'], offset, whereoffset = 'center')
                
                relevant_beamsize2 = get_relevant_beam_dimension(datasets_for_inputfile, dataset['axis2'])
                illumination_distance = calc_distance(dataset['start2'], dataset['end2'])
                stepsize = (illumination_distance - relevant_beamsize2) / (dataset['numframes2'] - 1)
                scan_distance = calculate_scan_distance_from_desired_illumination_distance(relevant_beamsize2, illumination_distance, 'dscan', stepsize)
                offset = scan_distance - illumination_distance
                scan_start2, scan_end2 = update_start_end(dataset['start2'],dataset['end2'], offset, whereoffset = 'center')

                optimized_scan_params = ScanType_5(dataset['axis1'], scan_start1, scan_end1, dataset['numframes1'],dataset['axis2'], scan_start2, scan_end2, dataset['numframes2'], dataset['flyaxis'], dataset['offbias'] )

            motor_speed = get_motor_speed(dataset['axis1'])
            ctime_input = optimized_scan_params[2:5] + (dataset['dwelltime'],motor_speed,)
            optimized_dwelltime = update_dwelltime(*ctime_input)

            #convert scan parameters into illumination lengths: 
            scan_distance = calc_distance(optimized_scan_params[2], optimized_scan_params[3])
            stepsize = scan_distance / (dataset['numframes1'] - 1)
            illumination_distance = calculate_illumination_distance_from_scan_distance(relevant_beamsize, scan_distance, 'flyscan', stepsize)
            offset = illumination_distance - scan_distance
            optimized_illumination_vol_start, optimized_illumination_vol_end = update_start_end(optimized_scan_params[2], optimized_scan_params[3], offset, whereoffset = 'center')

            scan_distance = calculate_scan_distance_from_desired_illumination_distance(relevant_beamsize, illumination_distance, 'flyscan', stepsize)
            offset = scan_distance - illumination_distance
            scan_start1, scan_end1 = update_start_end(dataset['start1'],dataset['end1'], offset, whereoffset = 'center')

            print_optimized_value_changes_start_end(dataset['dataset_ID'], dataset['start1'], dataset['end1'], optimized_illumination_vol_start,optimized_illumination_vol_end)
            print_optimized_dwell_time(dataset['dataset_ID'], dataset['dwelltime'], optimized_dwelltime)

        optimized_scan_params_summary.append(optimized_scan_params)
        optimized_dwelltime_summary.append(optimized_dwelltime)  

    return optimized_scan_params_summary, optimized_dwelltime_summary

#############################
### input textfile writer ###
#############################

def tuple_dataset_values(datasets_for_inputfile, lab_ref_points, optimized_dwelltime_summary, optimized_scan_params_summary, f, IntStart = 1):
    dataset_for_writer = []
    for idx in range(0,len(datasets_for_inputfile)):
        dataset = datasets_for_inputfile[idx]
        dwelltime = optimized_dwelltime_summary[idx]
        scan_params = optimized_scan_params_summary[idx]
        values = (f, IntStart, dataset['dataset_ID'], dataset['configuration_no'], lab_ref_points[idx], dwelltime, dataset['horz_slit'], dataset['vert_slit'], dataset['detector_slits'], scan_params)
        dataset_for_writer.append(values) 

    return dataset_for_writer

def combine_data_input(f, IntStart, DataNo, Config,  XYZWs , CtTime, bw, bh, rsgap_size,  Scan=0):
    appended_scans = []
    ### Vectors from scalars ###
    
    if np.isscalar(CtTime):
        CtTime = np.ones(XYZWs.shape[0]) * CtTime
        
    if np.isscalar(bw):
        bw = np.ones(XYZWs.shape[0]) * bw
        
    if np.isscalar(bh):
        bh = np.ones(XYZWs.shape[0]) * bh
    
    if np.isscalar(rsgap_size):
        rsgap_size = np.ones(XYZWs.shape[0]) * rsgap_size
    
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
    for ii in range(XYZWs.shape[0]):
        
        core_string = '%d %d %d %f %f %f %f %f %f %f %f %f '
        core_info   = ((ii+IntStart), DataNo, Config, XYZWs[ii,0], XYZWs[ii,1], XYZWs[ii,2], XYZWs[ii,3], XYZWs[ii,4], CtTime[ii], bw[ii], bh[ii], rsgap_size[ii])
        
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
    print ("For Dataset %d, The TARGETED start and end values were [%f, %f]" % (dataset_no, targeted_value_start,targeted_value_end))
    print ("For Dataset %d, The OPTIMIZED start and end values are [%f, %f]" % (dataset_no, actual_value_start,actual_value_end))
    return

def print_optimized_dwell_time(dataset_no, targeted_dwelltime, actual_dwelltime):
    print ("For Datset %d, The TARGETED dwelltime was %f" % (dataset_no, targeted_dwelltime))
    print ("For Datset %d, The OPTIMIZED dwelltime is %f" % (dataset_no, actual_dwelltime))
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