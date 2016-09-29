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
EXPERIMENT_NAME = '5_probes_to_alexa_top500'  # Needs to change
GENERATE_TYPE = 'ping'  # 'ping' or 'traceroute'
IP_VERSION = 'v4'  # 'v6'
RTT_TYPE = 'avg'  # 'min' or 'max'
CALCULATE_TYPE = 'mean'   # 'mean' or 'median'

FIGURE_PATH = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION))
RTT_REPORT =  os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION),
                           '{0}_{1}_report_{2}_{3}.csv'.format(GENERATE_TYPE,IP_VERSION,RTT_TYPE,CALCULATE_TYPE))

# From RTT_REPORT, we need to define a dict, which key = probe and value is its index in the tile of this file
# The following 2 dicts should be difned as the same time
probe_index_dict = {'mPlane': 2, 'FranceIX':3, 'LISP-Lab':4}
index_probe_dict = {2: 'mPlane', 3: 'FranceIX', 4: 'LISP-Lab'}
REF_RTT_PROBE = 'FranceIX'
COMPARED_RTT_PROBE = 'LISP-Lab'



# ==========================================Section: functions declaration======================================
# Plot the RTT series for all destinations
# If just want to plot for one measurement id, when you call this function, set the measurement id (str) as a variable,
# and uncomment 'if key[0] == m_id:'
# If plot for all, just comment 'if key[0] == m_id:'
def plot_rtt_series_by_mid(m_id):
    try:
        os.stat(os.path.join(FIGURE_PATH, 'time_sequence', RTT_TYPE))
    except:
        os.makedirs(os.path.join(FIGURE_PATH, 'time_sequence', RTT_TYPE))

    probes_list = ptma.get_probes()
    dest_probes_rtt_dict = ptma.get_clean_traces()
    for key in dest_probes_rtt_dict.keys():
        # if key[0] == m_id:
            for probe in probes_list:
                plt.plot(range(1, len(dest_probes_rtt_dict[key][probes_list[0]])+1), dest_probes_rtt_dict[key][probe], label=probe)
            plt.xlabel(r"\textrm{experiment round}", font)
            plt.ylabel(r"\textrm{RTT (ms)}", font)
            plt.title(r"\textrm{0}".format(key[1]), font)
            plt.xticks(fontsize=30, fontname="Times New Roman")
            plt.yticks(fontsize=30, fontname="Times New Roman")
            plt.xlim(1, len(dest_probes_rtt_dict[key][probes_list[0]]))
            plt.legend(loc='best', fontsize=30)
            plt.savefig(os.path.join(FIGURE_PATH, 'time_sequence', RTT_TYPE, '{0}_{1}.eps'.format(key[0],key[1])), dpi=300, transparent=True)
            plt.close()


# Get a raw_rtt_probes_dict from RTT_REPORT
# input = RTT_REPORT
# output = cdf raw_rtt_probes_dict
def get_raw_rtt_probes_dict():
    probes_list = ptma.get_probes()
    raw_rtt_probes_dict = {}
    with open(RTT_REPORT) as rtt_report:
        next(rtt_report)
        for line in rtt_report:
            for probe in probes_list:
                if probe not in raw_rtt_probes_dict.keys():
                    raw_rtt_probes_dict[probe] = [float(line.split(";")[probe_index_dict[probe]].strip())]
                else:
                    raw_rtt_probes_dict[probe].append(float(line.split(";")[probe_index_dict[probe]].strip()))

    return raw_rtt_probes_dict


# Plot cdf of RTT for every probe
# input = RTT_REPORT
# output = cdf figures
def plot_cdf_rtt_probes():
    print RTT_REPORT
    try:
        os.stat(os.path.join(FIGURE_PATH, 'CDF_figures', RTT_TYPE))
    except:
        os.makedirs(os.path.join(FIGURE_PATH, 'CDF_figures', RTT_TYPE))

    probes_list = ptma.get_probes()
    raw_rtt_probes_dict = get_raw_rtt_probes_dict()

    cdf_rtt_probes_dict = {}
    for probe in probes_list:
        print probe
        cdf_rtt_probes_dict[probe] = ECDF(raw_rtt_probes_dict[probe])
        x = range(int(math.floor(min(raw_rtt_probes_dict[probe]))), int(math.ceil(max(raw_rtt_probes_dict[probe]))+1))
        y = cdf_rtt_probes_dict[probe](range(int(math.floor(min(raw_rtt_probes_dict[probe]))), int(math.ceil(max(raw_rtt_probes_dict[probe]))+1)))
        # print int(math.floor(min(raw_rtt_probes_dict[probe]))), int(math.ceil(max(raw_rtt_probes_dict[probe]))+1)
        print int(math.floor(min(raw_rtt_probes_dict[probe]))), int(math.ceil(max(raw_rtt_probes_dict[probe]))+1)
        plt.plot(x, y, linewidth = 3, label = probe)

    plt.xlabel(r"\textrm{RTT (ms)}", font)
    plt.ylabel(r"\textrm{ECDF}", font)
    plt.xticks(fontsize=30, fontname="Times New Roman")
    plt.yticks(fontsize=30, fontname="Times New Roman")
    plt.legend(loc='best', fontsize=30)
    plt.savefig(os.path.join(FIGURE_PATH, 'CDF_figures', RTT_TYPE, 'CDF_{0}(RTT)_{1}.eps'.format(RTT_TYPE, CALCULATE_TYPE)), dpi=300, transparent=True)
    plt.close()


# Calculate the correlation of mean/median RTT of every dest compared to FranceIX
# input = RTT_REPORT
# output = correlation coefficient
def correlation_calculator():
    return mt.correlation_calculator(get_raw_rtt_probes_dict())


# Make a statistics of the smallest RTT between the different probes
# input = RTT_REPORT
# output = correlation coefficient
def smallest_continent_probe_rtt_finder():
    path_to_store = os.path.join(FIGURE_PATH, 'Histogram', 'Smallest_RTT')
    try:
        os.stat(path_to_store)
    except:
        os.makedirs(path_to_store)

    start_index = min(probe_index_dict.values())
    stop_index = max(probe_index_dict.values()) + 1

    continent_probe_smallest_rtt_dict = {}
    with open(RTT_REPORT) as rtt_report:
        next(rtt_report)
        for line in rtt_report:
            lines = [j.strip() for j in line.split(";")]
            temp_list = lines[start_index:stop_index]

            for i in mt.minimum_value_index_explorer(temp_list):
                if lines[-1] not in continent_probe_smallest_rtt_dict.keys():
                    continent_probe_smallest_rtt_dict[lines[-1]] = {}
                    if index_probe_dict[i+2] not in continent_probe_smallest_rtt_dict[lines[-1]].keys():
                        continent_probe_smallest_rtt_dict[lines[-1]][index_probe_dict[i+2]] = 1
                else:
                    if index_probe_dict[i+2] not in continent_probe_smallest_rtt_dict[lines[-1]].keys():
                        continent_probe_smallest_rtt_dict[lines[-1]][index_probe_dict[i + 2]] = 1
                    else:
                     continent_probe_smallest_rtt_dict[lines[-1]][index_probe_dict[i + 2]] += 1


    smallest_rtt_percentage = {}
    for continent in continent_probe_smallest_rtt_dict.keys():
        if continent not in smallest_rtt_percentage.keys():
            smallest_rtt_percentage[continent] = {}
            for probe in continent_probe_smallest_rtt_dict[continent].keys():
                smallest_rtt_percentage[continent][probe] = float(continent_probe_smallest_rtt_dict[continent][probe])/float(sum(continent_probe_smallest_rtt_dict[continent].values()))

    df = pd.DataFrame(paa.reverse_dict_keys(smallest_rtt_percentage))
    df.plot(kind='bar')
    plt.xlabel(r"\textrm{Continents of requested destinations}", font)
    plt.ylabel(r"\textrm{Percentage}", font)
    plt.xticks(fontsize=30, fontname="Times New Roman")
    plt.yticks(fontsize=30, fontname="Times New Roman")
    plt.savefig(os.path.join(path_to_store,
                             'Smallest_{0}_{1}(RTT)_proporation.eps'.format(CALCULATE_TYPE, RTT_TYPE)),
                dpi=300, transparent=True)
    plt.close()

    return continent_probe_smallest_rtt_dict


# Plot histogram of relative RTT using REF_RTT (Percentage)
# input = RTT_REPORT
# output = relative RTT
def plot_relative_rtt_hist():
    path_to_store = os.path.join(FIGURE_PATH, 'Histogram', 'Relative_RTT')
    try:
        os.stat(path_to_store)
    except:
        os.makedirs(path_to_store)

    relative_rtt = []
    with open(RTT_REPORT) as rtt_report:
        next(rtt_report)
        for line in rtt_report:
            lines = [j.strip() for j in line.split(";")]
            relative_rtt.append(float(lines[probe_index_dict[COMPARED_RTT_PROBE]]) - float(lines[probe_index_dict[REF_RTT_PROBE]]))

    print relative_rtt
    print int(math.ceil(max(relative_rtt)))
    y, x, _ = plt.hist(relative_rtt, int(math.ceil(max(relative_rtt))), normed=1)
    print "x.max() =", x.max()
    print "x.min() =", x.min()
    print "y.max() =", y.max()
    plt.xlabel(r"\textrm{Relative RTT (ms)}", font)
    plt.ylabel(r"\textrm{Probability}", font)
    plt.xticks(fontsize=30, fontname="Times New Roman")
    plt.yticks(fontsize=30, fontname="Times New Roman")
    plt.savefig(
        os.path.join(path_to_store, 'Relative_{0}_{1}(RTT)_{2}-{3}.eps'.format(CALCULATE_TYPE,RTT_TYPE,COMPARED_RTT_PROBE, REF_RTT_PROBE)),
        dpi=300, transparent=True)
    plt.close()



# Plot bar of relative RTT using REF_RTT as well as the geolocation
# input = RTT_REPORT
# output = relative RTT
def plot_relative_rtt_bar():
    path_to_store = os.path.join(FIGURE_PATH, 'Bar', 'Relative_RTT')
    try:
        os.stat(path_to_store)
    except:
        os.makedirs(path_to_store)

    # This dict of dict is used to store the relative RTT
    continent_probe_relative_rtt_dict = {}
    # This dict is used to store the number of negative relative RTT
    continent_probe_negative_relative_rtt_dict = {}
    with open(RTT_REPORT) as rtt_report:
        next(rtt_report)
        for line in rtt_report:
            lines = [j.strip() for j in line.split(";")]

            if lines[-1] not in continent_probe_relative_rtt_dict.keys():
                continent_probe_relative_rtt_dict[lines[-1]] = {}
                continent_probe_negative_relative_rtt_dict[lines[-1]] = 0
                if lines[0] not in continent_probe_relative_rtt_dict[lines[-1]].keys():
                    continent_probe_relative_rtt_dict[lines[-1]][lines[0]] = float(lines[probe_index_dict[COMPARED_RTT_PROBE]]) - float(lines[probe_index_dict[REF_RTT_PROBE]])
                    if continent_probe_relative_rtt_dict[lines[-1]][lines[0]] < 0:
                        continent_probe_negative_relative_rtt_dict[lines[-1]] += 1
                else:
                    print lines[0], 'is already in', continent_probe_relative_rtt_dict[lines[-1]].keys()
            else:
                if lines[0] not in continent_probe_relative_rtt_dict[lines[-1]].keys():
                    continent_probe_relative_rtt_dict[lines[-1]][lines[0]] = float(lines[probe_index_dict[COMPARED_RTT_PROBE]]) - float(lines[probe_index_dict[REF_RTT_PROBE]])
                    if continent_probe_relative_rtt_dict[lines[-1]][lines[0]] < 0:
                        continent_probe_negative_relative_rtt_dict[lines[-1]] += 1
                else:
                    print lines[0], 'is already in', continent_probe_relative_rtt_dict[lines[-1]].keys()


    total_dest_num = 0
    geo_line = 0
    relative_rtt_list = []
    xticks_list = []
    for continent in continent_probe_relative_rtt_dict.keys():
        print "There are", len(continent_probe_relative_rtt_dict[continent].keys()), "dest in", continent
        print continent_probe_negative_relative_rtt_dict[continent], "dest,", COMPARED_RTT_PROBE, "is faster than", REF_RTT_PROBE
        print continent_probe_relative_rtt_dict[continent]
        xticks_list.append(geo_line + 0.5*len(continent_probe_relative_rtt_dict[continent].keys()))
        geo_line = geo_line + len(continent_probe_relative_rtt_dict[continent].keys())
        total_dest_num = total_dest_num + len(continent_probe_relative_rtt_dict[continent].keys())
        relative_rtt_list.extend(continent_probe_relative_rtt_dict[continent].values())
        plt.axvline(geo_line, linewidth=3, color='k')

    print total_dest_num
    plt.bar(range(total_dest_num), relative_rtt_list)
    plt.xlim(min(range(total_dest_num)), max(range(total_dest_num)))
    plt.xlabel(r"\textrm{Destinations}", font)
    plt.ylabel(r"\textrm{Relative RTT (ms)}", font)
    plt.xticks(xticks_list,
               ['{0}:{1}'.format(continent, len(continent_probe_relative_rtt_dict[continent].keys())) for continent in continent_probe_relative_rtt_dict.keys()], fontsize=20, fontname="Times New Roman")
    plt.yticks(fontsize=30, fontname="Times New Roman")
    plt.savefig(os.path.join(path_to_store, 'Relative_{0}_{1}(RTT)_{2}-{3}.eps'.format(CALCULATE_TYPE, RTT_TYPE, COMPARED_RTT_PROBE, REF_RTT_PROBE)), dpi=300, transparent=True)
    plt.show()
    plt.close()

    return continent_probe_relative_rtt_dict







# ==========================================Section: main function declaration======================================
if __name__ == "__main__":
    # 检查是否有 FIGURE_PATH 存在，不存在的话 create
    try:
        os.stat(os.path.join(FIGURE_PATH))
    except:
        os.makedirs(os.path.join(FIGURE_PATH))

    # # To plot the RTT series figure for each dest
    # plot_rtt_series_by_mid('5276479')

    # # To plot the CDF of mean/median RTT in RTT_REPORT
    # plot_cdf_rtt_probes()

    # To calculate the correlation of mean/median RTT of every dest compared to FranceIX
    # print correlation_calculator()

    # print smallest_continent_probe_rtt_finder()

    # plot_relative_rtt_hist()

    # plot_relative_rtt_bar()

    print get_raw_rtt_probes_dict()