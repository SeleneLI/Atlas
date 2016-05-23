# -*- coding: utf-8 -*-
# 本script功能：
# 画关于 Histogram 的各种图
__author__ = 'yueli'

from config.config import *
import analyze_traces.ping_associated_analyzer as paa
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import analyze_traces.math_tool as mt
import plot.plot_rtt_geo as prg

mpl.rcParams['text.usetex'] = True
mpl.rcParams.update({'figure.autolayout': True})



# ==========================================Section: constant variable declaration======================================
# EXPERIMENT_NAME 为要处理的实验的名字，因为它是存储和生成trace的子文件夹名称
# TARGET_CSV_TRACES 为要分析的trace的文件名
EXPERIMENT_NAME = '4_probes_to_alexa_top50' # Needs to change
GENERATE_TYPE = 'PING'   # 'PING' or 'TRACEROUTE'
RTT_TYPE = 'avg'    # 'min' or 'avg' or 'max'
CALCULATE_TYPE = 'mean' # 'mean' or 'median'
# TARGET_CSV_TRACES = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_IPv4_report_{1}.csv'.format(GENERATE_TYPE, RTT_TYPE))
JSON2CSV_FILE = os.path.join(ATLAS_TRACES, 'json2csv', '{0}.csv'.format(EXPERIMENT_NAME))

# The title shown on the figure
# FIGURE_TITLE = "Percentage of every probe's minimum RTT" # Needs to change
# The full path and figure name
FIGURE_PATH_NAME = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'histogram')
X_LABEL = 'RTT(ms)'      # The name of x_label on the figure
Y_LABEL = 'pdf'       # The name of y_label on the figure
PLOT_PROBE = 'FranceIX' # 'LISP-Lab', 'mPlane', 'rmd', 'FranceIX'
INTERVAL = 1 # by default is 1ms
TARGET_HISTOGRAM_PATH = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'histogram', 'RTT_series_histogram',
                                          '{0}'.format(PLOT_PROBE), '{0}'.format(RTT_TYPE))


# ======================================================================================================================
# 此函数用于得到要处理的 csv 文件，即：TARGET_CSV_NAME
def get_target_csv_name(generate_type):
    if generate_type == 'PING':
        return os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_IPv4_report_{1}_{2}.csv'.format(GENERATE_TYPE, RTT_TYPE, CALCULATE_TYPE))
    elif generate_type == 'TRACEROUTE':
        return os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_IPv4_report.csv'.format(GENERATE_TYPE))
    else:
        print "Wrong GENERATE_TYPE !! It should be 'PING' or 'TRACEROUTE'"



# ======================================================================================================================
# 此函数可以按 input 的 dict_to_plot 画出！无序的！ histogram figure with/without a red line indicating overall
# 是否需要 overall 只需要把 overall_enable 设置为 True/False 即可
# input = 要 plot 的 dict, 以及 True/False
# output = histogram plot
def plot_histogram_disorder(dict_to_plot, overall_enable):
    print "plot_histogram_disorder is called", dict_to_plot
    n_groups = len(dict_to_plot.keys())
    indexs = range(n_groups)
    bar_width = 0.35
    y_values = dict_to_plot.values()

    # 画 overall 的红色虚线
    if overall_enable == True:
        x_overall_list = [-0.3, n_groups-0.3]
        y_overall = np.mean(y_values)
        y_overall_list = [y_overall, y_overall]
        plt.plot(x_overall_list, y_overall_list, '--', color='r', label='overall')

    plt.grid(True)

    plt.xlabel(r"\textrm{{{0}}}".format(X_LABEL), font)
    plt.ylabel(r"\textrm{{{0}}}".format(Y_LABEL), font)
    # plt.title('Percentage of stability for 5 vantage points', fontsize=18)
    plt.xticks([j+ bar_width/2 for j in indexs], dict_to_plot.keys(), fontsize=40, fontname='Times New Roman')
    plt.yticks(fontsize=40, fontname="Times New Roman")
    plt.xlim(-0.3, n_groups-0.3)
    plt.ylim(0, max(y_values)+1)
    # 不在每个柱状图上显示百分比
    rect = plt.bar(indexs, y_values, bar_width, color='b')
    # autolabel(rect)
    plt.legend(loc='best', fontsize=40)

    # 检查是否有 os.path.join(FIGURE_PATH, RTT_TYPE) 存在，不存在的话creat
    try:
        os.stat(os.path.join(FIGURE_PATH_NAME))
    except:
        os.makedirs(os.path.join(FIGURE_PATH_NAME))


    # if GENERATE_TYPE == 'PING':
    #     plt.savefig(os.path.join(FIGURE_PATH_NAME, 'Avg_variance_of_rtt_{0}.eps'.format(RTT_TYPE)), dpi=300, transparent=True)
    # elif GENERATE_TYPE == 'TRACEROUTE':
    #     plt.savefig(os.path.join(FIGURE_PATH_NAME, 'Avg_variance_of_hops_number.eps'), dpi=300, transparent=True)
    # else:
    #     print "Wrong GENERATE_TYPE !! It should be: 'PING' or 'TRACEROUTE'"

    # 每画一次图一定要 close 掉 ！！否则会不停叠加 ！！
    plt.close()



# ======================================================================================================================
# 此函数可以按 input 的 dict_to_plot 画出！有序的！ histogram figure with/without a red line indicating overall
# 是否需要 overall 只需要把 overall_enable 设置为 True/False 即可
# input = 要 plot 的 dict, 以及 True/False
# output = histogram plot
# input 中的 probe, dest 纯属用来最后保存文件使用
def plot_histogram_in_order(dict_to_plot, overall_enable, probe, dest):
    print "plot_histogram_in_order is called", "probe ->", probe, "dest ->", dest
    n_groups = len(dict_to_plot.keys())
    indexs = range(n_groups)
    bar_width = 0.5
    y_values = dict_to_plot.values()

    # 画 overall 的红色虚线
    if overall_enable == True:
        x_overall_list = [-0.3, n_groups-0.3]
        y_overall = np.mean(y_values)
        y_overall_list = [y_overall, y_overall]
        plt.plot(x_overall_list, y_overall_list, '--', color='r', label='overall')

    plt.grid(True)

    plt.xlabel(r"\textrm{{{0}}}".format(X_LABEL), font)
    plt.ylabel(r"\textrm{{{0}}}".format(Y_LABEL), font)
    # plt.title('Percentage of stability for 5 vantage points', fontsize=18)
    plt.xticks([j+ bar_width/2 for j in indexs], dict_to_plot.keys(), fontname='Times New Roman')
    plt.yticks(fontsize=40, fontname="Times New Roman")
    plt.xlim(-0.3, n_groups-0.3)
    # plt.ylim(0, 1)
    # 不在每个柱状图上显示百分比
    rect = plt.bar(indexs, y_values, bar_width, color='b')
    # autolabel(rect)
    plt.legend(loc='best', fontsize=40)

    # 检查是否有 os.path.join(TARGET_HISTOGRAM_PATH) 存在，不存在的话 create
    try:
        os.stat(os.path.join(TARGET_HISTOGRAM_PATH))
    except:
        os.makedirs(os.path.join(TARGET_HISTOGRAM_PATH))


    if GENERATE_TYPE == 'PING':
        plt.savefig(os.path.join(TARGET_HISTOGRAM_PATH, '{0}_{1}_RTT_series_histogram.eps'.format(probe, dest)), dpi=300, transparent=True)
    elif GENERATE_TYPE == 'TRACEROUTE':
        plt.savefig(os.path.join(TARGET_HISTOGRAM_PATH, '{0}_{1}_RTT_series_histogram.eps'.format(probe, dest)), dpi=300, transparent=True)
    else:
        print "Wrong GENERATE_TYPE !! It should be: 'PING' or 'TRACEROUTE'"

    # 每画一次图一定要 close 掉 ！！否则会不停叠加 ！！
    plt.close()


# ======================================================================================================================
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        print height
        plt.text(rect.get_x()+rect.get_width()/2-0.15, 1.0003*height, '%s' % round(height,2))


# ======================================================================================================================
# 此函数将数据处理＋画图封装起来，以完成给定某个 <probe, dest> pair 即可以把其对应的 RTT TYPE 的 RTT series 按照 interval = 1ms 的 histogram 画出来
def probe_dest_rtt_series_histogram(probe, dest, rtt_type, interval):
    plot_histogram_in_order(mt.sequence_pdf_producer(paa.remove_nonvalid_rtt(paa.get_dest_probe_rtt(JSON2CSV_FILE, dest, rtt_type)[probe]),interval), True, probe, dest)



# ======================================================================================================================
# 此函数将数据处理＋画图封装起来，以完成给定某个 CSV 文件即可以把其对应的关于某个特定 probe 的 RTT TYPE 的 RTT series 按照 interval = 1ms 的 histogram 画出来
def csv_rtt_series_histogram(target_file, probe, rtt_type, interval):
    dest_list = paa.get_all_dest(target_file)
    for dest in dest_list:
        probe_dest_rtt_series_histogram(probe, dest, rtt_type, interval)








# ======================================================================================================================
# 此函数
if __name__ == "__main__":
    # plot_histogram_disorder(paa.means_of_variance_calculator(get_target_csv_name(GENERATE_TYPE)), True)
    # probe_dest_rtt_series_histogram(PLOT_PROBE, '110.75.115.70', RTT_TYPE, INTERVAL)
    csv_rtt_series_histogram(JSON2CSV_FILE, PLOT_PROBE, RTT_TYPE, INTERVAL)