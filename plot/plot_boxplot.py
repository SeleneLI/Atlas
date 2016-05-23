# -*- coding: utf-8 -*-
# 本script功能：
# 基于某个例如：/Users/yueli/Documents/Codes/Atlas/traces/json2csv/4_probes_to_alexa_top50.csv 的文件，
# 画出根据地理位置变化的 LISP-Lab RTT 与 reference object(FranceIX) RTT 的 box 图
# 此文本只需改第 45 行的 PROBE 即可
__author__ = 'yueli'

from config.config import *
import numpy as np
import plot_rtt_geo as prg
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['text.usetex'] = True
mpl.rcParams.update({'figure.autolayout': True})

# ==========================================Section: constant variable declaration======================================
# EXPERIMENT_NAME 为要处理的实验的名字，因为它是存储和生成trace的子文件夹名称
# TARGET_CSV_TRACES 为要分析的trace的文件名
EXPERIMENT_NAME = '4_probes_to_alexa_top50' # Needs to change
GENERATE_TYPE = 'PING'   # 'PING' or 'TRACEROUTE'
RTT_TYPE = 'avg'    # 'min' or 'avg' or 'max'

# The title shown on the figure
# FIGURE_TITLE = "Percentage of every probe's minimum RTT" # Needs to change
# The full path and figure name
FIGURE_PATH_NAME = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'boxplot')
# 要产生的 probe 的名称
PROBE = 'FranceIX'    # 'LISP-Lab', 'mPlane', 'rmd', FranceIX


# ======================================================================================================================
# 此函数用于得到要处理的 csv 文件，即：TARGET_CSV_NAME
def get_target_csv_name(generate_type):
    if generate_type == 'PING':
        return os.path.join(ATLAS_TRACES, 'json2csv', '{0}.csv'.format(EXPERIMENT_NAME))
    else:
        print "Wrong GENERATE_TYPE !! It should be 'PING' or 'TRACEROUTE'"



# ======================================================================================================================
# 此函数可以从 4_probes_to_alexa_top50.csv 的文件中把所有的RTT按RTT_TYPE读出
# 并且把含有 -1 的元素都去掉，4个probes针对这个 dest 的此时刻 RTT 都去掉
# input = null (但实际为 4_probes_to_alexa_top50.csv)
# output = dict_rtt_series{'probe_1': {'dest_1': [RTT_1, RTT_2, ...]}, {'dest_1': [RTT_1, RTT_2, ...]}, ...,
#                          'probe_2': {'dest_1': [RTT_1, RTT_2, ...]}, {'dest_1': [RTT_1, RTT_2, ...]}, ...,
#                          'probe_3': {'dest_1': [RTT_1, RTT_2, ...]}, {'dest_1': [RTT_1, RTT_2, ...]}, ...,
#                          'probe_4': {'dest_1': [RTT_1, RTT_2, ...]}, {'dest_1': [RTT_1, RTT_2, ...]}, ...,
#                          }
def pick_up_rtt_series():
    dict_rtt_series_probe_dest = {}
    with open(get_target_csv_name(GENERATE_TYPE)) as f_handler:
        next(f_handler)
        for line in f_handler:
            lines = line.split(";")
            # 先判断需要的 probes 和 dest 是否都已在 keys 中：
            if lines[1] not in dict_rtt_series_probe_dest.keys():
                dict_rtt_series_probe_dest[lines[1]] = {}
                dict_rtt_series_probe_dest[lines[1]][lines[0]] = []
                dict_rtt_series_probe_dest[lines[1]][lines[0]].extend([float(i.split('/')[RTT_TYPE_ID_DICT[RTT_TYPE]]) for i in lines[2:]])
            else:
                dict_rtt_series_probe_dest[lines[1]][lines[0]] = []
                dict_rtt_series_probe_dest[lines[1]][lines[0]].extend([float(i.split('/')[RTT_TYPE_ID_DICT[RTT_TYPE]]) for i in lines[2:]])

    # 由于一些 RTT series 中含有 -1，所以需要把其余几个 probes 对应此dest的这一时刻点的RTT也删除掉
    # 先找出能够记录有 -1 的 dest 和 index
    non_valid_index_dict = {}
    for probe in dict_rtt_series_probe_dest.keys():
        for dest in dict_rtt_series_probe_dest[probe].keys():
            if -1.0 in dict_rtt_series_probe_dest[probe][dest]:
                if dest not in non_valid_index_dict.keys():
                    non_valid_index_dict[dest] = []
                    # 下句 extend 中内容是找出 list 中元素等于 -1.0 的所有坐标
                    non_valid_index_dict[dest].extend([i for i,val in enumerate(dict_rtt_series_probe_dest[probe][dest]) if val== -1.0])
                else:
                    non_valid_index_dict[dest].extend([i for i,val in enumerate(dict_rtt_series_probe_dest[probe][dest]) if val== -1.0])
    # print non_valid_index_dict
    # 开始 remove
    for dest in non_valid_index_dict.keys():
        for probe in dict_rtt_series_probe_dest.keys():
            dict_rtt_series_probe_dest[probe][dest] = np.delete(dict_rtt_series_probe_dest[probe][dest],non_valid_index_dict[dest]).tolist()
    return dict_rtt_series_probe_dest


# ======================================================================================================================
# 此函数可从 pick_up_rtt_series() 的 output 中选取出想要进行后续处理的某一 probe 的所有 dest 的 RTT
# input = pick_up_rtt_series() 的返回值
# output = probe_rtt_series: {'dest_1': [RTT_1, RTT_2, ...], 'dest_2': [RTT_1, RTT_2, ...], ...}
def pick_up_rtt_series_probe(probe):
    # print pick_up_rtt_series()[probe]
    return pick_up_rtt_series()[probe]

# ======================================================================================================================
# 此函数对 boxplot 进行预处理，即计算所有要在 boxplot 里用到的参数
# input = pick_up_rtt_series_probe(probe)
# output = [dest1_processed_data, dest2_processed_data, dest3_processed_data]
def calculate_parameters_boxplot(dict_rtt_series_probe):
    processed_data_list = []
    dest_list = []
    for dest in dict_rtt_series_probe:
        rtt_series = dict_rtt_series_probe[dest]
        median = np.ones(len(rtt_series)) * np.median(rtt_series) #sorted(rtt_series)[len(rtt_series)/2]
        box_low = np.ones(len(rtt_series)) * (np.mean(rtt_series) - np.std(rtt_series))
        box_high = np.ones(len(rtt_series)) * (np.mean(rtt_series) + np.std(rtt_series))
        data = np.concatenate((rtt_series, median, box_low, box_high), 0)
        dest_list.append(dest)
        processed_data_list.append(data)
    # print processed_data
    return dest_list, processed_data_list


# ======================================================================================================================
# 此函数可以画出基于地理位置的 LISP-Lab RTT 与 reference object(FranceIX) RTT 的 box 图
# input = probe
# output = a boxplot
def plot_boxplot(probe):
    dest_list, processed_data_list = calculate_parameters_boxplot(pick_up_rtt_series_probe(probe))
    plt.boxplot(processed_data_list)
    plt.xlabel(r"\textrm{destinations}", font)
    plt.ylabel(r"\textrm{RTT (ms)}", font)
    plt.xticks(range(1,37), dest_list, fontsize=20, fontname="Times New Roman", rotation='vertical')
    plt.yticks(fontsize=40, fontname="Times New Roman")
    # 为了 4 张图方便比较，把 y 轴高度设为一样的
    plt.ylim(0, 600)

    # 检查是否有 os.path.join(FIGURE_PATH, RTT_TYPE) 存在，不存在的话creat
    try:
        os.stat(os.path.join(FIGURE_PATH_NAME))
    except:
        os.makedirs(os.path.join(FIGURE_PATH_NAME))
    plt.savefig(os.path.join(FIGURE_PATH_NAME, '{0}_to_alexa_top_50_box.eps'.format(probe)), dpi=300, transparent=True)
    plt.show()


if __name__ == "__main__":
    # print pick_up_rtt_series()
    plot_boxplot(PROBE)


