# -*- coding: utf-8 -*-
# The function of this script: try some new methods
__author__ = 'yueli'


from config.config import *
import numpy as np
import scipy.stats as st
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import collections
import pandas as pd
from pandas.tools.plotting import autocorrelation_plot
import ping_associated_analyzer as paa
import scipy as sp
import scipy.stats

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


# ======================================================================================================================
if __name__ == "__main__":
    dict_target = {'MR_1':[2, 5, 5],
                   'MR_2': [5, 5, 5]}
    print correlation_calculator(dict_target)