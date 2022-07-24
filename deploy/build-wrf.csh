#!/bin/csh

#	It looks like we may run out of stack sometimes, so make it
#	as large as we can.

unlimit stacksize

#	We are either asking for a BUILD or a RUN function. This script is
#	set up in two pieces (the over arching IF test) based on this value.

set WHICH_FUNCTION    = $1
shift

#	The BUILD function runs the clean (optional), configure, and compile
#	steps. Input is provided for whether or not to run clean, the options
#	appended at the end of the configure command, the numerical choices and
#	nesting options for configure, and the target for the compile command.

if      ( $WHICH_FUNCTION == BUILD ) then

	#	There are at least four args that are required for a BUILD step.
	#	1. Clean? If yes then the value is CLEAN, if no then any other string.
	#	2. The configuration number. For example, Linux GNU MPI = 34.
	#	3. The nest option for the configuration. Always 1, unless a moving domain.
	#	4. The build target for compile, for example, "em_real".

	if ( ${#argv} < 4 ) then
		touch /wrf/wrfoutput/FAIL_BUILD_ARGS
		exit ( 1 )
	endif

	set CLEAN             = $1
	set CONF_BUILD_NUM    = $2
	set CONF_BUILD_NEST   = $3
	set COMP_BUILD_TARGET = $4
	shift
	shift
	shift
	shift

	#	Check for additional arguments, first those that are passed to configure.
	#	These are denoted as they start with a leading dash "-". If we find a option
	#	that does not fit this criteria, we move to the next type of optional
	#	input to the BUILD step.

	set CONF_OPT = " "
	while ( ${#argv} )
		set HOLD = $1
		set str = "-"
		set loc = `awk -v a="$HOLD" -v b="$str" 'BEGIN{print index(a,b)}'`
		if ( $loc == 1 ) then
			set CONF_OPT = ( $CONF_OPT " " $HOLD )
			shift
		else
			break
		endif
	end

	#	The second type of optional input is for setting env variables. The syntax is
	#	similar to bash, for example "WRF_CHEM=1". No spaces and no quotes. If a space
	#	is required, fill it with an at symbol, "@". For example, "J=-j@3".

	set NMM_IS_FOUND = FALSE
	set str = @
	while ( ${#argv} )
		set PACKAGE = $1
		set loc = `awk -v a="$PACKAGE" -v b="$str" 'BEGIN{print index(a,b)}'`
		if ( $loc != 0 ) then
			echo $PACKAGE > .orig_with_at
			sed -e 's/@/ /g' .orig_with_at > .new_without_at
			set PACKAGE = `cat .new_without_at`
		endif
		set ARGUMENT =  `echo $PACKAGE | cut -d"=" -f1`
		set VALUE    = "`echo $PACKAGE | cut -d"=" -f2`"
		setenv $ARGUMENT "$VALUE"
		if ( $ARGUMENT == WRF_NMM_CORE ) then
			set NMM_IS_FOUND = TRUE
		endif
		shift
	end

	#	We have now processed all of the input for the BUILD step. The next steps
	#	are the traditional pieces required to build the WRF model. The SUCCESS or
	#	FAILURE of each step is determined and then that information is passed on in
	#	two different ways: both a flagged file and a return code.

	#	Get into the WRF directory.

	cd WRF >& /dev/null
	
	#	Remove all specially named flagged files in the special directory.

	rm /wrf/wrfoutput/{FAIL,SUCCESS}_BUILD_WRF_${COMP_BUILD_TARGET}_${CONF_BUILD_NUM} >& /dev/null

	#	There are the usual three steps for a BUILD: clean, configure, compile.
	#	We start those here.

	#	Are we asked to clean the directory structure? If so, then do it.

	if ( $CLEAN == CLEAN ) then
		./clean -a >& /dev/null
	endif
	
	#	The configure step has three pieces of input information. 
	#	1. There are the associated option flags, for example "-d".
	#	2. There is the numerical selection, for example Linux GNU MPI = 34.
	#	3. There is the nesting, typically = 1.

	./configure ${CONF_OPT} << EOF >& configure.output
$CONF_BUILD_NUM
$CONF_BUILD_NEST
EOF

	#	With GNU 9, the troubles with the RRTMG-derivative -d builds have gone
	#	away. Remove the prophylaxis for RRTMG FAST and RRTMG KIAPS. Remember,
	#	lest we forget the dark night, that NMM is still built with GNU 7.
	#	Ergo, if this is an NMM build, we leave those RRTMG-deviative schemes OUT.

	if ( $NMM_IS_FOUND == FALSE ) then
		sed -e 's/-DBUILD_RRTMG_FAST=0/-DBUILD_RRTMG_FAST=1/' configure.wrf > .foo1
		mv -f .foo1 configure.wrf
		sed -e 's/-DBUILD_RRTMK=0/-DBUILD_RRTMK=1/' configure.wrf > .foo1
		mv -f .foo1 configure.wrf
	endif
	
	#	The compile command takes only one input option, the compilation
	#	target. Any and all environment variables have already been processed
	#	at input and have been set. There are occassional problems with the
	#	build. Once *most* of the code is built, a re-compile is quick. If the
	#	executables already exist, then "no harm, no foul". If the executables
	#	do not exist, this is a quick way to grab that karma we have all earned.

	./compile $COMP_BUILD_TARGET >& compile.log.$COMP_BUILD_TARGET.$CONF_BUILD_NUM
	echo "ONCE MORE WITH FEELING" >>& compile.log.$COMP_BUILD_TARGET.$CONF_BUILD_NUM
	./compile $COMP_BUILD_TARGET >>& compile.log.$COMP_BUILD_TARGET.$CONF_BUILD_NUM
	if ( ! -e main/wrf.exe ) then
		echo "THEY GOT THE MUSTARD OUT" >>& compile.log.$COMP_BUILD_TARGET.$CONF_BUILD_NUM
		./compile $COMP_BUILD_TARGET >>& compile.log.$COMP_BUILD_TARGET.$CONF_BUILD_NUM
	endif

	#	We need to test to see if the BUILD worked. This is most easily handled
	#	by looking at the executable files that were generated. Since the compiled
	#	targets produce different numbers of executables and different names of
	#	executables, each compile has to be handled separately, so there is a 
	#	lengthy IF test.
	
	if      ( $COMP_BUILD_TARGET ==  em_real ) then
		if ( ( -e main/wrf.exe       ) && \
		     ( -e main/real.exe      ) && \
		     ( -e main/tc.exe        ) && \
		     ( -e main/ndown.exe     ) ) then
			touch /wrf/wrfoutput/SUCCESS_BUILD_WRF_${COMP_BUILD_TARGET}_${CONF_BUILD_NUM}
			exit ( 0 )
		else
			touch /wrf/wrfoutput/FAIL_BUILD_WRF_${COMP_BUILD_TARGET}_${CONF_BUILD_NUM}
			exit ( 2 )
		endif
	
	else if ( $COMP_BUILD_TARGET == nmm_real ) then
		if ( ( -e main/wrf.exe       ) && \
		     ( -e main/real_nmm.exe  ) ) then
			touch /wrf/wrfoutput/SUCCESS_BUILD_WRF_${COMP_BUILD_TARGET}_${CONF_BUILD_NUM}
			exit ( 0 )
		else
			touch /wrf/wrfoutput/FAIL_BUILD_WRF_${COMP_BUILD_TARGET}_${CONF_BUILD_NUM}
			exit ( 2 )
		endif
	endif
endif
#	That is the end of the BUILD phase.
