########################
# read namelist and out files to obtain data
#   nems.configure -> ESMF configure
#   input.nml, model_configure -> FV3
#   MOM_input -> MOM6
#   ice_in -> CICE
#   log.ww3 -> WW3
####################################
import os
def read_nemsconfigure(dir_name):
    import numpy as np
    DICT = {}
    config_file = dir_name + '/nems.configure'
    if not os.path.exists(config_file):
        config_file = dir_name + '/gfsfcst.log'
    L = []
    for line in open(config_file): 
        if 'EARTH_component_list:' in line:
            DICT['COMPONENTS'] = line.strip('EARTH_component_list:').strip().replace(' ','-')
            DICT['COMPS'] = DICT['COMPONENTS'].replace('-',' ').split(' ')
        if 'omp_num_threads:' in line:
            DICT[line[0:3] + 'thr'] = int(line.split(':')[-1])
        if 'mesh_' in line:
            C = line.split('mesh_')[-1][0:3].upper()
            RES = line.strip()[-6:-3]
            if RES[0] == '0':
                RES= '0.' + RES.split('0')[-1]
            DICT[C + 'res'] = RES
        if '_petlist_bounds' in line:
            if line[0] != '+':
                DICT[line.split('_petlist_bounds')[0].strip() + 'pet_beg'] = \
                    int(line.split('_petlist_bounds:')[-1].strip().split(' ')[0])
                DICT[line.split('_petlist_bounds')[0].strip() + 'pet_end'] = \
                    int(line.split('_petlist_bounds:')[-1].strip().split(' ')[-1])
        if '@' in line:
            if line.strip()[0] == '@':
                if len(line.strip()) > 1:
                    L.append(int(line.strip().strip('@')))
    if len(L) > 2:
        print('WARNING: more than two coupling loops found')
    DICT['LOOPslow'] = max(L)
    DICT['LOOPfast'] = min(L)
    return DICT

####################################
def read_model_configure(dir_name):
    DICT = {}
    config_file = dir_name + '/model_configure'
    if not os.path.exists(config_file):
        config_file = dir_name + '/gfsfcst.log'
    for line in open(config_file):
        if 'nhours_fcst' in line:
            DICT['TAU'] = int(line.split(':')[-1])
        if 'restart_interval:' in line:
            DICT['RESTART_N'] = int(line.split('restart_interval:')[1].strip().split(' ')[0])
        if 'dt_atmos' in line:
            DICT['ATMdt'] = int(line.strip('dt_atmos:'))
    config_file = dir_name + '/input.nml'
    if not os.path.exists(config_file):
        config_file = dir_name + '/gfsfcst.log'
    for line in open(config_file):
        if 'npx' in line and line[0] != '+':
            DICT['ATMres'] = 'C' + str(int(line.split('npx =')[-1].strip()) - 1)
        if 'levp =' in line and line[0] != '+':
            ATMlev = str(int(line.split('levp = ')[-1].strip()) - 1)
        if ' layout =' in line and line[0] != '+':
            DICT['ATMlayout'] = line.split(' layout = ')[-1].strip()
        if 'io_layout' in line and line[0] != '+':
            DICT['ATMiolayout'] = line.strip('io_layout =').strip()
    if 'ATMres' in DICT:
        DICT['ATMres'] = DICT['ATMres'] + 'L' + ATMlev
        DICT['CHMres'] = DICT['ATMres']
    return DICT

####################################
def read_stdout(dir_name):
    DICT = {}
    config_file = dir_name + '/out' #RT testing
    if not os.path.exists(config_file):
        config_file = dir_name + '/gfsfcst.log' # global-workflow testing
    if not os.path.exists(config_file):
        config_file = dir_name + '/logfile.000000.out' # global-workflow testing
    if os.path.exists(config_file):
        for line in open(config_file,'r'):
            if (os.path.basename(config_file) == 'out'):
                if 'The total amount of wall time ' in line:
                    DICT['WALLTIMEsec'] = float(line.split('=')[-1]) 
                    DICT['WALLTIME'] = round(float(line.split('=')[-1]) / 3600.,2)
            elif (os.path.basename(config_file) == 'gfsfcst.log'):
                if 'Total runtime ' in line:
                    DICT['WALLTIMEsec'] = float(line.split('runtime ')[-1].split()[1])
                    DICT['WALLTIME'] = round(float(line.split('runtime ')[-1].split()[1]) / 3600.,2)
                    break
            else:
                if 'Total runtime ' in line:
                    DICT['WALLTIMEsec'] = float(line.split('runtime ')[-1].strip())
                    DICT['WALLTIME'] = round(float(line.split('runtime ')[-1].strip()) / 3600.,2)
                    break
    return DICT

####################################
def read_fv_core_netcdf(dir_name):
    import xarray as xr
    import numpy as np
    DICT = {}
    config_file = dir_name + '/RESTART/fv_core.res.nc' 
    if os.path.exists(config_file):
        dtype = xr.open_dataset(config_file)['ak'].values.dtype
        if dtype == np.dtype('float32'):
            DICT['FV3_32BIT'] = 'T'
        elif dtype == np.dtype('float64'):
            DICT['FV3_32BIT'] = 'F'
    else:
        DICT['FV3_32BIT'] = 'unknown'
    return DICT

####################################
def read_MOM_input(dir_name):
    DICT = {}
    config_file = dir_name + '/INPUT/MOM_input'
    if os.path.exists(config_file):
        for line in open(config_file):
            if 'NIGLOBAL = ' in line:
                I = int(line.split('NIGLOBAL = ')[1].split(' ')[0])
            if 'NJGLOBAL = ' in line:
                J = int(line.split('NJGLOBAL = ')[1].split(' ')[0])
            if 'NK = ' in line:
                L = 'L' + line.split('NK = ')[1].split('!')[0].strip() 
            if 'DT =' in line:
                DICT['OCNdt'] = int(line.strip('DT =').split('!')[0])
            if 'DT_THERM =' in line:
                DICT['OCNdttherm'] = int(line.strip('DT_THERM =').split('!')[0])
        if I == 1440 and J == 1080:
            RES = '0.25'
        elif I == 360 and J == 320:
            RES = '1.00'
        else:
            print('FATAL: OCNres unknown from I and J: I =', I, ' J =', J)
        DICT['OCNres'] = RES + L
    config_file = dir_name + '/INPUT/MOM_layout'
    if os.path.exists(config_file):
        for line in open(config_file):
            if 'IO_LAYOUT' in line:
                DICT['OCNiolayout'] = line.strip('IO_LAYOUT =').strip()
    return DICT

####################################
def read_ice_in(dir_name):
    DICT = {}
    config_file = dir_name + '/ice_in'
    if os.path.exists(config_file):
        for line in open(config_file):
            if '  dt  ' in line:
                DICT['ICEdt'] = int(line.split('=')[-1])
    return DICT

####################################
def read_job_card(dir_name):
    DICT = {}
    config_file = dir_name + '/job_card'
    if os.path.exists(config_file):
        for line in open(config_file):
            if '--nodes=' in line: #slurm
                DICT['NODES'] = int(line.split('--nodes=')[-1])
            elif 'select=' in line: #pbs
                DICT['NODES'] = int(line.split('select=')[-1].split(':')[0])
    return DICT

