__all__ = ['get']
import argparse
import os

class get:
    parser = argparse.ArgumentParser(description="This script parses the stout_espc.list file to display a summary of UFS forecast timings")
    parser.add_argument('-d', '--directory', action='store', default='RTs', nargs = 1, help="top directory to search for stout_espc.list files")
    parser.add_argument('-sb', '--sortby', action='store', default=['MINpDAY'], nargs = 1, help='header to sort results, default is MINpDAY')
    parser.add_argument('-m', '--med', action='store_true', help='show mediator MPI, PE and Timings')
    parser.add_argument('-s', '--sec', action='store_true', help='show seconds for timings instead of Minutes Per Day')
    parser.add_argument('-per', '--percent', action='store_true', help='show percentage for timings instead of Minutes Per Day')
    parser.add_argument('-io', '--io', action='store_true', help='show ATM IO timings, ATM io layout, and OCN io layout')
    parser.add_argument('-xy', '--xylayout', action='store_true', help='show X,Y mpi layout for FV3')
    parser.add_argument('-l', '--loop', action='store_true', help='show what coupling loop component is on')
    parser.add_argument('-pe', '--pes', action='store_true', help='show PEs for components')
    parser.add_argument('-p', '--plot', action='store_true', default=None, help='plot Secs for total model')
    parser.add_argument('-pc', '--plot_components', action='store_true', default=None, help='plot Secs for components')
    ####################################
    def __new__(self, args = parser.parse_args()):
        TOPDIR = args.directory
        if TOPDIR == 'RTs':
            self.TOPDIR = os.environ['NPB_WORKDIR'] + '/RUNs/UFS'
        else:
            self.TOPDIR = TOPDIR[0]
        self.SHOW_MED =  args.med
        self.SHOW_SEC =  args.sec
        self.SHOW_PERCENT =  args.percent
        if args.sec and args.percent:
            print('cannot show seconds per componenet and percentage of component at same time')
            exit(1)
        self.SHOW_IO = args.io
        self.SHOW_XYLAYOUT = args.xylayout
        self.SHOW_LOOP = args.loop
        self.SHOW_PES = args.pes
        self.SORTBY = args.sortby[0]
        if args.plot is not None:
            self.PLOT = True
        else:
            self.PLOT = False
        if args.plot_components is not None:
            self.PLOT_COMPONENTS = True
        else:
            self.PLOT_COMPONENTS = False
        return self
