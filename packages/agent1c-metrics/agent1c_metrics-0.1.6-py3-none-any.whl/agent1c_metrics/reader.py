import agent1c_metrics
import os, json, re

def read1C_cfgFile(cfg_file):
    cfgdata = {'cluster':[],'bases':[]}

    if not os.path.isfile(cfg_file):
        return cfgdata | {'message':f'File not exists: {cfg_file}'}
    
    str_original = ''
    with open(cfg_file,encoding='utf-8') as cfg:
        str_original = cfg.read().replace("\r\n",'\n').replace('\n','').replace('\uFEFF','').replace('{','[').replace('}',']')
    str_original = re.sub(r"([0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12})",wrap_by_quotes,str_original)
    str_original = re.sub(r"[^,\[](\"\")",replace_double_quotes,str_original)
    str_original = re.sub(r",(0\d+)",wrap_by_quotes,str_original)
    #str_original = re.sub(r",(0\d+),",wrap_by_quotes,str_original)
    try:
        data = json.loads(str_original)
    except:
        print(f'Error when readint 1c file: {cfg_file}')
        print(f'Result of preparations:{str_original}')
        data = None

    if data:
    
        cluster_fields = ['id','name','port','host']

        cfgdata['cluster'] = {cluster_fields[i]:data[1][i] for i in range(len(cluster_fields))}

        ib_fields = ['id','name','discription','dbtype','dbserver','dbname','dbuser','dbpasshash','dbstr','p1','block','block_tasks','p2','p3','p4','p5','p6','p7','p8']

        for ibdata in data[2][1:]:
            cfgdata['bases'].append({ib_fields[i]:ibdata[i] for i in range(len(ib_fields))})
    else:
        return cfgdata | {'error':'Error when reading 1c file', 'file_content':str_original}

    return cfgdata

def wrap_by_quotes(match_obj):
    environment = match_obj.group()
    value = match_obj.group(1)
    replacement = environment.replace(value,f'"{value}"')
    if value is not None:
        return replacement

def replace_double_quotes(match_obj):
    value = match_obj.group()
    if value is not None:
        return value.replace('""','\\"')

def get_data():
    data = {}
    for path1c in agent1c_metrics.settings['folders']:
        cfg_file = os.path.join(path1c,'1CV8Clst.lst')
        cfg_data = read1C_cfgFile(cfg_file)
        data[path1c] = cfg_data

        for ib in cfg_data['bases']:
            ibpath = os.path.join(path1c,ib['id'],'1Cv8Log')

            # get log type
            ib['logtype'] = 'txt' if os.path.isfile(os.path.join(ibpath,'1Cv8.lgf')) else 'sqlite'
            
            # get size
            ib['logsize'] = 0
            if os.path.exists(ibpath):
                for ele in os.scandir(ibpath):
                    #print('-',ele)
                    ib['logsize'] += os.path.getsize(ele)
    return data
