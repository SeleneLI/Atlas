# -*- coding: utf-8 -*-
# 本script功能：
# 画关于 Histogram 的各种图
__author__ = 'yueli'

from config.config import *
import analyze_traces.ping_associated_analyzer as paa
import matplotlib.pyplot as plt
import numpy as np



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
RTT_TYPE = 'min'    # 'min' or 'avg' or 'max'
# TARGET_CSV_TRACES = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_IPv4_report_{1}.csv'.format(GENERATE_TYPE, RTT_TYPE))

# The title shown on the figure
# FIGURE_TITLE = "Percentage of every probe's minimum RTT" # Needs to change
# The full path and figure name
FIGURE_PATH_NAME = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'histogram')
X_LABEL = 'probes'      # The name of x_label on the figure
Y_LABEL = 'means of variance (%)'       # The name of y_label on the figure


# ======================================================================================================================
# 此函数用于得到要处理的 csv 文件，即：TARGET_CSV_NAME
def get_target_csv_name(generate_type):
    if generate_type == 'PING':
        return os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_IPv4_report_{1}.csv'.format(GENERATE_TYPE, RTT_TYPE))
    elif generate_type == 'TRACEROUTE':
        return os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_IPv4_report.csv'.format(GENERATE_TYPE))
    else:
        print "Wrong GENERATE_TYPE !! It should be 'PING' or 'TRACEROUTE'"



# ======================================================================================================================
# 此函数可以画出 histogram figure
def plot_histogram(list_to_plot, overall_enable):
    print "plot_histogram is called", list_to_plot
    n_groups = len(list_to_plot.keys())
    indexs = range(n_groups)
    bar_width = 0.35
    y_values = list_to_plot.values()

    # 画 overall 的红色虚线
    if overall_enable == True:
        x_overall_list = [-0.3, n_groups-0.3]
        y_overall = np.mean(y_values)
        y_overall_list = [y_overall, y_overall]
        plt.plot(x_overall_list, y_overall_list, '--', color='r', label='overall')

    plt.grid(True)

    plt.xlabel(X_LABEL, fontsize=20)
    plt.ylabel(Y_LABEL, fontsize=20)
    # plt.title('Percentage of stability for 5 vantage points', fontsize=18)
    plt.xticks([j+ bar_width/2 for j in indexs], list_to_plot.keys(), fontsize=16)
    plt.xlim(-0.3, n_groups-0.3)
    plt.ylim(0, max(y_values)+1)
    rect = plt.bar(indexs, y_values, bar_width, color='b')
    autolabel(rect)
    plt.legend(loc='upper right')

    # 检查是否有 os.path.join(FIGURE_PATH, RTT_TYPE) 存在，不存在的话creat
    try:
        os.stat(os.path.join(FIGURE_PATH_NAME))
    except:
        os.makedirs(os.path.join(FIGURE_PATH_NAME))


    if GENERATE_TYPE == 'PING':
        plt.savefig(os.path.join(FIGURE_PATH_NAME, 'Avg_variance_of_rtt_{0}.eps'.format(RTT_TYPE)), dpi=300)
    elif GENERATE_TYPE == 'TRACEROUTE':
        plt.savefig(os.path.join(FIGURE_PATH_NAME, 'Avg_variance_of_hops_number.eps'), dpi=300)
    else:
        print "Wrong GENERATE_TYPE !! It should be: 'PING' or 'TRACEROUTE'"

    plt.show()


def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        print height
        plt.text(rect.get_x()+rect.get_width()/2-0.15, 1.0003*height, '%s' % round(height,2))


if __name__ == "__main__":
    plot_histogram(paa.means_of_variance_calculator(get_target_csv_name(GENERATE_TYPE)), True)