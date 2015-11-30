# -*- coding: utf-8 -*-
# 本script功能：
# 定义了一些基本的数学方面运算函数，供别的 script 调用
__author__ = 'yueli'


import pprint
from config.config import *
import numpy as np
import re
from scipy.stats import pearsonr
import rpy2.robjects as robjects
import matplotlib.pyplot as plt

# ==========================================Section: constant variable declaration======================================
EXPERIMENT_NAME = '4_probes_to_alexa_top50'

# We define a CONSTANT variable: EXP_INTERVAL, to represent the time interval between two consecutive command
# (e.g. ping or traceroute)
EXP_INTERVAL = 600.0
# We also define a CONSTANT variable: EXP_DUREE, to represent the time span of experimentation
EXP_SPAN = 6.0*60*60
# The variable DIMENSION describe the list (containing the RTT) length
DIMENSION = EXP_SPAN/EXP_INTERVAL





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
    N = fft_size = len(sig)        # 即：FFT_SIZE
    t = np.arange(0,N)*T_interval
    freq = np.linspace(0,Freq_max,N/2+1)

    # 做FFT之后的信号
    fft_sig = np.fft.rfft(sig,N)/N

    # 为了把频谱的X轴由Frequence (Hz)更换为Time (Hour)，生成最终想显示的几个X轴上的数值然后求倒数，
    # 但目前还未用到频谱图上
    freqs_xticks_inverse = []
    for f in freq:
        if f == 0:
            freqs_xticks_inverse.append("endless")
        else:
            freqs_xticks_inverse.append(round(1/f,2))
    print "freqs_xticks_inverse:", freqs_xticks_inverse


    # print len(t), "t:", t
    print len(sig), "sig:", sig
    # print len(freq), "freq:", freq
    print len(fft_sig), "fft_sig:", fft_sig

    #画出时间域的幅度图
    plt.subplot(211)
    plt.plot(np.arange(1,N+1),sig,'blue')
    plt.xlabel("Experiment number")
    plt.ylabel("Mean")
    plt.xlim(0,len(sig))
    plt.legend()
    plt.title("Time waveform for mean of overall change number")


    #画出频域图,你会发现你的横坐标无从下手？虽然你懂了后面的东西后可以返回来解决，但是现在就非常迷惑。现在只能原封不懂的画出频率图
    plt.subplot(212)

    plt.plot(freq,2*np.abs(fft_sig),'red')#如果用db作单位则20*np.log10(2*np.abs(fft_sig))
    plt.xlabel('Frequency(Hz)')
    plt.ylabel('Proportion')
    plt.xlim(0,Freq_max)
    plt.title('Frenquency spectrum for mean of overall change number')
    plt.show()



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

    # r = robjects.r
    # r('library("dtw")')
    # idx = r.seq(0,6.28,len=100)
    # x = [1, 2, 3, 4]
    # print x
    #
    # y = [1.5, 2.5, 3.5, 4.5]
    # print y
    #
    # z = [2, 3, 4, 5]
    # print z
    #
    # alignment = r.dtw(x, y, keep=True)
    # dist1 = alignment.rx('distance')[0][0]
    # print(dist1)
    #
    # alignment = r.dtw(y, z, keep=True)
    # dist2 = alignment.rx('distance')[0][0]
    # print(dist2)
    #
    # alignment = r.dtw(x, z, keep=True)
    # dist3 = alignment.rx('distance')[0][0]
    # print(dist3)

    # periodicity_verified_ftt([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    #periodicity_verified_ftt([1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0])
    #periodicity_verified_ftt([1.0, 2.0, 3.0, 2.0, 1.0, 2.0, 3.0, 2.0, 1.0, 2.0, 3.0, 2.0, 1.0])
    t = range(0,1000)
    periodicity_verified_ftt(np.cos(2*np.pi*100*t))




