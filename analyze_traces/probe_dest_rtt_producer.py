# -*- coding: utf-8 -*-
# 本script功能：
# 对 $HOME/Documents/Codes/Atlas/traces/Produced_traces 中存储的各实验下的 measurement_id.json 文件进行 .csv 转化
__author__ = 'yueli'

from config.config import *
import json
import csv


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

# 想要生成的 .csv file 中 RTT 的type，若为空则全写进去
RTT_TYPE = 'min'    # 'min' or 'avg' or 'max' or 'all'

JSON2CSV_FILE = os.path.join(ATLAS_TRACES, 'json2csv', '{0}_{1}.csv'.format(EXPERIMENT_NAME, RTT_TYPE))

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
# 此函数负责把 measurement_id.json 的文件转化成1个 EXPERIMENT_NAME.csv 文件，每个元素包含 min/avg/max 等3个RTT值
# 存在 $HOME/Documents/Codes/Atlas/traces/json2csv/EXPERIMENT_NAME.csv 中
# input = .json file
# output = .csv file
def probes_dest_rtts_csv_producer(target_files, stored_file, rtt_type):
    # 检查是否有 JSON2CSV_FILE 存在，不存在的话creat
    try:
        os.stat(os.path.join(ATLAS_TRACES, 'json2csv'))
    except:
        os.makedirs(os.path.join(ATLAS_TRACES, 'json2csv'))

    dict_rtt = {'min': 0, 'avg': 1, 'max': 2}

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
                        print "rtts_probes[key]:", rtts_probes[key]


                    for probe in probes:
                        rtts = [dest, PROBE_NAME_ID_DICT[str(probe)]]
                        for rtt in rtts_probes[probe]:
                            if rtt_type == 'all':
                                rtts.append("/".join([str(element) for element in rtt]))
                            else:
                                rtts.append(rtt[dict_rtt[rtt_type]])

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
    # probes_dest_rtts_csv_producer(json_file_finder('2841097.json'), JSON2CSV_FILE, RTT_TYPE)
    probes_dest_rtts_csv_producer(json_file_finder(PING_MEASUREMENT_ID_LIST), JSON2CSV_FILE, RTT_TYPE)