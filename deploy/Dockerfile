FROM davegill/wrf-coop:fifteenthtry
USER root

RUN git config --global http.postBuffer 50M \
  && git clone https://github.com/wrf-model/WRF.git WRF \
  && cd WRF && git checkout release-v4.4 && cd .. \
  && git clone https://github.com/wrf-model/WPS.git WPS \
  && cd WPS && git checkout release-v4.4 && cd .. \
  && git clone https://github.com/davegill/SCRIPTS.git SCRIPTS \
  && ln -sf SCRIPTS/Namelists . 

RUN pip3 install --upgrade pip \
  && git clone https://github.com/vysitu/wrf-helper.git \
  && pip3 install -r wrf-helper/deploy/req.txt \
  && pip3 install -r wrf-helper/deploy/req_visual.txt \
  && cp wrf-helper/deploy/*.csh /wrf/

CMD ["/bin/tcsh"]

RUN chmod 755 build-wrf.csh \
  && ./build-wrf.csh BUILD CLEAN 34 1 em_real -d J=-j@8 \
  && chmod 755 build-wps.csh

ENV WRF_DIR=/wrf/WRF/

RUN mv /wrf/build-wps.csh /wrf/WPS/ \
  && cd /wrf/WPS/ \
  && ./build-wps.csh 3 8