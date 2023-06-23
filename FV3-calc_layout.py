#!/usr/bin/env python3
########################################################################
#
# Calculate FV3 x,y layout options for 
#	agruments:
#		resolution:					resolution of model, examples
#										384
#
########################################################################
import argparse
from functools import reduce
from itertools import product
import numpy as np

####################################
# parse agruments
parser = argparse.ArgumentParser(description="description: calculates the FV3 INPES JNPES options for a resolution")
parser.add_argument('RES', metavar = 'resolution', action = 'store', \
					nargs = '?', default="C384", \
					help="Resolution of the FV3 model. examples include: C384")
args = parser.parse_args()
RES = args.RES
print(RES)
print(type(RES))
TILES = 6
####################################
#TILES=6
n=int(RES[1::])
#The only rules I know is that there must be at least four points in each of the horizontal directions for the MPI-domain.  So for C384 it is layout=96,96. You may want to use a balance of MPI-ranks and
############################################################
def factors(n):    
	return sorted(reduce(list.__add__,([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))
X, Y = [], []
for i in factors(n):
    if (384/i) >= 4:
        X.append(i)
        Y.append(i)
PROCS = []
XYS = []
for x,y in list(product(X,Y)):
    XYS.append([x, y])
    PROCS.append(x*y)

PROCS = np.array(PROCS)
XYS = np.array(XYS)
print("resolution: " + RES + ' with ' + str(TILES) + ' tiles')
print('nprocs\t INPES JNPES options')
for P in np.sort(np.unique(PROCS)):
    text = ''
    N_COM = XYS[PROCS == P].shape[0]
    if N_COM > 1:
        N_COM = int(np.ceil(N_COM/2.)) #+ 1
    for i in (np.arange(N_COM,0,-1) - 1): 
        text = text + '[' + str(XYS[PROCS == P][i][0]) + ',' + str(XYS[PROCS == P][i][1]) + ']'
    print(P*TILES,'\t', text)
print('nprocs\t INPES JNPES options')
print("resolution: " + RES + ' with ' + str(TILES) + ' tiles')

