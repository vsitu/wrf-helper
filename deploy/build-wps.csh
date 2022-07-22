#!/bin/csh

unlimit stacksize
set MODE = $1
set NP = $2
/wrf/WPS/configure << EOF
$MODE
EOF

/wrf/WPS/compile << EOF >& log.wrfcompile
em_real 
-j 
$NP 
EOF
