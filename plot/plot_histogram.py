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
TARGET_CSV_NAME = 'PING_IPv4_report_min.csv' # Needs to change
TARGET_CSV_TRACES = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, TARGET_CSV_NAME)

# The title shown on the figure
# FIGURE_TITLE = "Percentage of every probe's minimum RTT" # Needs to change
# The full path and figure name
FIGURE_PATH_NAME = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'Avg_variance_of_rtt_min.eps') # Needs to change
X_LABEL = 'probes' # The name of x_label on the figure
Y_LABEL = 'means of variance (%)' # The name of y_label on the figure


# ======================================================================================================================
# 此函数可以画出Pie figure
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
    plt.savefig(FIGURE_PATH_NAME)
    plt.show()


def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        print height
        plt.text(rect.get_x()+rect.get_width()/2-0.15, 1.0003*height, '%s' % round(height,2))


if __name__ == "__main__":
    plot_histogram(paa.means_of_variance_calculator(TARGET_CSV_TRACES), True)