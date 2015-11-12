# -*- coding: utf-8 -*-
# 本script功能：
# 画关于时序的各种图
__author__ = 'yueli'

from config.config import *
import analyze_traces.ping_associated_analyzer as paa
import matplotlib.pyplot as plt
import numpy as np
import re


# ==========================================Section: constant variable declaration======================================
# probe id和此probe的IP地址间的对应关系
PROBE_NAME_ID_DICT = {

    "FranceIX": "6118",
    "mPlane": "13842",
    "rmd": "16958",
    "LISP-Lab": "22341"
}

# EXPERIMENT_NAME 为要处理的实验的名字，因为它是存储和生成trace的子文件夹名称
# TARGET_CSV_TRACES 为要分析的trace的文件名
EXPERIMENT_NAME = '4_probes_to_alexa_top50'  # Needs to change
TARGET_CSV_TRACES = os.path.join(ATLAS_TRACES, 'json2csv', '{0}.csv'.format(EXPERIMENT_NAME))

# The title shown on the figure
# The full path and figure name
# 因为要从 TARGET_CSV_TRACES 中一下生成 destination 数目个 figure，所以此处是定义出要存 figure 的路径，
# 具体名称在生成图的时候按照 destination 给出
FIGURE_PATH = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'time_sequence')  # Needs to change
RTT_TYPE = 'avg'
X_LABEL = 'experiment number'
Y_LABEL = 'rtt (ms)'
FONTSIZE = 20


# ======================================================================================================================
# 此函数可以根据给出的字典画出时间序列图
# input = {'probe_1': [rtt1, rtt2, rtt3],
# 'probe_2': [rtt1, rtt2, rtt3],
#          'probe_3': [rtt1, rtt2, rtt3],
#          'probe_4': [rtt1, rtt2, rtt3]}
# output = X轴是时间，Y轴是4个probes 在每一时刻对应的rtt
def plot_time_sequence(probes_rtt_dict, target_variable):
    x_length = 0
    for key in probes_rtt_dict.keys():
        x_length = len(probes_rtt_dict[key])
        plt.plot([x+1 for x in range(x_length)], probes_rtt_dict[key], label = key)
        # plt.plot([x+1 for x in range(x_length)], probes_rtt_dict[key])

    plt.xlim(1, x_length)
    plt.xlabel(X_LABEL, fontsize = FONTSIZE)
    plt.ylabel(Y_LABEL, fontsize = FONTSIZE)
    plt.legend(loc='best')

    # 检查是否有 os.path.join(FIGURE_PATH, RTT_TYPE) 存在，不存在的话creat
    try:
        os.stat(os.path.join(FIGURE_PATH))
    except:
        os.mkdir(os.path.join(FIGURE_PATH))

    try:
        os.stat(os.path.join(FIGURE_PATH, RTT_TYPE))
    except:
        os.mkdir(os.path.join(FIGURE_PATH, RTT_TYPE))

    plt.savefig(os.path.join(FIGURE_PATH, RTT_TYPE, '{0}.eps'.format(target_variable)))
    # 每画一次图一定要 close 掉 ！！否则会不停叠加 ！！
    plt.close()


# ======================================================================================================================
# 此函数可以从 TARGET_CSV_TRACES 中提取出针对某一 destination 所对应的一个关于 rtt 的字典
# input = 要处理的文件, 要处理的 destination (string类型), min/avg/max的rtt
# output = {'probe_1': [rtt1, rtt2, rtt3],
#          'probe_2': [rtt1, rtt2, rtt3],
#          'probe_3': [rtt1, rtt2, rtt3],
#          'probe_4': [rtt1, rtt2, rtt3]}
def probes_rtt_dict_finder(target_file, target_dest, type_rtt):
    probes_rtt_dict = {}

    with open(target_file) as f_handler:
        next(f_handler)
        for line in f_handler:
            # 按照 dest 来匹配索要提取的那几行
            if line.split(';')[0] == target_dest:
                probes_rtt_dict[line.split(';')[1]] = []
                for rtt_str in line.split(';')[2:]:
                    rtt_list = eval(rtt_str)
                    if type_rtt == 'min':
                        probes_rtt_dict[line.split(';')[1]].append(rtt_list[0])
                    elif type_rtt == 'avg':
                        probes_rtt_dict[line.split(';')[1]].append(rtt_list[1])
                    elif type_rtt == 'max':
                        probes_rtt_dict[line.split(';')[1]].append(rtt_list[2])
                    else:
                        print "Wrong RTT type !!"

    return probes_rtt_dict



# ======================================================================================================================
# 此函数可以从 TARGET_CSV_TRACES 中提取出针对某一 probe 所对应的一个关于 rtt 的字典
# input = 要处理的文件, 要处理的 probe (string类型), min/avg/max的rtt
# output = {'dest_1': [rtt1, rtt2, rtt3],
#          'dest_2': [rtt1, rtt2, rtt3],
#          'dest_3': [rtt1, rtt2, rtt3],
#          'dest_4': [rtt1, rtt2, rtt3]}
def destinations_rtt_dict_finder(target_file, target_probe, type_rtt):
    destinations_rtt_dict = {}

    with open(target_file) as f_handler:
        next(f_handler)
        for line in f_handler:
            # 按照 probe 来匹配索要提取的那几行
            if line.split(';')[1] == target_probe:
                destinations_rtt_dict[line.split(';')[0]] = []
                for rtt_str in line.split(';')[2:]:
                    rtt_list = eval(rtt_str)
                    if type_rtt == 'min':
                        destinations_rtt_dict[line.split(';')[0]].append(rtt_list[0])
                    elif type_rtt == 'avg':
                        destinations_rtt_dict[line.split(';')[0]].append(rtt_list[1])
                    elif type_rtt == 'max':
                        destinations_rtt_dict[line.split(';')[0]].append(rtt_list[2])
                    else:
                        print "Wrong RTT type !!"

    return destinations_rtt_dict



# ======================================================================================================================
# 此函数把 TARGET_CSV_TRACES 中的所有 destination 提取出来放到一个 list 中
# input = TARGET_CSV_TRACES
# output = [dest_1, dest_2, dest_3, dest_4]
def get_dest_list(target_file):
    dest_list = []
    with open(target_file) as f_handler:
        next(f_handler)
        for line in f_handler:
            dest_list.append(line.split(';')[0])

    return list(set(dest_list))


# ======================================================================================================================
# 此函数把 TARGET_CSV_TRACES 中的所有 probe 提取出来放到一个 list 中
# input = TARGET_CSV_TRACES
# output = [probe_1, probe_2, probe_3, probe_4]
def get_probe_list(target_file):
    probe_list = []
    with open(target_file) as f_handler:
        next(f_handler)
        for line in f_handler:
            probe_list.append(line.split(';')[1])

    return list(set(probe_list))

if __name__ == "__main__":
    for dest in get_dest_list(TARGET_CSV_TRACES):
        plot_time_sequence(probes_rtt_dict_finder(TARGET_CSV_TRACES, dest, RTT_TYPE), dest)

    # for probe in get_probe_list(TARGET_CSV_TRACES):
    #     plot_time_sequence(destinations_rtt_dict_finder(TARGET_CSV_TRACES, probe, RTT_TYPE), probe)

