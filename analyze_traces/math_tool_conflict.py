# -*- coding: utf-8 -*-
# 本script功能：
# 定义了一些基本的数学方面运算函数，供别的 script 调用
__author__ = 'yueli'


import pandas as pd
from collections import Counter
import math
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import numpy as np
from math import *
import collections
import os

# ==========================================Section: constant variable declaration======================================
EXPERIMENT_NAME = '4_probes_to_alexa_top50'
RTT_TYPE = 'avg'

# We define a CONSTANT variable: EXP_INTERVAL, to represent the time interval between two consecutive command
# (e.g. ping or traceroute)
EXP_INTERVAL = 600.0
# We also define a CONSTANT variable: EXP_DUREE, to represent the time span of experimentation
EXP_SPAN = 6.0*60*60
# The variable DIMENSION describe the list (containing the RTT) length
DIMENSION = EXP_SPAN/EXP_INTERVAL

FIGURE_PATH = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'time_sequence')
# 函数 csv_file_pick_rtt_series 执行后的output所需调用的函数，目前可为： 'periodicity' or 'rtt_statistics'
ACTION = 'rtt_statistics'



# ======================================================================================================================
# 此函数会返回一个list中最小值的一个或多个index，
# e.g.: a = [1.0, 2.0, 3.0, 4.0]，则会返回[0]；a = [1.0, 1.0, 3.0, 4.0]，则会返回[0, 1]；a = [1.0, 1.0, 1.0, 1.0]，则会返回[0, 1, 2, 3]；
# input: 含有要处理数据的list
# output: list中最小值的index所组成的list
def minimum_value_index_explorer(target_list):
    return [i for i, x in enumerate(target_list) if x == min(target_list)]



# ======================================================================================================================
# 此函数可以计算2个相同长度的 list 的 correlation，以矩阵形式返回
# input = dict{ 'probe_1': [rtt_1, rtt_2, rtt_3, ...],
#               'probe_2': [rtt_1, rtt_2, rtt_3, ...],
#               'probe_3': [rtt_1, rtt_2, rtt_3, ...],
#               'probe_4': [rtt_1, rtt_2, rtt_3, ...]
#                }
# output = dict{'probe_1': [value_1, value_2, value_3, ...],
#               'probe_2': [value_1, value_2, value_3, ...],
#               'probe_3': [value_1, value_2, value_3, ...],
#               'probe_4': [value_1, value_2, value_3, ...]
#                }
def correlation_calculator(dict_target):
    dict_correlation = {}
    for i in sorted(dict_target.keys()):
        temp = []
        for j in sorted(dict_target.keys()):
            temp.append(round(pearsonr(dict_target[i], dict_target[j])[0], 4))
        dict_correlation[i] = temp

    return dict_correlation


def minimum_value_index_explorer2(target_list):

    return [i for i, x in enumerate(target_list) if x == min(target_list)]


# ======================================================================================================================
# 此函数可以通过 FTT 来计算1个 list 的 periodicity
def periodicity_verified_ftt(sig):
    # 快速傅立叶变换，要变换的原始信号为 a series, named sig

    #最先确定的是采样率，采样率确定意味着两方面的事情。
    #1.时间轴：确定每隔多久对信号采样一次，即离散化的时域轴的间隔确定，但是总长没定。
    #2.频率轴：的总长确定了，为采样率的一半，但是间隔没定。
    Fs = 1.0/EXP_INTERVAL
    T_interval = 1/Fs
    Freq_max = Fs/2

    #之后要确定的是采样的个数，采样的个数的确定也意味着两件事情。
    #1.时间轴：采样的总时间确定了,配合上面的间隔，也就全定了。
    #2.频率轴：频率轴的间隔定了，配合上面的总长，也就全定了。
    fft_size = len(sig)        # 即：FFT_SIZE
    t = np.arange(0, fft_size)*T_interval
    freq = np.linspace(0, Freq_max, fft_size/2+1)

    # 做FFT之后的信号
    fft_sig = np.fft.rfft(sig, fft_size)/fft_size

    # 为了把频谱的X轴由Frequence (Hz)更换为Time (Hour)，生成最终想显示的几个X轴上的数值然后求倒数，
    # 但目前还未用到频谱图上
    freqs_xticks_inverse = []
    for f in freq:
        if f == 0:
            freqs_xticks_inverse.append("endless")
        else:
            freqs_xticks_inverse.append(round(1/f,2))
    print "fft_sig:", fft_sig

    return fft_size, freq, fft_sig, Freq_max




# ======================================================================================================================
<<<<<<< HEAD
# 此函数针为某一给定的 list & interval 求出其相应的 "pdf"
# input = [data_1, data_2, data_3, ...], interval
# output = 1 dict:
#          index 为 key
#          percentage 为 value
# output 的 index_1(index_n) 为 input 中每个元素向上取整后的最小(大)数，并且 index_list 已按增序排列
def sequence_pdf_producer(target_list, interval):

    target_ceil_counter = Counter([math.floor(i / interval) for i in target_list])
    target_ceil_dict = dict(target_ceil_counter)
    if len(target_ceil_dict.keys()) < (max(target_ceil_dict.keys()) - min(target_ceil_dict.keys()) + 1):
        for index in range(int(min(target_ceil_dict.keys())), int(max(target_ceil_dict.keys())) + 1):
            if index not in target_ceil_dict.keys():
                target_ceil_dict[float(index)] = 0.0

    # 把 target_ceil_dict.values() 中的个数改成 pdf
    sum_number = sum(target_ceil_dict.values())
    for index in target_ceil_dict.keys():
        target_ceil_dict[index] = target_ceil_dict[index]/sum_number*100.0

    return target_ceil_dict


def sortedDictValues1(adict):
    keys = adict.keys()
    keys.sort()
    sorted_dict = {}
    for key in keys:
        sorted_dict[key] = adict[key]
    return sorted_dict




# ======================================================================================================================
# 此函数针为某一给定的 list & interval 求出其相应的 "pdf", 但这个 list 会有正数也会有负数
# 正数部分一律向下取整，负数部分一律向上取整
# input = [data_1, data_2, data_3, ...], interval
# output = 2 lists:
#          pdf_list =[pdf_1, pdf_2, ..., pdf_n]
#          index_list = [index_1, index_2, ..., index_n]
# output 的 index_1(index_n) 为 input 中每个元素向上取整后的最小(大)数，并且 index_list 已按增序排列
def sequence_pdf_producer_2_sides(target_list, interval):
    print "sequence_pdf_producer is called"
    int_list = []

    for i in target_list:
        if i >= 0:
            int_list.append(math.floor(i / interval))
        else:
            int_list.append(math.ceil(i / interval))
    target_counter = Counter(int_list)

    # target_counter = Counter([math.ceil(i) for i in target_list])
    target_dict = dict(target_counter)
    if len(target_dict.keys()) < (max(target_dict.keys()) - min(target_dict.keys()) + 1):
        for index in range(int(min(target_dict.keys())), int(max(target_dict.keys())) + 1):
            if index not in target_dict.keys():
                target_dict[float(index)] = 0.0

    # 把 target_ceil_dict.values() 中的个数改成 pdf
    sum_number = sum(target_dict.values())
    for index in target_dict.keys():
        target_dict[index] = target_dict[index]/sum_number

    # 由于计算时有按 zoom 缩放过原数据，所以现在需要把其还原，否则 target_dict 中的 key 始终是 zoom 过的
    target_dict_final = {}
    for index in target_dict.keys():
        target_dict_final[index * interval] = target_dict[index]
=======
# 此函数可以通过 Auto-correlation 来计算1个 list 的 periodicity
def periodicity_verified_autocorr(sig,lags): #计算lags阶以内的自相关系数，返回lags个值，分别计算序列均值，标准差
        n = len(sig)
        print "n:", n
        x = np.array([float(sig) for sig in sig])
        print "x:", x
        result = [np.correlate(x[i:]-x[i:].mean(),x[:n-i]-x[:n-i].mean())[0]\
            /(x[i:].std()*x[:n-i].std()*(n-i)) \
            for i in range(1,lags+1)]
        print "result:", result

        return result

# ======================================================================================================================
# 此函数通过 periodicity_verified_ftt 和 periodicity_verified_autocorr 的返回值进行画图
# 画的图为 original signal, fft, autucorrelation 三图合一
def plot_fft_autocorr(sig, dest, probe):
    fft_size, freq, fft_sig, Freq_max = periodicity_verified_ftt(sig)
    correlation_result = periodicity_verified_autocorr(sig, fft_size-1)

    #画出时间域的幅度图
    plt.subplot(311)
    plt.plot(np.arange(1, fft_size+1), sig, 'black')
    plt.xlabel("Experiment number")
    plt.ylabel("RTT (ms)")
    plt.xlim(0,len(sig))
    # plt.legend()
    plt.title("RTT series")


    #画出频域图,你会发现你的横坐标无从下手？虽然你懂了后面的东西后可以返回来解决，但是现在就非常迷惑。现在只能原封不懂的画出频率图
    plt.subplot(312)
    plt.plot(freq, 2*np.abs(fft_sig),'blue')#如果用db作单位则20*np.log10(2*np.abs(fft_sig))
    plt.xlabel('Frequency(Hz)')
    plt.ylabel('Frenquency\nspectrum')
    plt.xlim(0, Freq_max)
    # plt.title('Frenquency spectrum for RTT series')

    #画出 auto-correlation的图
    plt.subplot(313)
    plt.plot(np.arange(1, fft_size), correlation_result,'red')
    plt.xlim(1, len(np.arange(1, fft_size))/2)
    plt.xlabel("Order from 1 to n/2-1")
    plt.ylabel("Auto-\ncorrelation")
    # plt.title('Auto-correlation for RTT series')


    # 检查是否有 JSON2CSV_FILE 存在，不存在的话creat
    try:
        os.stat(os.path.join(FIGURE_PATH, 'periodicity_verified', RTT_TYPE, probe))
    except:
        os.makedirs(os.path.join(FIGURE_PATH, 'periodicity_verified', RTT_TYPE, probe))
    plt.savefig(os.path.join(FIGURE_PATH, 'periodicity_verified', RTT_TYPE, probe, '{0}.eps'.format(dest)), dpi=300)
    plt.close()



# ======================================================================================================================
# 此函数可从 json2csv/4_probes_to_alexa_top50_*.csv 文件里逐行挑出一个 RTT series，
# 使之成为函数 目标函数 的 input 而调用那个函数
# input = json2csv/4_probes_to_alexa_top50_*.csv
# output = 由 action 指令来决定进行周期性测量 .csv file 里所有行所产生的 RTT series 调用函数 periodicity_verified_ftt 而生成的 FFT 图
#          还是 RTT 数值的统计
def csv_file_pick_rtt_series(target_csv, action):
    with open(target_csv) as f_handler:
        next(f_handler)
        for line in f_handler:
            dest = line.split(';')[0]
            probe = line.split(';')[1]
            rtt_series_one_line = [lines for lines in line.split(';')[2:]]

            if action == "periodicity":
                plot_fft_autocorr(rtt_series_one_line, dest, probe)
            elif action == "rtt_statistics":
                rtt_statistics(rtt_series_one_line, dest, probe)


# ======================================================================================================================
# 此函数用来统计某一 <probe-dest> 的 RTT series 落在每个 RTT 值区间的 RTT 值个数，并以 histogram 的形式画出来
def rtt_statistics(rtt_series, dest, probe):

    rtt_series_int = [int(float(value)) for value in rtt_series]
    print "rtt_series_int:", rtt_series_int

    dict_rtt_statistics = {}
    for rtt in rtt_series_int:
        if rtt not in dict_rtt_statistics.keys():
            dict_rtt_statistics[rtt] = 1
        else:
            dict_rtt_statistics[rtt] += 1

    dict_rtt_statistics = collections.OrderedDict(sorted(dict_rtt_statistics.items()))

    n_groups = len(dict_rtt_statistics.keys())
    indexs = range(n_groups)
    bar_width = 0.35
    y_values = dict_rtt_statistics.values()

    plt.grid(True)

    plt.xlabel("RTT value", fontsize=20)
    plt.ylabel("Number of RTT", fontsize=20)
    # plt.title('Percentage of stability for 5 vantage points', fontsize=18)
    plt.xticks([j+ bar_width/2 for j in indexs], dict_rtt_statistics.keys(), fontsize=16)
    plt.xlim(-0.3, n_groups-0.3)
    plt.ylim(0, max(y_values)+1)
    rect = plt.bar(indexs, y_values, bar_width, color='b')
    # autolabel(rect)
    # plt.legend(loc='upper right')

    # 检查是否有 JSON2CSV_FILE 存在，不存在的话 create
    try:
        os.stat(os.path.join(FIGURE_PATH, 'rtt_statistics', RTT_TYPE, probe))
    except:
        os.makedirs(os.path.join(FIGURE_PATH, 'rtt_statistics', RTT_TYPE, probe))
    plt.savefig(os.path.join(FIGURE_PATH, 'rtt_statistics', RTT_TYPE, probe, '{0}.eps'.format(dest)), dpi=300)
    plt.close()




# ======================================================================================================================
if __name__ == "__main__":

    # x = np.arange(0, 2*pi, 0.1)
    # y_sin = np.sin(100*x)
    # print "y_sin:", y_sin
    # periodicity_verified_ftt(y_sin)

    csv_file_pick_rtt_series(os.path.join(ATLAS_TRACES, 'json2csv', '{0}_{1}.csv'.format(EXPERIMENT_NAME, RTT_TYPE)), ACTION)
>>>>>>> 352fe51d3afcbf5f50ce9ae0376f24d8b1f2e94b


    index_min = min(target_dict_final.keys())
    index_max = max(target_dict_final.keys())

    return target_dict_final, index_min, index_max




# ======================================================================================================================
# 此函数可求一个 list 的 median 值
# input = [a, b, c, d, e, ...]
# output = median 值
def median(target_list):
    return np.median(target_list)




# ======================================================================================================================
if __name__ == "__main__":

    # print  minimum_value_index_explorer([2.0, 1.0, 3.0, 4.0, 3.0, 1.0])
    #
    # dict = {"lisp":[147.61, 18.33, 419.09],
    #         "mplane":[131.16, 13.65, 304.15],
    #         "franceIX":[158.42, 16.79, 252.14],
    #         "rmd":[27.87, 13.24, 63.27]
    #         }
    #
    # test_example = [5,5,4,4,4,3,3,2,2]
    #
    # test2 = [2.0, 1.0, 3.0, 3.0, 4.0, 1.0]

    # index_list, pdf_list = sequence_pdf_producer([14.2, 19.1, 18.5,14.3,15.7,18.9],1)
    # print index_list
    # print pdf_list

    # print sequence_pdf_producer([18.2, 12.6, 14.5,15.3,17.5,18.1],1)
    # d = {'rmd': {15.0: 0.3333333333333333, 16.0: 0.16666666666666666, 17.0: 0.0, 18.0: 0.0, 19.0: 0.3333333333333333, 20.0: 0.16666666666666666},
    #      'mPlane': {13.0: 0.16666666666666666, 14.0: 0.0, 15.0: 0.16666666666666666, 16.0: 0.16666666666666666, 17.0: 0.0, 18.0: 0.16666666666666666, 19.0: 0.3333333333333333}}
    # pd.DataFrame(d).plot(kind='bar')
    # plt.show()
    # print sequence_pdf_producer_2_sides([-2.2, 0.0, 1.5], 1.0)

    print median([3,1,2,5,4])


