import args, esmfprofile, namelists, plot

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
    LOOP_ALL = []
    for C in COMPS_NOMED:
        LOOP_ALL.append(DICT[C+'loop'])
    PET_DATA = np.zeros([len(COMPS_NOMED),2]) - 9999
    for k, C in enumerate(COMPS_NOMED):
        PET_DATA[k,0] = DICT[C+'pet_beg']
        PET_DATA[k,1] = DICT[C+'pet_end']
        DICT[C+'loop'] = 'Slow' if DICT[C+'loop'] == min(LOOP_ALL) else 'Fast'
    DICT['MEDloop'] = 'MED'
    # summarize variables when compoents on same PETS
    index = np.where(np.diff(PET_DATA[:,0]) == 0)[0]
    DICT['COMPS_SAMEPETS'] = []
    for k in index:
        C0 = COMPS_NOMED[k]
        C1 = COMPS_NOMED[k+1]
        C_NAME = C0 + "+" + C1 
        DICT[C_NAME+'loop'] = DICT[C+'loop']
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

########################
def print_summary(df, ARGS):
    import pandas as pd
    # create pandas from summaries
    pd.options.display.max_rows = None
    pd.options.display.max_columns = 99
    pd.options.display.width = 500
    pd.options.display.colheader_justify = 'center'
    
    # filter through what to print from MODEL_header
    FP = 'NODES' if 'NODES' in df.columns else 'PETs'
    
    HEAD_PRINT = ['CONFIG', 'RESOLUTION', 'TAU', 'MINpDAY_GFS', 'MINpDAY_GEFS', 'MINpDAY', FP, 'FV3_32BIT']
    if ARGS.SHOW_SEC:
        HEAD_PRINT.insert(HEAD_PRINT.index('MINpDAY')+1,'UFSsec_max')
    
    for H in HEAD_PRINT:
        if H not in df.columns:
            HEAD_PRINT.remove(H)
    HEAD_COMPS = df['COMPS'][1].copy() 
    HEAD_COMPS.remove('MED')
    REMOVE_HEAD_PRINT = []
    for C in HEAD_COMPS: 
        HEAD_PRINT.append(C+'mpi-t')
        if C+'dt' in df.columns:
            HEAD_PRINT.append(C+'dt')
        for SM in df['COMPS_SAMEPETS'][1]:
            if C not in SM:
                HEAD_PRINT.append(C+'mpi-t')
        if C == 'ATM' and 'ATMIOmpi' in df.columns:
            HEAD_PRINT.append('ATMIOmpi')
    
    TS = '_MpD'
    if ARGS.SHOW_SEC:
        TS = 'sec_max' 
    if ARGS.SHOW_PERCENT:
        TS = '%' 
  
    for C in HEAD_COMPS: 
        HEAD_PRINT.append(C+TS)

    # remove items that share PEs
    for C in REMOVE_HEAD_PRINT:
        HEAD_PRINT.remove(C+'mpi-t')
        HEAD_PRINT.remove(C+TS)
        
    if (df['ATMmpi-t'] != df['MEDmpi-t']).any():
        HEAD_PRINT.append('MEDmpi-t')

    # if showing ATMIO stats
    PRINT_ATMIO = False
    if ARGS.SHOW_IO:
        HEAD_PRINT.insert(HEAD_PRINT.index('ATM'+TS) + 1,'ATMIO'+TS)
        HEAD_PRINT.append('ATMiolayout')
        if 'OCNiolayout' in df.columns:
            HEAD_PRINT.append('OCNiolayout')
    elif 'ATMiosec_max' in df.columns:
        if  (( (df['ATMsec_max'] - df['ATMIOsec_max']) / df['ATMsec_max'] * 100.0 ) < 10.).any():
            PRINT_ATMIO = True
            HEAD_PRINT.insert(HEAD_PRINT.index('ATM'+TS) + 1,'ATMIO'+TS)
            HEAD_PRINT.append('ATMiolayout')

    # if showing loop
    if ARGS.SHOW_LOOP:
        for C in COMPS_NOMED:
            HEAD_PRINT.append(C+'loop')

    # if showing PEs
    if ARGS.SHOW_PES:
        for C in HEAD_COMPS:
            try:
                HEAD_PRINT.insert(HEAD_PRINT.index(C+'mpi-t')+1,C+'pe')
            except:
                pass

    # if showing MEDIATOR variables
    if ARGS.SHOW_MED:
        HEAD_PRINT.append('INIT'+TS)
        HEAD_PRINT.append('FINAL'+TS)
        for M in ARGS.MED_VAR:
            HEAD_PRINT.append(M+TS)
    
    # if shoing xy FV3 layout
    if ARGS.SHOW_XYLAYOUT:
        try:
            HEAD_PRINT.insert(HEAD_PRINT.index('ATMmpi-t')+1,'ATMlayout')
        except:
            HEAD_PRINT.insert(HEAD_PRINT.index('ATM+CHMmpi-t')+1,'ATMlayout')
    
    if 'RESTART_N' in df.columns:
        if (df['RESTART_N'] != df['TAU']).all():
            HEAD_PRINT.append('RESTART_N')
    
    # remove items that are the same 
    SUM = ''
    if df.shape[0] > 1:
        SUM = 'SHARED \n'
    LOOP = HEAD_PRINT.copy()
    for H in LOOP:
        if (df[H] == df[H][1]).all():
            TABS = ': \t'
            if len(H) < 5:
                TABS = ': \t\t'
            elif len(H) < 6:
                TABS = ': \t\t'
            SUM = SUM + H + TABS + str(df[H][1]) + '\n'
            HEAD_PRINT.remove(H)
    if PRINT_ATMIO:
        SUM = SUM + 'WARNING: ATMIOsec_max is close to or greater than ATMsec_max' + '\n'

    if ARGS.SORTBY not in HEAD_PRINT:
        HEAD_PRINT.append(ARGS.SORTBY)

    df = df.sort_values('CONFIG')
    df = df.sort_values('RESOLUTION')
    df = df.sort_values('TAU')
    df = df.sort_values(ARGS.SORTBY)
    fw = 'esmf_summary.txt'
    print('\n\n\n')
    print(SUM)
    if df.shape[0] > 1:
        print(df[HEAD_PRINT])
        df[HEAD_PRINT].to_string(fw) 
    f = open(fw,'a')
    f.write('\n\n')
    f.write(SUM)
    f.write('\n') 
    for i in range(df.shape[0]):
        f.write(str(i+1) + ' ' + df['NAME'][i+1] + '\n')
    f.close()

