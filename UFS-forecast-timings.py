#!/usr/bin/env python3 
########################
#  Neil P. Barton (NOAA-EMC), 2022-08-30 Tue 08:05 AM UTC
#   tools to determing timings for different MPI configurations for running coupled model
# http://earthsystemmodeling.org/docs/release/ESMF_8_3_0/ESMF_refdoc/node6.html#SECTION060132200000000000000
########################
import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(__file__) + "/TIMING_TOOLS")
import TIMING_TOOLS as tt 
    
if __name__ == '__main__':
    ARGS = tt.args.get()
    
    files = tt.esmfprofile.getfiles(ARGS.TOPDIR)
    # get data from each file/directory maybe parralize this
    MODEL_SUMMARY, MODEL_header, MED_VARS = [], [], []
    for i, f in enumerate(files):
        # set up dictionary
        print(i+1, os.path.dirname(f))
        DICT = { }
        dir_name = os.path.dirname(f)
        DICT['NAME'] = dir_name 
        
        # get information from files
        DICT.update(tt.namelists.read_nemsconfigure(dir_name))
        DICT.update(tt.namelists.read_model_configure(dir_name))
        DICT.update(tt.namelists.read_stdout(dir_name))
        DICT.update(tt.namelists.read_MOM_input(dir_name))
        DICT.update(tt.namelists.read_ice_in(dir_name))
        DICT.update(tt.namelists.read_log_ww3(dir_name))
        DICT.update(tt.namelists.read_fv_core_netcdf(dir_name))
        DICT.update(tt.namelists.read_job_card(dir_name))
        
        # ESMF.Profile.summary read depenedent on tt.nameruns()
        ESMF_df, MED_VAR = tt.esmfprofile.to_panda(f)
        for M in MED_VAR: MED_VARS.append(M)
        
        # examine if components are on same pets and generalize some names
        DICT = tt.esmfprofile.panda_addto_dict(ESMF_df, DICT, MED_VAR)
        DICT = tt.parse_same_pets(DICT)
        DICT = tt.nameruns(DICT)
        
        # calc minute per day for forecast: goal is 8 minutes per day
        if 'WALLTIMEsec' in DICT.keys() and 'TAU' in DICT.keys():
            DICT['MINpDAY'] = round((DICT['WALLTIMEsec'] / 60.0) / (DICT['TAU'] / 24.0),1) 
        else:
            DICT['MINpDAY'] = 'Unknown'
            SORT_MINpDAY = False
        DICT['MINpDAY_GFS'] = 8.
        DICT['MINpDAY_GEFS'] = 10.
        for keys in DICT.items():
            if keys[0] not in MODEL_header:
                MODEL_header.append(keys[0])
        MODEL_SUMMARY.append(DICT)
    
    # after looping through files
    ARGS.MED_VAR = [*set(MED_VARS)]
    #make panda data frame for model summary
    MODEL_df = pd.DataFrame(MODEL_SUMMARY, np.arange(len(files)) + 1, MODEL_header )
    
    # check to see if the SORTBY option is possible
    if ARGS.SORTBY not in MODEL_df.keys():
        print("WARNING: sort variable ", ARGS.SORTBY, " not found in header, will sort by PETs")
        ARGS.SORTBY = 'PETs'

    #print statistcs to screen and write to file
    tt.summary.write(MODEL_df, ARGS)
    
    # plot data
    if ARGS.PLOT or ARGS.PLOT_COMPONENTS:
        print('\nPLOTTING: may take same time')
        tt.plot.ufs.df = MODEL_df
        tt.plot.ufs.app = MODEL_df['CONFIG'][1]
    if ARGS.PLOT:
        print('   TOTAL WALLTIME')
        COMPS_PLOT = MODEL_df['COMPS'][1].copy() 
        COMPS_PLOT.remove('MED')
        if 'ATM' in COMPS_PLOT:
            COMPS_PLOT.append('ATMIO')
        for M in ARGS.MED_VAR:
            COMPS_PLOT.append(M)
        tt.plot.ufs.all_comps = COMPS_PLOT
        tt.plot.ufs.all_plot()
    if ARGS.PLOT_COMPONENTS:
        print('   COMPONENT WALLTIME')
        tt.plot.ufs.all_comps = MODEL_df['COMPS'][1]
        for C in tt.plot.ufs.all_comps:
            print('\t',C)
            tt.plot.ufs.comp = C
            tt.plot.ufs.FILTER = C + 'thr'
            #tt.plot.ufs.FILTER = 'RESTART_N'
            tt.plot.ufs.x_axis = 'pe'
            tt.plot.ufs.x_label = 'MPI tasks X Threads'
            #tt.plot.ufs.comp_plot()
            tt.plot.ufs.x_axis = 'mpi'
            tt.plot.ufs.x_label = 'MPI tasks'
            #tt.plot.ufs.comp_plot()
    if ARGS.PLOT or ARGS.PLOT_COMPONENTS:
        import matplotlib.pyplot as plt
        plt.show()



