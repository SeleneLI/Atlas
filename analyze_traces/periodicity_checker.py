# -*- coding: utf-8 -*-
# 本script功能：
# 基于 $HOME/Documents/Codes/Atlas/traces/json2csv/ 中存储的各实验下的 4_probes_to_alexa_top50.csv 文件而进行的更深入分析，
# 以验证每一个 <probe, dest> pair 所产生的所有 RTT series 是否有 periodicity，用 FFT 和 Auto-correlation 的图画出结果
# 结果存在 $HOME/Documents/Codes/Atlas/figures_and_tables/4_probes_to_alexa_top50/periodicity_verify/ 文件夹下
__author__ = 'yueli'

from config.config import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['text.usetex'] = True
mpl.rcParams.update({'figure.autolayout': True})

# ==========================================Section: constant variable declaration======================================
# EXPERIMENT_NAME 为要处理的实验的名字，因为它是存储和生成trace的子文件夹名称
# TARGET_CSV_TRACES 为要分析的trace的文件名
EXPERIMENT_NAME = '5_probes_to_alexa_top510'
RTT_TYPE = 'avg'
TARGET_CSV_FILE = os.path.join(ATLAS_TRACES, 'json2csv', '{0}.csv'.format(EXPERIMENT_NAME))
RESULT_FIGURES_PATH = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'periodicity_verify')

# 验证 periodicity 的方式
VERIFY_MODE = 'FFT' #此处可为 'FFT' 和 'Auto-correlation' 两种
PROBE = 'LISP-Lab'
DEST = '31.13.76.102'

# 实验时的一些参数
INTERVAL = 600.0  #此处给出做实验的间隔，单位为秒
FFT_XAXIS = 'HZ' #此处给出FFT变换结果图的横坐标单位，可用 frequency: 'HZ' 也可用 time/interval: 'min'


# ======================================================================================================================
# 此函数对某一个 <probe, dest> pair 所产生的所有 RTT series 进行计算处理，可得到其 periodicity，
# 并以图的形式返回
def rtt_series_periodicity_checker(probe, dest, rtt_type):
    rtt_list =[]
    if rtt_type == 'min':
        rtt_type_numer = 0
    elif rtt_type == 'avg':
        rtt_type_numer = 1
    elif rtt_type == 'max':
        rtt_type_numer = 2

    with open(TARGET_CSV_FILE) as f_handler:
        next(f_handler)
        for line in f_handler:
            if dest == line.split(';')[0] and probe == line.split(';')[1]:
                for i in line.split(';')[2:]:
                    if i == '-1/-1/-1':
                        print "Invalid RTT series, since there is at least 1 experiment round having no response"
                        return
                    else:
                        rtt_list.append(i.split('/')[rtt_type_numer])

    print rtt_list
    # 检查是否有 os.path.join(FIGURE_PATH, RTT_TYPE) 存在，不存在的话creat
    try:
        os.stat(os.path.join(RESULT_FIGURES_PATH, VERIFY_MODE, probe, RTT_TYPE))
    except:
        os.makedirs(os.path.join(RESULT_FIGURES_PATH, VERIFY_MODE, probe, RTT_TYPE))

    if VERIFY_MODE == 'FFT':
        fft_periodicity_checker(probe, dest, rtt_list)
    elif VERIFY_MODE == 'Auto-correlation':
        autocorr_periodicity_checker(probe, dest, rtt_list)

# 快速傅立叶变换以求 periodicity，要变换的原始信号为rtt_series
def fft_periodicity_checker(probe, dest, rtt_series):
    sig = rtt_series
    #最先确定的是采样率，采样率确定意味着两方面的事情。
    #1.时间轴：确定每隔多久对信号采样一次，即离散化的时域轴的间隔确定，但是总长没定。
    #2.频率轴：的总长确定了，为采样率的一半，但是间隔没定。
    Fs = 1.0/INTERVAL
    Freq_max = Fs/2

    #之后要确定的是采样的个数，采样的个数的确定也意味着两件事情。
    #1.时间轴：采样的总时间确定了,配合上面的间隔，也就全定了。
    #2.频率轴：频率轴的间隔定了，配合上面的总长，也就全定了。
    N = fft_size = len(sig)        # 即：FFT_SIZE
    t = np.arange(0,N)*INTERVAL
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
            freqs_xticks_inverse.append(round(1/f/60.0,2))
    print "freqs_xticks_inverse:", freqs_xticks_inverse

    #画出时间域的幅度图
    plt.subplot(211)
    print "In the 1st figure:"
    print "x-axis =", np.arange(1,N+1)
    print "y-axis =", sig
    plt.plot(np.arange(1,N+1),sig,'black')
    plt.xlabel(r"\textrm{experiment number}", font)
    plt.ylabel(r"\textrm{rtt (ms)}", font)
    plt.xticks(fontsize=30, fontname='Times New Roman')
    plt.yticks(fontsize=30, fontname='Times New Roman')
    plt.xlim(0,len(sig))

    #画出频域图
    plt.subplot(212)
    print "In the 2nd figure:"
    print "x-axis =", freq
    print "y-axis =", 2*np.abs(fft_sig)
    print "len of x-axis =", len(freq)
    plt.plot(freq,2*np.abs(fft_sig),'black')#如果用db作单位则20*np.log10(2*np.abs(fft_sig))
    if FFT_XAXIS == 'HZ':
        plt.xlabel(r"\textrm{frequency(Hz)}", font)
        plt.xticks(fontsize=30, fontname='Times New Roman')
    elif FFT_XAXIS == 'min':
        plt.xlabel(r"\textrm{interval (min)}", font)
        plt.xticks(freq, freqs_xticks_inverse, fontsize=10, fontname='Times New Roman')
    plt.ylabel(r"\textrm{proportion}", font)
    plt.yticks(fontsize=30, fontname='Times New Roman')
    plt.xlim(0,Freq_max)
    plt.savefig(os.path.join(RESULT_FIGURES_PATH, VERIFY_MODE, probe, RTT_TYPE, "{0}_{1}_{2}_periodicity_result.eps".format(probe,dest,VERIFY_MODE)), dpi=300, transparent=True)
    # 每画一次图一定要 close 掉 ！！否则会不停叠加 ！！
    plt.close()
    # plt.show()

# 用Autocorrelation 求 periodicity，要计算的原始信号为rtt_series
def autocorr_periodicity_checker(probe, dest, rtt_series):
    x = [float(rtt) for rtt in rtt_series]
    # 计算从k＝1 到 k＝experiment number-1 阶的auto-correlation，
    # 因为 k＝experiment number-1 时计算的已是X(1)和X(n)间的相关性了，
    # k ＝ experiment number的相关性不存在或无法计算，
    # 但实际看几阶相关，周期为几时只看 experiment number/2 即可，后半程无意义，因为2个X序列已无交集
    lags = len(x)-1
    n = N = len(x)
    x = np.array(x)
    print "x =", x
    correlation_result = [np.correlate(x[i:]-x[i:].mean(), x[:n-i]-x[:n-i].mean())[0]/(x[i:].std()*x[:n-i].std()*(n-i))
                          for i in range(1,lags+1)]

    print "correlation_result:", correlation_result
    print "np.arange(1,N) length:", len(np.arange(1,N))
    print "correlation_result length:", len(correlation_result)
    plt.plot(np.arange(1,N), correlation_result, 'black')
    plt.xlim(1, len(np.arange(1,N))/2)
    # plt.ylim(-0.4, 0.61)
    plt.xlabel("order from 1 to n/2-1", font)
    plt.ylabel("coefficient of Auto-correlation", font)
    plt.xticks(fontsize=40, fontname='Times New Roman')
    plt.yticks(fontsize=40, fontname='Times New Roman')
    plt.savefig(os.path.join(RESULT_FIGURES_PATH, VERIFY_MODE, probe, RTT_TYPE, "{0}_{1}_{2}_periodicity_result.eps".format(probe,dest,VERIFY_MODE)), dpi=300, transparent=True)
    # 每画一次图一定要 close 掉 ！！否则会不停叠加 ！！
    plt.close()
    # plt.show()


if __name__ == "__main__":
    # 求指定好的单个 <probe,dest> 的periodicity时用此句
    # rtt_series_periodicity_checker(PROBE, DEST, RTT_TYPE)

    # 批量生成文件时用以下语句：
    with open(TARGET_CSV_FILE) as f_handler:
        next(f_handler)
        for line in f_handler:
            dest = line.split(';')[0]
            probe = line.split(';')[1]
            rtt_series_periodicity_checker(probe, dest, RTT_TYPE)
