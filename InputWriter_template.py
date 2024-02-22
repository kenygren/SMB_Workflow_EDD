import # --------- import dependecies ----------
        import numpy as np
        import InputWriterUtil as iwrite

        # ---------- name input textfile -----------
        base_dir = ''
        filename = 'OutputForSpec_date_sample.txt'
        f = base_dir+filename_suffix

        # ---------- generate reference points ----------
        
        ##########################################
        ##### This section is user-defined #######
        ##### See reference examples #############
        ##########################################
        
        ome = 0.0
        omeoff = 0.0
        omecorr = 0.5

        # lab_ref_points_<datasetno> is an array of points in the lab reference frame generated in this section:

        lab_ref_points_1 = XYZAll
        lab_ref_points_2 = XYZAll2

        # ---------- configuration for each dataset  -----------

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
            'dataset_ID': 4,
            'configuration_no': 2,

            'horz_slit': 0.08,
            'vert_slit': 0.08,
            'detector_slits': 0.08,

            'scantype': 3,

            'axis1': 'z',
            'start1': -0.5,
            'end1': 0.5,
            'numframes1': 5,

            'axis1': 'z',
            'start1': -0.5,
            'end1': 0.5,
            'numframes1': 5,

            'offbias': 'fix_end',

            'dwelltime': 3
        }

        # ---------- write text array  -----------

        datasets_for_inputfile = [config_dataset_1, config_dataset_2] #write in priority order
        lab_ref_points = [lab_ref_points_1, lab_ref_points_2] #match with above priority order

        iwrite.combine_and_write_datasets(datasets_for_inputfile, lab_ref_points, f, ome, omeoff)