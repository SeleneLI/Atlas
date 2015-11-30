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

    r = robjects.r
    r('library("dtw")')
    idx = r.seq(0,6.28,len=100)
    x = [1, 2, 3, 4]
    print x

    y = [1.5, 2.5, 3.5, 4.5]
    print y

    z = [2, 3, 4, 5]
    print z

    alignment = r.dtw(x, y, keep=True)
    dist1 = alignment.rx('distance')[0][0]
    print(dist1)

    alignment = r.dtw(y, z, keep=True)
    dist2 = alignment.rx('distance')[0][0]
    print(dist2)

    alignment = r.dtw(x, z, keep=True)
    dist3 = alignment.rx('distance')[0][0]
    print(dist3)




