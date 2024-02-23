# Optimized Flyparameter Commandline Calculator #    
        
The `OptimizedFlyparameter_CLI.py` tool is a quick way to validate the parameters for your flyscan/dscan configuration dictionary 

There are many ways to think about each aspect of a SCAN: 
- Scan **number of frames** (intervals)
- Scan **illumination coverage distance**
- Scan **Start** and **Stop** positions 
- Scan **stepsize**

The *configuration input dictionary* (cf `InputWriterREADME.md`)
wants this described as the **start**,  **stop**, and **number of frames** (intervals) you wish to capture in the dataset.

However, typically researchers prefer to prescribe their scans based on:
- **Illumination coverage** over a particular distance
- And either **scanstepsize** or **number of frames**

The X-ray beam has a width and height, so the total illuminated region is larger than the difference between the **start** and **stop** positions of each scan. See the illustration below. 

[image!]

The calculator will take in an **illumination distance** and provide an updated **scan_distance** defined as :

    scan_distance =  abs(start - end)








    
    
    
    [ken38@lnx201 EDD_Workflows_2024]$ python OptimizeFlyparameter_CLI.py --numpts 5 --distance 1 --dwelltime 13 --beamsize 0.05
    
    Updated distance: 0.9499594870218769
    New step size: 0.1899918974043754
    Number of points 5
    Updated dwell time 12.896
        
    [ken38@lnx201 EDD_Workflows_2024]$ python OptimizeFlyparameter_CLI.py --stepsize 0.05 --distance 1 --dwelltime 13 --beamsize 0.05
        
    Updated distance: 0.9507214866103972
    New step size: 0.05003797297949459
    Number of points 19.0
    Updated dwell time 12.312