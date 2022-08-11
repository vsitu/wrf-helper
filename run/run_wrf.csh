#!/bin/tcsh

ln -sf /wrf_data/WPS/zunyi/met_em* .
mpirun -np 8 --allow-run-as-root ./real.exe
mpirun -np 8 --allow-run-as-root ./wrf.exe