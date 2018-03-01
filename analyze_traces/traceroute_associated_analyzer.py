# -*- coding: utf-8 -*-
# 本script功能：
# 基于 $HOME/Documents/Codes/Atlas/figures_and_tables 中存储的各实验下的 TRACEROUTE_IPv4_report.csv文件而进行的更深入分析
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
    "LIP6": "2403",
    "LISP-Lab": "22341",
    "Gandi": "3141"
}

# EXPERIMENT_NAME 为要处理的实验的名字，因为它是存储和生成trace的子文件夹名称
# TARGET_CSV_TRACES 为要分析的trace的文件名
EXPERIMENT_NAME = '5_probes_to_alexa_top510'
GENERATE_TYPE = 'traceroute'  # 'ping' or 'traceroute'
IP_VERSION = 'v4'  # 'v6'
TARGET_CSV_TRACES = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE, IP_VERSION), '{0}_{1}_report.csv'.format(GENERATE_TYPE, IP_VERSION))

# ======================================================================================================================
# 此函数会挑出4个probes traceroute 同一个 dest 时hops数最小的那个probe
# 针对 target file 计算出每个probe共有多少次是hops数最小的，最后除以traceroute过的dest数求出百分比
# input: targeted_file
# output: dict={'probe_name': hops数最小的次数（或百分比）}
def minimum_hops_calculator(targeted_file):
    min_hops_dict = {}
    index__hops_list = []
    index_probe_name_dict = {}

    with open(targeted_file) as f_handler:
        for line in f_handler:
            # 通过第一行把这个 .csv 文件中存在的与 variance 相关的 probe 名称都取出来，作为 means_of_variance_dict 的 keys
            if line.split(';')[0] == 'mesurement id':
                index_hops = -1
                for title in line.split(';'):
                    print "title ==", title
                    index_hops += 1
                    # 找到含有'avg'的那几列
                    if re.match(r'hop', title):
                        min_hops_dict[title.split(' ')[3].strip()] = 0
                        print "min_hops_dict =", min_hops_dict
                        # 用 index_variance_list 来记录含有 variance 值的是哪几列
                        index__hops_list.append(index_hops)
                        print "index__hops_list =", index__hops_list
                        # index 和 probe name 的对应关系
                        index_probe_name_dict[index_hops] = title.split(' ')[3].strip()
                        print "index_probe_name_dict =", index_probe_name_dict
            else:
                min_hops_list = []
                # 在每行中，都需要对每个目标probe所产生的hops数值依次写入可记录 min_hops 的字典中
                for index in index__hops_list:
                    min_hops_list.append(float(line.split(';')[index].strip()))
                # 挑出4个probe traceroute同一dest时（即：每行中）hops 数最小的那个
                for index in math_tool.minimum_value_index_explorer(min_hops_list):
                    min_hops_dict[index_probe_name_dict[index + index__hops_list[0]]] += 1

    # 如果只想知道每个 probe 所对应的 hops 最小的次数，那就注释掉这一步；
    # 如果想知道每个 probe 所对应的 hops 最小的次数所占百分比，那就通过这一步来计算
    # format(小数, '.2%') 表示把小数转换成对应的百分比，小数点后留2位。
    # 鉴于有可能存在几个 probe ping 同一个 dest 时 RTT 是相同的情况，所以算百分比时不能单纯的只除以 measurement 次数，
    # 而需要除以每个 probe 所对应的 hops 最小次数的总和
    total_rtt_times = float(sum(min_hops_dict.values()))
    for key in min_hops_dict:
        # 若只 run 本 script，可用下语句直接表示出百分比结果，e.g.: 46.00%
        # min_hops_dict[key] = format(min_hops_dict[key] / measurement_times, '.2%')
        # 若此函数被调用来画图，则需注释掉上面语句而用下面语句，结果仅显示百分比的数字部分而不加百分号，即：46.00
        min_hops_dict[key] = round(min_hops_dict[key] / total_rtt_times * 100, 2)

    return min_hops_dict




if __name__ == "__main__":
    print "min:", minimum_hops_calculator(TARGET_CSV_TRACES)
