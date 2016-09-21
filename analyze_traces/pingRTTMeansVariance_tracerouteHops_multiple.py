# -*- coding: utf-8 -*-
# 本script功能：
# 为分析Atlas的 traces 而写。针对不同probes ping 同一目的地，可以计算各自的平均值(mean)和方差(variance)；
# 针对不同probes traceroute 同一目的地，可以计算各自的最常用路径的跳数(hops)
# 此script处理得是针对一个measurement id 表示多个probes ping同一个dest
__author__ = 'yueli'

import json
from datetime import datetime
import os
import numpy as np
import csv
from collections import Counter
from config.config import *

# ==========================================Section: constant variable declaration======================================
# probe id和此probe的IP地址间的对应关系
PROBE_ID_IP_DICT = {
    "132.227.120.130": "22341",
    "37.49.234.132": "6118",
    "137.194.165.62": "13842",
    "153.16.38.64": "2403",
    "81.56.47.149": "2848"
}

PROBE_ID_NAME_DICT = {

    "6118"  : "FranceIX",
    "13842" : "mPlane",
    "2403" : "LIP6",
    "22341" : "LISP-Lab",
    "2848": "home"
}
# 需要 generate ping report 还是 traceroute report，写 'PING' 或 'TRACEROUTE'
GENERATE_TYPE = 'ping'  # 'ping' or 'traceroute'
IP_VERSION = 'v4'  # 'v6'
RTT_TYPE = 'avg'    # 'min' or 'max'，当 GENERATE_TYPE = 'TRACEROUTE' 时忽略此变量，什么都不用更改
MES_ID_TYPE = 'txt'     # 'list' or 'txt'
MES_ID_LIST = ['2841000', '2841002', '2841003']    # 只有当 MES_ID_TYPE = 'list' 时，此参数才有用。即指定处理哪几个实验
CALCULATE_TYPE = 'median'   # 'mean' or 'median'

# EXPERIMENT_NAME 为实验起个名字，会作为存储和生成trace的子文件夹名称
# TARGET_JSON_TRACES_DIR 为要分析的trace的path
# ANALYZED_TRACE_FILE 为分析完要以.csv形式存储的文件path
EXPERIMENT_NAME = '5_probes_to_alexa_top500'
TARGET_JSON_TRACES_DIR = os.path.join(ATLAS_TRACES, 'Produced_traces', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION))
ANALYZED_TRACE_FILE = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION))


# ======================================================================================================================
# 此函数从只存有 measurement_id 的.txt文档里读出所有的 measurement_id 以 list 形式返回
# input = ('PING' or 'TRACEROUTE', list' or 'txt')
# output = list of measurement id
def get_measurement_id_list(generate_type, mes_id_type):
    if mes_id_type == 'txt':
        if generate_type == 'PING':
            mes_id_ping_record_file = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, EXPERIMENT_NAME, '{0}_ping_measurement_ids_complete.txt'.format(EXPERIMENT_NAME))
            with open(mes_id_ping_record_file) as f_handler:
                PING_V4_MES_IDS = [i.strip() for i in f_handler.readlines()] # .strip()用于去掉跟在measurement id后面的换行符
            return PING_V4_MES_IDS
        elif generate_type == 'TRACEROUTE':
            mes_id_traceroute_record_file = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, EXPERIMENT_NAME, '{0}_traceroute_measurement_ids_complete.txt'.format(EXPERIMENT_NAME))
            with open(mes_id_traceroute_record_file) as f_handler:
                TRACEROUTE_V4_MES_IDS = [i.strip() for i in f_handler.readlines()] # .strip()用于去掉跟在measurement id后面的换行符
            return TRACEROUTE_V4_MES_IDS

    elif mes_id_type == 'list':
        return MES_ID_LIST

    else:
        print "Wrong MES_ID_TYPE !! It should be 'list' or 'txt'"



# ======================================================================================================================
# 此函数按照 measurement_id 和 probe_id 以及 RTT 类型把针对某一 dest 的各 probe 的 rtt 按照字典形式表示出来
# input = measurement_id, probe_id 和 RTT type
# output = dest, {'probe_1': [rtt_1, rtt_2, rtt_3, ...],
#                 'probe_2': [rtt_1, rtt_2, rtt_3, ...],
#                 'probe_3': [rtt_1, rtt_2, rtt_3, ...],
#                 'probe_4': [rtt_1, rtt_2, rtt_3, ...]
#                 }
def ping_traces_resume(mes_id, probe_ids, rtt_type):
    # 要处理的traces来源
    file_name = os.path.join(TARGET_JSON_TRACES_DIR, "{0}.json".format(mes_id))
    dst_addr = ""
    # src_addr = ""
    # avg_min = float('inf')
    # std = float('inf')
    rtt_probes_dict = {}
    for probe in probe_ids:
        rtt_probes_dict[probe] = []

    with open(file_name) as f_handler:
        # The obtained 'json_data' is of type 'list'. Thus we can use list comprehension to generate the list of min
        # RTT value
        json_data = json.load(f_handler)
        # Since it is possible that a given file is an empty file
        # (Actually, this 'empty' file contains just a pair of square bracket.).
        # Thus, it is necessary to verify whether the input file is empty before further processing.
        # In addition, in case of empty input file, the retured dictionary is empty, which is equivalent to 'False'
        # in python.
    if len(json_data) != 0:
        # Retrieve the min/avg/max RTT for each ping and then get the average value
        for element in json_data:
            if PROBE_ID_IP_DICT[element['from']] in rtt_probes_dict.keys():
                # 如果‘avg’的值为不为-1，那么我们把'avg'的value存到list里
                if element[rtt_type] != -1:
                    rtt_probes_dict[PROBE_ID_IP_DICT[element['from']]].append(element[rtt_type])
                # 如果为-1，那么我们则添加一个0到list里面，一则是避免出现list最后为empty的情况
                # 因为对empty list调用np.mean(), 会发出警告， 二则是避免-1对平均值的影响
                else:
                    rtt_probes_dict[PROBE_ID_IP_DICT[element['from']]].append(0)

    print rtt_probes_dict
    for key in rtt_probes_dict.keys():
        # 按照 CALCULATE_TYPE 计算相应结果
        if CALCULATE_TYPE == 'mean':
            rtt_probes_dict[key].append(round(np.mean(rtt_probes_dict[key]), 2))
        elif CALCULATE_TYPE == 'median':
            rtt_probes_dict[key].append(round(np.median(rtt_probes_dict[key]), 2))
        # 因为我们把means存在了 rtt_probes_dict[key] list中的最后一个元素，为了不影响下一行求std的结果，
        # std的input范围应不包含list的最后一个元素即means值本身，[:-1] 即表示从list的第一个元素到倒数第二个元素
        rtt_probes_dict[key].append(round(np.std(rtt_probes_dict[key][:-1]), 2))
        dst_addr = str(json_data[0]["dst_addr"])


    print "dest ---->", dst_addr
    return dst_addr, rtt_probes_dict



def traceroute_traces_resume(mes_id, probe_ids):
    """
        Since we can not directly get the desired information from the inital JSON file, we need resume a given JSON to list
        the measurement id to which the JSON file corresponds, the destination of traceroute command, the source
        destination of traceroute, etc.

        In terms of input, this function just take two parameters:
            @mes_id, type of str, represents the measurement id to which the JSON file corresponds
            @prob_id, type of str, represents the probe id to which the JSON file corresponds

        Given that the JSON file's name respects to a fixed pattern, for example:
            RIPE-Atlas-measurement-1017-probe-13842.json
        we can easily construct the file name if mesurement id and probe id are both given.

    """
    # 要处理的traces来源
    file_name = os.path.join(TARGET_JSON_TRACES_DIR, "{0}.json".format(mes_id))
    frequent_route_list = []
    dst_adr = ""
    # src_addr = ""
    hops_number = 0
    hops_number_probes_dict = {}
    for probe in probe_ids:
        hops_number_probes_dict[probe] = {'frequent_route_list': []}

    with open(file_name) as f_handler:
        json_data = json.load(f_handler)
        if len(json_data) != 0:
            dst_adr = json_data[0]['dst_addr']
            # src_addr = json_data[0]["src_addr"]
            for record in json_data:
                if PROBE_ID_IP_DICT[record['from']] in hops_number_probes_dict.keys():
                    hops_number_probes_dict[PROBE_ID_IP_DICT[record['from']]]['exp_date'] = datetime.fromtimestamp(int(record["timestamp"])).strftime('%Y-%m-%d %H:%M')
                    hops_number_probes_dict[PROBE_ID_IP_DICT[record['from']]]['src_addr'] = record["src_addr"]
                    hops_number_probes_dict[PROBE_ID_IP_DICT[record['from']]]['dst_adr'] = record['dst_addr']
                    hops_number_probes_dict[PROBE_ID_IP_DICT[record['from']]]['hop_list'] = record['result']

                    # exp_date = datetime.fromtimestamp(int(record["timestamp"])).strftime('%Y-%m-%d %H:%M')
                    # src_addr = record["src_addr"]
                    # dst_adr = record['dst_addr']
                    # hop_list = record['result']
                    # print hop_list
                    hops_number_probes_dict[PROBE_ID_IP_DICT[record['from']]]['hop_list'] = [retrieve_traversed_ip(hop['result']) for hop in hops_number_probes_dict[PROBE_ID_IP_DICT[record['from']]]['hop_list']]
                    # print hops_number_probes_dict[PROBE_ID_IP_DICT[record['from']]]['exp_date'], hops_number_probes_dict[PROBE_ID_IP_DICT[record['from']]]['src_addr'], dst_adr, "->".join(hops_number_probes_dict[PROBE_ID_IP_DICT[record['from']]]['hop_list'])
                    hops_number_probes_dict[PROBE_ID_IP_DICT[record['from']]]['frequent_route_list'].append("->".join(hops_number_probes_dict[PROBE_ID_IP_DICT[record['from']]]['hop_list']))

    # we can rely the most_common() method to find out the most occurrences of routes
    # The output of most_common() is a list of tuple
    if len(json_data) != 0:
        for probe in probe_ids:
            # print Counter(hops_number_probes_dict[probe]['frequent_route_list']).most_common(1)[0][0]
            hops_number_probes_dict[probe]['hops_number'] = len(Counter(hops_number_probes_dict[probe]['frequent_route_list']).most_common(1)[0][0].split("->"))

    return dst_adr, hops_number_probes_dict
    # http://customer.xfinity.com/help-and-support/internet/run-traceroute-command/ 该Link 对某一行中偶尔出现的星号
    # 进行了解释, 简单来说就是，如果 originator 在 规定的timeout时间内没有收到回复，则输出星号，表示没有收到回复。


def retrieve_traversed_ip(results):
    """
        Retrive the traversed IP address from a given list of dictionary
    """
    res = "*"
    for icmp_reply in results:
        if "from" in icmp_reply.keys():
            return icmp_reply['from']
    # If no ICMP reply record contains key "from", means all the ICMP reply timeout, return symbol of star
    return res



# ======================================================================================================================
# 此函数用于产生 .csv 文件
def generate_report(mes_ids, probe_ids, command, name, rtt_type):
    """
        Given a list of mesurement id and a list of probe id, generate a report of format CSV
    """
    probe_name_list = PROBE_ID_NAME_DICT.values()


    if command == "PING":
        report_name_ping = os.path.join(ANALYZED_TRACE_FILE, EXPERIMENT_NAME, "{0}_{1}_report_{2}_{3}.csv".format(command, name, rtt_type, CALCULATE_TYPE))
        # 检查是否有 os.path.join(ANALYZED_TRACE_FILE) 存在，部存在的话create
        try:
            os.stat(os.path.join(ANALYZED_TRACE_FILE))
        except:
            os.mkdir(os.path.join(ANALYZED_TRACE_FILE))


        with open(report_name_ping, 'wb') as f_handler:
            a = csv.writer(f_handler, dialect='excel', delimiter=";")
            csv_title = ['mesurement id', 'Destination']
            csv_title.extend(
                ["avg({0} RTT) from {1}".format(rtt_type, probe_name) for probe_name in probe_name_list ]
            )
            csv_title.extend(
                ["variance from {1}".format(rtt_type, probe_name) for probe_name in probe_name_list]
            )
            a.writerow(csv_title)
            success_ping_mes_id_file = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, EXPERIMENT_NAME, '{0}_ping_measurement_ids_success.txt'.format(EXPERIMENT_NAME))
            f = open(success_ping_mes_id_file, 'w')
            for mes_id in mes_ids:
                output_row = [mes_id]
                dst_addr, rtt_probes_dict = ping_traces_resume(mes_id, probe_ids, rtt_type)
                output_row.append(dst_addr)

                # e.g. probe_name_list = ["FranceIX", "mPlane", "rmd", "LISP-Lab"]
                for probe_name in probe_name_list:
                    # for example , rtt_probes_dict.keys() may be ["6118", "13842", "16958", "22341"]
                    for key in rtt_probes_dict.keys():
                        if PROBE_ID_NAME_DICT[key] == probe_name:
                            output_row.append(rtt_probes_dict[key][-2])

                #上述循环结束之后，output_row(注：类型为list) 会增加 len(probe_name_list) 个元素，每个元素均为RTT值，
                #且和CSV开头的title中的出现的Probe的顺序一致
                #举例说明：假如CSV开头的title为：
                #avg(avg RTT) from LISP-Lab; avg(avg RTT) from mPlane; avg(avg RTT) from FranceIX; avg(avg RTT) from rmd
                #那么output_row新添加的四个元素，分别是这几个 Probe 下实验得到的 RTT 值

                for probe_name in probe_name_list:
                    for key in rtt_probes_dict.keys():
                        if PROBE_ID_NAME_DICT[key] == probe_name:
                            output_row.append(rtt_probes_dict[key][-1])
                # 设定一个 写操作的flag, 其默认值为 1，接下来该flag会通过循环依次于output_row中RTT元素依次进行 与操作
                # 如任意一个Probe对应的 RTT值为0，则write_flag会被设置成0
                write_flag = 1

                for rtt in output_row[2:len(probe_name_list)+2]:
                    write_flag = write_flag and rtt

                # 去掉 avg 有 0 的那一列，即：针对某一 dest，如果至少有一个 probe 没有 ping 通，则把这个 dest 不考虑在内
                if write_flag != 0:
                    a.writerow(output_row)
                    # 把能 ping 通的所有 measurement id 记录到一个新的 .txt 文件中，方便后续实验处理
                    f.write(str(mes_id)+'\n')
                    print mes_id
            f.close()

    if command == "TRACEROUTE":
        report_name_traceroute = os.path.join(ANALYZED_TRACE_FILE, EXPERIMENT_NAME, "{0}_{1}_report.csv".format(command, name))
        # 检查是否有 os.path.join(ANALYZED_TRACE_FILE) 存在，不存在的话creat
        try:
            os.stat(os.path.join(ANALYZED_TRACE_FILE))
        except:
            os.mkdir(os.path.join(ANALYZED_TRACE_FILE))

        with open(report_name_traceroute, 'wb') as f_handler:
            a = csv.writer(f_handler, dialect='excel', delimiter=";")
            csv_title = ['mesurement id', 'target of traceroute']
            csv_title.extend(
                ["hops number from {0}".format(probe_name) for probe_name in probe_name_list]
            )
            a.writerow(csv_title)

            for mes_id in mes_ids:
                output_row = [mes_id]
                dst_addr, hops_number_probes_dict = traceroute_traces_resume(mes_id, probe_ids)
                output_row.append(dst_addr)

                # e.g. probe_name_list = ["FranceIX", "mPlane", "rmd", "LISP-Lab"]
                for probe_name in probe_name_list:
                    # for example , rtt_probes_dict.keys() may be ["6118", "13842", "16958", "22341"]
                    for key in hops_number_probes_dict.keys():
                        if PROBE_ID_NAME_DICT[key] == probe_name:
                            output_row.append(hops_number_probes_dict[key]['hops_number'])

                a.writerow(output_row)


if __name__ == "__main__":
    if GENERATE_TYPE == 'PING':
        generate_report(get_measurement_id_list(GENERATE_TYPE, MES_ID_TYPE), PROBE_ID_IP_DICT.values(), GENERATE_TYPE, IP_VERSION, RTT_TYPE)
    elif GENERATE_TYPE == 'TRACEROUTE':
        generate_report(get_measurement_id_list(GENERATE_TYPE, MES_ID_TYPE), PROBE_ID_IP_DICT.values(), GENERATE_TYPE, IP_VERSION, "")
    else:
        print "Generate type should be 'PING' or 'TRACEROUTE' !!"



