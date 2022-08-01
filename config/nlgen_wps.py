import os
import json
from pathlib import Path
script_path = os.path.dirname(Path(__file__))

target_fields = [
    'max_dom',
    'start_date',
    'end_date',
    'interval_seconds',
    'opt_output_from_geogrid_path',
    'opt_output_from_metgrid_path'
]

def update_line(str_old:str, info:str):
    str_new = str_old.split('=')[0]
    str_new += '= ' + info + ',\n'
    return(str_new)

def quote_wrap(value:str):
    return('\''+value+'\'')

def interpret_wps(conf_dict, output_wps):
    template_file = os.path.join(script_path, 'nl_template_wps.txt')
    with open(template_file) as fp:
        wps_info = fp.readlines()
    
    # extract information to strings
    max_dom_int = int(conf_dict['domain_count'])
    date_start = conf_dict['date_start']
    date_end = conf_dict['date_end']
    interval_sec_int = int(int(conf_dict['interval_hours']) * 3600)
    wps_output_path = conf_dict['wps_output_path']

    # update info
    for linenum, line in enumerate(wps_info):
        if 'max_dom' in line:
            wps_info[linenum] = update_line(line, str(max_dom_int))
        elif 'start_date' in line:
            wps_info[linenum] = update_line(line, ','.join([quote_wrap(date_start)]*max_dom_int))
        elif 'end_date' in line:
            wps_info[linenum] = update_line(line, ','.join([quote_wrap(date_end)]*max_dom_int))
        elif 'interval_seconds' in line: 
            wps_info[linenum] = update_line(line, str(interval_sec_int))
        elif 'opt_output_from_geogrid_path' in line:
            wps_info[linenum] = update_line(line, quote_wrap(wps_output_path))
        elif 'opt_output_from_metgrid_path' in line:
            wps_info[linenum] = update_line(line, quote_wrap(wps_output_path))


        
    with open(output_wps, 'w') as f:
        for line in wps_info:
            f.writelines(line)

if __name__=='__main__':
    nl_conf_default = os.path.join(script_path, 'nl.conf')
    nl_conf = input(f'Input config file. Default: {nl_conf_default}')
    if len(nl_conf) < 1:
        nl_conf = nl_conf_default 
    conf_file = open(nl_conf)
    conf_dict = json.load(conf_file)
    output_file = os.path.join(script_path, 'namelist.wps.test')
    interpret_wps(conf_dict, output_file)