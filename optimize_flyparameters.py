import numpy as np 
import argparse

#functions

motor_speed = 3937.01 #hardcoded motor speed for rsampX, rsampY, rsampZ

def calculate_updated_distance_from_num_points(desired_numpts, desired_distance, motor_speed):
    # Calculate starting effective stepsize
    stepsize = desired_distance / desired_numpts

    #calculate total steps required 
    total_steps_required = stepsize * motor_speed

    # Round the total steps to the nearest integer
    nearest_integer_steps = np.round(total_steps_required)
 
    #newstepsize
    newstepsize = nearest_integer_steps / motor_speed 

    # Calculate the updated distance based on the rounded steps
    updated_distance = desired_numpts * newstepsize

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

    # Calculate the updated distance 
    updated_distance = numpts * newstepsize
 
    return updated_distance, newstepsize, numpts


def update_dwelltime(updated_distance, newstepsize, numpts, desired_dwelltime, motor_speed):

    #calculate speed for desired dwell time with previously optimized distance and number of points
    speed = ((updated_distance * motor_speed) / (desired_dwelltime * numpts))
 
    #find closest even integer for speed
    even_int_speed = round_to_nearest_even(speed)
  
    #update dwelltime to compenstate for changes in integer speed
    updated_dwelltime = ((updated_distance * motor_speed) / (even_int_speed * numpts))
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

    parser.add_argument("--distance", type=float, required=True, help="Desired distance in mm.")
    parser.add_argument("--dwelltime", type=float, help="Dwell time in seconds.")

    args = parser.parse_args()

    if args.stepsize and args.numpts:
        print("Choose either a stepsize or number of points.")
    elif args.stepsize:
        updated_distance, newstepsize, numpts = calculate_updated_distance_from_desired_stepsize(args.stepsize, args.distance, motor_speed)
        print("Updated distance:", updated_distance)
        print("New step size:", newstepsize)
        print("Number of points", numpts)  
        if args.dwelltime:
            newdwelltime, updated_distance, numpts, newdwelltime = update_dwelltime(updated_distance, newstepsize, numpts, args.dwelltime, motor_speed)
            print("Updated dwell time", newdwelltime)
    elif args.numpts:
        updated_distance, newstepsize, numpts = calculate_updated_distance_from_num_points(args.numpts, args.distance, motor_speed)
        print("Updated distance:", updated_distance)
        print("New step size:", newstepsize)
        print("Number of points", numpts)
        if args.dwelltime:
            newdwelltime, updated_distance, numpts, newdwelltime = update_dwelltime(updated_distance, newstepsize, numpts, args.dwelltime, motor_speed)
            print("Updated dwell time", newdwelltime)

if __name__ == "__main__":
    main()

"""
###########
#step 1: determine updated distance and number of points based on desired values: 
###########
#inputs for option 1: calculate from desired number of points & desired distance
motor_speed = 3937.01 # steps per mm
desired_distance = 1 # mm
desired_numpts = 500

updated_distance, newstepsize, numpts = calculate_updated_distance_from_num_points(desired_numpts, desired_distance, motor_speed)
print("Updated distance:", updated_distance)
print("New step size:", newstepsize)
print("Number of points", numpts)

#inputs for option 2: calculate values from desired stepsize & desired distance
#desired_stepsize = 0.02
motor_speed = 3937.01 # steps per mm
#desired_distance = 1 # mm


updated_distance, newstepsize, numpts = calculate_updated_distance_from_desired_stepsize(desired_stepsize, desired_distance, motor_speed)
#print("Updated distance:", updated_distance)
#print("New step size:", newstepsize)
#print("Number of points", numpts)


##########
#step 2: calculate updated dwell time to achieve even interger frequency value with inputs from step 1
##########
desired_dwelltime = 10 # seconds 

newdwelltime, updated_distance, numpts, newdwelltime = update_dwelltime(updated_distance, newstepsize, numpts, desired_dwelltime, motor_speed)
print("Updated distance:", updated_distance)
print("New step size:", newstepsize)
print("Number of points", numpts)
print("Updated dwell time", newdwelltime)
"""