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
                    if re.match(r'variance', title):
                        variance_list_dict[title.split(' ')[2].strip()] = []
                        index_variance_list.append(index_variance)
                        index_probe_name_dict[index_variance] = title.split(' ')[2].strip()
            else:
                for index in index_variance_list:
                    # 需加float()强制转换，因为直接从 .csv 文件中读出的数值是str类型
                    variance_list_dict[index_probe_name_dict[index]].append(float(line.split(';')[index].strip()))

    # 依次算出 variance_list_dict 各个key包含的list的平均值赋给 means_of_variance_dict，最终返回回去
    for key in variance_list_dict.keys():
        means_of_variance_dict[key] = np.mean(variance_list_dict[key])

    return means_of_variance_dict




if __name__ == "__main__":
    print means_of_variance_calculator(TARGET_CSV_TRACES)