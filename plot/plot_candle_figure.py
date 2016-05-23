# -*- coding: utf-8 -*-
# 本script功能：
# 画关于 candledtick chart 的各种图
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

# 存储路径
FIGURE_PATH = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'candlestick_chart', 'mean_of_RTT_diff_compared_with_{0}'.format(REF_PROBE)) # Needs to change


# 画出从 ping_associated_analyzer.difference_calculator 得到的结果
# 即：以 REF_PROBE 为参考点，其余 probe 与其 RTT 的差值的平均值及方差
def plot_diff_rtt(target_csv, ref_probe):
    dict_probe_dest_mean, dict_probe_dest_var = ping_associated_analyzer.difference_calculator(target_csv, ref_probe)
    for key_probe in dict_probe_dest_mean.keys():
        dest_list = dict_probe_dest_mean[key_probe].keys()
        rtt_list = dict_probe_dest_mean[key_probe].values()

        plt.plot(range(1,len(dest_list)+1), rtt_list)

        # 检查是否有 os.path.join(FIGURE_PATH) 存在，不存在的话creat
        try:
            os.stat(FIGURE_PATH)
        except:
            os.makedirs(FIGURE_PATH)

        plt.savefig(os.path.join(FIGURE_PATH, '{0}_&_{1}.eps'.format(key_probe, REF_PROBE)), dpi=300)
        # 每画一次图一定要 close 掉 ！！否则会不停叠加 ！！
        plt.close()


if __name__ == "__main__":
    plot_diff_rtt(TARGET_CSV_DIFF, REF_PROBE)