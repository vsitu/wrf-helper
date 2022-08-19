import os, sys
import json
import datetime as dt
from copy import deepcopy as dc 
from pathlib import Path
script_path = os.path.dirname(Path(__file__))
sys.path.append(os.path.dirname(script_path))  # wrf-helper

from config.nesting import Box, Nest 
from config.nledit import (update_line, quote_wrap, 
                            list_to_str, default_dup)



target_fields = [
    'max_dom',
    'start_date',
    'end_date',
    'interval_seconds',
    'wrf_output_path',
]

datetime_fields = {
    'start_year':'%Y','start_month':'%m',
    'start_day':'%d','start_hour':'%H',
    'end_year':'%Y','end_month':'%m',
    'end_day':'%d','end_hour':'%H'}


def date_component(start_date: str, end_date: str, varname: str):
    start_obj = dt.datetime.strptime(start_date, '%Y-%m-%d_%H:%M:%S')
    end_obj = dt.datetime.strptime(end_date, '%Y-%m-%d_%H:%M:%S')
    var_type = varname.split('_')[0]
    if var_type == 'start':
        output = dt.datetime.strftime(start_obj, datetime_fields[varname])
    elif var_type == 'end':
        output = dt.datetime.strftime(end_obj, datetime_fields[varname])
    return str(output)




def interpret_wrf(conf_dict, output_wrf):
    template_file = os.path.join(script_path, '/templates/nl_template_wrf.txt')
    with open(template_file) as fp:
        wrf_info = fp.readlines()
    
    # extract information to strings
    num_proc = int(conf_dict['processors'])
    nproc_x = int(num_proc/2)
    max_dom_int = int(conf_dict['domain_count'])
    date_start = conf_dict['date_start']
    date_end = conf_dict['date_end']
    interval_sec_int = int(int(conf_dict['interval_hours']) * 3600)
    wrf_output_path = os.path.join(conf_dict['wrf_output_path'],
                                    'wrfout_d<domain>_<date>')
    # make dirs
    os.makedirs(conf_dict['wrf_output_path'], exist_ok=True)

    # optional settings
    try: 
        history_interval = eval(conf_dict['history_interval'])
    except: 
        history_interval = False

    # domains
    sub_doms = max_dom_int - 1
    main_box_geo = eval(conf_dict['main_box'])
    main_box = Box(geo_desc=main_box_geo, box_num=1)
    main_dx = main_box_geo[4]; main_dy = main_box_geo[5]

    parent_id_list = [0]; ratio_list = [1] 
    i_start_list = [1]; j_start_list = [1]
    e_we_list = [main_box_geo[2]]; e_sn_list = [main_box_geo[3]]
    grid_id = [1];
    for i in range(1, sub_doms + 1):
        sub_box_def = eval(conf_dict[f'sub_box_{i}'])
        sub_box_id = sub_box_def[5]  # id for nesting
        sub_box_ratio = sub_box_def[4]
        sub_box_geo = dc(sub_box_def[:4])
        sub_box_geo.append(int(main_dx / sub_box_ratio))
        sub_box_geo.append(int(main_dy / sub_box_ratio))
        sub_box = Box(geo_desc=sub_box_geo, box_num=sub_box_id)
        n = Nest()
        parent_id, nested_id, i_start, j_start = n.nest(main_box, sub_box)
        parent_id_list.append(parent_id)
        ratio_list.append(sub_box_ratio)
        i_start_list.append(round(i_start))
        j_start_list.append(round(j_start))
        sub_we_size = int(sub_box_geo[2])
        sub_sn_size = int(sub_box_geo[3])
        while sub_we_size % int(sub_box_ratio) != 1:
            sub_we_size += 1
        while sub_sn_size % int(sub_box_ratio) != 1:
            sub_sn_size += 1
        e_we_list.append(sub_we_size)
        e_sn_list.append(sub_sn_size)
        grid_id.append(i+1)

    # update info
    for linenum, line in enumerate(wrf_info):
        if '=' not in line:
            continue
        else:
            varname = line.split('=')[0]
            varname = varname.strip(' ')
            

    for linenum, line in enumerate(wrf_info):
        if '=' not in line:
            continue
        else:
            varname = line.split('=')[0]
            varname = varname.strip(' ')
        # datetime 
        if varname in datetime_fields.keys():
            datestr = date_component(date_start, date_end, varname)
            wrf_info[linenum] = update_line(line, ','.join([datestr]*max_dom_int))
        # common fields
        if varname == 'nproc_x':
            wrf_info[linenum] = update_line(line, str(nproc_x))
        elif varname == 'max_dom':
            wrf_info[linenum] = update_line(line, str(max_dom_int))
        elif varname == 'interval_seconds':
            wrf_info[linenum] = update_line(line, str(interval_sec_int))
        elif varname == 'history_outname':
            wrf_info[linenum] = update_line(line, quote_wrap(wrf_output_path))
        elif varname == 'time_step':
            wrf_info[linenum] = update_line(line, str(int(main_box_geo[4] /1000.0 * 5.0)))
        elif varname == 'ref_lon':
            wrf_info[linenum] = update_line(line, str(main_box_geo[0]))
        elif varname == 'ref_lat':
            wrf_info[linenum] = update_line(line, str(main_box_geo[1]))
        elif varname == 'dx':
            wrf_info[linenum] = update_line(line, str(main_box_geo[4]))
        elif varname == 'dy':
            wrf_info[linenum] = update_line(line, str(main_box_geo[5]))
        elif varname == 'grid_id':
            wrf_info[linenum] = update_line(line, list_to_str(grid_id))
        elif varname == 'parent_id':
            wrf_info[linenum] = update_line(line, list_to_str(parent_id_list))
        elif varname == 'parent_grid_ratio':
            wrf_info[linenum] = update_line(line, list_to_str(ratio_list))
        elif varname == 'parent_time_step_ratio':
            wrf_info[linenum] = update_line(line, list_to_str(ratio_list))
        elif varname == 'i_parent_start':
            wrf_info[linenum] = update_line(line, list_to_str(i_start_list))
        elif varname == 'j_parent_start':
            wrf_info[linenum] = update_line(line, list_to_str(j_start_list))
        elif varname == 'e_we':
            wrf_info[linenum] = update_line(line, list_to_str(e_we_list))
        elif varname == 'e_sn':
            wrf_info[linenum] = update_line(line, list_to_str(e_sn_list))
        # gwd_opt and history_interval are different for now
        elif varname == 'gwd_opt':
            gwd_opt = [1] + [0]*sub_doms
            wrf_info[linenum] = update_line(line, list_to_str(gwd_opt))
        elif varname == 'history_interval':  # default: 60min for main-box, 10min for sub-box
            if history_interval:
                hist_intv = history_interval
            else:
                hist_intv = [60] + [10]*sub_doms
            wrf_info[linenum] = update_line(line, list_to_str(hist_intv))

        # duplicate default values
        if varname in ['input_from_file','frames_per_outfile','e_vert',
            'radt','bldt','cudt','sf_urban_physics',
            'diff_opt','km_opt','diff_6th_opt','diff_6th_factor',
            'zdamp','dampcoef','khdif','kvdif','non_hydrostatic',
            'moist_adv_opt','scalar_adv_opt'
            ]:
            wrf_info[linenum] = default_dup(line, max_dom_int)
        
    with open(output_wrf, 'w') as f:
        for line in wrf_info:
            f.writelines(line)

if __name__=='__main__':
    nl_conf_default = os.path.join(script_path, 'nl.conf')
    nl_conf = input(f'Input config file. Default: {nl_conf_default} \n>>')
    if len(nl_conf) < 1:
        nl_conf = nl_conf_default 
    conf_file = open(nl_conf)
    conf_dict = json.load(conf_file)
    output_file = os.path.join(script_path, 'namelist.wrf.test')
    # sub grid format:
    # lon, lat, xsize, ysize, xratio, yratio, parent_id

    interpret_wrf(conf_dict, output_file)
    # template_file = os.path.join(script_path, 'nl_template_wrf.txt')
    # with open(template_file) as fp:
    #     wrf_info = fp.readlines()
    # var_list = []
    # for line in wrf_info:
    #     if '=' in line:
    #         varname = line.split('=')[0]
    #         varname = varname.strip(' ')
    #         var_list.append(varname)
    # print(var_list)