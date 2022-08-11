import os
import json
from copy import deepcopy as dc 

from pathlib import Path
script_path = os.path.dirname(Path(__file__))

def interpret_run_wps(conf_dict, output_run):
    template_file = os.path.join(os.path.dirname(script_path), 'run/run_wps.csh')
    with open(template_file) as fp:
        run_info = fp.readlines()

    geog_dir = conf_dict['wps_output_path']
    geog_path = os.path.join(geog_dir, 'geo_em.d*')
    line3 = f'ls -lath {geog_path}\n'
    run_info[3] = line3

    met_input = conf_dict['met_input_path']
    met_path = os.path.join(met_input, '*')
    line4 = f'./link_grib.csh {met_path}\n'
    run_info[4] = line4

    with open(output_run, 'w') as fp:
        fp.writelines(run_info)

def interpret_run_wrf(conf_dict, output_run):
    template_file = os.path.join(os.path.dirname(script_path), 'run/run_wrf.csh')
    with open(template_file) as fp:
        run_info = fp.readlines()

    met_dir = conf_dict['wps_output_path']
    met_path = os.path.join(met_dir, 'met_em.d*')
    line2 = f'ln -sf {met_path} . \n'
    run_info[2] = line2

    nproc = conf_dict['processors']
    line_real = f'mpirun -np {nproc} --allow-run-as-root ./real.exe \n'
    run_info[3] = line_real
    line_wrf = f'mpirun -np {nproc} --allow-run-as-root ./wrf.exe \n'
    run_info[4] = line_wrf

    with open(output_run, 'w') as fp:
        fp.writelines(run_info)

if __name__=='__main__':
    with open(os.path.join(script_path,'nl.conf'), 'r') as fp:
        conf_dict = json.load(fp)
    helper_dir = os.path.dirname(script_path)
    # print('Saving test csh scripts to: ',helper_dir)
    interpret_run_wps(conf_dict,os.path.join(helper_dir, 'run/run_wps.csh.output'))
    interpret_run_wrf(conf_dict,os.path.join(helper_dir, 'run/run_wrf.csh.output'))


