# -*- coding: utf-8 -*-
# 本script功能：
# 为分析Atlas的 traces 而写。基于Atlas/traces/json2csv/5_probes_to_alexa_top500/ping_v4/5_probes_to_alexa_top500_avg.csv等files
# 针对不同probes ping 同一目的地，可以计算各自的平均值(mean)和方差(variance)；
# 针对不同probes traceroute 同一目的地，可以计算各自的最常用路径的跳数(hops)
__author__ = 'yueli'

from config.config import *
import math_tool as math_tool
import csv
import numpy as np

# ==========================================Section: constant variable declaration======================================

# 需要 generate ping report 还是 traceroute report，写 'PING' 或 'TRACEROUTE'
GENERATE_TYPE = 'ping'  # 'ping' or 'traceroute'
IP_VERSION = 'v4'  # 'v6'
RTT_TYPE = 'avg'    # 'avg' or 'min' or 'max'，当 GENERATE_TYPE = 'TRACEROUTE' 时忽略此变量，什么都不用更改
MES_ID_TYPE = 'txt'     # 'list' or 'txt'
MES_ID_LIST = ['2841000', '2841002', '2841003']    # 只有当 MES_ID_TYPE = 'list' 时，此参数才有用。即指定处理哪几个实验
CALCULATE_TYPE = 'mean'   # 'mean' or 'median'

# EXPERIMENT_NAME 为实验起个名字，会作为存储和生成trace的子文件夹名称
EXPERIMENT_NAME = '5_probes_to_alexa_top500'
# The .csv tables we need to base on
JSON2CSV_FILE = os.path.join(ATLAS_TRACES, 'json2csv', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION),'{0}_{1}.csv'.format(EXPERIMENT_NAME,RTT_TYPE))
# The folder path, where we will store the filtered .csv tables
FILTERED_TRACE_PATH = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION))


# ==========================================Section: functions declaration======================================
# Get the probes_list from JSON2CSV_FILE
# input = JSON2CSV_FILE
# output = ['mPlane', 'FranceIX', 'LISP-Lab']
def get_probes():
    probes_list = []
    with open(JSON2CSV_FILE) as f_handler:
        next(f_handler)
        for line in f_handler:
            probes_list.append(line.split(";")[2].strip())

    return list(set(probes_list))



# Judge whether all the probes receive RTT.
# To filter the destation in the following case, caused by probe_2:
"""
    dest    probe_1    [RTT, RTT, ..., RTT]
    dest    probe_2    [-1, -1, ..., -1]
    dest    probe_3    [RTT, RTT, ..., RTT]
"""
# input = {'FranceIX':[RTT, RTT, ..., RTT], 'mPlane':[-1, -1, ..., -1], 'LISP-Lab':[RTT, RTT, ..., RTT]}
# output = True or False
def all_probes_have_rtt(dest_probes_rtt_dict):
    result = True
    if not dest_probes_rtt_dict:
        result = False
    for probe in dest_probes_rtt_dict.keys():
        if list(set(dest_probes_rtt_dict[probe]))[0] == '-1': # 因为当整个list都为-1时,最后会得到[-1],仅有一个元素且为-1
             return False
    return result # when input dict is empty, return False



# Clean the RTT series received by all probes.
# To remove the RTT in a dedicated experiment round in the following case:
"""
input =
    dest    probe_1    [RTT, RTT, RTT, RTT, -1,  RTT]
    dest    probe_2    [RTT, -1,  RTT, RTT, RTT, RTT]
    dest    probe_3    [RTT, RTT, RTT, RTT, RTT, RTT]

output =
    dest    probe_1    [RTT, RTT, RTT, RTT]
    dest    probe_2    [RTT, RTT, RTT, RTT]
    dest    probe_3    [RTT, RTT, RTT, RTT]
"""
def clean_rtt_series(dest_probes_rtt_dict):
    index = []
    for probe in dest_probes_rtt_dict.keys():
        index.extend([i for i, x in enumerate(dest_probes_rtt_dict[probe]) if x == '-1'])

    # index.sort()    # Let the index to remove is sorted from small to big
    # reversed_index = [i for i in reversed(index)]   # Remove the element with a high index to ensure the order don' change

    clean_dest_probes_rtt_dict = {}
    for probe in dest_probes_rtt_dict.keys():
        clean_dest_probes_rtt_dict[probe] = [rtt for i, rtt in enumerate(dest_probes_rtt_dict[probe]) if i not in index]

    return clean_dest_probes_rtt_dict


# def get_clean_traces():
#     temp_probes_list = []
#     dest_probes_rtt_dict = {}
#     probes_rtt_dict = {}
#     m_id = ''
#     m_id_list = []
#     dest = ''
#     with open(JSON2CSV_FILE) as json2csv_file:
#         next(json2csv_file)
#         j=0
#         for line in json2csv_file:
#             current_m_id = line.split(";")[0].strip()
#             current_dest = line.split(";")[1].strip()
#             probe = line.split(";")[2].strip()
#
#
#
#             temp_probes_list.append(probe)
#
#             if (len(temp_probes_list) <= 3): # and (line.split(";")[1].strip() in probes_list):
#                 probes_rtt_dict[line.split(";")[2].strip()] = [i.strip() for i in line.split(";")[3:]]
#
#             elif len(temp_probes_list) > 3:
#                 if all_probes_have_rtt(probes_rtt_dict):
#                     dest_probes_rtt_dict[dest] = clean_rtt_series(probes_rtt_dict)
#                     print dest_probes_rtt_dict[dest]
#                     m_id_list.append(m_id)
#
#                 else:
#                     print "Bad dest:", dest
#                 temp_probes_list = []
#                 temp_probes_list.append(probe)
#                 probes_rtt_dict = {}
#                 probes_rtt_dict[line.split(";")[2].strip()] = [i for i in line.split(";")[3:]]
#
#             m_id = current_m_id
#             dest = current_dest
#
#     print "len(dest_probes_rtt_dict.keys())", len(dest_probes_rtt_dict.keys())
#     print "len(m_id_list):", len(m_id_list)
#     print dest_probes_rtt_dict.keys()


def get_clean_traces():
    temp_probes_list = []
    dest_probes_rtt_dict = {}
    probes_rtt_dict = {}
    m_id_list = []


    with open(JSON2CSV_FILE) as json2csv_file:
        next(json2csv_file)
        line = next(json2csv_file)
        first_line = [element.strip() for element in line.split(";")]
        dest = first_line[1]
        m_id = first_line[0]
        probe = first_line[2]

        probes_rtt_dict[probe] = first_line[3:]

        for line in json2csv_file:
            tmp_list = [element.strip() for element in line.split(";")]
            current_m_id = tmp_list[0]
            current_dest = tmp_list[1]
            probe = tmp_list[2]

            if dest != current_dest:

                if all_probes_have_rtt(probes_rtt_dict): # if probes_rtt_dict is not empty and has no RTT with all -1
                    dest_probes_rtt_dict[(m_id, dest)] = clean_rtt_series(probes_rtt_dict)
                    m_id_list.append(m_id)
                    # update m_id and dest value
                    # print "dest", dest
                    # print dest_probes_rtt_dict[dest]
                # else:
                #     print "Bad dest:", dest

                dest = current_dest
                m_id = current_m_id

                # Intialize probes_rtt_dict
                probes_rtt_dict = {}

                temp_probes_list.append(probe)

            probes_rtt_dict[probe] = tmp_list[3:]

    print "len(dest_probes_rtt_dict.keys())", len(dest_probes_rtt_dict.keys())
    print "len(m_id_list):", len(m_id_list)
    # print dest_probes_rtt_dict
    return dest_probes_rtt_dict




def generate_report(dest_probes_rtt_dict):
    try:
        os.stat(FILTERED_TRACE_PATH)
    except:
        os.makedirs(FILTERED_TRACE_PATH)

    clean_file = os.path.join(FILTERED_TRACE_PATH, '{0}_{1}_report_{2}_{3}.csv'.format(GENERATE_TYPE,IP_VERSION,RTT_TYPE,CALCULATE_TYPE))

    probes_list = get_probes()

    with open(clean_file, 'wb') as f_handler:
        csv_writter = csv.writer(f_handler, delimiter=';')
        csv_title = ['mesurement id', 'Destination']
        csv_title.extend(
            ["{0}({1} RTT) from {2}".format(CALCULATE_TYPE,RTT_TYPE, probe_name) for probe_name in probes_list])
        csv_title.extend(
            ["variance from {1}".format(RTT_TYPE, probe_name) for probe_name in probes_list])
        csv_writter.writerow(csv_title)
        for key, value in dest_probes_rtt_dict.iteritems():
            # print "value ---->", value
            csv_row = []
            current_m_id, current_dest = key[0], key[1]
            csv_row.append(current_m_id)
            csv_row.append(current_dest)
            rtts = []
            for probe in probes_list:
                rtt_tmp = [float(element) for element in value[probe]]
                rtts.append(rtt_tmp)

            csv_row.extend([np.mean(element) for element in rtts])
            csv_row.extend([np.var(element) for element in rtts])

            csv_writter.writerow(csv_row)





# ==========================================Section: main function declaration======================================

if __name__ == "__main__":
    # print get_probes()
    dict_target = {'MR_1': [2, 5, 5, -1, 3],
                   'MR_2': [1, -1, 1, 5, 2]}
    # print all_probes_have_rtt(dict_target)
    # print clean_rtt_series(dict_target)


    generate_report(get_clean_traces())
    # print all_probes_have_rtt({})


    # probes_rtt_dict = {}
    # with open(JSON2CSV_FILE) as json2csv_file:
    #     next(json2csv_file)
    #     for line in json2csv_file:
    #         if line.split(";")[0].strip() == '199.182.216.166':
    #             probes_rtt_dict[line.split(";")[1].strip()] = list(set([i.strip() for i in line.split(";")[2:]]))
    #
    #
    # if all_probes_have_rtt(probes_rtt_dict):
    #     print "Yes"
    # generate_report()




