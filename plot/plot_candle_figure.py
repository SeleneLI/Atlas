# -*- coding: utf-8 -*-
# 本script功能：
# 画关于 candle figure 的各种图
__author__ = 'yueli'

from config.config import *
from analyze_traces import ping_associated_analyzer
import matplotlib.pyplot as plt


# ==========================================Section: constant variable declaration======================================
# EXPERIMENT_NAME 为要处理的实验的名字，因为它是存储和生成trace的子文件夹名称
# TARGET_CSV_TRACES 为要分析的trace的文件名
EXPERIMENT_NAME = '4_probes_to_alexa_top50'
RTT_TYPE = 'avg'
TARGET_CSV_DIFF = os.path.join(ATLAS_TRACES, 'json2csv', '{0}_{1}.csv'.format(EXPERIMENT_NAME, RTT_TYPE))
# 计算差值时的参考 probe
REF_PROBE = 'FranceIX'


if __name__ == "__main__":
    dict_probe_dest_mean = {}
    dict_probe_dest_var = {}
    dict_probe_dest_mean, dict_probe_dest_var = ping_associated_analyzer.difference_calculator(TARGET_CSV_DIFF, REF_PROBE)
    for key in dict_probe_dest_mean.keys():
        dest_list = dict_probe_dest_mean[key].keys()
        rtt_list = dict_probe_dest_mean[key].values()
        plt.plot(range(1,len(dest_list)+1), rtt_list)
        plt.show()