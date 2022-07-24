# Files
build-wrf.csh is for configuring and compiling WRF. 

build-wps.csh is for configuring and compiling WPS. 

Dockerfile is for downloading and installing WRF and WPS together with Dave Gill's test script.


# Different layers of the deployment
1. WRF running environment
2. WRF and WPS code
3. WRF software
4. WPS software

## WRF running environment
The WRF docker image is based on containerized environment by Dave Gill.   
Currently at the [fifteenth try](https://hub.docker.com/r/davegill/wrf-coop/tags). 

## WRF and WPS code
WRF software can be found at Dave Gill's page. I recommend going to the [official GitHub page](https://github.com/wrf-model/WRF) for the latest WRF code.       
The [official GitHub page for WPS](https://github.com/wrf-model/WPS) can be found in the same user's page.

I recommend downloading the codes when building the docker image. That helps avoiding connection instabilities to GitHub in some areas of the world. To take it one step further, one can build WRF and WPS when building the docker image, and it should be ready for use out of the box.

## WRF software
The original compilation script for WRF can be found at Dave Gill's [GitHub site](https://github.com/davegill/SCRIPTS).     
One can compile WRF manually step-by-step (in a few steps), but I experienced Noah-MP error when I do it after an accidental server reset (run level 5 -> 2). If the user experiences the same error, please try Dave's script as they make things a lot easier. 

## WPS software
WPS (WRF Pre-Processing System) should be installed after WRF.      
Configuring and compiling WPS is more straight forward than WRF. One only needs to set the running mode (e.g. '3' for gfortran-dmpar) when configuring and the number of processors to use when compiling. 

## Note
For more complicated settings, please refer to WRF and WPS [official user guide](https://www2.mmm.ucar.edu/wrf/users/docs/user_guide_v4/contents.html).