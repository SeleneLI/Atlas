# -*- coding: utf-8 -*-
# 本script功能：
# 基于某个例如：/Users/yueli/Documents/Codes/Atlas/figures_and_tables/4_probes_to_alexa_top50/PING_IPv4_report_avg_AS.csv 的文件，
# 画出根据地理位置变化的 rtt 图
__author__ = 'yueli'

from config.config import *
import analyze_traces.ping_associated_analyzer as paa
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

mpl.rcParams['text.usetex'] = False
mpl.rcParams.update({'figure.autolayout': True})

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
EXPERIMENT_NAME = '4_probes_to_alexa_top50' # Needs to change
GENERATE_TYPE = 'PING'   # 'PING' or 'TRACEROUTE'
RTT_TYPE = 'avg'    # 'min' or 'avg' or 'max'

# The title shown on the figure
# FIGURE_TITLE = "Percentage of every probe's minimum RTT" # Needs to change
# The full path and figure name
FIGURE_PATH_NAME = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'rtt_geographic')
X_LABEL = 'probes'      # The name of x_label on the figure
Y_LABEL = 'rtt (ms)'       # The name of y_label on the figure


# ======================================================================================================================
# 此函数用于得到要处理的 csv 文件，即：TARGET_CSV_NAME
def get_target_csv_name(generate_type, rtt_type):
    if generate_type == 'PING':
        return os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_IPv4_report_{1}_AS.csv'.format(generate_type, rtt_type))
    else:
        print "Wrong GENERATE_TYPE !! It should be 'PING' or 'TRACEROUTE'"


# ======================================================================================================================
# 此函数可以得到一个按 probe-contitent 存储的 rtt 的 dict
# input ＝ csv file
# output = {probe_1: {'Europe':[rtt_1, rtt_2, rtt_3, ...],
#                     'US':[rtt_1, rtt_2, rtt_3, ...],
#                     'Asia':[rtt_1, rtt_2, rtt_3, ...]},
#           probe_2: {'Europe':[rtt_1, rtt_2, rtt_3, ...],
#                     'US':[rtt_1, rtt_2, rtt_3, ...],
#                     'Asia':[rtt_1, rtt_2, rtt_3, ...]},
#           probe_3: {'Europe':[rtt_1, rtt_2, rtt_3, ...],
#                     'US':[rtt_1, rtt_2, rtt_3, ...],
#                     'Asia':[rtt_1, rtt_2, rtt_3, ...]},
#           probe_4: {'Europe':[rtt_1, rtt_2, rtt_3, ...],
#                     'US':[rtt_1, rtt_2, rtt_3, ...],
#                     'Asia':[rtt_1, rtt_2, rtt_3, ...]}}
# def get_rtt_by_geo(target_file):
#     dict_probe_cont_rtt = {}
#     row_indicator = 0
#
#     with open(target_file) as f_handler:
#         for line in f_handler:
#             lines = line.split(";")
#             for item in lines[2:]:
#                 if row_indicator == 0:
#                     if item.split(" ")[1] == 'RTT':
#                         dict_probe_cont_rtt[item.split(" ")[-1]] = {}
#                         row_indicator += 1
#                 else:
#                     for probe in dict_probe_cont_rtt.keys():
#                         dict_probe_cont_rtt[probe][]

# 先简单来做一个 def get_rtt_by_geo(target_file): 的版本
def get_rtt_by_geo(target_file):
    print "get_rtt_by_geo(target_file) is called"
    dict_probe_cont_rtt = {'LISP-Lab':{'Europe':[],'America':[],'Asia':[]}, 'mPlane':{'Europe':[],'America':[],'Asia':[]},
                           'FranceIX':{'Europe':[],'America':[],'Asia':[]},'rmd':{'Europe':[],'America':[],'Asia':[]}}

    with open(target_file) as f_handler:
        next(f_handler)
        for line in f_handler:
            lines = line.split(";")
            i = 0
            for probe in dict_probe_cont_rtt.keys():
                dict_probe_cont_rtt[probe][lines[12].strip()].append([lines[2+i]])
                i += 1

    # for probe in dict_probe_cont_rtt.keys():
    #     for geo in dict_probe_cont_rtt[probe].keys():
    #         print probe, geo, len(dict_probe_cont_rtt[probe][geo])
    return dict_probe_cont_rtt



# ======================================================================================================================
# 此函数可以画出基于地理位置的 4 个 rtt 图
def plot_rtt_geo(dict_probe_cont_rtt):
    x_axis = range(0,36)
    y_axis = {}
    geo_len_counter = {} # 用此 dict 记录每个geo的数据长度值，以方便在图中画出虚线以隔开每个geo

    for probe in dict_probe_cont_rtt.keys():
        y_axis[probe] = []
        for geo in dict_probe_cont_rtt[probe].keys():
            print "dict_probe_cont_rtt[{0}][{1}]:".format(probe, geo), dict_probe_cont_rtt[probe][geo]
            geo_len_counter[geo] = (len(dict_probe_cont_rtt[probe][geo]))
            y_axis[probe].extend(dict_probe_cont_rtt[probe][geo])

    print "geo_len_counter", geo_len_counter
    # 在图上按照 geo 的长度把虚线标出来
    for geo in geo_len_counter.keys():
        geo_len_counter[geo] ##### 此处需查在 X-axis 某点画直线的指令即可完成
    dict_maker = {'LISP-Lab': '*', 'mPlane': 'ˆ', "FranceIX": 'o', "rmd": '.'}

    for probe in y_axis.keys():
        plt.plot(x_axis, y_axis[probe], label=probe)

    plt.xlabel("destination", font)
    plt.ylabel("rtt (ms)", font)
    plt.xticks(fontsize=40, fontname="Times New Roman")
    plt.yticks(fontsize=40, fontname="Times New Roman")
    plt.legend(loc='best', fontsize=40)
    plt.savefig(os.path.join(FIGURE_PATH_NAME, '{0}.eps'.format(EXPERIMENT_NAME)), dpi=300, transparent=True)
    plt.show()



# ======================================================================================================================
# 此函数可以画出基于地理位置的 LISP-Lab rtt 相较于平均 rtt 的图
def plot_lisp_rtt_geo(target_file):
    dict_geo_mean_rtt = {'Europe':[],'America':[],'Asia':[]}
    dict_geo_lisp_rtt = {'Europe':[],'America':[],'Asia':[]}
    dict_geo_FranceIX_rtt = {'Europe':[],'America':[],'Asia':[]}

    with open(target_file) as f_handler:
        next(f_handler)
        for line in f_handler:
            lines = line.split(";")
            dict_geo_lisp_rtt[lines[12].strip()].append(float(lines[2]))
            dict_geo_FranceIX_rtt[lines[12].strip()].append(float(lines[4]))
            dict_geo_mean_rtt[lines[12].strip()].append(np.mean([float(lines[i]) for i in range(2,6)]))


    # Plot Part
    mean_rtt_list = []
    lisp_rtt_list = []
    FranceIX_rtt_list = []
    for geo in dict_geo_lisp_rtt:
        lisp_rtt_list.extend(dict_geo_lisp_rtt[geo])
        FranceIX_rtt_list.extend(dict_geo_FranceIX_rtt[geo])
        mean_rtt_list.extend(dict_geo_mean_rtt[geo])

    x_axis = range(1, len(lisp_rtt_list)+1)
    plt.scatter(x_axis, lisp_rtt_list, c='blue', s=50, label='LISP-Lab')
    plt.plot(x_axis, FranceIX_rtt_list, label='FraceIX')
    plt.plot(x_axis, mean_rtt_list, c='green', label='mean')
    plt.xlabel('destination', font)
    plt.ylabel('rtt (ms)', font)
    plt.legend(loc=4, scatterpoints=1, fontsize=40)
    plt.xticks(fontsize=40, fontname="Times New Roman")
    plt.yticks(fontsize=40, fontname="Times New Roman")
    plt.xlim(0,37)
    plt.ylim(0,500)
    plt.grid(True)
    plt.show()


    return dict_geo_lisp_rtt, dict_geo_mean_rtt


def proporation_rtt_geo(target_file):
    dict_probe_cont_rtt = get_rtt_by_geo(target_file)


if __name__ == "__main__":
    print get_target_csv_name(GENERATE_TYPE, RTT_TYPE)

    plot_rtt_geo(get_rtt_by_geo(get_target_csv_name(GENERATE_TYPE, RTT_TYPE)))

    # dict_geo_lisp_rtt, dict_geo_mean_rtt = plot_lisp_rtt_geo(get_target_csv_name(GENERATE_TYPE, RTT_TYPE))
    # print "dict_geo_lisp_rtt =", dict_geo_lisp_rtt
    # print "dict_geo_mean_rtt =", dict_geo_mean_rtt

