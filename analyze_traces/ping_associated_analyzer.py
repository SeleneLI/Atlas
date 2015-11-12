# -*- coding: utf-8 -*-
# 本script功能：
# 基于 $HOME/Documents/Codes/Atlas/figures_and_tables 中存储的各实验下的PING_IPv4_report.csv文件而进行的更深入分析
__author__ = 'yueli'

from config.config import *
import numpy as np
import re
import math_tool as math_tool


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
EXPERIMENT_NAME = '4_probes_to_alexa_top50'
TARGET_CSV_TRACES = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'PING_IPv4_report_avg.csv')

# ======================================================================================================================
# 此函数对targeted_file进行计算处理，可得到每个probe在整个实验中的variance的平均数
# input: targeted_file
# output: dict={'probe_name': means of variance}
def means_of_variance_calculator(targeted_file):
    # .csv文件中以probe为key，以其每个不同measurement id所对应的variance值即纵列数值所组成的list记录下来方便最后计算mean
    variance_list_dict = {}
    # 以probe为key，每个key所对应的value只有一个值，即各自的variance平均值
    means_of_variance_dict = {}
    index_probe_name_dict = {}
    index_variance_list = []

    with open(targeted_file) as f_handler:
        for line in f_handler:
            # 通过第一行把这个 .csv 文件中存在的与 variance 相关的 probe 名称都取出来，作为 means_of_variance_dict 的 keys
            if line.split(';')[0] == 'mesurement id':
                index_variance = -1
                for title in line.split(';'):
                    index_variance = index_variance + 1
                    # 找到含有'variance'的那几列
                    if re.match(r'variance', title):
                        variance_list_dict[title.split(' ')[2].strip()] = []
                        # 用 index_variance_list 来记录含有 variance 值的是哪几列
                        index_variance_list.append(index_variance)
                        # index 和 probe name 的对应关系
                        index_probe_name_dict[index_variance] = title.split(' ')[2].strip()
            else:
                # 在每行中，都需要对目标列进行循环，把数值依次写入可记录variance的字典中
                for index in index_variance_list:
                    # 需加float()强制转换，因为直接从 .csv 文件中读出的数值是str类型
                    variance_list_dict[index_probe_name_dict[index]].append(float(line.split(';')[index].strip()))

    # 依次算出 variance_list_dict 各个key包含的list的平均值赋给 means_of_variance_dict，最终返回回去
    for key in variance_list_dict.keys():
        means_of_variance_dict[key] = np.mean(variance_list_dict[key])

    return means_of_variance_dict


# ======================================================================================================================
# 此函数会挑出4个probes ping 同一个dest时平均RTT最小的那个probe
# 针对 target file 计算出每个probe共有多少次是RTT最小的，最后除以ping过的dest数求出百分比
# input: targeted_file
# output: dict={'probe_name': RTT最小的次数（或百分比）}
def minimum_rtt_calculator(targeted_file):
    min_rtt_dict = {}
    index__rtt_list = []
    index_probe_name_dict = {}

    with open(targeted_file) as f_handler:
        for line in f_handler:
            # 通过第一行把这个 .csv 文件中存在的与 variance 相关的 probe 名称都取出来，作为 means_of_variance_dict 的 keys
            if line.split(';')[0] == 'mesurement id':
                index_rtt = -1
                for title in line.split(';'):
                    index_rtt = index_rtt + 1
                    # 找到含有'avg'的那几列
                    if re.match(r'avg', title):
                        min_rtt_dict[title.split(' ')[3].strip()] = 0
                        # 用 index_variance_list 来记录含有 variance 值的是哪几列
                        index__rtt_list.append(index_rtt)
                        # index 和 probe name 的对应关系
                        index_probe_name_dict[index_rtt] = title.split(' ')[3].strip()
            else:
                min_rtt_list = []
                # 在每行中，都需要对每个目标probe所产生的最小 RTT 依次写入可记录 min_rtt 的字典中
                for index in index__rtt_list:
                    min_rtt_list.append(float(line.split(';')[index].strip()))
                # 挑出4个probe ping同一dest时（即：每行中）RTT最小的那个
                for index in math_tool.minimum_value_index_explorer(min_rtt_list):
                    min_rtt_dict[index_probe_name_dict[index + index__rtt_list[0]]] += 1

    # 如果只想知道每个 probe 所对应的 RTT 最小的次数，那就注释掉这一步；
    # 如果想知道每个 probe 所对应的 RTT 最小的次数所占百分比，那就通过这一步来计算
    # format(小数, '.2%') 表示把小数转换成对应的百分比，小数点后留2位。
    # 鉴于有可能存在几个 probe ping 同一个 dest 时 RTT 是相同的情况，所以算百分比时不能单纯的只除以 measurement 次数，
    # 而需要除以每个 probe 所对应的 RTT 最小次数的总和
    total_rtt_times = float(sum(min_rtt_dict.values()))
    for key in min_rtt_dict:
        # 若只 run 本 script，可用下语句直接表示出百分比结果，e.g.: 46.00%
        # min_rtt_dict[key] = format(min_rtt_dict[key] / measurement_times, '.2%')
        # 若此函数被调用来画图，则需注释掉上面语句而用下面语句，结果仅显示百分比的数字部分而不加百分号，即：46.00
        min_rtt_dict[key] = round(min_rtt_dict[key] / total_rtt_times * 100, 2)

    return min_rtt_dict

# ======================================================================================================================
# 此函数会挑出4个probes ping 同一个dest时每一时刻的RTT最小的那个probe
# 针对 target file 计算出每个probe共有多少次是RTT最小的，最后除以ping过的dest数求出百分比
# input: targeted_file
# output: dict={'probe_name': RTT最小的次数（或百分比）}
def probes_dest_min_rtt_percentage(targeted_file):

    return None



if __name__ == "__main__":
    print means_of_variance_calculator(TARGET_CSV_TRACES)
    print minimum_rtt_calculator(TARGET_CSV_TRACES)
