# -*- coding: utf-8 -*-
__author__ = 'yueli'
# RIPE Atlas API demo
# Read the list of measurement id from a text file, fetch the results of the measurement and store them in a local folder traces/


import requests
import os
import sys
from config.config import *

# ==========================================Section: constant variable declaration======================================
# probe id和此probe的IP地址间的对应关系 22341, 2403, 13842, 2848, 6118
# PROBE_ID_IP_DICT = {
#     "132.227.120.130": "22341",
#     "37.49.234.132": "6118",
#     "137.194.165.62": "13842",
#     "153.16.38.64": "2403",
#     "217.70.181.250": "3141"
# }
# 
# PROBE_ID_NAME_DICT = {
#
#     "6118"  : "FranceIX",
#     "13842" : "mPlane",
#     "2403" : "LIP6",
#     "22341" : "LISP-Lab",
#     "3141": "Gandi"     # Gandi Massena Paris
# }

# EXPERIMENT_NAME 为实验起个名字，会作为存储和生成trace的自文件夹名称
# MEASUREMENT_ID_RECORD_FILE 为存储measurement id的.txt文档
EXPERIMENT_NAME = 'Low_reliability_verification'
GENERATE_TYPE = 'traceroute'  # 'ping' or 'traceroute'
IP_VERSION = 'v4'  # 'v6'
MEASUREMENT_ID_RECORD_FILE = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, EXPERIMENT_NAME,'{0}_{1}_{2}_measurement_ids_complete.txt'.format(EXPERIMENT_NAME,GENERATE_TYPE,IP_VERSION))
# ======================================================================================================================

def downlod_trace(measurement_id):

    requests.packages.urllib3.disable_warnings() #disable urllib3 warnings n

    # read key from auth filebv
    # if not os.path.exists(ATLAS_AUTH):
    #     raise CredentialsNotFound(authfile)
    auth = open(ATLAS_AUTH)
    key = auth.readline()[:-1]
    auth.close()

    url = "https://atlas.ripe.net/api/v2/measurements/%s/results?start=1495497600&stop=1495583999&format=json" % int(measurement_id)
    params = {"key": key}
    headers = {"Accept": "application/json"}
    results = requests.get(url=url, params=params, headers=headers)

    return results

if __name__ == "__main__":
    # 此处需要给出要下载的 measurement id 的来源，即 measurement id 在
    # $HOME/Documents/Codes/Atlas/conduct_measurements 之后存储的子文件夹名称 & 文件名
    # 这里的子文件夹名称会同时用作traces实际存储的路径子文件夹名

    with open(MEASUREMENT_ID_RECORD_FILE) as f_handler:
        for measurement_id in f_handler:
            id = measurement_id.strip()

            # 检查是否有 EXPERIMENT_NAME 的文件夹存在在os.path.join(ATLAS_TRACES, 'Produced_traces', EXPERIMENT_NAME)，不存在的话create
            try:
                os.stat(os.path.join(ATLAS_TRACES, 'Produced_traces', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION)))
            except:
                os.makedirs(os.path.join(ATLAS_TRACES, 'Produced_traces', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION)))

            file = os.path.join(ATLAS_TRACES, 'Produced_traces', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION), '{0}.json'.format(id))
            if os.path.exists(file):
                print id + ".json has already existed in" + os.path.join(ATLAS_TRACES, 'Produced_traces', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION)) + ", no need to download it again!!"
            else:
                f = open(file, 'w')
                f.write(downlod_trace(id).text)
                f.close()
