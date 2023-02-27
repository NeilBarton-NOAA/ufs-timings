# UFS_TIMINGS
Tools to explore the timings in the UFS runs

to run
./UFS-forecast-timings.py -d $TOP_DIRECTORY_OF_RUNS

explore options by running
./UFS-forecast-timings.py -h

Note, tools are in rapid development

FV-calc_layout.py 
    lists the total procs and associated INPES and JNPES for scaling testes
        defaults to C384
        add -r for new resolution

CICE-calc_nprocs.py
    lists the total procs that can be used for a particular resolution
        only supported for 0.25 UFS grid
