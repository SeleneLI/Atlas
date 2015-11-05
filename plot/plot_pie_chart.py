# -*- coding: utf-8 -*-
# 本script功能：
# 画关于 Pie figure 的各种图
__author__ = 'yueli'

from config.config import *
import re
import analyze_traces.ping_associated_analyzer as paa
import analyze_traces.traceroute_associated_analyzer as taa
import matplotlib.pyplot as plt



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
EXPERIMENT_NAME = '4_probes_to_alexa_top100' # Needs to change
TARGET_CSV_NAME = 'TRACEROUTE_IPv4_report.csv' # Needs to change
TARGET_CSV_TRACES = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, TARGET_CSV_NAME)

# The title shown on the figure
# FIGURE_TITLE = "Percentage of every probe's minimum RTT" # Needs to change
# The full path and figure name
FIGURE_PATH_NAME = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'Percentage_every_probe_minimum_hops_number.eps') # Needs to change
# 需要根据最终Pie图有几部分而分配几种颜色
COLORS = ['red', 'green', 'yellow', 'lightskyblue'] # Maybe needs to change
# 最终 Pie 图有几部分写几个0。此处表示扇形和扇形之间的距离，如果均为0则表示各扇形间无缝相连
EXPLODE=(0, 0, 0, 0)  # Maybe needs to change


# ======================================================================================================================
# 此函数可以画出Pie figure
def plot_pie_figure(list_to_plot):
    fracs = [float(percentage) for percentage in list_to_plot.values()]
    print fracs
    labels = list_to_plot

    # autopct='%1.2f%%' means that the pie chart will display 2 decimal points
    plt.pie(fracs, explode=EXPLODE, labels=labels, colors=COLORS, autopct='%1.2f%%', startangle=345)
                    # The default startangle is 0, which would start
                    # the Frogs slice on the x-axis.  With startangle=90,
                    # everything is rotated counter-clockwise by 90 degrees,
                    # so the plotting starts on the positive y-axis.

    # plt.title(FIGURE_TITLE)
    plt.savefig(FIGURE_PATH_NAME)
    plt.show()

if __name__ == "__main__":
    if re.match(r'PING', TARGET_CSV_NAME):
        plot_pie_figure(paa.minimum_rtt_calculator(TARGET_CSV_TRACES))
    elif re.match(r'TRACEROUTE', TARGET_CSV_NAME):
        plot_pie_figure(taa.minimum_hops_calculator(TARGET_CSV_TRACES))
    else:
        print "The target .csv file does not exist ..."
