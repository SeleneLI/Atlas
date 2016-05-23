# -*- coding: utf-8 -*-
# 本script功能：
# 画关于时序的各种图
__author__ = 'yueli'

from config.config import *
import analyze_traces.ping_associated_analyzer as paa
import matplotlib.pyplot as plt
import numpy as np
import re
import matplotlib as mpl
import pandas as pd

mpl.rcParams['text.usetex'] = True
mpl.rcParams.update({'figure.autolayout': True})


# ==========================================Section: constant variable declaration======================================
# EXPERIMENT_NAME 为要处理的实验的名字，因为它是存储和生成trace的子文件夹名称
# TARGET_CSV_TRACES 为要分析的trace的文件名
EXPERIMENT_NAME = '4_probes_to_alexa_top50'  # Needs to change
TARGET_CSV_TRACES = os.path.join(ATLAS_TRACES, 'json2csv', '{0}.csv'.format(EXPERIMENT_NAME))
RTT_TYPE_TARGET = 'avg'
TARGET_CSV_TRACES_CDF = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'PING_IPv4_report_{0}.csv'.format(RTT_TYPE_TARGET))
FILE_PATH_CDF_FIGURE = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'CDF_figures')
FILE_PATH_CSV_COMP = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'comp_RTTs_between_probes_{0}.eps'.format(RTT_TYPE_TARGET))

# The title shown on the figure
# The full path and figure name
# 因为要从 TARGET_CSV_TRACES 中一下生成 destination 数目个 figure，所以此处是定义出要存 figure 的路径，
# 具体名称在生成图的时候按照 destination 给出
FIGURE_PATH = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'time_sequence')  # Needs to change
RTT_TYPE_FIGURE = 'avg'    # 'min' or 'avg' or 'max'
X_LABEL = 'experiment number'
Y_LABEL = 'rtt (ms)'

# Plot 时的参考变量
# 如果是 n 个 probes 对同一 destination 而产生的与 destination 数量一致的 figure 数，输入：'dest'
# 如果是 1 个 probe 对所有 destinations 而产生的与 probes 数量一致的 figure 数，输入：'probe'
GENERATE_VARIABLE = 'dest'  # 'dest' or 'probe'

# ======================================================================================================================
# 此函数可以根据给出的字典画出时间序列图
# input = {'probe_1': [rtt1, rtt2, rtt3],
# 'probe_2': [rtt1, rtt2, rtt3],
#          'probe_3': [rtt1, rtt2, rtt3],
#          'probe_4': [rtt1, rtt2, rtt3]}
# output = X轴是时间，Y轴是4个probes 在每一时刻对应的rtt
def plot_time_sequence(probes_rtt_dict, target_variable, generate_variable):
    x_length = 0
    for key in probes_rtt_dict.keys():
        x_length = len(probes_rtt_dict[key])
        plt.plot([x+1 for x in range(x_length)], probes_rtt_dict[key], label = key)
        # plt.plot([x+1 for x in range(x_length)], probes_rtt_dict[key])

    plt.xlim(1, x_length)
    plt.xlabel(X_LABEL, font)
    plt.ylabel(Y_LABEL, font)
    if generate_variable == 'dest':
        plt.legend(loc='best', fontsize=40)

    # 检查是否有 os.path.join(FIGURE_PATH, RTT_TYPE) 存在，不存在的话creat
    try:
        os.stat(os.path.join(FIGURE_PATH, RTT_TYPE_FIGURE))
    except:
        os.makedirs(os.path.join(FIGURE_PATH, RTT_TYPE_FIGURE))

    plt.savefig(os.path.join(FIGURE_PATH, RTT_TYPE_FIGURE, '{0}.eps'.format(target_variable)), dpi=300)
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
                        print "Wrong RTT type !! It should be 'min', 'avg' or 'max'"

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
                        print "Wrong RTT type !! It should be 'min', 'avg' or 'max'"

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



# ======================================================================================================================
# 此函数可以画出 CDF figure
# input = 想要生成 CDF 的 file
# output ＝ 存储在相应路径下的一张图
def plot_cdf_from_file(target_file, saving_path_name):
    cdf_dict = paa.cdf_for_dict(target_file)
    for probe_key in cdf_dict.keys():
        x_axis = range(0, len(paa.cdf_for_dict(target_file)[probe_key]))
        plt.plot(x_axis, paa.cdf_for_dict(target_file)[probe_key], label = probe_key, linewidth = 5)
        print probe_key, ":", x_axis
        print "cdf =", paa.cdf_for_dict(target_file)[probe_key]

    # plt.gcf().set_size_inches(9,7)
    plt.xlabel(r"\textrm{RTT (ms)}", font)
    plt.ylabel(r"\textrm{cdf (\%)}", font)
    plt.xticks(fontsize=40, fontname = 'Times New Roman')
    plt.yticks(fontsize=40, fontname = 'Times New Roman')
    plt.legend(loc='best', fontsize=40)
    plt.grid(True)
    # plt.savefig(os.path.join(FILE_PATH_CDF_FIGURE, 'CDF_RTT_{0}.eps'.format(RTT_TYPE_TARGET)), dpi=300, transparent=True)
    plt.show()

# 此函数用做画出 probes 对不同 destinations 产生的平均 RTT 的比较情况，可以 anchor 为参考目标得出各个probe与其的差值
# input = target_file
# output = 有 probes 条曲线的一张图
def comp_means_rtt_dests(target_file, saving_path_name):
    rtt_means_dict = {}
    probe_int_dict = {}
    probe_color_dict = {'mPlane': 'red',
                        'LISP-Lab': 'blue',
                        'rmd': 'green',
                        'FranceIX': 'black'}

    with open(target_file) as f_handler:
        count = 0
        for line in f_handler:
            lines = line.split(";")
            if lines[0] == 'mesurement id':
                    for name in lines:
                        if count > 1:
                            if name.split(" ")[0] != 'variance':
                                rtt_means_dict[name.split(" ")[-1]] = []
                                probe_int_dict[name.split(" ")[-1]] = count
                                count += 1
                        else:
                            count += 1
            else:
                for key in rtt_means_dict.keys():
                    rtt_means_dict[key].append(lines[probe_int_dict[key]])

    for key in rtt_means_dict.keys():
        x_axis = range(0, len(rtt_means_dict[key]))
        plt.plot(x_axis, rtt_means_dict[key], label = key, linewidth = 1)
        # plt.scatter(x_axis, rtt_means_dict[key], label = key, c=probe_color_dict[key])

    # plt.gcf().set_size_inches(8,6)
    plt.xlabel(r'destinations', font)
    plt.ylabel(r'rtt (ms)', font)
    plt.xticks(fontsize=40, fontname = 'Times New Roman')
    plt.yticks(fontsize=40, fontname = 'Times New Roman')
    plt.legend(loc='best', fontsize=40)
    plt.grid(True)
    # plt.savefig(saving_path_name, dpi=300, transparent=True)
    plt.show()



# ======================================================================================================================
# 此函数可以画出 CDF figure
# input = 想要生成 CDF 的 dict
# output ＝ 存储在相应路径下的一张图
def plot_cdf_from_dict(dict_to_plot):
    data = pd.DataFrame(dict_to_plot)
    print data
    data.plot(linewidth = 5)
    plt.xlabel(r"\textrm{robustness (\%)}", font)
    plt.ylabel(r"\textrm{cdf}", font)
    plt.xticks(fontsize=30, fontname="Times New Roman")
    plt.yticks(fontsize=30, fontname="Times New Roman")
    plt.legend(loc='best', fontsize=30)
    plt.savefig(os.path.join(FILE_PATH_CDF_FIGURE, 'CDF_robustness_{0}.eps'.format(RTT_TYPE_TARGET)), dpi=300, transparent=True)
    plt.show()

    return pd.DataFrame(dict_to_plot)




if __name__ == "__main__":
    # 检查是否有 os.path.join(TARGET_HISTOGRAM_PATH) 存在，不存在的话 create
    try:
        os.stat(os.path.join(FILE_PATH_CDF_FIGURE))
    except:
        os.makedirs(os.path.join(FILE_PATH_CDF_FIGURE))
    # if GENERATE_VARIABLE == 'dest':
    #     for dest in get_dest_list(TARGET_CSV_TRACES):
    #         plot_time_sequence(probes_rtt_dict_finder(TARGET_CSV_TRACES, dest, RTT_TYPE), dest, GENERATE_VARIABLE)
    # elif GENERATE_VARIABLE == 'probe':
    #     for probe in get_probe_list(TARGET_CSV_TRACES):
    #         plot_time_sequence(destinations_rtt_dict_finder(TARGET_CSV_TRACES, probe, RTT_TYPE), probe, GENERATE_VARIABLE)

    #comp_means_rtt_dests(TARGET_CSV_TRACES_CDF, FILE_PATH_CSV_COMP)

    # plot_cdf_from_file(TARGET_CSV_TRACES_CDF, FILE_PATH_CDF_FIGURE)
    plot_cdf_from_dict(paa.all_probe_robustness_cdf_calculator())

