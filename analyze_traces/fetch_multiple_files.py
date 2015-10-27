__author__ = 'yueli'
# -*- coding: utf-8 -*-
# RIPE Atlas API demo
# Read the list of measurement id from a text file, fetch the results of the measurement and store them in a local folder traces/


import requests
import os
import sys
from config.config import *


def downlod_trace(measurement_id):

    requests.packages.urllib3.disable_warnings() #disable urllib3 warnings

    # read key from auth file
    if not os.path.exists(ATLAS_AUTH):
        raise CredentialsNotFound(authfile)
    auth = open(ATLAS_AUTH)
    key = auth.readline()[:-1]
    auth.close()

    url = "https://atlas.ripe.net/api/v1/measurement/%s/result/" % int(measurement_id)
    params = {"key": key}
    headers = {"Accept": "application/json"}
    results = requests.get(url=url, params=params, headers=headers)

    return results

if __name__ == "__main__":
    # 此处需要给出要下载的 measurement id 的来源，即 measurement id 在
    # $HOME/Documents/Codes/Atlas/conduct_measurements 之后存储的子文件夹名称 & 文件名
    # 这里的子文件夹名称会同时用作traces实际存储的路径子文件夹名
    subfolder_name = '4_probes_to_alexa_top100'
    file_name = '4_top100_measurement_ids.txt'

    with open(os.path.join(ATLAS_CONDUCT_MEASUREMENTS, subfolder_name, file_name)) as f_handler:
        for measurement_id in f_handler:
            id = measurement_id.strip()
            file = os.path.join(ATLAS_TRACES, 'Produced_traces', subfolder_name, id+'.json')
            if os.path.exists(file):
                print id + ".json has already existed in" + os.path.join(ATLAS_TRACES, 'Produced_traces', subfolder_name) + ", no need to download it again!!"
            else:
                f = open(file, 'w')
                f.write(downlod_trace(id).text)
                f.close()
