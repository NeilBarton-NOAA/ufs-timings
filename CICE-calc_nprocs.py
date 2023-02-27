#!/usr/bin/env python2
########################################################################
#
# Calculate CICE compile options for Resolutions 
#	a re-write of parts in comp_ice of the cice model
# 	from comp_ice:
#   	NTASK equals nprocs in ice_in
#   	use processor_shape = slenderX1 or slenderX2 in ice_in
# 		If BLCKX (BLCKY) does not divide NXGLOB (NYGLOB) evenly, padding
# 		will be used on the right (top) of the grid.
#	agruments:
#		resolution:					resolution of model, examples
#										0.25
#		processor shape (optional):	shape of processers (1 or 2)
#										default is 1
#
########################################################################
import argparse
from functools import reduce

####################################
# parse agruments
parser = argparse.ArgumentParser(description="description: calculates the CICE compile options for different Resolutions.")
parser.add_argument('RES', metavar = 'resolution', action = 'store', \
					nargs='?', default=["0.25"], \
					help="Resolution of the CICE model. examples include: 0.25")
parser.add_argument('-s', '--shape', metavar = 'processor shape (e.g., slenderx1, slenderx2) in x-direction', action='store', \
					default=[2], nargs=1, help="processor shape used in the mode. usually 1 or 2")
args = parser.parse_args()
RES = args.RES[0]
SHAPE = int(args.shape[0])

####################################
GLOB={ 
"0.25" : {"NXGLOB" : 1440, "NYGLOB" : 1080},
}

if RES not in GLOB.keys():
	print 'resolution does not match known keys:'
	print ' given resolution:'
	print '  ', RES
	print ' known resolutions:'
	for k in GLOB.keys():
		print '  ', k
	exit(1)

############################################################
def factors(n):    
	return sorted(reduce(list.__add__,([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))

############################################################
NTASKS = factors(GLOB[RES]['NXGLOB']) 
NXGLOB=GLOB[RES]['NXGLOB']
NYGLOB=GLOB[RES]['NYGLOB']
BPX = 1			# number of blocks per processor in x direction (1 for straight MPI)
BPY = 1 		# number of blocks per processor in y direction (1 for straight MPI)
MXBLCKS = BPX * BPY

print "resolution: \t " + RES + " " + str(NXGLOB) + "x" + str(NYGLOB) + " (NXGLOB x NYGLOB)"
print "processor shape: slenderX"+str(SHAPE)
print 'nprocs\tBLCKX\tBLCKY\tMXBLCKS'
for N in NTASKS:
	if (N > 1) and (N != NXGLOB) and ( (N / SHAPE) > 1):
		NPX = N / SHAPE		#number of processors in x direction (user defined)
		NPY = N / NPX  	    #number of processors in y direction (user defined)
		BLCKX = (NXGLOB / NPX) if ((NXGLOB % NPX) == 0) else ((NXGLOB / NPX) + 1)
		BLCKY = (NYGLOB / NPY) if ((NYGLOB % NPY) == 0) else ((NYGLOB / NPY) + 1)
		MXBLCKS = (NXGLOB * NYGLOB) / (BLCKX * BLCKY * N)
		if MXBLCKS == 0: MXBLCKS = MXBLCKS + 1
		print str(N*SHAPE)+"\t", str(BLCKX/SHAPE)+"\t", str(BLCKY)+"\t", str(MXBLCKS)
print 'nprocs\tBLCKX\tBLCKY\tMXBLCKS'
print "resolution: \t " + RES + " " + str(NXGLOB) + "x" + str(NYGLOB) + " (NXGLOB x NYGLOB)"
print "processor shape: slenderX"+str(SHAPE)
