__all__ = ['write']

########################
def write(df, ARGS):
    import pandas as pd
    # create pandas from summaries
    pd.options.display.max_rows = None
    pd.options.display.max_columns = 99
    pd.options.display.width = 500
    pd.options.display.colheader_justify = 'center'
    
    # filter through what to print from MODEL_header
    FP = 'NODES' if ('NODES' == df.columns).all() else 'PETs'
    
    HEAD_PRINT = ['CONFIG', 'TAU', 'MINpDAY_GFS', 'MINpDAY_GEFS', 'MINpDAY', FP, 'FV3_32BIT']
    if ARGS.SHOW_SEC:
        HEAD_PRINT.insert(HEAD_PRINT.index('MINpDAY')+1,'UFSsec_max')
    
    for H in HEAD_PRINT:
        if H not in df.columns:
            HEAD_PRINT.remove(H)
    HEAD_COMPS = df['COMPS'].loc[df['COMPS'].str.len().max() == df['COMPS'].str.len()].values[0]
    HEAD_COMPS.remove('MED')
    REMOVE_HEAD_PRINT = []
    for C in HEAD_COMPS: 
        if (C+'res' == df.columns).any():
            HEAD_PRINT.append(C+'res')
        if (C+'mpi-t' == df.columns).any():
            HEAD_PRINT.append(C+'mpi-t')
        if (C+'dt' == df.columns).any():
            HEAD_PRINT.append(C+'dt')
        if (C+'tracers_n' == df.columns).any():
            HEAD_PRINT.append(C+'tracers_n')
        for SM in df['COMPS_SAMEPETS'][1]:
            if C not in SM:
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
        if C+TS in df.columns:
            HEAD_PRINT.append(C+TS)

    # remove items that share PEs
    for C in REMOVE_HEAD_PRINT:
        HEAD_PRINT.remove(C+'mpi-t')
        HEAD_PRINT.remove(C+TS)
    
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
        if C != 'MED':
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
        HEAD_PRINT.append('MEDmpi-t')
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
    df = df.sort_values('TAU')
    df = df.sort_values(ARGS.SORTBY)
    fw = 'esmf_summary.txt'
    print('\n')
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


