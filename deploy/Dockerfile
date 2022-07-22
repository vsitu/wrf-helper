FROM davegill/wrf-coop:fifteenthtry
USER root

RUN git config --global http.postBuffer 50M \
  && git clone https://github.com/wrf-model/WRF.git WRF \
  && cd WRF && git checkout release-v4.4 && cd .. \
  && git clone https://github.com/wrf-model/WPS.git WPS \
  && cd WPS && git checkout release-v4.4 && cd .. \
  && git clone https://github.com/davegill/SCRIPTS.git SCRIPTS \
  && cp SCRIPTS/rd_l2_norm.py . && chmod 755 rd_l2_norm.py \
  && ln -sf SCRIPTS/Namelists . \
  && git config --global --unset http.proxy \
  && git config --global --unset https.proxy 

CMD ["/bin/tcsh"]

COPY ./*.csh /wrf/

RUN chmod 755 build-wrf.csh \
  && ./script-situ.csh BUILD CLEAN 34 1 em_real -d J=-j@8 \
  && chmod 755 build-wps.csh

ENV WRF_DIR=/wrf/WRF/

RUN mv /wrf/build-wps.csh /wrf/WPS/ \
  && cd /wrf/WPS/ \
  && ./build-wps.csh 3 8
