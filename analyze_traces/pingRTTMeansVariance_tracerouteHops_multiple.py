# -*- coding: utf-8 -*-
# 本script功能：
# 为分析Atlas自带的Built-in Measurements而写。针对不同probes ping 同一目的地，可以计算各自的平均值(mean)和方差(variance)；
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

    "37.49.233.130": "6118",
    "137.194.165.62": "13842",
    "82.123.188.59": "16958",
    "82.123.244.192": "16958",
    "132.227.120.130": "22341"
}

# EXPERIMENT_NAME 为实验起个名字，会作为存储和生成trace的自文件夹名称
# TARGET_JSON_TRACES_DIR 为要分析的trace的path
# ANALYZED_TRACE_FILE 为分析完要以.csv形式存储的文件path
EXPERIMENT_NAME = '2_probes_Lyon_anchor'
TARGET_JSON_TRACES_DIR = os.path.join(ATLAS_TRACES, 'Produced_traces', EXPERIMENT_NAME)
ANALYZED_TRACE_FILE = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME)


# 定义本次实验所涉及到的probe id (PROBE_IDS)以及相关实验的measurement id (PING_V4_MES_IDS)，要么均以list形式直接给出
# 要么会把纯id以每行一个的形式存在.txt文档里，由mes_id_ping_record_file调出进行处理后转换成list的形式赋值给PING_V4_MES_IDS
# 在更改了probe后，还应在函数generate_report中更改相应的在.csv中要显示的和计算的信息
PROBE_IDS = ['22341', '13842']
# IPv4 -- ping
# 以下方式二选一，一为直接给出list of probe id，二为读取.txt文档获得
# PING_V4_MES_IDS = ['2841000', '2841002', '2841004', '2841006']
mes_id_ping_record_file = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, EXPERIMENT_NAME, '{0}_measurement_ids_ping.txt'.format(EXPERIMENT_NAME))
with open(mes_id_ping_record_file) as f_handler:
    PING_V4_MES_IDS = [i.strip() for i in f_handler.readlines()] # .strip()用于去掉跟在measurement id后面的换行符

# IPv4 -- traceroute
# 以下方式二选一，一为直接给出list of probe id，二为读取.txt文档获得
# TRACEROUTE_V4_MES_IDS = ['2841001', '2841003', '2841005', '2841007']
mes_id_traceroute_record_file = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, EXPERIMENT_NAME, '{0}_measurement_ids_traceroute.txt'.format(EXPERIMENT_NAME))
with open(mes_id_traceroute_record_file) as f_handler:
    TRACEROUTE_V4_MES_IDS = [i.strip() for i in f_handler.readlines()] # .strip()用于去掉跟在measurement id后面的换行符

# ======================================================================================================================
def ping_traces_resume(mes_id, probe_ids):
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
        # Retrieve the min RTT for each ping and then get the average value
        for element in json_data:
            if PROBE_ID_IP_DICT[element['from']] in rtt_probes_dict.keys():
                rtt_probes_dict[PROBE_ID_IP_DICT[element['from']]].append(element['min'])

    for key in rtt_probes_dict.keys():
        rtt_probes_dict[key].append(np.mean(rtt_probes_dict[key]))
        # 因为我们把means存在了 rtt_probes_dict[key] list中的最后一个元素，为了不影响下一行求std的结果，
        # std的input范围应不包含list的最后一个元素即means值本身，[:-1] 即表示从list的第一个元素到倒数第二个元素
        rtt_probes_dict[key].append(np.std(rtt_probes_dict[key][:-1]))
        dst_addr = str(json_data[0]["dst_addr"])

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


def generate_report(mes_ids, probe_ids, command, name):
    """
        Given a list of mesurement id and a list of probe id, generate a report of format CSV
    """

    if command == "PING":
        report_name_ping = os.path.join(ANALYZED_TRACE_FILE, "{0}_{1}_report.csv".format(command, name))
        # 检查是否有 os.path.join(ANALYZED_TRACE_FILE) 存在，部存在的话creat
        try:
            os.stat(os.path.join(ANALYZED_TRACE_FILE))
        except:
            os.mkdir(os.path.join(ANALYZED_TRACE_FILE))

        with open(report_name_ping, 'wb') as f_handler:
            a = csv.writer(f_handler, dialect='excel', delimiter=";")
            a.writerow(
                [
                    'mesurement id', 'Destination',
                    'avg(min RTT) from LISP-Lab', 'avg(min RTT) from mPlane',
                    'variace from LISP-Lab', 'variace from mPlane']
            )
            for mes_id in mes_ids:
                output_row = [mes_id]
                dst_addr, rtt_probes_dict = ping_traces_resume(mes_id, probe_ids)
                output_row.append(dst_addr)
                avg_min_lispLab = avg_min_mPlane = avg_min_FranceIX = avg_min_rmd = \
                    std_lispLab = std_mPlane = std_FranceIX = std_rmd = 0
                for key in rtt_probes_dict.keys():
                    if key == '22341':
                        avg_min_lispLab = rtt_probes_dict[key][-2]
                        std_lispLab = rtt_probes_dict[key][-1]
                    elif key == '13842':
                        avg_min_mPlane = rtt_probes_dict[key][-2]
                        std_mPlane = rtt_probes_dict[key][-1]
                    elif key == '6118':
                        avg_min_FranceIX = rtt_probes_dict[key][-2]
                        std_FranceIX = rtt_probes_dict[key][-1]
                    elif key == '16958':
                        avg_min_rmd = rtt_probes_dict[key][-2]
                        std_rmd = rtt_probes_dict[key][-1]

                output_row.append(avg_min_lispLab)
                output_row.append(avg_min_mPlane)
                #output_row.append(avg_min_FranceIX)
                #output_row.append(avg_min_rmd)
                output_row.append(std_lispLab)
                output_row.append(std_mPlane)
                #output_row.append(std_FranceIX)
                #output_row.append(std_rmd)
                a.writerow(output_row)

    if command == "TRACEROUTE":
        report_name_traceroute = os.path.join(ANALYZED_TRACE_FILE, "{0}_{1}_report.csv".format(command, name))
        # 检查是否有 os.path.join(ANALYZED_TRACE_FILE) 存在，部存在的话creat
        try:
            os.stat(os.path.join(ANALYZED_TRACE_FILE))
        except:
            os.mkdir(os.path.join(ANALYZED_TRACE_FILE))

        with open(report_name_traceroute, 'wb') as f_handler:
            a = csv.writer(f_handler, dialect='excel', delimiter=";")
            a.writerow(['mesurement id', 'target of traceroute',
                        'hops number from LISP-Lab', 'hops number from mPlane'])
            for mes_id in mes_ids:
                output_row = [mes_id]
                dst_addr, hops_number_probes_dict = traceroute_traces_resume(mes_id, probe_ids)
                output_row.append(dst_addr)
                hops_number_LISPLab = hops_number_mPlane = hops_number_FranceIX = hops_number_rmd = 0
                for key in hops_number_probes_dict.keys():
                    if key == '22341':
                        hops_number_LISPLab = hops_number_probes_dict[key]['hops_number']
                    elif key == '13842':
                        hops_number_mPlane = hops_number_probes_dict[key]['hops_number']
                    elif key == '6118':
                        hops_number_FranceIX = hops_number_probes_dict[key]['hops_number']
                    elif key == '16958':
                        hops_number_rmd = hops_number_probes_dict[key]['hops_number']

                output_row.append(hops_number_LISPLab)
                output_row.append(hops_number_mPlane)
                #output_row.append(hops_number_FranceIX)
                #output_row.append(hops_number_rmd)
                a.writerow(output_row)


if __name__ == "__main__":
    generate_report(PING_V4_MES_IDS, PROBE_IDS, "PING", "IPv4")
    generate_report(TRACEROUTE_V4_MES_IDS, PROBE_IDS, "TRACEROUTE", "IPv4")

    # TRACEROUT_V6_MES_IDS = ['6002', '6007', '6017', '6018', '6019', '6020', '6021', '6022']
    # PING_V6_MES_IDS = ['2017', '2019', '2020', '2022']
    # generate_report(TRACEROUT_V6_MES_IDS, PROBE_IDS, "TRACEROUTE", "IPv6")
    # generate_report(PING_V6_MES_IDS, PROBE_IDS, "PING", "IPv6")



