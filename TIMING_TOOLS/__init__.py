import args, esmfprofile, namelists, plot, summary

####################################
def nameruns(DICT):
    COMPS = DICT['COMPS']
    if 'ATM' and 'OCN' and 'ICE' and 'WAV' and 'CHM' in COMPS:
        DICT['CONFIG'] = 'S2SWA'
    elif ('ATM' in COMPS) and ('OCN' in COMPS) and ('ICE' in COMPS) and ('WAV' in COMPS) and ('CHM' not in COMPS):
        DICT['CONFIG'] = 'S2SW'
    elif ('ATM' in COMPS) and ('OCN' in COMPS) and ('ICE' in COMPS) and ('WAV' not in COMPS) and ('CHM' not in COMPS):
        DICT['CONFIG'] = 'S2S'
    elif ('ATM' in COMPS) and ('OCN' and 'ICE' and 'WAV' and 'CHM' not in COMPS):
        DICT['CONFIG'] = 'ATM'
    else:
        print('FATAL: configuration unkown from', COMPS)
        exit(1)
    COMPS = DICT['COMPS']
    COMPS_NOMED = COMPS.copy()
    COMPS_NOMED.remove('MED')
    DICT['RESOLUTION'] = ''
    for C in COMPS_NOMED:
        if '+' in C:
            DICT['RESOLUTION'] = DICT['RESOLUTION'] + DICT[C.split('+')[0] + 'res'] + ' '
        if C != 'CHM' and C != 'ICE' and '+' not in C:
            DICT['RESOLUTION'] = DICT['RESOLUTION'] + DICT[C+'res'] + ' '
        elif C == 'ICE' and DICT['ICEres'] != DICT['OCNres'][0:4]:
            DICT['RESOLUTION'] = DICT['RESOLUTION'] + DICT[C+'res'] + ' '
    return DICT

####################################
def parse_same_pets(DICT):
    import numpy as np
    # get start and ending PETS
    COMPS = DICT['COMPS']
    COMPS_NOMED = COMPS.copy()
    COMPS_NOMED.remove('MED')
    PET_DATA = np.zeros([len(COMPS_NOMED),2]) - 9999
    for k, C in enumerate(COMPS_NOMED):
        PET_DATA[k,0] = DICT[C+'pet_beg']
        PET_DATA[k,1] = DICT[C+'pet_end']
    # summarize variables when compoents on same PETS
    index = np.where(np.diff(PET_DATA[:,0]) == 0)[0]
    DICT['COMPS_SAMEPETS'] = []
    for k in index:
        C0 = COMPS_NOMED[k]
        C1 = COMPS_NOMED[k+1]
        C_NAME = C0 + "+" + C1
        DICT[C_NAME+'pet_beg'] = min(DICT[C0+'pet_beg'], DICT[C1+'pet_beg'])
        DICT[C_NAME+'pet_end'] = min(DICT[C0+'pet_end'], DICT[C1+'pet_end'])
        DICT[C_NAME+'mpi'] = max(DICT[C0+'mpi'], DICT[C1+'mpi'])
        DICT[C_NAME+'thr'] = max(DICT[C0+'thr'], DICT[C1+'thr'])
        DICT[C_NAME+'pe'] = max(DICT[C0+'pe'], DICT[C1+'pe'])
        DICT[C_NAME+'mpi-t'] = str(DICT[C_NAME+'mpi']) + '-' + str(DICT[C0+'thr']) 
        DICT[C_NAME+'sec_mean'] = DICT[C0+'sec_mean'] + DICT[C1+'sec_mean']
        DICT[C_NAME+'sec_max'] = DICT[C0+'sec_max'] + DICT[C1+'sec_max']
        DICT['COMPS_SAMEPETS'].append(C_NAME)
    return DICT

####################################
def procs_not_used(DICT):
    COMPS = DICT['COMPS']
    COMPS_PROCS = COMPS.copy()
    COMPS_PROCS.remove('MED')
    if 'CHM' in COMPS:
        COMPS_PROCS.remove('CHM')
    COMPS_PROCS.append('ATMIO')
    TP = 0
    for k, C in enumerate(COMPS_PROCS):
        try:
            thr = DICT[C+'thr']
        except:
            thr = 1
        try:
            mpi = DICT[C+'mpi']
        except:
            mpi = 0
        TP = TP + (mpi * thr)
    DICT['UNUSED_PROCS'] = DICT['PETs'] - TP
    return DICT

