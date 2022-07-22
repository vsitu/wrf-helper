#!/bin/tcsh

./geogrid.exe
ls -lath /wrf_data/ysitu/wrf/WPS/geo_em.d*
./link_grib.csh /wrf_data/ysitu/gfs_2017/0615/gfs*
ln -sf ungrib/Variable_Tables/Vtable.GFS Vtable
./ungrib.exe
ls -lath FILE*
./metgrid.exe
