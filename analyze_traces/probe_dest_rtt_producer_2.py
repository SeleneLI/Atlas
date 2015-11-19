# -*- coding: utf-8 -*-
# 本script功能：
# 对 $HOME/Documents/Codes/Atlas/traces/Produced_traces 中存储的各实验下的 measurement_id.json 文件进行 .csv 转化
__author__ = 'yueli'

import pprint
from config.config import *
import json
import csv
from datetime import datetime
import numpy as np
import re
import math_tool as math_tool
import socket


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
PING_MEASUREMENT_ID_LIST = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, EXPERIMENT_NAME, '{0}_ping_measurement_ids_success.txt'.format(EXPERIMENT_NAME))
JSON2CSV_FILE = os.path.join(ATLAS_TRACES, 'json2csv', '{0}_song.csv'.format(EXPERIMENT_NAME))

# We define a CONSTANT variable: EXP_INTERVAL, to represent the time interval between two consecutive command
# (e.g. ping or traceroute)
EXP_INTERVAL = 600.0
# We also define a CONSTANT variable: EXP_DUREE, to represent the time span of experimentation
EXP_SPAN = 6.0*60*60
# The variable DIMENSION describe the list (containing the RTT) length
DIMENSION = EXP_SPAN/EXP_INTERVAL

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
def probes_dest_rtt_csv_producer(target_files, stored_file):
    # 检查是否有 JSON2CSV_FILE 存在，不存在的话creat
    try:
        os.stat(os.path.join(ATLAS_TRACES, 'json2csv'))
    except:
        os.mkdir(os.path.join(ATLAS_TRACES, 'json2csv'))

    if len(target_files) == 0:
        return "There is no .json file as input"

    else:
        # 打开一个 .csv file
        with open(stored_file, 'wb') as csv_handler:
            a = csv.writer(csv_handler, dialect='excel', delimiter=";")
            title = ['destination', 'probe']

            # 先用第一个 .json file 写 .csv file 的 title
            with open(target_files[0]) as json_handler:
                json_data = json.load(json_handler)
                probes =  probes_finder(json_data)
                experiment_number = len(json_data)/len(probes)

            for i in range(experiment_number):
                title.append('{0}_min/avg/max'.format(i+1))
            a.writerow(title)

            # 依次读入需要写入的 .json file，把需要的 rtt 的3个值都写入 .csv file
            for target_file in target_files:
                with open(target_file) as f_handler:
                    json_data = json.load(f_handler)
                    dest = destination_finder(json_data)
                    probes =  probes_finder(json_data)
                    rtts_probes = rtt_finder(probes_finder(json_data), json_data)
                    for key in rtts_probes.keys():
                        print rtts_probes[key]


                    for probe in probes:
                        rtts = [dest, PROBE_NAME_ID_DICT[str(probe)]]
                        for rtt in rtts_probes[probe]:
                            rtts.append("/".join([str(element) for element in rtt]))

                        a.writerow(rtts)





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
    """
        @:param probes, type of list, which contains a list of probe ID present in a given JSON file
        @:param json_data, type of JSON object, which is iterable and obtained from a input JSON file.

        @:return rtt_probes_dict, type pf dictionary, whose possible format is as follows:
                {
                'probe_1': ['min'/'avg'/'max', ..., 'min'/'avg'/'max'],
                'probe_2': ['min'/'avg'/'max', ..., 'min'/'avg'/'max'],
                'probe_3': ['min'/'avg'/'max', ..., 'min'/'avg'/'max'],
                'probe_4': ['min'/'avg'/'max', ..., 'min'/'avg'/'max']
                }

        The basic idea of this function is:
        first, we populate the output (namely, the variable rtt_probes_dict with key and its default value: [-1,-1,-1])
        then, we modified the aforementioned dictionary, more precisely the value in dictionary, according to the index,
         which is calculated by timestamp
    """
    rtt_probes_dict = {}
    # 记录每一个实验中, 每个probe的第一命令的发起时间
    ref_time_dict = {}
    for n, probe in enumerate(probes):
        # rtt_probes_dict[probe] = []
        rtt_probes_dict[probe] = [[-1, -1, -1] for x in range(int(DIMENSION))]
        ref_time_dict[json_data[n]['prb_id']] = int(json_data[n]['timestamp'])

    print ref_time_dict



    for record in json_data:
        current_time = int(record['timestamp'])
        # 如果第一个实验数据的timestamp12：00，实验间隔是10分钟，下一个实验数据是12：10，那么该数据对应的index就是1，如果是下一个
        # 实验数据点的时刻是 12：20，那么该数据的index是2，下标为1点，则永远保持为[-1.0, -1.0, -1.0]
        index = int(round((current_time - ref_time_dict[record['prb_id']])/EXP_INTERVAL))
        print "index", index
        rtt_probes_dict[record['prb_id']][index] = [record['min'], record['avg'], record['max']]
        
    return rtt_probes_dict



if __name__ == "__main__":
    # probes_dest_rtt_csv_producer(json_file_finder('2841097.json'), JSON2CSV_FILE)
    probes_dest_rtt_csv_producer(json_file_finder(PING_MEASUREMENT_ID_LIST), JSON2CSV_FILE)

    input_dict = {}
    output_dict = {}
    with open(JSON2CSV_FILE) as f_handler:
        next(f_handler)
        for line in f_handler:
            line_list = line.split(";")
            print line_list
            if line_list[0] not in input_dict.keys():
                input_dict[line_list[0]] = {}
                input_dict[line_list[0]][line_list[1]] = [float(element.split('/')[1]) for element in line_list[2:]]
            elif line_list[0] in input_dict.keys():
                input_dict[line_list[0]][line_list[1]] = [float(element.split('/')[1]) for element in line_list[2:]]

    pprint.pprint(input_dict)

    # approach 1: 将 所有的-1.0 以list平均值替代
    # 比如 有这样的字典
    # {
    #   '1.2.3.4':{
    #               'A': [4.0, 8.0, 5.0, 4.3, 7.1, 8,2, -1.0]
    #               'B': [2.0, 6.0, -1.0, 7.3, 1.1, 8,2, 8.6]
    #               'C': [2.0, 6.0, 3.3, 7.3, 1.1, 8,2, 8.6]
    #               'D': [2.0, 6.0, 11.0, 7.3, 1.1, -1.0, 8.6]
    #             }
    # }
    # 由于，坏点(也即是-1.0)的存在，如果我们把A，B，C，D对应的list看作一个矩阵的话，我们想法是把所有-1.0都用其所在行的平均值代替
    # 第一步需要先把所有的-1.0替换成0，这样不会影响计算平均值
    # 最后得到的字典应该是：
    # {
    #   '1.2.3.4':{
    #               'A': [4.0, 8.0, 5.0, 4.3, 7.1, 8,2, 0.0]
    #               'B': [2.0, 6.0, 0.0, 7.3, 1.1, 8,2, 8.6]
    #               'C': [2.0, 6.0, 3.3, 7.3, 1.1, 8,2, 8.6]
    #               'D': [2.0, 6.0, 11.0, 7.3, 1.1, 0.0, 8.6]
    #             }
    # }
    # 接下来，再继续将0替换成平均值
    # {
    #   '1.2.3.4':{
    #               'A': [4.0, 8.0, 5.0, 4.3, 7.1, 8,2, MEAN]
    #               'B': [2.0, 6.0, MEAN, 7.3, 1.1, 8,2, 8.6]
    #               'C': [2.0, 6.0, 3.3, 7.3, 1.1, 8,2, 8.6]
    #               'D': [2.0, 6.0, 11.0, 7.3, 1.1, MEAN, 8.6]
    #             }
    # }
    for dst in input_dict.keys():
        output_dict[dst] = {}
        for probe_name in input_dict[dst].keys():
            # 将输入字典中所有的 -1.0用 0.0 来替换
            input_dict[dst][probe_name] = [0.0 if x == -1.0 else x for x in input_dict[dst][probe_name]]
            # 进一步将所有的零以该行的平均值替换
            input_dict[dst][probe_name] = [np.mean(input_dict[dst][probe_name]) if x == 0.0 else x for x in input_dict[dst][probe_name]]
        # 替换完毕后，得到一个干净的字典，其形式为
        # {
        #   'A': [4.0, 8.0, 5.0, 4.3, 7.1, 8,2, MEAN]
        #   'B': [2.0, 6.0, MEAN, 7.3, 1.1, 8,2, 8.6]
        #   'C': [2.0, 6.0, 3.3, 7.3, 1.1, 8,2, 8.6]
        #   'D': [2.0, 6.0, 11.0, 7.3, 1.1, MEAN, 8.6]
        # }
        # 并对以上字典，调用correlation_calculator()计算平均值
        output_dict[dst] = math_tool.correlation_calculator(input_dict[dst])


    pprint.pprint(output_dict)
    for dst in sorted(output_dict.keys(), key=lambda item: socket.inet_aton(item)):
        print dst
        for probe_name in sorted(output_dict[dst].keys()):
            # print '%12s  %36s ' % (probe_name, output_dict[dst][probe_name])
            print '\t{:<12}\t{:<36}'.format(probe_name, output_dict[dst][probe_name])


    # approach 2: 将 所有的零 所在的列都删除
    # 比如 有这样的字典
    # {
    #   '1.2.3.4':{
    #               'A': [4.0, 8.0, 5.0, 4.3, 7.1, 8,2, -1.0]
    #               'B': [2.0, 6.0, -1.0, 7.3, 1.1, 8,2, 8.6]
    #               'C': [2.0, 6.0, 3.3, 7.3, 1.1, 8,2, 8.6]
    #               'D': [2.0, 6.0, 11.0, 7.3, 1.1, -1.0, 8.6]
    #             }
    # }
    # 由于，坏点(也即是-1.0)的存在，如果我们把A，B，C，D对应的list看作一个矩阵的话，我们想法是把含有 -1.0的列都删去
    # 最后得到的字典应该是：
    # {
    #   '1.2.3.4':{
    #               'A': [4.0, 8.0, 4.3, 7.1]
    #               'B': [2.0, 6.0, 7.3, 1.1]
    #               'C': [2.0, 6.0, 7.3, 1.1]
    #               'D': [2.0, 6.0, 7.3, 1.1]
    #             }
    # }

    output_dict_2 = {}
    with open(JSON2CSV_FILE) as f_handler:
        next(f_handler)
        for line in f_handler:
            line_list = line.split(";")
            print line_list
            if line_list[0] not in input_dict.keys():
                input_dict[line_list[0]] = {}
                input_dict[line_list[0]][line_list[1]] = [float(element.split('/')[1]) for element in line_list[2:]]
            elif line_list[0] in input_dict.keys():
                input_dict[line_list[0]][line_list[1]] = [float(element.split('/')[1]) for element in line_list[2:]]
    # pprint.pprint(input_dict)
    for dst in input_dict.keys():
        # 针对每一个 destination @Ip 做如下处理
        output_dict_2[dst] = {}
        # index_list 存放 需要被删除的元素的下标
        index_list = []
        # 以Probe name为key, 遍历一个字典，对应key的value实际上为一个含有RTT数值的list,
        # 找到所有list中元素为-1.0为index,并且存放到一个list中
        for probe_name in input_dict[dst].keys():
            tmp = [n for n, x in enumerate(input_dict[dst][probe_name]) if x == -1.0]
            index_list.extend(tmp)
            # 删除可能重复的下标
        index_list = list(set(index_list))

        for probe_name in input_dict[dst].keys():
            # 我们只保留 下标没有出现在 index_list 中的点，即删除所有坏点以及坏点所在列的其他所有点
            input_dict[dst][probe_name] = [x for i, x in enumerate(input_dict[dst][probe_name]) if i not in index_list]

        # print dst, index_list, len(input_dict[dst][probe_name])
        output_dict_2[dst] = math_tool.correlation_calculator(input_dict[dst])


    pprint.pprint(output_dict_2)
    for dst in sorted(output_dict_2.keys(), key=lambda item: socket.inet_aton(item)):
        print dst
        for probe_name in sorted(output_dict_2[dst].keys()):
            # print '%12s  %36s ' % (probe_name, output_dict[dst][probe_name])
            print '\t{:<12}\t{:<36}\t{:<36}'.format(probe_name, output_dict[dst][probe_name], output_dict_2[dst][probe_name])

