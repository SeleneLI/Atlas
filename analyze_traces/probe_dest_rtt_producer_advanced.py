# -*- coding: utf-8 -*-
# 本script功能：
# 对 $HOME/Documents/Codes/Atlas/traces/Produced_traces 中存储的各实验下的 measurement_id.json 文件进行 .csv 转化
# 相较于 probe_dest_rtt_producer.py,此script的不同之处在于:在进行大型实验时,并不是每一次所有probe都有响应,所以只能动态添加RTT等数值
__author__ = 'yueli'

from config.config import *
import ping_associated_analyzer as paa
import pandas as pd
import numpy as np


# ==========================================Section: constant variable declaration======================================

# EXPERIMENT_NAME 为要处理的实验的名字，因为它是存储和生成trace的子文件夹名称
# TARGET_CSV_TRACES 为要分析的trace的文件名
EXPERIMENT_NAME = '5_probes_to_alexa_top510'
GENERATE_TYPE = 'ping'  # 'ping' or 'traceroute'
IP_VERSION = 'v4'  # 'v6'
TARGET_TRACES_PATH = os.path.join(ATLAS_TRACES, 'Produced_traces', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION))
PING_MEASUREMENT_ID_LIST = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, EXPERIMENT_NAME, '{0}_{1}_{2}_measurement_ids_complete.txt'.format(EXPERIMENT_NAME,GENERATE_TYPE,IP_VERSION))

# 想要生成的 .csv file 中 RTT 的type，若为空则全写进去
RTT_TYPE = 'max'    # 'min' or 'avg' or 'max' or 'all'

JSON2CSV_FILE = os.path.join(ATLAS_TRACES, 'json2csv', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION), 'completed_traces', '{0}_{1}_completed.csv'.format(EXPERIMENT_NAME, RTT_TYPE))
JSON2CSV_FILE_FILTERED = os.path.join(ATLAS_TRACES, 'json2csv', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION), '{0}_{1}.csv'.format(EXPERIMENT_NAME, RTT_TYPE))


# We define a CONSTANT variable: EXP_INTERVAL, to represent the time interval between two consecutive command
# (e.g. ping or traceroute)
EXP_INTERVAL = 1800.0
# We also define a CONSTANT variable: EXP_DUREE, to represent the time span of experimentation
EXP_SPAN = (15*24)*60*60.0
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
        m_id_list = []
        # 开文件继续处理
        with open(file_string) as f_handler:
            for line in f_handler:
                json_file_list.append(os.path.join(ATLAS_TRACES, 'Produced_traces', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION), '{0}.json'.format(line.strip())))
                m_id_list.append(line.strip())

        return m_id_list, json_file_list
    else:
        return "This file extension cannot be resolved"



# ======================================================================================================================
# 此函数负责把 measurement_id.json 的文件转化成1个 EXPERIMENT_NAME.csv 文件，每个元素包含 min/avg/max 等3个RTT值
# 存在 $HOME/Documents/Codes/Atlas/traces/json2csv/EXPERIMENT_NAME.csv 中
# input = .json file
# output = .csv file
def probes_dest_rtts_csv_producer(m_id_list, target_files, stored_file, rtt_type):
    # 检查是否有 JSON2CSV_FILE 存在，不存在的话creat
    try:
        os.stat(os.path.join(ATLAS_TRACES, 'json2csv', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION), 'completed_traces'))
    except:
        os.makedirs(os.path.join(ATLAS_TRACES, 'json2csv', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION), 'completed_traces'))

    dict_rtt = {'min': 0, 'avg': 1, 'max': 2}

    if len(target_files) == 0:
        return "There is no .json file as input"

    else:
        # 打开一个 .csv file
        with open(stored_file, 'wb') as csv_handler:
            a = csv.writer(csv_handler, dialect='excel', delimiter=";")
            title = ['measurement_id', 'destination', 'probe']

            # 先用第一个 .json file 写 .csv file 的 title
            with open(target_files[0]) as json_handler:
                json_data = json.load(json_handler)
                probes =  probes_finder(json_data)
                experiment_number = len(json_data)/(len(probes)-2)

            for i in range(int(DIMENSION)):
                if RTT_TYPE == 'all':
                    title.append('{0}_min/avg/max'.format(i+1))
                else:
                    title.append('{0}_{1}'.format((i + 1), RTT_TYPE))
            a.writerow(title)

            i = -1
            # 依次读入需要写入的 .json file，把需要的 rtt 的3个值都写入 .csv file
            for target_file in target_files:
                i += 1
                with open(target_file) as f_handler:
                    json_data = json.load(f_handler)
                    dest = destination_finder(json_data)
                    probes =  probes_finder(json_data)
                    rtts_probes = rtt_finder(probes_finder(json_data), json_data)
                    # for key in rtts_probes.keys():
                    #     print "rtts_probes[{0}]:".format(key), rtts_probes[key]


                    for probe in probes:
                        rtts = [m_id_list[i], dest, PROBE_ID_NAME_DICT[str(probe)]]
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
    first_probes = []
    fake_time = 0
    for n, probe in enumerate(probes):
        rtt_probes_dict[probe] = [[-1, -1, -1] for x in range(int(DIMENSION))]
        if json_data[n]['prb_id'] not in first_probes:
            ref_time_dict[json_data[n]['prb_id']] = int(json_data[n]['timestamp'])
            first_probes.append(json_data[n]['prb_id'])
            fake_time = int(json_data[n]['timestamp'])

    first_no_probes = [i for i in probes if i not in first_probes]
    for no_probe in first_no_probes:
        ref_time_dict[no_probe] = fake_time




    for record in json_data:
        current_time = int(record['timestamp'])
        # 如果第一个实验数据的timestamp12：00，实验间隔是10分钟，下一个实验数据是12：10，那么该数据对应的index就是1，如果是下一个
        # 实验数据点的时刻是 12：20，那么该数据的index是2，下标为1点，则永远保持为[-1.0, -1.0, -1.0]
        index = int(round((current_time - ref_time_dict[record['prb_id']])/EXP_INTERVAL))
        rtt_probes_dict[record['prb_id']][index] = [record['min'], record['avg'], record['max']]
        
    return rtt_probes_dict


# # 由于一些 probes 在实验期间是没有响应的,所以在最后计算时直接将它们剔除掉
# # 但是针对 5_probes_to_alexa_top500 来说因为 home & LIP6 回复始终是 -1, 所以可以直接剔除掉含有这2个probe的所有信息
# # 不过是快捷之举,并不普适,所以又写了一个同名 method
# # input = 5_probes_to_alexa_top500_all.csv
# # output = 5_probes_to_alexa_top500_all_filtered.csv
# def filtered_probes_rtt_producer(original_file, filtered_file):
#     # 检查是否有 JSON2CSV_FILE_FILTERED 存在，不存在的话create
#     try:
#         os.stat(os.path.join(ATLAS_TRACES, 'json2csv', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION)))
#     except:
#         os.makedirs(os.path.join(ATLAS_TRACES, 'json2csv', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION)))
#
#     # Open a file to write down
#     with open(filtered_file, 'wb') as csv_handler:
#         a = csv.writer(csv_handler, dialect='excel', delimiter=";")
#
#         # Open a file to read
#         with open(original_file) as f_handler:
#             for line in f_handler:
#                 if line.split(';')[1] == 'destination':
#                     a.writerow([i.strip() for i in line.split(';')])
#                 # 通过第一行把这个 .csv 文件中存在的与 variance 相关的 probe 名称都取出来，作为 means_of_variance_dict 的 keys
#                 elif line.split(';')[2] not in ['home', 'LIP6', 'probe']:
#                     a.writerow([i.strip() for i in line.split(';')])


# 由于一些 probes 在实验期间是没有响应的,所以在最后计算时直接将与它一样 dest 的所有 probes 信息都剔除掉
# input = 5_probes_to_alexa_top500_all.csv
# output = 5_probes_to_alexa_top500_all_filtered.csv
def filtered_probes_rtt_producer(original_file, filtered_file):
    # 检查是否有 JSON2CSV_FILE_FILTERED 存在，不存在的话create
    try:
        os.stat(os.path.join(ATLAS_TRACES, 'json2csv', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION)))
    except:
        os.makedirs(os.path.join(ATLAS_TRACES, 'json2csv', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION)))

    df = pd.read_csv(original_file, sep=";").dropna(axis=1, how='all')
    # df1 = df.iloc[:, 0:3]
    # df_min_rtt = df.iloc[:, 3:].apply(lambda x: x.str.split("/", expand=True)[0]).astype(float)
    df_min_rtt = df.iloc[:, 3:]
    # df_min = pd.concat([df1, df_min_rtt], axis=1)
    drop_measure_id = set(df[df_min_rtt.apply(pd.Series.nunique, axis=1) == 1].iloc[:, 0].values)
    # print drop_measure_id
    # print df_min['measurement_id'].isin(drop_measure_id)
    # print df_min[~df_min['measurement_id'].isin(drop_measure_id)]
    df_new = df[~df['measurement_id'].isin(drop_measure_id)]

    df_new.to_csv(filtered_file, index=False, header=True, sep=';', encoding='utf-8')








if __name__ == "__main__":
    # probes_dest_rtts_csv_producer(json_file_finder('6963471.json'), JSON2CSV_FILE, RTT_TYPE)

    # m_id_list, json_file = json_file_finder(PING_MEASUREMENT_ID_LIST)
    # probes_dest_rtts_csv_producer(m_id_list, json_file, JSON2CSV_FILE, RTT_TYPE)

    filtered_probes_rtt_producer(JSON2CSV_FILE, JSON2CSV_FILE_FILTERED)