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
import analyze_traces.pingRTTMeansVariance_tracerouteHops_multiple_advance as ptma
from statsmodels.distributions.empirical_distribution import ECDF
import analyze_traces.math_tool as mt

mpl.rcParams['text.usetex'] = True
mpl.rcParams.update({'figure.autolayout': True})


# ==========================================Section: constant variable declaration======================================
# EXPERIMENT_NAME 为要处理的实验的名字，因为它是存储和生成trace的子文件夹名称
# TARGET_CSV_TRACES 为要分析的trace的文件名
EXPERIMENT_NAME = '5_probes_to_alexa_top510'  # Needs to change
GENERATE_TYPE = 'ping'  # 'ping' or 'traceroute'
IP_VERSION = 'v6'  # 'v6'
RTT_TYPE = 'avg'  # 'min' or 'max'
CALCULATE_TYPE = 'median'   # 'mean' or 'median'

FIGURE_PATH = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION))
RTT_REPORT =  os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION),
                           '{0}_{1}_report_{2}_{3}.csv'.format(GENERATE_TYPE,IP_VERSION,RTT_TYPE,CALCULATE_TYPE))
TRACEROUTE_REPORT =  os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION),
                           '{0}_{1}_report.csv'.format(GENERATE_TYPE,IP_VERSION))
RELIABILITY_FILE = os.path.join(ATLAS_TRACES, 'json2csv', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION),
                           '{0}_{1}.csv'.format(EXPERIMENT_NAME, RTT_TYPE))

NEW_PRODUCED_FILE = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION),
                           '{0}_{1}_report_{2}_{3}_changed.csv'.format(GENERATE_TYPE,IP_VERSION,RTT_TYPE,CALCULATE_TYPE))

# From RTT_REPORT, we need to define a dict, which key = probe and value is its index in the tile of this file
# The following 2 dicts should be difned as the same time
probe_index_dict = {'Gandi':2, 'mPlane':3, 'FranceIX':4, 'LISP-Lab':5, 'LIP6':6}    # !!!!!!!!!!!!!! Needs to check for every different experiment !!!!!!!!!!!!
index_probe_dict = {2: 'Gandi', 3: 'mPlane', 4: 'FranceIX', 5: 'LISP-Lab', 6:'LIP6'}    # !!!!!!!!!!!!!! Needs to check for every different experiment !!!!!!!!!!!!
REF_RTT_PROBE = 'FranceIX'
COMPARED_RTT_PROBE = 'LIP6'


# Plot cdf of RTT for every probe
# input = RTT_REPORT
# output = cdf figures
def plot_cdf_rtt_probes():
    print RTT_REPORT
    try:
        os.stat(os.path.join(FIGURE_PATH, 'CDF_figures', RTT_TYPE))
    except:
        os.makedirs(os.path.join(FIGURE_PATH, 'CDF_figures', RTT_TYPE))

    probes_list = probe_index_dict.keys()
    raw_rtt_probes_dict = get_raw_rtt_probes_dict()

    cdf_rtt_probes_dict = {}
    for probe in probes_list:
        print probe
        cdf_rtt_probes_dict[probe] = ECDF(raw_rtt_probes_dict[probe])
        x = range(int(math.floor(min(raw_rtt_probes_dict[probe]))), int(math.ceil(max(raw_rtt_probes_dict[probe]))+1))
        y = cdf_rtt_probes_dict[probe](range(int(math.floor(min(raw_rtt_probes_dict[probe]))), int(math.ceil(max(raw_rtt_probes_dict[probe]))+1)))
        print x
        print y
        # print int(math.floor(min(raw_rtt_probes_dict[probe]))), int(math.ceil(max(raw_rtt_probes_dict[probe]))+1)
        print int(math.floor(min(raw_rtt_probes_dict[probe]))), int(math.ceil(max(raw_rtt_probes_dict[probe]))+1)
        plt.plot(x, y, linewidth = 3, label = probe)

    plt.xlabel(r"\textrm{RTT (ms)}", font)
    plt.ylabel(r"\textrm{ECDF}", font)
    plt.xticks(fontsize=30, fontname="Times New Roman")
    plt.yticks(fontsize=30, fontname="Times New Roman")
    plt.legend(loc='best', fontsize=30)
    plt.grid(True)
    # plt.savefig(os.path.join(FIGURE_PATH, 'CDF_figures', RTT_TYPE, 'CDF_{0}(RTT)_{1}.eps'.format(RTT_TYPE, CALCULATE_TYPE)), dpi=300, transparent=True)
    plt.show()
    plt.close()


# ==========================================Section: main function declaration======================================
if __name__ == "__main__":
    plot_cdf_rtt_probes()
