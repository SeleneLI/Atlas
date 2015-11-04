# -*- coding: utf-8 -*-
# 本script功能：
# 基于 $HOME/Documents/Codes/Atlas/figures_and_tables 中存储的各实验下的PING_IPv4_report.csv文件而进行的更深入分析
__author__ = 'yueli'

from config.config import *
import numpy as np
import re

# ==========================================Section: constant variable declaration======================================


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
        return [target_list.index(min(target_list))]
    # 如果 identical_elements_value_list is not None
    else:
        # 如果 identical_elements_value_list 中的元素 不是 target_list 中的最小值
        # 那就直接返回 target_list 最小值的index即可
        if identical_elements_value_list[0] != min(target_list):
            return [target_list.index(min(target_list))]
        # 如果 identical_elements_value_list 中的元素 就是 target_list 中的最小值
        # 那就需要返回 identical_elements_index_list，因为它记录了多个最小值的 index 的 list
        else:
            return identical_elements_index_list