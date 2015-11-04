# -*- coding: utf-8 -*-
# 本script功能：
# 基于 $HOME/Documents/Codes/Atlas/figures_and_tables 中存储的各实验下的PING_IPv4_report.csv文件而进行的更深入分析
__author__ = 'yueli'

from config.config import *
import numpy as np
import re


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
EXPERIMENT_NAME = '4_probes_to_alexa_top100'
TARGET_CSV_TRACES = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'PING_IPv4_report.csv')

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
# 此函数会挑出4个probes ping 同一个dest时RTT最小的那个probe
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
                # 在每行中，都需要对目标列进行循环，把数值依次写入可记录variance的字典中
                for index in index__rtt_list:
                    min_rtt_list.append(float(line.split(';')[index].strip()))
                # 挑出4个probe ping同一dest时（即：每行中）RTT最小的那个
                for index in minimum_value_index_explorer(min_rtt_list):
                    min_rtt_dict[index_probe_name_dict[index + index__rtt_list[0]]] += 1
                # min_rtt_dict[index_probe_name_dict[min_rtt_list.index(min(min_rtt_list)) + index__rtt_list[0]]] += 1

    return min_rtt_dict


# ======================================================================================================================
# 此函数会返回一个list中最小值的一个或多个index，
# e.g.: a = [1.0, 2.0, 3.0, 4.0]，则会返回[0]；a = [1.0, 1.0, 3.0, 4.0]，则会返回[0, 1]；a = [1.0, 1.0, 1.0, 1.0]，则会返回[0, 1, 2, 3]；
# input: 含有要处理数据的list
# output: list中最小值的index所组成的list
def minimum_value_index_explorer(target_list):

    # 在 target_list 中挑出有相同数值所对应的 index 而组成的list
    identical_elements_value_list = [value for index, value in enumerate(target_list) if target_list.count(value) > 1]
    identical_elements_index_list = [index for index, value in enumerate(target_list) if target_list.count(value) > 1]

    # 如果 identical_elements_value_list is None
    if len(identical_elements_value_list) == 0:
        print [target_list.index(min(target_list))]
        return [target_list.index(min(target_list))]
    # 如果 identical_elements_value_list is not None
    else:
        # 如果 identical_elements_value_list 中的元素 不是 target_list 中的最小值
        # 那就直接返回 target_list 最小值的index即可
        if identical_elements_value_list[0] != min(target_list):
            print [target_list.index(min(target_list))]
            return [target_list.index(min(target_list))]
        # 如果 identical_elements_value_list 中的元素 就是 target_list 中的最小值
        # 那就需要返回 identical_elements_index_list，因为它记录了多个最小值的 index 的 list
        else:
            print identical_elements_index_list
            return identical_elements_index_list





if __name__ == "__main__":
    # print means_of_variance_calculator(TARGET_CSV_TRACES)
    print minimum_rtt_calculator(TARGET_CSV_TRACES)
