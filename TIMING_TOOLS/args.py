__all__ = ['get']
import argparse
import os

class get:
    parser = argparse.ArgumentParser(description="This script parses the log files from a global UFS forecast to display timing")
    parser.add_argument('-d', '--directory', action='store', default='NeilBarton', nargs = 1, help="top directory to search for RUNDIRS of UFS, which need to include the ESMF Profile file")
    parser.add_argument('-sb', '--sortby', action='store', default=['MINpDAY'], nargs = 1, help='header to sort results, default is MINpDAY')
    parser.add_argument('-m', '--med', action='store_true', help='show mediator MPI, PE and Timings')
    parser.add_argument('-s', '--sec', action='store_true', help='show seconds for timings instead of Minutes Per Day')
    parser.add_argument('-per', '--percent', action='store_true', help='show percentage for timings instead of Minutes Per Day')
    parser.add_argument('-io', '--io', action='store_true', help='show ATM IO timings, ATM io layout, and OCN io layout')
    parser.add_argument('-c', '--cplsec', action='store_true', help='show coupling seconds for component')
    parser.add_argument('-pe', '--pes', action='store_true', help='show PEs for components')
    parser.add_argument('-xy', '--xylayout', action='store_false', help='do not show X,Y mpi layout for FV3')
    parser.add_argument('-ap', '--advanceprocs', action='store_true', help='show unused procs and core hours per forecast day')
    parser.add_argument('-p', '--plot', action='store_true', default=None, help='plot Secs for total model')
    parser.add_argument('-pc', '--plot_components', action='store_true', default=None, help='plot Secs for components')
    ####################################
    def __new__(self, args = parser.parse_args()):
        TOPDIR = args.directory
        if TOPDIR == 'NeilBarton':
            HOME = os.environ['HOME']
            if 'neil.barton' not in HOME.lower():
                print('must supply a directory in script')
                print('./UFS-timing-tools.py -d $YOUR_DIRECTORY')
                exit(1)
            else:
                self.TOPDIR = os.environ['NPB_WORKDIR'] + '/RUNS/UFS'
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
        self.SHOW_CPLSEC = args.cplsec
        self.SHOW_PES = args.pes
        self.SORTBY = args.sortby[0]
        self.SHOW_ADVANCE_PROCS = args.advanceprocs
        if args.plot is not None:
            self.PLOT = True
        else:
            self.PLOT = False
        if args.plot_components is not None:
            self.PLOT_COMPONENTS = True
        else:
            self.PLOT_COMPONENTS = False
        return self
