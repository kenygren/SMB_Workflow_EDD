import numpy as np 
import argparse

#functions

motor_speed = 2000.0#3937.01 #hardcoded motor speed for rsampX, rsampY, rsampZ

def calculate_distance_from_desired_illumination_region(beamsize, illumination_region, scantype, stepsize):
    if scantype == 'dscan':
        distance = illumination_region - beamsize
    elif scantype == 'flyscan':
        distance = illumination_region - beamsize - stepsize
    #distance = (input flight range) + (interval size) + (beam width)
    return distance

def calculate_illumination_distance_from_scan_distance(beamsize, scan_distance, scantype, stepsize): 
    if scantype == 'dscan':
        distance = scan_distance + beamsize
    elif scantype == 'flyscan':
        distance = scan_distance + beamsize + stepsize 
    return distance

def calculate_updated_distance_from_num_points(desired_numpts, desired_distance, motor_speed):
    # Calculate starting effective stepsize
    intervals = desired_numpts-1
    stepsize = desired_distance / intervals

    #calculate total steps required 
    total_steps_required = stepsize * motor_speed

    # Round the total steps to the nearest integer
    nearest_integer_steps = np.round(total_steps_required)
 
    #newstepsize
    newstepsize = nearest_integer_steps / motor_speed 

    # Calculate the updated distance based on the rounded steps
    updated_distance = intervals * newstepsize

    return updated_distance, newstepsize, desired_numpts


def calculate_updated_distance_from_desired_stepsize(desired_stepsize, desired_distance, motor_speed):
    
    # Calculate the total steps required from approx step size
    total_steps_required = desired_stepsize * motor_speed
  
    # Round the total steps to the nearest integer
    nearest_integer_steps = np.round(total_steps_required)
 
    #calculate newstepsize
    newstepsize = nearest_integer_steps / motor_speed 

    #calculate interger number of points
    numpts = np.round(desired_distance / newstepsize)

    new_numpts = numpts + 1

    # Calculate the updated distance 
    updated_distance = numpts * newstepsize
 
    return updated_distance, newstepsize, new_numpts


def update_dwelltime(updated_distance, newstepsize, numpts, desired_dwelltime, motor_speed):

    #calculate speed for desired dwell time with previously optimized distance and number of points
    speed = ((updated_distance * motor_speed) / (desired_dwelltime * numpts-1))
 
    #find closest even integer for speed
    even_int_speed = round_to_nearest_even(speed)
  
    #update dwelltime to compenstate for changes in integer speed
    updated_dwelltime = ((updated_distance * motor_speed) / (even_int_speed * numpts-1))
    safe_dwelltime = np.floor(updated_dwelltime * 1000) / 1000

    return updated_distance, newstepsize, numpts, safe_dwelltime


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

def main():
    parser = argparse.ArgumentParser(description="Calculate updated parameters based on DESIRED parameters for rsampX, rsampY, rsampZ flyscans.", 
                                    epilog="Additional information: You must provide a target DISTANCE and EITHER a STEPSIZE or NUMBER OF POINTS. If you provide a DWELLTIME, it will also be optimized.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--stepsize", type=float, help="Desired step size in mm.")
    group.add_argument("--numpts", type=int, help="Desired number of points.")

    parser.add_argument("--distance", type=float, required=True, help="Desired distance to be illuminated in mm.")
    parser.add_argument("--dwelltime", type=float, help="Dwell time in seconds.")
    parser.add_argument("--beamsize", type=float, required=True, help="size of beamsize in mm in dimension you are scanning.")

    group2 = parser.add_mutually_exclusive_group(required=True)
    group2.add_argument("-flyscan", "--flyscan", action= 'store_true', help="indicates flyscan type ")
    group2.add_argument("-dscan", "--dscan", action= 'store_true', help="indicates dscan type")

    args = parser.parse_args()

    if args.stepsize and args.numpts:
        print("Choose either a stepsize or number of points.")
    if args.flyscan and args.dscan: 
        print("Choose either flyscan or dscan type")    
    if args.flyscan:
        scantype = 'flyscan'
        
        if args.stepsize:
            distance = calculate_distance_from_desired_illumination_region(args.beamsize, args.distance, scantype, args.stepsize)
            updated_distance, newstepsize, numpts = calculate_updated_distance_from_desired_stepsize(args.stepsize, distance, motor_speed)
            illuminated_distance = calculate_illumination_distance_from_scan_distance(args.beamsize, updated_distance,scantype,newstepsize)
            print("Illuminated distance:", illuminated_distance)
            print("scan_distance:", updated_distance)
            print("New step size:", newstepsize)
            print("Number of frames", numpts)  
            print("Want this as a SPEC scan? Try 'flydscan  <flymotor>  %f  %f  %d  <dwelltime>'" % (-(illuminated_distance/2), (illuminated_distance/2), (numpts-1)))
            if args.dwelltime:
                newdwelltime, updated_distance, numpts, newdwelltime = update_dwelltime(updated_distance, newstepsize, numpts, args.dwelltime, motor_speed)
                print("Updated dwell time", newdwelltime)
                print("Want this as a SPEC scan? Try 'flyscan  <motor>  %f  %f  %d  %f'" % (-(illuminated_distance/2), illuminated_distance/2, numpts-1, newdwelltime ))

        elif args.numpts:
            stepsize = (args.distance - args.beamsize) / (args.numpts-1) 
            distance = calculate_distance_from_desired_illumination_region(args.beamsize, args.distance, scantype, stepsize)
            updated_distance, newstepsize, numpts = calculate_updated_distance_from_num_points(args.numpts, distance, motor_speed)
            illuminated_distance = calculate_illumination_distance_from_scan_distance(args.beamsize, updated_distance,scantype,newstepsize)
            print("Illuminated distance:", illuminated_distance)
            print("scan_distance:", updated_distance)
            print("New step size:", newstepsize)
            print("Number of frames", numpts)
            print("Want this as a SPEC scan? Try 'flydscan  <flymotor>  %f  %f  %d  <dwelltime>'" % (-(illuminated_distance/2), (illuminated_distance/2), (numpts-1)))

            if args.dwelltime:
                newdwelltime, updated_distance, numpts, newdwelltime = update_dwelltime(updated_distance, newstepsize, numpts, args.dwelltime, motor_speed)
                print("Updated dwell time", newdwelltime)
                print("Want this as a SPEC scan? Try 'flyscan  <motor>  %f  %f  %d  %f'" % (-(illuminated_distance/2), illuminated_distance/2, numpts-1, newdwelltime ))

    if args.dscan:
        scantype = 'dscan'
        
        if args.stepsize:
            distance = calculate_distance_from_desired_illumination_region(args.beamsize, args.distance, scantype, args.stepsize)
            numpts = (np.round(distance/args.stepsize))
            numberframes = numpts + 1
            updated_distance = args.stepsize * numberframes
            illuminated_distance = calculate_illumination_distance_from_scan_distance(args.beamsize, updated_distance,scantype,args.stepsize)
            print("Illuminated distance:", illuminated_distance)
            print("scan_distance:", updated_distance)
            print("Stepsize", args.stepsize)
            print("Number of Frames", numberframes)
            print("Want this as a SPEC scan? Try 'dscan  <motor>  %f  %f  %d  <dwelltime>'" % (-(illuminated_distance/2), (illuminated_distance/2), (numberframes-1)))

            if args.dwelltime:
                print("Updated dwell time", args.dwelltime)
                print("Want this as a SPEC scan? Try 'dscan  <motor>  %f  %f  %d  %f'" % (-(illuminated_distance/2), illuminated_distance/2, numberframes-1, args.dwelltime ))

        if args.numpts:
            distance = args.distance - args.beamsize
            stepsize = distance/(args.numpts-1)
            updated_distance = stepsize * (args.numpts-1)
            illuminated_distance = calculate_illumination_distance_from_scan_distance(args.beamsize, updated_distance,scantype,stepsize)
            print("Illuminated distance:", illuminated_distance)
            print("scan_distance", updated_distance)
            print("Stepsize", stepsize)
            print("Number of Frames", args.numpts)
            print("Want this as a SPEC scan? Try 'dscan  <motor>  %f  %f  %d  <dwelltime>'" % (-(illuminated_distance/2), (illuminated_distance/2), (args.numpts-1)))

            if args.dwelltime:
                print("Updated dwell time", args.dwelltime)
                print("Want this as a SPEC scan? Try 'dscan  <motor>  %f  %f  %d  %f'" % (-(illuminated_distance/2), illuminated_distance/2, args.numpts-1, args.dwelltime ))


if __name__ == "__main__":
    main()

