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
import pandas as pd
from collections import Counter
import re
import analyze_traces.math_tool as math_tool

mpl.rcParams['text.usetex'] = True
mpl.rcParams.update({'figure.autolayout': True})

# ==========================================Section: constant variable declaration======================================



# EXPERIMENT_NAME 为要处理的实验的名字，因为它是存储和生成trace的子文件夹名称
# TARGET_CSV_TRACES 为要分析的trace的文件名
EXPERIMENT_NAME = '4_probes_to_alexa_top50' # Needs to change
GENERATE_TYPE = 'PING'   # 'PING' or 'TRACEROUTE'
RTT_TYPE = 'avg'    # 'min' or 'avg' or 'max'
CALCULATE_TYPE = 'median' # 'mean' or 'median'

# The title shown on the figure
# FIGURE_TITLE = "Percentage of every probe's minimum RTT" # Needs to change
# The full path and figure name
FIGURE_PATH_NAME = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'rtt_geographic')
X_LABEL = 'destination'      # The name of x_label on the figure
Y_LABEL = 'RTT (ms)'       # The name of y_label on the figure
RELATIVE_KEY_A = 'LISP-Lab' # 想要比较 RTT series 与 'FranceIX' 之间差值的 probe 名称，如果相比较所有时留空，即：''
RELATIVE_KEY_REF = 'FranceIX' # 比较 RTT series 差值时的 reference 的 probe name
# ZOOM = 10.0
INTERVAL = 0.1
TYPE_HISTOGRAM = 'relative' # 'relative' or 'diff'，但尽量不要生成 diff 的，否则把 interval 变大些，否则画图会用很久时间

# ======================================================================================================================
# 此函数用于得到要处理的 csv 文件，即：TARGET_CSV_NAME
def get_target_csv_name(generate_type, rtt_type, calculate_type):
    if generate_type == 'PING':
        return os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_IPv4_report_{1}_{2}_AS.csv'.format(generate_type, rtt_type, calculate_type))
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
    print target_file
    dict_probe_cont_rtt = {'LISP-Lab':{'Europe':[],'America':[],'Asia':[]}, 'mPlane':{'Europe':[],'America':[],'Asia':[]},
                           'FranceIX':{'Europe':[],'America':[],'Asia':[]},'rmd':{'Europe':[],'America':[],'Asia':[]}}

    with open(target_file) as f_handler:
        next(f_handler)
        for line in f_handler:
            lines = line.split(";")
            print "lines:", lines
            for probe in dict_probe_cont_rtt.keys():
                dict_probe_cont_rtt[probe][lines[12].strip()].append([lines[PROBE_NAME_COLUMN_DICT[probe]]])

    # for probe in dict_probe_cont_rtt.keys():
    #     for geo in dict_probe_cont_rtt[probe].keys():
    #         print probe, geo, len(dict_probe_cont_rtt[probe][geo])
    print "get_rtt_by_geo(target_file) is called ---->", dict_probe_cont_rtt
    return dict_probe_cont_rtt



# ======================================================================================================================
# 此函数可以画出基于地理位置的 4 个 rtt 图
def plot_rtt_geo(target_file):
    # 调用 demarcate_regions(target_file) 来生成边界及 X-axis 的相关信息等
    y_axis, geo_temp, x_axis_ticks, x_axis_name = demarcate_regions(target_file)
    x_axis = range(1, geo_temp + 1)

    for probe in y_axis.keys():
        plt.plot(x_axis, y_axis[probe], label=probe)

    # print 'x_axis_ticks:', x_axis_ticks
    # print 'x_axis_name', x_axis_name
    plt.xlabel(r"\textrm{destinations}", font)
    plt.ylabel(r"\textrm{RTT (ms)}", font)
    # plt.xticks(fontsize=40, fontname="Times New Roman") # 可加此变量，让横坐标的 name 竖直显示： rotation='vertical'
    plt.xticks(x_axis_ticks, x_axis_name, fontsize=40, fontname="Times New Roman")
    plt.yticks(fontsize=40, fontname="Times New Roman")
    plt.legend(loc='best', fontsize=40)
    plt.xlim(1, geo_temp)   # 用 plot 的 plt.xlim
    # plt.xlim(0.5, geo_temp+0.5)   # 用 scatter 的 plt.xlim
    plt.ylim(0, 510)
    plt.savefig(os.path.join(FIGURE_PATH_NAME, '{0}_{1}_geo.eps'.format(EXPERIMENT_NAME, CALCULATE_TYPE)), dpi=300, transparent=True)
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
        # print "dict_geo_lisp_rtt[{0}]:".format(geo), dict_geo_lisp_rtt[geo]
        lisp_rtt_list.extend(dict_geo_lisp_rtt[geo])
        FranceIX_rtt_list.extend(dict_geo_FranceIX_rtt[geo])
        mean_rtt_list.extend(dict_geo_mean_rtt[geo])


    # 调用 demarcate_regions(target_file) 来生成边界及 X-axis 的相关信息等
    y_axis, geo_temp, x_axis_ticks, x_axis_name = demarcate_regions(target_file)
    x_axis = range(1, geo_temp + 1)
    plt.scatter(x_axis, lisp_rtt_list, c='green', s=100, label='LISP-Lab')
    # plt.plot(x_axis, lisp_rtt_list, label='LISP-Lab')
    plt.plot(x_axis, FranceIX_rtt_list, label='FraceIX')
    # plt.plot(x_axis, mean_rtt_list, c='green', label='mean')
    plt.xlabel(r"\textrm{{0}}".format(X_LABEL), font)
    plt.ylabel(r"\textrm{{0}}".format(Y_LABEL), font)
    plt.legend(loc='best', scatterpoints=1, fontsize=40)
    plt.xticks(x_axis_ticks, x_axis_name, fontsize=40, fontname="Times New Roman")
    plt.yticks(fontsize=40, fontname="Times New Roman")
    plt.xlim(1, geo_temp)   # 用 plot 的 plt.xlim
    plt.ylim(0,500)
    # plt.savefig(os.path.join(FIGURE_PATH_NAME, 'LISP_FranceIX_to_alexa_top_50_geo.eps'), dpi=300, transparent=True)
    plt.show()


    return dict_geo_lisp_rtt, dict_geo_mean_rtt


# ======================================================================================================================
# 此函数为了给不同区域划界限
# input = PING_IPv4_report_avg_AS.csv
# output = 直接在正在 plot 的图上画出 region 的边界线，并返回 y_axis(以每一个 probe 为 key 而记录的 RTT series),
#          geo_temp(x-axis 的个数)，x_axis_ticks (要标注横 region 名称的 x-axis 的坐标), x_axis_name(region 的名称)
def demarcate_regions(target_file):
    y_axis = {}
    geo_len_counter = {} # 用此 dict 记录每个geo的数据长度值，以方便在图中画出虚线以隔开每个geo
    dict_probe_cont_rtt = get_rtt_by_geo(target_file)

    for probe in dict_probe_cont_rtt.keys():
        y_axis[probe] = []
        for geo in dict_probe_cont_rtt[probe].keys():
            # print "dict_probe_cont_rtt[{0}][{1}]:".format(probe, geo), dict_probe_cont_rtt[probe][geo]
            geo_len_counter[geo] = (len(dict_probe_cont_rtt[probe][geo]))
            y_axis[probe].extend(dict_probe_cont_rtt[probe][geo])

    # print "geo_len_counter", geo_len_counter
    # 在图上按照 geo 的长度把虚线标出来
    geo_temp = 0
    geo_temp_list = []
    # 为了使 X-axis 显示不同地域名称，而把不同地域的中新坐标存入 x_axis_ticks 中，把地域名称存入 x_axis_name 中
    x_axis_ticks = []
    x_axis_name = []
    for geo in geo_len_counter.keys():
        x_axis_ticks.append(geo_temp + float(geo_len_counter[geo])/2.0)
        x_axis_name.append("{0}: {1}".format(geo, geo_len_counter[geo]))
        geo_temp = geo_temp + geo_len_counter[geo]
        # print "geo_temp =", geo_temp
        geo_temp_list.append(geo_temp)
        ##### 在某个地域边界线上画竖直线来分开不同地域
        print "geo_temp - 0.5 =", geo_temp - 0.5
        plt.vlines(geo_temp - 0.5, -1000, 1000)

    return y_axis, geo_temp, x_axis_ticks, x_axis_name




# ======================================================================================================================
# 此函数用于计算在每个 geo 中，各个 probe 的 RTT最小的百分比数
# input = PING_IPv4_report_avg_AS.csv
# output = {'Europe': {'rmd': 22.22, 'mPlane': 0.0, 'FranceIX': 77.78, 'LISP-Lab': 0.0},
#           'America': {'rmd': 11.76, 'mPlane': 23.53, 'FranceIX': 64.71, 'LISP-Lab': 0.0},
#           'Asia': {'rmd': 50.0, 'mPlane': 30.0, 'FranceIX': 0.0, 'LISP-Lab': 20.0}}
def proporation_rtt_geo_probe(target_file):
    print target_file
    min_rtt_dict = {}

    for geo in GEO_LIST:
        min_rtt_dict[geo] = {}
        index__rtt_list = []
        index_probe_name_dict = {}

        with open(target_file) as f_handler:
            for line in f_handler:
                # 通过第一行把这个 .csv 文件中存在的与 variance 相关的 probe 名称都取出来，作为 means_of_variance_dict 的 keys
                if line.split(';')[0] == 'mesurement id':
                    index_rtt = -1
                    for title in line.split(';'):
                        index_rtt = index_rtt + 1
                        # 找到含有'avg'的那几列
                        if re.match(r'{0}'.format(RTT_TYPE), title):
                            min_rtt_dict[geo][title.split(' ')[3].strip()] = 0
                            # 用 index_variance_list 来记录含有 variance 值的是哪几列
                            index__rtt_list.append(index_rtt)
                            # index 和 probe name 的对应关系
                            index_probe_name_dict[index_rtt] = title.split(' ')[3].strip()
                else:
                    if line.split(';')[12].strip() == geo:
                        min_rtt_list = []
                        # 在每行中，都需要对每个目标probe所产生的最小 RTT 依次写入可记录 min_rtt 的字典中
                        for index in index__rtt_list:
                            min_rtt_list.append(float(line.split(';')[index].strip()))
                        # 挑出4个probe ping同一dest时（即：每行中）RTT最小的那个
                        for index in math_tool.minimum_value_index_explorer(min_rtt_list):
                            print index
                            min_rtt_dict[geo][index_probe_name_dict[index + index__rtt_list[0]]] += 1

        # 如果只想知道每个 probe 所对应的 RTT 最小的次数，那就注释掉这一步；
        # 如果想知道每个 probe 所对应的 RTT 最小的次数所占百分比，那就通过这一步来计算
        # format(小数, '.2%') 表示把小数转换成对应的百分比，小数点后留2位。
        # 鉴于有可能存在几个 probe ping 同一个 dest 时 RTT 是相同的情况，所以算百分比时不能单纯的只除以 measurement 次数，
        # 而需要除以每个 probe 所对应的 RTT 最小次数的总和
        total_rtt_times = float(sum(min_rtt_dict[geo].values()))
        for key in min_rtt_dict[geo]:
            # 若只 run 本 script，可用下语句直接表示出百分比结果，e.g.: 46.00%
            # min_rtt_dict[key] = format(min_rtt_dict[key] / measurement_times, '.2%')
            # 若此函数被调用来画图，则需注释掉上面语句而用下面语句，结果仅显示百分比的数字部分而不加百分号，即：46.00
            min_rtt_dict[geo][key] = round(min_rtt_dict[geo][key] / total_rtt_times * 100, 2)

    return min_rtt_dict




# ======================================================================================================================
# 此函数与 proporation_rtt_geo_probe(target_file) 效果类似，只不过把结果 dict 的两层 key 颠倒顺序，以适应不同的画图需求
def proporation_rtt_probe_geo(target_file):

    return paa.reverse_dict_keys(proporation_rtt_geo_probe(target_file))




# ======================================================================================================================
# 此函数用来产生以 'Europe', 'America', 'Asia' 为顺序的，以 probe 为 key 的 RTT 字典
def probe_rtt_dict_by_geo(target_file):
    dict_probe_cont_rtt = get_rtt_by_geo(target_file)
    probe_rtt_dict = {}

    for probe in dict_probe_cont_rtt.keys():
        probe_rtt_dict[probe] = []
        for geo in dict_probe_cont_rtt[probe].keys():
            for i in dict_probe_cont_rtt[probe][geo]:
                probe_rtt_dict[probe].append(float(i[0]))

    return probe_rtt_dict





# ======================================================================================================================
# 此函数借用 Pandas 来画两层字典的 bar 图
# input = target_file
# 中间调用 analyze_traces.ping_associated_analyzer.proporation_rtt_geo_probe 或 proporation_rtt_probe_geo 来产生两层的字典，
# 然后用这个两层字典来画图
# output = bar
def plot_proportion_bar_geo(target_file):
    d = proporation_rtt_probe_geo(target_file)
    df = pd.DataFrame(d)

    df.plot(kind='bar')
    plt.xlabel(r"\textrm{continents of requested destinations}", fontsize=60, fontname="Times New Roman")
    # plt.ylabel(r"\textrm{proportion that one probe's RTT is the minimum}", fontsize=40, fontname="Times New Roman")
    plt.ylabel(r"\textrm{percentage (\%)}", fontsize=60, fontname="Times New Roman")

    plt.xticks(fontsize=40, fontname="Times New Roman", rotation='horizontal') # 可加此变量，让横坐标的 name 竖直显示： rotation='vertical'
    plt.yticks(fontsize=40, fontname="Times New Roman")
    plt.legend(loc='best', fontsize=40)

    plt.savefig(os.path.join(FIGURE_PATH_NAME, '{0}_proportion_{1}_bar_geo.eps'.format(EXPERIMENT_NAME, CALCULATE_TYPE)), dpi=300, transparent=True)
    plt.show()



# ======================================================================================================================
# 此函数借用 Pandas 来画两层字典的 stacked bar 图
# input = target_file
# 中间调用 analyze_traces.ping_associated_analyzer.proporation_rtt_geo_probe 或 proporation_rtt_probe_geo 来产生两层的字典，
# 然后用这个两层字典来画图
# output = stacked bar
def plot_proportion_stacked_bar_geo(target_file):
    d = proporation_rtt_probe_geo(target_file)
    df = pd.DataFrame(d)

    df.plot(kind='bar', stacked=True)
    plt.xlabel(r"\textrm{continents of requested destinations}", fontsize=40, fontname="Times New Roman")
    plt.ylabel(r"\textrm{proportion}", fontsize=40, fontname="Times New Roman")
    plt.xticks(fontsize=30, fontname="Times New Roman", rotation='horizontal') # 可加此变量，让横坐标的 name 竖直显示： rotation='vertical'
    plt.yticks(fontsize=30, fontname="Times New Roman")
    plt.legend(loc='best', fontsize=30)

    plt.savefig(os.path.join(FIGURE_PATH_NAME, '{0}_proportion_{1}_stacked_bar_geo.eps'.format(EXPERIMENT_NAME, CALCULATE_TYPE)), dpi=300, transparent=True)
    plt.show()






# ======================================================================================================================
# 此函数借用 Pandas 来画两层字典的 bar 图
# input = target_file
# 中间调用 probe_rtt_dict_by_geo(target_file) 来产生一层字典，然后用这个单层字典来画图
# output = bar
def plot_rtt_bar_by_dest_geo(target_file):
    d = probe_rtt_dict_by_geo(target_file)
    df = pd.DataFrame(d)
    print df

    df.plot(kind='bar')

    y_axis, geo_temp, x_axis_ticks, x_axis_name = demarcate_regions(target_file)

    plt.xlabel(r"\textrm{destinations}", font)
    plt.ylabel(r"\textrm{rtt(ms)}", font)
    plt.xticks(x_axis_ticks, x_axis_name, fontsize=30, fontname="Times New Roman", rotation='horizontal')
    plt.yticks(fontsize=30, fontname="Times New Roman")
    plt.legend(loc='best', fontsize=30)
    plt.ylim(0, 510)

    plt.savefig(os.path.join(FIGURE_PATH_NAME, '{0}_rtt_{1}_dest_geo.eps'.format(EXPERIMENT_NAME, CALCULATE_TYPE)), dpi=300, transparent=True)
    plt.show()





# ======================================================================================================================
# 此函数在一个 dict 中选出想要比较的 2 个 list
# input = target_dict, key_a, key_base, target_file
# output = list_a, list_base
def get_lists_from_dict(target_dict, key_a, key_base):
    list_a = []
    list_base = []

    for probe in target_dict.keys():
        if probe == key_a:
            for geo in target_dict[probe].keys():
                list_a.extend([float(i[0]) for i in target_dict[probe][geo]])
        elif probe == key_base:
            for geo in target_dict[probe].keys():
                list_base.extend([float(i[0]) for i in target_dict[probe][geo]])
        # else:
        #     print "Detected key is", probe
        #     print "No key is found neither according to key_a nor key_base !! Change a key of dictionary"

    return list_a, list_base




# ======================================================================================================================
# 此函数计算 2 lists 的各元素差值，并以 histogram 的形式画出来
# input = key_a, key_base, target_file
# 其中 target_file 完全是用来调用 demarcate_regions(demarcate_regions) 函数
# output = histogram
# !!!!!!!!!!!!!! 可用下面的 plot_diff_bar_dict_given_2_lists() 函数代替，效果更好
def plot_diff_bar_lists(list_a, list_base, target_file):
    list_diff = paa.diff_of_list_calculator(list_a, list_base)
    pd.DataFrame(list_diff).plot(kind='bar')
    plt.axhline(0, color='k')

    y_axis, geo_temp, x_axis_ticks, x_axis_name = demarcate_regions(target_file)
    plt.xlabel(r"\textrm{destinations}", font)
    plt.ylabel(r"\textrm{relative RTT (ms)}", font)
    plt.xticks(x_axis_ticks, x_axis_name, fontsize=30, fontname="Times New Roman", rotation='horizontal')   # 可加此变量，让横坐标的 name 竖直显示： rotation='vertical'
    plt.yticks(fontsize=30, fontname="Times New Roman")
    plt.legend(loc='best', fontsize=30)
    plt.xlim(-0.5, geo_temp-0.5)   # 用 plot 的 plt.xlim
    plt.ylim(min(list_diff)-10.0, max(list_diff)+10.0)
    plt.savefig(os.path.join(FIGURE_PATH_NAME, '{0}_relative_rtt_{1}_{2}_geo.eps'.format(EXPERIMENT_NAME, RELATIVE_KEY_A, RELATIVE_KEY_REF)), dpi=300, transparent=True)

    plt.show()



# ======================================================================================================================
# 此函数计算 1 dict 的各 key 间的元素差值（其中一个 key 作为 reference），并以 histogram 的形式画出来
# input = target_dict, key_a, key_ref, target_file
# 其中 key_a 表示只想画出 key_a 与 key_ref 间的 relative performance，当想画所有时将 key_a 留空，即：RELATIVE_KEY_A = ''
# target_file 完全是用来调用 demarcate_regions(demarcate_regions) 函数
# output = histogram
# 需要更改的参数为: RELATIVE_KEY_A, RELATIVE_KEY_REF
def diff_bar_dict(target_dict, key_a, key_ref):
    print "plot_diff_bar_dict(target_dict, key_a, key_ref, target_file) is called"
    diff_dict = {}
    min_temp = 0
    max_temp = 0

    if key_a != '':
        for probe in target_dict.keys():
            if (probe == key_a) and (probe != key_ref):
                list_a, list_base = get_lists_from_dict(target_dict, probe, key_ref)
                diff_dict[probe] = paa.diff_of_list_calculator(list_a, list_base)
                if min(diff_dict[probe]) < min_temp:
                    min_temp = min(diff_dict[probe])
                if max(diff_dict[probe]) > max_temp:
                    max_temp = max(diff_dict[probe])
    else:
        for probe in target_dict.keys():
            if probe != key_ref:
                list_a, list_base = get_lists_from_dict(target_dict, probe, key_ref)
                diff_dict[probe] = paa.diff_of_list_calculator(list_a, list_base)
                if min(diff_dict[probe]) < min_temp:
                    min_temp = min(diff_dict[probe])
                if max(diff_dict[probe]) > max_temp:
                    max_temp = max(diff_dict[probe])

    return diff_dict, min_temp, max_temp

def plot_diff_bar_dict(target_dict, key_a, key_ref, target_file):
    diff_dict, min_temp, max_temp = diff_bar_dict(target_dict, key_a, key_ref)
    print "min_temp =", min_temp
    print "max_temp =", max_temp
    pd.DataFrame(diff_dict).plot(kind='bar')
    plt.axhline(0, color='k')

    y_axis, geo_temp, x_axis_ticks, x_axis_name = demarcate_regions(target_file)
    plt.xlabel(r"\textrm{destinations}", font)
    if RELATIVE_KEY_A == 'LISP-Lab':
        if CALCULATE_TYPE == 'mean':
            # plt.ylabel(r"\textrm{RTT\_LISP-Lab - RTT\_FranceIX (ms)}", font)
            plt.ylabel(r"\textrm{relative mean RTT (ms)}", font)
        elif CALCULATE_TYPE == 'median':
            # plt.ylabel(r"\textrm{RTT\_LISP-Lab - RTT\_FranceIX (ms)}", font)
            plt.ylabel(r"\textrm{relative median RTT (ms)}", font)
    elif RELATIVE_KEY_A == '':
        plt.ylabel(r"\textrm{RTT\_probe - RTT\_FranceIX (ms)}", font)
    plt.xticks(x_axis_ticks, x_axis_name, fontsize=40, fontname="Times New Roman", rotation='horizontal')   # 可加此变量，让横坐标的 name 竖直显示： rotation='vertical'
    plt.yticks(fontsize=40, fontname="Times New Roman")
    plt.legend(loc=3, fontsize=40)
    plt.xlim(-0.5, geo_temp-0.5)
    plt.ylim(min(min_temp - 5.0, -150.0), max(max_temp + 5.0, 50.0))
    if key_a != '':
        plt.savefig(os.path.join(FIGURE_PATH_NAME, '{0}_diff_rtt_{1}_{2}_{3}_geo.eps'.format(EXPERIMENT_NAME, RELATIVE_KEY_A, RELATIVE_KEY_REF, CALCULATE_TYPE)), dpi=300, transparent=True)
    else:
        plt.savefig(os.path.join(FIGURE_PATH_NAME, '{0}_diff_rtt_to_{1}_{2}_geo.eps'.format(EXPERIMENT_NAME, RELATIVE_KEY_REF, CALCULATE_TYPE)), dpi=300, transparent=True)

    plt.show()

    return diff_dict



# ======================================================================================================================
# 此函数计算 1 dict 的各 key 间的元素差值（其中一个 key 作为 reference），并以 histogram 的形式画出来
# input = target_dict, key_a, key_ref, target_file
# 其中 key_a 表示只想画出 key_a 与 key_ref 间的 relative performance，当想画所有时将 key_a 留空，即：RELATIVE_KEY_A = ''
# target_file 完全是用来调用 demarcate_regions(demarcate_regions) 函数
# output = histogram
# 需要更改的参数为: RELATIVE_KEY_A, RELATIVE_KEY_REF
def relative_bar_dict(target_dict, key_a, key_ref):
    print "plot_relative_bar_dict(target_dict, key_a, key_ref, target_file) is called:"
    relative_dict = {}
    min_temp = 0
    max_temp = 0

    if key_a != '':
        for probe in target_dict.keys():
            if (probe == key_a) and (probe != key_ref):
                list_a, list_base = get_lists_from_dict(target_dict, probe, key_ref)
                relative_dict[probe] = paa.relative_performance_list_calculator(list_a, list_base)
                if min(relative_dict[probe]) < min_temp:
                    min_temp = min(relative_dict[probe])
                if max(relative_dict[probe]) > max_temp:
                    max_temp = max(relative_dict[probe])
    else:
        for probe in target_dict.keys():
            if probe != key_ref:
                list_a, list_base = get_lists_from_dict(target_dict, probe, key_ref)
                relative_dict[probe] = paa.relative_performance_list_calculator(list_a, list_base)
                if min(relative_dict[probe]) < min_temp:
                    min_temp = min(relative_dict[probe])
                if max(relative_dict[probe]) > max_temp:
                    max_temp = max(relative_dict[probe])

    return relative_dict, min_temp, max_temp
# ======================================================================================================================
def plot_relative_bar_dict(target_dict, key_a, key_ref, target_file):
    relative_dict, min_temp, max_temp = relative_bar_dict(target_dict, key_a, key_ref)

    pd.DataFrame(relative_dict).plot(kind='bar')
    plt.axhline(0, color='k', linewidth = 5)
    plt.text(4, 0.75, 'FranceIX faster', fontsize=30, fontname="Times New Roman")
    plt.text(4, -0.75, 'probe faster', fontsize=30, fontname="Times New Roman")

    y_axis, geo_temp, x_axis_ticks, x_axis_name = demarcate_regions(target_file)
    plt.xlabel(r"\textrm{destinations}", font)
    plt.ylabel(r"\textrm{relative RTT: (slower-faster)/slower}", font)
    plt.xticks(x_axis_ticks, x_axis_name, fontsize=30, fontname="Times New Roman", rotation='horizontal')   # 可加此变量，让横坐标的 name 竖直显示： rotation='vertical'
    plt.yticks([-1.0, -0.5, 0, 0.5, 1.0], [1.0, 0.5, 0, 0.5, 1.0], fontsize=30, fontname="Times New Roman")
    plt.legend(loc='best', fontsize=30)
    plt.xlim(-0.5, geo_temp-0.5)
    plt.ylim(-1.0, 1.0)
    if key_a != '':
        plt.savefig(os.path.join(FIGURE_PATH_NAME, '{0}_relative_rtt_{1}_{2}_{3}_geo.eps'.format(EXPERIMENT_NAME, RELATIVE_KEY_A, RELATIVE_KEY_REF, CALCULATE_TYPE)), dpi=300, transparent=True)
    else:
        plt.savefig(os.path.join(FIGURE_PATH_NAME, '{0}_relative_rtt_to_{1}_{2}_geo.eps'.format(EXPERIMENT_NAME, RELATIVE_KEY_REF, CALCULATE_TYPE)), dpi=300, transparent=True)

    plt.show()

    return relative_dict



# ======================================================================================================================
# 此函数画出 plot_relative_bar_dict 中各值在以 1 为 interval 时的 histogrm
# input = 1 层 dict，key 为 probe  (plot_relative_bar_dict(target_dict, key_a, key_ref, target_file) 的结果)
# output = histogram plot
def histogram_for_diff_relative(target_dict, key_a, key_ref, interval):
    processed_dict = {}
    if TYPE_HISTOGRAM == 'diff':
        processed_dict, min_temp, max_temp = diff_bar_dict(target_dict, key_a, key_ref)
    elif TYPE_HISTOGRAM == 'relative':
        processed_dict, min_temp, max_temp = relative_bar_dict(target_dict, key_a, key_ref)

    else:
        "Wrong type of histogram is given!!!!"

    processed_histogram_dict = {}
    index_min=0
    index_max =0

    for probe in processed_dict.keys():
        processed_histogram_dict[probe] = {}
        processed_histogram_dict[probe], index_min_temp, index_max_temp = math_tool.sequence_pdf_producer_2_sides([i for i in processed_dict[probe]], interval)
        if index_min_temp < index_min:
            index_min = index_min_temp
        if index_max_temp > index_max:
            index_max = index_max_temp

    return processed_histogram_dict, index_min, index_max

def plot_histogram_for_diff_relative(target_dict, key_a, key_ref, interval):
    processed_histogram_dict, index_min, index_max = histogram_for_diff_relative(target_dict, key_a, key_ref, interval)

    pd.DataFrame(processed_histogram_dict).plot(kind='bar')
    plt.axvline(x= np.abs(index_min)/INTERVAL, color='k', linewidth=3)
    plt.ylabel(r"\textrm{probability}", font)
    xticks_old = np.arange(0, (np.abs(index_min)+np.abs(index_max))/INTERVAL+1,1)
    print xticks_old
    xticks_new = [round(np.abs(i), 2) for i in np.arange(index_min , index_max+INTERVAL, INTERVAL)]
    print xticks_new
    plt.xticks(xticks_old, xticks_new, fontsize=30, fontname="Times New Roman", rotation='horizontal')
    plt.yticks(fontsize=30, fontname="Times New Roman")
    plt.legend(loc='best', fontsize=30)
    if RELATIVE_KEY_A == 'LISP-Lab':
        plt.text(np.abs(index_min)/INTERVAL/7.0, 0.25, 'LISP-Lab faster', fontsize=30, fontname="Times New Roman")
    elif RELATIVE_KEY_A == '':
        plt.text(np.abs(index_min)/INTERVAL/7.0, 0.25, 'probe faster', fontsize=30, fontname="Times New Roman")
    plt.text((np.abs(index_min)/INTERVAL+np.abs(index_max)/INTERVAL/3.0), 0.25, 'FranceIX faster', fontsize=30, fontname="Times New Roman")

    if TYPE_HISTOGRAM == 'diff':
        plt.xlabel(r"\textrm{diff RTT: (slower-faster)/slower}", font)
        if key_a != '':
            plt.savefig(os.path.join(FIGURE_PATH_NAME, '{0}_diff_rtt_{1}_{2}_{3}_histogram_geo.eps'.format(EXPERIMENT_NAME, RELATIVE_KEY_A, RELATIVE_KEY_REF, CALCULATE_TYPE)), dpi=300, transparent=True)
        else:
            plt.savefig(os.path.join(FIGURE_PATH_NAME, '{0}_diff_rtt_to_{1}_{2}_histogram_geo.eps'.format(EXPERIMENT_NAME, RELATIVE_KEY_REF, CALCULATE_TYPE)), dpi=300, transparent=True)
    elif TYPE_HISTOGRAM == 'relative':
        plt.xlabel(r"\textrm{relative RTT: (slower-faster)/slower}", font)
        if key_a != '':
            plt.savefig(os.path.join(FIGURE_PATH_NAME, '{0}_relative_rtt_{1}_{2}_{3}_histogram_geo.eps'.format(EXPERIMENT_NAME, RELATIVE_KEY_A, RELATIVE_KEY_REF, CALCULATE_TYPE)), dpi=300, transparent=True)
        else:
            plt.savefig(os.path.join(FIGURE_PATH_NAME, '{0}_relative_rtt_to_{1}_{2}_histogram_geo.eps'.format(EXPERIMENT_NAME, RELATIVE_KEY_REF, CALCULATE_TYPE)), dpi=300, transparent=True)

    plt.show()

    return processed_histogram_dict



if __name__ == "__main__":
    # print get_target_csv_name(GENERATE_TYPE, RTT_TYPE, CALCULATE_TYPE)

    # plot_rtt_geo(get_target_csv_name(GENERATE_TYPE, RTT_TYPE, CALCULATE_TYPE))

    # dict_geo_lisp_rtt, dict_geo_mean_rtt = plot_lisp_rtt_geo(get_target_csv_name(GENERATE_TYPE, RTT_TYPE, CALCULATE_TYPE))
    # print "dict_geo_lisp_rtt =", dict_geo_lisp_rtt
    # print "dict_geo_mean_rtt =", dict_geo_mean_rtt
    # print plot_bar(get_target_csv_name(GENERATE_TYPE, RTT_TYPE, CALCULATE_TYPE))
    # plot_rtt_bar_by_dest_geo(get_target_csv_name(GENERATE_TYPE, RTT_TYPE, CALCULATE_TYPE))
    # get_rtt_by_geo(get_target_csv_name(GENERATE_TYPE, RTT_TYPE, CALCULATE_TYPE))
    # plot_diff_bar()

    # list_a, list_base = get_lists_from_dict(get_rtt_by_geo(get_target_csv_name(GENERATE_TYPE, RTT_TYPE, CALCULATE_TYPE)), RELATIVE_KEY_A, RELATIVE_KEY_BASE)
    # plot_diff_bar_lists(list_a, list_base, get_target_csv_name(GENERATE_TYPE, RTT_TYPE, CALCULATE_TYPE))

    # plot_proportion_bar_geo(get_target_csv_name(GENERATE_TYPE, RTT_TYPE, CALCULATE_TYPE))
    # plot_proportion_stacked_bar_geo(get_target_csv_name(GENERATE_TYPE, RTT_TYPE, CALCULATE_TYPE))

    plot_diff_bar_dict(get_rtt_by_geo(get_target_csv_name(GENERATE_TYPE, RTT_TYPE, CALCULATE_TYPE)), RELATIVE_KEY_A, RELATIVE_KEY_REF, get_target_csv_name(GENERATE_TYPE, RTT_TYPE, CALCULATE_TYPE))
    # plot_relative_bar_dict(get_rtt_by_geo(get_target_csv_name(GENERATE_TYPE, RTT_TYPE, CALCULATE_TYPE)), RELATIVE_KEY_A, RELATIVE_KEY_REF, get_target_csv_name(GENERATE_TYPE, RTT_TYPE, CALCULATE_TYPE))
    # plot_histogram_for_diff_relative(get_rtt_by_geo(get_target_csv_name(GENERATE_TYPE, RTT_TYPE, CALCULATE_TYPE)), RELATIVE_KEY_A, RELATIVE_KEY_REF, INTERVAL)
