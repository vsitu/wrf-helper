def update_line(str_old:str, info:str):
    str_new = str_old.split('=')[0]
    str_new += '= ' + info + ',\n'
    return(str_new)

def quote_wrap(value:str):
    return('\''+value+'\'')

def list_to_str(lst):
    return ', '.join([str(x) for x in lst])

def default_dup(line:str, dup_num:int):
    value = line.split('=')[-1].split(',')[0].strip(' ')
    newvalue = ','.join([str(value)]*dup_num)
    new_line = update_line(line, newvalue)
    return new_line