# -*- coding: utf-8 -*-
# 本script功能：
# 基于 $HOME/Documents/Codes/Atlas/figures_and_tables 中存储的各实验下的PING_IPv4_report.csv文件而进行的更深入分析
__author__ = 'yueli'

from config.config import *
import numpy as np
import re
import math_tool as math_tool
import pprint
import socket


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
RTT_TYPE = 'avg'
TARGET_CSV_TRACES = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, 'PING_IPv4_report_{0}.csv'.format(RTT_TYPE))
JSON2CSV_FILE = os.path.join(ATLAS_TRACES, 'json2csv', '{0}.csv'.format(EXPERIMENT_NAME))
TARGET_CSV_DIFF = os.path.join(ATLAS_TRACES, 'json2csv', '{0}_{1}.csv'.format(EXPERIMENT_NAME, RTT_TYPE))

# 为计算某一特定 probe 的 correlation 时才需此参数
CORR_PROBE = 'LISP-Lab'     # 'FranceIX' or 'LISP-Lab' or 'mPlane' or 'rmd'

# 计算差值时的参考 probe
REF_PROBE = 'FranceIX'

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
# 此函数可以从读入的 csv 文件中提取出以 probe name 为字典 keys，以 RTT 为字典 values 的字典
# input: targeted_file（会按照文件名格式判断读入 rtt 的方式）
# output: dict{ 'probe_1': [rtt_1, rtt_2, rtt_3, ...],
#               'probe_2': [rtt_1, rtt_2, rtt_3, ...],
#               'probe_3': [rtt_1, rtt_2, rtt_3, ...],
#               'probe_4': [rtt_1, rtt_2, rtt_3, ...]
#                }
def get_probe_rtt_mean_list(targeted_file):
    dict_probe_rtt = {}
    dict_probe_index = {}
    index = -1
    print "get_probe_rtt_mean_list(targeted_file) has been called"

    with open(targeted_file) as f_handler:
        for line in f_handler:
            if line.split(';')[0] == 'mesurement id':
                for title in line.split(';'):
                    index = index + 1
                    if re.match(r'avg', title):
                        dict_probe_rtt[title.split()[3]] = []
                        dict_probe_index[index] = title.split()[3]
            else:
                for index in dict_probe_index.keys():
                    dict_probe_rtt[dict_probe_index[index]].append(float(line.split(';')[index]))

    return dict_probe_rtt


# ======================================================================================================================
# 此函数可以从读入的 csv 文件中提取出以 probe name 为字典 keys，以 RTT 为字典 values 的字典
# input: targeted_file（会按照文件名格式判断读入 rtt 的方式）
# output: dict{ 'probe_1': [rtt_1, rtt_2, rtt_3, ...],
#               'probe_2': [rtt_1, rtt_2, rtt_3, ...],
#               'probe_3': [rtt_1, rtt_2, rtt_3, ...],
#               'probe_4': [rtt_1, rtt_2, rtt_3, ...]
#                }
def get_dest_probe_rtt(targeted_file, dest, rtt_type):
    dict_probe_rtt = {}
    rtt_type_index = {'min': 0, 'avg': 1, 'max': 2}

    with open(targeted_file) as f_handler:
        next(f_handler)
        for line in f_handler:
            if line.split(';')[0] == dest:
                if line.split(';')[1] not in dict_probe_rtt.keys():
                    dict_probe_rtt[line.split(';')[1]] = []
                for element in line.split(';')[2:]:
                    dict_probe_rtt[line.split(';')[1]].append(float(element.split(',')[rtt_type_index[rtt_type]]))

    return dict_probe_rtt




# ======================================================================================================================
# 此函数可以从读入的 csv 文件中提取出所有的 dest 并装入一个 list 中：
# input = target file
# output = [dest_1, dest_2, ..., dest_n]
def get_all_dest(targeted_file):
    dest_list = []

    with open(targeted_file) as f_handler:
        next(f_handler)
        for line in f_handler:
            dest_list.append(line.split(';')[0])

    return list(set(dest_list))



# To get a dictionary of dedicated rtt type for evey destination
# input = target json2csv file
# output = dict{ dict{ [] } }
# input_dict 把从 JSON2CSV_FILE 得到的数据以字典的形式记录下来
"""
    dict_rtt = {'dest_1': {'probe_1': [float(rtt), ..., float(rtt)],
                             'probe_2': [float(rtt), ..., float(rtt)],,
                             'probe_3': [float(rtt), ..., float(rtt)]
                             'probe_4': [float(rtt), ..., float(rtt)]},
                  'dest_2': {'probe_1': [float(rtt), ..., float(rtt)],
                             'probe_2': [float(rtt), ..., float(rtt)],,
                             'probe_3': [float(rtt), ..., float(rtt)]
                             'probe_4': [float(rtt), ..., float(rtt)]},
                  ...
                  }
"""
def get_dict_rtt_from_json2csv_file(target_file, rtt_type):
    # 先根据输入的 rtt_type 找出在dict里存储时的相应 index
    rtt_type_dict = {'min': 0,
                     'avg': 1,
                     'max': 2}

    dict_rtt = {}
    with open(target_file) as f_handler:
        next(f_handler)
        for line in f_handler:
            line_list = line.split(";")
            if line_list[0] not in dict_rtt.keys():
                dict_rtt[line_list[0]] = {}
                dict_rtt[line_list[0]][line_list[1]] = [float(element.split('/')[rtt_type_dict[rtt_type]]) for element in line_list[2:]]
            elif line_list[0] in dict_rtt.keys():
                dict_rtt[line_list[0]][line_list[1]] = [float(element.split('/')[rtt_type_dict[rtt_type]]) for element in line_list[2:]]

    return dict_rtt



# 用 2 种方法分别实现对齐一个 list 的维度
# 第一种方法是对于有缺失值的情况下，用自己所有实验的平均值来填补，corr_align_list_dimension_add(target_file, rtt_type)
# 第二种方法是对于某一probe在某一时刻有缺失时，剔除其余所有probes在此时刻的rtt值，corr_align_list_dimension_remove(target_file, rtt_type)
# 两种方法的具体操作都在 code 中有注释
# input = json2csv file
# output = dict{ dict{ [] } }
def corr_align_list_dimension_add(target_file, rtt_type):
    input_dict = get_dict_rtt_from_json2csv_file(target_file, rtt_type)
    output_dict = {}

    # approach 1: 将 所有的-1.0 以list平均值替代
    # 比如 有这样的字典
    # {
    #   '1.2.3.4':{
    #               'A': [4.0, 8.0, 5.0, 4.3, 7.1, 8,2, -1.0]
    #               'B': [2.0, 6.0, -1.0, 7.3, 1.1, 8,2, 8.6]
    #               'C': [2.0, 6.0, 3.3, 7.3, 1.1, 8,2, 8.6]
    #               'D': [2.0, 6.0, 11.0, 7.3, 1.1, -1.0, 8.6]
    #             }
    # }
    # 由于，坏点(也即是-1.0)的存在，如果我们把A，B，C，D对应的list看作一个矩阵的话，我们想法是把所有-1.0都用其所在行的平均值代替
    # 第一步需要先把所有的-1.0替换成0，这样不会影响计算平均值
    # 最后得到的字典应该是：
    # {
    #   '1.2.3.4':{
    #               'A': [4.0, 8.0, 5.0, 4.3, 7.1, 8,2, 0.0]
    #               'B': [2.0, 6.0, 0.0, 7.3, 1.1, 8,2, 8.6]
    #               'C': [2.0, 6.0, 3.3, 7.3, 1.1, 8,2, 8.6]
    #               'D': [2.0, 6.0, 11.0, 7.3, 1.1, 0.0, 8.6]
    #             }
    # }
    # 接下来，再继续将0替换成平均值
    # {
    #   '1.2.3.4':{
    #               'A': [4.0, 8.0, 5.0, 4.3, 7.1, 8,2, MEAN]
    #               'B': [2.0, 6.0, MEAN, 7.3, 1.1, 8,2, 8.6]
    #               'C': [2.0, 6.0, 3.3, 7.3, 1.1, 8,2, 8.6]
    #               'D': [2.0, 6.0, 11.0, 7.3, 1.1, MEAN, 8.6]
    #             }
    # }
    for dst in input_dict.keys():
        output_dict[dst] = {}
        for probe_name in input_dict[dst].keys():
            # 将输入字典中所有的 -1.0用 0.0 来替换
            input_dict[dst][probe_name] = [0.0 if x == -1.0 else x for x in input_dict[dst][probe_name]]
            # 进一步将所有的零以该行的平均值替换
            input_dict[dst][probe_name] = [np.mean(input_dict[dst][probe_name]) if x == 0.0 else x for x in input_dict[dst][probe_name]]
        # 替换完毕后，得到一个干净的字典，其形式为
        # {
        #   'A': [4.0, 8.0, 5.0, 4.3, 7.1, 8,2, MEAN]
        #   'B': [2.0, 6.0, MEAN, 7.3, 1.1, 8,2, 8.6]
        #   'C': [2.0, 6.0, 3.3, 7.3, 1.1, 8,2, 8.6]
        #   'D': [2.0, 6.0, 11.0, 7.3, 1.1, MEAN, 8.6]
        # }
        # 并对以上字典，调用correlation_calculator()计算平均值
        output_dict[dst] = math_tool.correlation_calculator(input_dict[dst])

    # 以下几行只是为了漂亮地 print 出来，注释与否与最终输出结果无关
    # pprint.pprint(output_dict)
    # for dst in sorted(output_dict.keys(), key=lambda item: socket.inet_aton(item)):
    #     print dst
    #     for probe_name in sorted(output_dict[dst].keys()):
    #         # print '%12s  %36s ' % (probe_name, output_dict[dst][probe_name])
    #         print '\t{:<12}\t{:<36}'.format(probe_name, output_dict[dst][probe_name])
    return output_dict

def corr_align_list_dimension_remove(target_file, rtt_type):
    input_dict = get_dict_rtt_from_json2csv_file(target_file, rtt_type)
    output_dict = {}
    # approach 2: 将 所有的零 所在的列都删除
    # 比如 有这样的字典
    # {
    #   '1.2.3.4':{
    #               'A': [4.0, 8.0, 5.0, 4.3, 7.1, 8,2, -1.0]
    #               'B': [2.0, 6.0, -1.0, 7.3, 1.1, 8,2, 8.6]
    #               'C': [2.0, 6.0, 3.3, 7.3, 1.1, 8,2, 8.6]
    #               'D': [2.0, 6.0, 11.0, 7.3, 1.1, -1.0, 8.6]
    #             }
    # }
    # 由于，坏点(也即是-1.0)的存在，如果我们把A，B，C，D对应的list看作一个矩阵的话，我们想法是把含有 -1.0的列都删去
    # 最后得到的字典应该是：
    # {
    #   '1.2.3.4':{
    #               'A': [4.0, 8.0, 4.3, 7.1]
    #               'B': [2.0, 6.0, 7.3, 1.1]
    #               'C': [2.0, 6.0, 7.3, 1.1]
    #               'D': [2.0, 6.0, 7.3, 1.1]
    #             }
    # }

    for dst in input_dict.keys():
        # 针对每一个 destination @Ip 做如下处理
        output_dict[dst] = {}
        # index_list 存放 需要被删除的元素的下标
        index_list = []
        # 以Probe name为key, 遍历一个字典，对应key的value实际上为一个含有RTT数值的list,
        # 找到所有list中元素为-1.0为index,并且存放到一个list中
        for probe_name in input_dict[dst].keys():
            tmp = [n for n, x in enumerate(input_dict[dst][probe_name]) if x == -1.0]
            index_list.extend(tmp)
            # 删除可能重复的下标
        index_list = list(set(index_list))

        for probe_name in input_dict[dst].keys():
            # 我们只保留 下标没有出现在 index_list 中的点，即删除所有坏点以及坏点所在列的其他所有点
            input_dict[dst][probe_name] = [x for i, x in enumerate(input_dict[dst][probe_name]) if i not in index_list]

        # print dst, index_list, len(input_dict[dst][probe_name])
        output_dict[dst] = math_tool.correlation_calculator(input_dict[dst])

    # 以下几行只是为了漂亮地 print 出来，注释与否与最终输出结果无关
    # pprint.pprint(output_dict)
    # for dst in sorted(output_dict.keys(), key=lambda item: socket.inet_aton(item)):
    #     print dst
    #     for probe_name in sorted(output_dict[dst].keys()):
    #         # print '%12s  %36s ' % (probe_name, output_dict[dst][probe_name])
    #         print '\t{:<12}\t{:<36}\t{:<36}'.format(probe_name, output_dict[dst][probe_name], output_dict[dst][probe_name])

    return output_dict


# Pick up the correlation only associated with a dedicated probe
# input = corr_align_list_dimension_add(target_file, rtt_type)
#         or
#         corr_align_list_dimension_remove(target_file, rtt_type)
# output = 只针对某一特定 probe 的 correlation 列表
def pick_up_corr_dedicated_probe(target_file, rtt_type, probe):
    dict_corr_all_probes = corr_align_list_dimension_remove(target_file, rtt_type)
    dict_corr_dedicated_probe = {}

    for key in dict_corr_all_probes.keys():
        dict_corr_dedicated_probe[key] = dict_corr_all_probes[key][probe]

    return dict_corr_dedicated_probe



# 此函数对已得到的针对某一特定 probe 的 correlation 列表求平均值
# input = pick_up_corr_dedicated_probe(JSON2CSV_FILE, RTT_TYPE, CORR_PROBE)
# output = [FranceIX_LISP-Lab_correlation, LISP-Lab_LISP-Lab_correlation, mPlane_LISP-Lab_correlation, rmd_LISP-Lab_correlation, ]
def means_correlation(target_file, rtt_type, probe):
    dict_corr_dedicated_probe = pick_up_corr_dedicated_probe(target_file, rtt_type, probe)
    matrix_corr = np.mat(dict_corr_dedicated_probe.values())

    print "Means of correlation for {0} to all the other probes:".format(probe)
    return matrix_corr.mean(0)



# 此函数以 FranceIX 为参考计算其差值，可以返回 means 和 variance
# input = { 'probe_1': [],
#           'probe_2': [],
#           'probe_3': [],
#           'probe_4': [],
#                           },
#           ref_probe   # 以哪个 probe 为参考对象点
# output:
#       dict_mean = { 'probe_1': mean_1,
#                     'probe_2': mean_2,
#                     'probe_3': mean_3}
#       dict_var  = { 'probe_1': var_1,
#                     'probe_2': var_2,
#                     'probe_3': var_3}
def difference_calculator_mean_var(target_dict, ref_probe):
    dict_mean = {}
    dict_var = {}

    for key in target_dict.keys():
        if key != ref_probe:
            dict_mean[key] = np.mean(abs(np.matrix(target_dict[key]) - np.matrix(target_dict[ref_probe])).tolist()[0])
            dict_var[key] = np.var(abs(np.matrix(target_dict[key]) - np.matrix(target_dict[ref_probe])).tolist()[0])

    return dict_mean, dict_var



# 此函数从 .csv file 中读入数值并以 dest 为 key 依次调用 difference_calculator(target_dict, ref_probe)
# input = .csv_file
# output:
#       dict_mean = {'probe_1': {'dest_1': mean_1}, {'dest_1': mean_1}, ..., {'dest_1': mean_50},
#                    'probe_2': {'dest_1': mean_1}, {'dest_1': mean_1}, ..., {'dest_1': mean_50},
#                    'probe_3': {'dest_1': mean_1}, {'dest_1': mean_1}, ..., {'dest_1': mean_50}
#                   }
#       dict_var  = {'probe_1': {'dest_1': var_1}, {'dest_1': var_1}, ..., {'dest_1': var_50},
#                    'probe_2': {'dest_1': var_1}, {'dest_1': var_1}, ..., {'dest_1': var_50},
#                    'probe_3': {'dest_1': var_1}, {'dest_1': var_1}, ..., {'dest_1': var_50}
#                   }
def difference_calculator(target_file, ref_probe):

    # 把 .csv_file 里的元素转化到 dict_dest_probe_rtts = {} 里来
    dict_dest_probe_rtts = {}
    with open(target_file) as f_handler:
        next(f_handler)
        for line in f_handler:
            line_list = line.split(";")
            if line_list[0] not in dict_dest_probe_rtts.keys():
                dict_dest_probe_rtts[line_list[0]] = {}
                dict_dest_probe_rtts[line_list[0]][line_list[1]] = [float(element) for element in line_list[2:]]
            elif line_list[0] in dict_dest_probe_rtts.keys():
                dict_dest_probe_rtts[line_list[0]][line_list[1]] = [float(element) for element in line_list[2:]]

    # 依次对 key 调用 difference_calculator(target_dict, ref_probe)
    # 把结果以 probe 为 key 以此记录下来
    dict_probe_dest_mean = {}
    dict_probe_dest_var = {}
    for key_dest in dict_dest_probe_rtts.keys():
        dict_mean_temp, dict_var_temp = difference_calculator_mean_var(dict_dest_probe_rtts[key_dest], ref_probe)
        for key_probe in dict_mean_temp.keys():
            if key_probe not in dict_probe_dest_mean.keys():
                dict_probe_dest_mean[key_probe] = {}
                dict_probe_dest_mean[key_probe][key_dest] = dict_mean_temp[key_probe]
                dict_probe_dest_var[key_probe] = {}
                dict_probe_dest_var[key_probe][key_dest] = dict_var_temp[key_probe]
            else:
                dict_probe_dest_mean[key_probe][key_dest] = dict_mean_temp[key_probe]
                dict_probe_dest_var[key_probe][key_dest] = dict_var_temp[key_probe]


    print "dict_probe_dest_mean =", dict_probe_dest_mean
    print "dict_probe_dest_var =", dict_probe_dest_var
    return dict_probe_dest_mean, dict_probe_dest_var




if __name__ == "__main__":
    # print means_of_variance_calculator(TARGET_CSV_TRACES)
    # print minimum_rtt_calculator(TARGET_CSV_TRACES)
    # print math_tool.correlation_calculator(get_probe_rtt_mean_list(TARGET_CSV_TRACES))

    # print corr_align_list_dimension_add(JSON2CSV_FILE, RTT_TYPE)
    # print corr_align_list_dimension_remove(JSON2CSV_FILE, RTT_TYPE)
    # print pick_up_corr_dedicated_probe(JSON2CSV_FILE, RTT_TYPE, CORR_PROBE)
    # print means_correlation(JSON2CSV_FILE, RTT_TYPE, CORR_PROBE)
    dict_probe_dest_mean = {}
    dict_probe_dest_var = {}
    dict_probe_dest_mean, dict_probe_dest_var = difference_calculator(TARGET_CSV_DIFF, REF_PROBE)
