# -*- coding: utf-8 -*-
# 本script功能：
# 对 $HOME/Documents/Codes/Atlas/traces/Produced_traces 中存储的各实验下的 measurement_id.json 文件进行 .csv 转化
__author__ = 'yueli'

from config.config import *
import json
import csv
import numpy as np
import re
import math_tool as math_tool


# ==========================================Section: constant variable declaration======================================
# probe id和此probe的IP地址间的对应关系
PROBE_NAME_ID_DICT = {

    "6118": "FranceIX",
    "13842": "mPlane",
    "16958": "rmd",
    "22341": "LISP-Lab"
}

# EXPERIMENT_NAME 为要处理的实验的名字，因为它是存储和生成trace的子文件夹名称
# TARGET_CSV_TRACES 为要分析的trace的文件名
EXPERIMENT_NAME = '4_probes_to_alexa_top50'
TARGET_TRACES_PATH = os.path.join(ATLAS_TRACES, 'Produced_traces', EXPERIMENT_NAME)
PING_MEASUREMENT_ID_LIST = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, EXPERIMENT_NAME, '4_probes_to_alexa_top100_measurement_ids_ping.txt')
JSON2CSV_FILE = os.path.join(ATLAS_TRACES, 'json2csv', '{0}.csv'.format(EXPERIMENT_NAME))

# ======================================================================================================================
# 此函数负责从 PING_MEASUREMENT_ID_LIST 的txt文档中逐一读出 measurement_id，
# 并转化成路径文件名的方式返回
# input = ****.json 或是 还有一个 measurement_id 列表的 ****.txt
# output = 含有 ****.json 文件的列表，
# 即：[['/Users/yueli/Documents/Codes/Atlas/traces/Produced_traces/4_probes_to_alexa_top50/2841000.json',
# '/Users/yueli/Documents/Codes/Atlas/traces/Produced_traces/4_probes_to_alexa_top50/2841002.json']
def json_file_finder(file_string):
    # 首先对 file_string 进行判断，如果 file_string 本来就是
    # $HOME/Documents/Codes/Atlas/traces/Produced_traces/EXPERIMENT_NAME/measurement_id.json 则无需转化，
    # 直接调用 probe_dest_rtt_csv_producer
    # 如果 file_string == PING_MEASUREMENT_ID_LIST，则需打开文件继续处理
    # os.path.splitext(file_name)是用来把文件名分成文件的名字&后缀两部分，[1]即提取file extension
    if os.path.splitext(file_string)[1] in ['.json']:
        return [os.path.join(TARGET_TRACES_PATH, file_string)]
    elif os.path.splitext(file_string)[1] in ['.txt']:
        json_file_list = []
        # 开文件继续处理
        with open(file_string) as f_handler:
            for line in f_handler:
                json_file_list.append(os.path.join(ATLAS_TRACES, 'Produced_traces', EXPERIMENT_NAME, '{0}.json'.format(line.strip())))

        return json_file_list
    else:
        return "This file extension cannot be resolved"



# ======================================================================================================================
# 此函数负责把 measurement_id.json 的文件转化成1个 EXPERIMENT_NAME.csv 文件，
# 存在 $HOME/Documents/Codes/Atlas/traces/json2csv/EXPERIMENT_NAME.csv 中
# input = .json file
# output = .csv file
def probes_dest_rtt_csv_producer(target_file, stored_file):
    # 检查是否有 JSON2CSV_FILE 存在，不存在的话creat
    try:
        os.stat(os.path.join(ATLAS_TRACES, 'json2csv'))
    except:
        os.mkdir(os.path.join(ATLAS_TRACES, 'json2csv'))

    if len(target_file) == 0:
        return "There is no .json file as input"
    elif len(target_file) == 1:
        with open(target_file[0]) as f_handler:
            json_data = json.load(f_handler)
            dest = destination_finder(json_data)
            probes =  probes_finder(json_data)
            rtts_probes = rtt_finder(probes_finder(json_data), json_data)
            experiment_number = len(json_data)/len(probes)

            with open(stored_file, 'wb') as f_handler:
                a = csv.writer(f_handler, dialect='excel', delimiter=";")
                title = ['destination', 'probe']
                for i in range(experiment_number):
                    title.append('{0}_min/avg/max'.format(i+1))
                a.writerow(title)

                for probe in probes:
                    rtts = [dest, PROBE_NAME_ID_DICT[str(probe)]]
                    for rtt in rtts_probes[probe]:
                        rtts.append(rtt)
                    a.writerow(rtts)




    else: # TBD!!!!一个file list的输入时怎么办
        for target_file in target_file:


    return json_data



# ======================================================================================================================
# 此函数负责在 .json 文件中找出destination
# input = .json file
# output = [destination]
def destination_finder(json_data):
    destinations = []
    for record in json_data:
        # 因为dest_addr都是类似于 u'31.13.76.102' 的格式，用.encode()之后即可得到 '31.13.76.102'
        destinations.append(record['dst_addr'].encode())

    if len(set(destinations)) == 1:
        return "".join(list(set(destinations)))
    else:
        return "There is more than 1 destination in this .json file"

# ======================================================================================================================
# 此函数负责在 .json 文件中找出参与实验的所有 probes
# input = .json file
# output = [probes]
def probes_finder(json_data):
    probes = []
    for record in json_data:
        # 因为dest_addr都是类似于 u'31.13.76.102' 的格式，用.encode()之后即可得到 '31.13.76.102'
        probes.append(record['prb_id'])

    return list(set(probes))



# ======================================================================================================================
# 此函数负责在 .json 文件中找出每个 probe 相对应的 rtt list
"""
    input = .json file
    # output = {'probe_1': ['min'/'avg'/'max', ..., 'min'/'avg'/'max'],
                'probe_2': ['min'/'avg'/'max', ..., 'min'/'avg'/'max'],
                'probe_3': ['min'/'avg'/'max', ..., 'min'/'avg'/'max'],
                'probe_4': ['min'/'avg'/'max', ..., 'min'/'avg'/'max']}
"""
def rtt_finder(probes, json_data):
    rtt_probes_dict = {}
    for probe in probes:
        rtt_probes_dict[probe] = []

    for record in json_data:
        rtt_probes_dict[record['prb_id']].append([record['min'],record['avg'],record['max']])

    return rtt_probes_dict



if __name__ == "__main__":
    print json_file_finder(PING_MEASUREMENT_ID_LIST)
    # print json_file_finder('2841000.json')
    # print probes_dest_rtt_csv_producer(json_file_finder('2841000.json'), JSON2CSV_FILE)
    # print probes_dest_rtt_csv_producer(json_file_finder(PING_MEASUREMENT_ID_LIST), JSON2CSV_FILE)