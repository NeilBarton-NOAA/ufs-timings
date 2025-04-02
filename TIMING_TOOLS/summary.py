__all__ = ['write']

########################
def write(df, ARGS):
    import pandas as pd
    import numpy as np
    import os
    # create pandas from summaries
    pd.options.display.max_rows = None
    pd.options.display.max_columns = 99
    pd.options.display.width = 500
    pd.options.display.colheader_justify = 'center'
    
    # filter through what to print from MODEL_header
    FP = 'NODES'
    if 'NODES' not in df.columns:
        FP = 'PETs'
    elif np.isnan(df['NODES']).any():
        FP = 'PETs'
    
    # list components
    HEAD_COMPS = df['COMPS'].loc[df['COMPS'].str.len().max() == df['COMPS'].str.len()].values[0]
    HEAD_COMPS.remove('MED')
    SHARED_COMPS = []
    for SM in df['COMPS_SAMEPETS'][1]:
        print(SM)
        for S in SM.split('+'):
            SHARED_COMPS.append(S)
        HEAD_COMPS.insert(HEAD_COMPS.index(SHARED_COMPS[1]) + 1, SM)
     
    HEAD_PRINT = ['CONFIG']
    
    # Resolution
    ADDS = ['res', 'dt', 'trancers_n']
    for A in ADDS: 
        for C in HEAD_COMPS: 
            if ((C+A == df.columns).any()) and (C != 'CHM') and (C != 'ICE'):
                HEAD_PRINT.append(C+A)
    
    HEAD_PRINT.extend(['FV3_32BIT', 'HYDROSTATIC', 'MINpDAY_GFS', 'MINpDAY_GEFS', 'MINpDAY', FP, 'TAU'])
    
    if ARGS.SHOW_SEC:
        HEAD_PRINT.insert(HEAD_PRINT.index('MINpDAY')+1,'UFSsec_max')
        HEAD_PRINT.insert(HEAD_PRINT.index('MINpDAY')+1,'WALLTIMEsec')
    
    for H in HEAD_PRINT:
        if H not in df.columns:
            HEAD_PRINT.remove(H)
    
    for C in HEAD_COMPS: 
        if (C+'mpi-t' == df.columns).any() and C not in SHARED_COMPS:
            HEAD_PRINT.append(C+'mpi-t')
        if C == 'ATM' and 'ATMIOmpi' in df.columns:
            HEAD_PRINT.append('ATMIOmpi')
    
    # how to show timings for components, defaults to minutes per day
    TS = '_MpD'
    if ARGS.SHOW_SEC:
        TS = 'sec_max' 
    if ARGS.SHOW_PERCENT:
        TS = '%' 
    
    for C in HEAD_COMPS: 
        if C+TS in df.columns and C not in SHARED_COMPS:
            HEAD_PRINT.append(C+TS)
    
    # if showing ATMIO stats
    PRINT_ATMIO = False
    if ARGS.SHOW_IO:
        if 'ATMIO'+TS in df.columns:
            HEAD_PRINT.insert(HEAD_PRINT.index('ATM'+TS) + 1,'ATMIO'+TS)
        HEAD_PRINT.append('ATMiolayout')
        if 'OCNiolayout' in df.columns:
            HEAD_PRINT.append('OCNiolayout')
    elif 'ATMiosec_max' in df.columns:
        if  (( (df['ATMsec_max'] - df['ATMIOsec_max']) / df['ATMsec_max'] * 100.0 ) < 10.).any():
            PRINT_ATMIO = True
            if 'ATMIO'+TS in df.columns:
                HEAD_PRINT.insert(HEAD_PRINT.index('ATM'+TS) + 1,'ATMIO'+TS)
            HEAD_PRINT.append('ATMiolayout')
 
    if ARGS.SHOW_ADVANCE_PROCS:
        HEAD_PRINT.append('UNUSED_PROCS')
        HEAD_PRINT.append('COREHOURSpDAY')
    
    # if showing loop
    if ARGS.SHOW_CPLSEC:
        for C in HEAD_COMPS:
            if C != 'MED' and '+' not in C:
                HEAD_PRINT.append(C+'cplsec')

    # if showing PEs
    if ARGS.SHOW_PES:
        for C in HEAD_COMPS:
            try:
                HEAD_PRINT.insert(HEAD_PRINT.index(C+'mpi-t')+1,C+'pe')
            except:
                pass

    # if showing MEDIATOR variables
    if ARGS.SHOW_MED:
        if 'UFS'+TS not in HEAD_PRINT:
            HEAD_PRINT.insert(HEAD_PRINT.index('MINpDAY')+1,'UFS'+TS)
        HEAD_PRINT.append('MEDmpi-t')
        HEAD_PRINT.append('INIT'+TS)
        HEAD_PRINT.append('FINAL'+TS)
        for M in ARGS.MED_VAR:
            HEAD_PRINT.append(M+TS)
    
    # if showing xy FV3 layout
    if ARGS.SHOW_XYLAYOUT:
        try:
            HEAD_PRINT.insert(HEAD_PRINT.index('ATMmpi-t'),'ATMlayout')
        except:
            HEAD_PRINT.insert(HEAD_PRINT.index('ATM+CHMmpi-t'),'ATMlayout')
    
    if 'RESTART_N' in df.columns:
        if (df['RESTART_N'] != df['TAU']).all():
            HEAD_PRINT.append('RESTART_N')
    
    # remove items that are the same 
    SUM = []
    if df.shape[0] > 1:
        SUM.append(['SHARED:', '  '])
    else:
        HEADER = ['INFO:', ' ']
    LOOP = HEAD_PRINT.copy()
    for H in LOOP:
        if (df[H] == df[H][1]).all():
            SUM.append([H+':', str(df[H][1])])
            HEAD_PRINT.remove(H)
    
    if PRINT_ATMIO:
        SUM.append(['WARNING:', 'ATMIOsec_max is close to or greater than ATMsec_max'])

    if ARGS.SORTBY not in HEAD_PRINT:
        HEAD_PRINT.append(ARGS.SORTBY)
    
    df = df.sort_values('CONFIG')
    df = df.sort_values('TAU')
    df = df.sort_values(ARGS.SORTBY)
    
    # print to screen
    df_sum = pd.DataFrame(SUM)
    print('\n')
    print(df_sum.to_string(index=False, header=False)) 
    print('\n')
    if df.shape[0] > 1:
        print(df[HEAD_PRINT])
    # write to file
    fw = 'esmf_summary.txt'
    f = open(fw,'w')
    f.write('RUN DIRECTORIES:\n')
    for i in range(df.shape[0]):
        f.write(str(i+1) + ' ' + df['NAME'][i+1] + '\n')
    f.close()
    df_sum.to_string('temp1.txt', index=False, header=False)
    
    if df.shape[0] > 1:
        df[HEAD_PRINT].to_string('temp2.txt') 
        with open(fw,'a') as outfile:
            for f in ['temp1.txt', 'temp2.txt']:
                with open(f) as infile:
                    outfile.write('\n')
                    outfile.write(infile.read())
                    outfile.write('\n')
                os.remove(f)
    else:
        os.remove('temp1.txt')
   

