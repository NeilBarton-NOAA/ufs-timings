import matplotlib.pyplot as plt
import numpy as np

class ufs(object):
    @classmethod
    def comp_plot(cls):
        if cls.FILTER == 'thr':
            label_t = 'Threads'
        elif cls.FILTER == 'RESTART_N':
            label_t = 'Restart Freq.'
        else:
            label_t = cls.FILTER
        df = cls.df.groupby([cls.comp + 'mpi', cls.FILTER]).mean().sort_values(cls.comp + cls.x_axis).reset_index()
        fig, ax1 = plt.subplots()
        #ax2 = ax1.twinx()
        #SAME_PETS = cls.df['COMPS_SAMEPETS'][1]
        #LOOP_COMPS = cls.all_comps.copy()
        #LOOP_COMPS.remove(cls.comp)
        #AT = ''
        #for C in SAME_PETS:
        #    AT = AT + C + ':' + cls.df[C+'mpi-t'].mode()[0] + ' '
        #for C in LOOP_COMPS:
        #    df = df.loc[df[C+'mpi'].mode()[0] == df[C+'mpi']]
        #    df = df.loc[df[C+'thr'].mode()[0] == df[C+'thr']]
        #    for M in SAME_PETS:
        #        if C not in M:
        #            AT = AT + C + ':' + cls.df[C+'mpi-t'].mode()[0] + ' '
        for i in np.sort(df[cls.FILTER].unique()):
            X = df[df[cls.FILTER] == i][cls.comp + cls.x_axis] 
            Y = df[df[cls.FILTER] == i][cls.comp + 'sec_max']
            Y2 = df[df[cls.FILTER] == i]['WALLTIME'] * 3600.0
            ax1.plot(X,Y, '-o', label = label_t + ' = ' + str(i))
        #    ax2.plot(X,Y2, ':x', label = 'Threads = ' + str(i), alpha = 0.45)
        ax1.legend(loc='upper center', bbox_to_anchor=(0.5,-0.10), ncol = i, frameon = False)
        ax1.set_xlabel(cls.x_label)
        ax1.set_ylabel(cls.comp +' secs')
        #ax2.set_ylabel(cls.app +' secs' + '\n' + AT)
        TARGET = ( 8. * 60. ) / ( df['TAU'][1] / 24. )
        ax1.plot([np.min(X), np.max(X)],[TARGET, TARGET], ':k', label = 'Target: 8 CPU min / Forecast Day', alpha = 0.50)
        ax1.set_xlim([np.min(X), np.max(X)])
        try:
            FL = str(df['TAU'][1])
        except:
            FL = str(df['TAU'][0])
        plt.title(cls.comp + ': FL ' + FL + ' hours')
        plt.tight_layout()
        plt.savefig(cls.comp + '_' + cls.x_axis + '_timings.png')
    
    @classmethod
    def all_plot(cls):
        df = cls.df.sort_values('PETs')
        X = df['PETs'] 
        Y = df['WALLTIMEsec']
        fig, ax = plt.subplots()
        fig.set_size_inches(10, 6)
        ax.plot(X, Y, '-ok', label = 'Total Walltime')
        for C in cls.all_comps:
            style = '--' if C[0:3] == 'MED' or C[-3::] == 'MED' else '-'
            ax.plot(X, df[C + 'sec_max'], style, label = C + ' RunPhase', alpha = 0.75)
        TARGET = ( df['MINpDAY_GEFS'] * 60. ) * ( df['TAU'] / 24. ) # convert to seconds for all forecast run
        ax.plot(X, TARGET, ':k', label = 'Target: 8 CPU min / Forecast Day', alpha = 0.50)
        # get components needed to write informatoin
        SAME_PETS = cls.df['COMPS_SAMEPETS'][1]
        COMPS = cls.all_comps
        COMP_WRITE = SAME_PETS.copy()
        for C in COMP_WRITE:
            CC = C.split('+')[0][0:3]
            if CC in COMPS:
                COMPS.remove(CC)
            CC = C.split('+')[-1][0:3]
            if CC in COMPS:
                COMPS.remove(CC)
        for C in COMPS:
            if 'MED' not in C:
                COMP_WRITE.append(C)
        COMP_WRITE.append('MED')
        # print min and max runs
        N_write = [[X[X.idxmin()], X.idxmin()]]
        N_write.append([X[Y.idxmax()], Y.idxmax()])
        N_write.append([X[Y.idxmin()], Y.idxmin()])
        N_write.append([X[X.idxmax()], X.idxmax()])
        N_write = np.array(N_write)
        AT = '\n\n'
        for i, NN in enumerate(np.unique(N_write[:,0])):
            N = N_write[np.where(NN == N_write[:,0])[0][0],1]
            AT = AT + '(' + str(i+1) + ') '
            for C in COMP_WRITE:
                if C == 'ATMIO':
                    AT = AT + C + ':' + str(cls.df[C+'mpi'][N]) + ' '
                else:
                    AT = AT + C + ':' + str(cls.df[C+'mpi-t'][N]) + ' '
            ax.text(X[N], Y[N] + 25, str(i + 1),  fontweight = 'bold', va = 'bottom', ha = 'center')
            AT = AT + '\n'
        ax.set_xlim([np.min(X), np.max(X)])
        ax.set_xlabel('Total PETs' + AT)
        ax.set_ylabel('secs')
        ax.legend(loc='center left', bbox_to_anchor=(1., 0.5), frameon = False)
        plt.title(cls.app + ': FL ' + str(df['TAU'][1]) + ' hours')
        plt.tight_layout()
        plt.savefig('TOTAL_WALLTIME.png')

