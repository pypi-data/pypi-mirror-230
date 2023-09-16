import os
import json
import re
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from string import Template

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn
import click

app = FastAPI(title="1C-agent metrics")

settings = {'folders':['c:\\Program Files\\1cv8\\srvinfo\\reg_1541']}

#with open('agent1c_settings.yaml') as settings_file:
#    settings = load(settings_file,Loader=Loader)


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
    data = json.loads(str_original)

    #print(dump(data, Dumper=Dumper))
    
    cluster_fields = ['id','name','port','host']

    cfgdata['cluster'] = {cluster_fields[i]:data[1][i] for i in range(len(cluster_fields))}

    ib_fields = ['id','name','discription','dbtype','dbserver','dbname','dbuser','dbpasshash','dbstr','p1','block','block_tasks','p2','p3','p4','p5','p6','p7','p8']

    for ibdata in data[2][1:]:
        cfgdata['bases'].append({ib_fields[i]:ibdata[i] for i in range(len(ib_fields))})
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
    for path1c in settings['folders']:
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

@app.get('/metrics')
async def metrics():
    result = []
    result.append("# HELP logsize_by_infobase Cumulative size of 1cv8log folder.")
    result.append("# TYPE logsize_by_infobase gauge")
    result.append("# TYPE logtype_by_infobase gauge")
    t_logsize = Template("logsize_by_infobase{host=\"$host\",port=\"$port\",ibname=\"$ibname\",ibid=\"$ibid\"} $size")
    t_logtype = Template("logtype_by_infobase{host=\"$host\",port=\"$port\",ibname=\"$ibname\",ibid=\"$ibid\",type=\"$type\"} 1")
    data = get_data()
    for cluster_info in data.values():
        for ib in cluster_info['bases']:
            result.append(t_logsize.substitute(
                host=cluster_info['cluster']['host'],
                port=cluster_info['cluster']['port'],
                ibname=ib['name'],
                ibid=ib['id'],
                size=ib['logsize']
            ))
            result.append(t_logtype.substitute(
                host=cluster_info['cluster']['host'],
                port=cluster_info['cluster']['port'],
                ibname=ib['name'],
                ibid=ib['id'],
                type=ib['logtype']
            ))
    return PlainTextResponse('\n'.join(result))


@app.get("/")
async def root():

    result = get_data()
    
    #print('result',result)

    return result

@click.command()
@click.option("--reload", is_flag=True, help="Reload if code changes")
@click.option("--host", default='0.0.0.0', type=str, required=False, help="Host for reading")
@click.option("--port", default='8144', type=str, required=False, help="Port for reading")
def run(reload:bool,host:str, port:str) -> None:
    uvicorn.run("src.agent1c_metrics.agent1c_metrics:app", port=8144, log_level="info", host=host, reload=reload)

if __name__ == "__main__":
    run()
else:
    print(settings)
