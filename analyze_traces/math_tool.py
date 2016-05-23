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

# ==========================================Section: constant variable declaration======================================
EXPERIMENT_NAME = '4_probes_to_alexa_top50'

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


