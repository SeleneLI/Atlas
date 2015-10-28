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
PROBE_ID_IP_DICT = {

    "37.49.233.130": "6118",
    "137.194.165.62": "13842",
    "82.123.188.59": "16958",
    "82.123.244.192": "16958",
    "132.227.120.130": "22341"
}

JSON_DIR = os.path.join(ATLAS_TRACES, 'Produced_traces', '4_probes_to_alexa_top100')
# ======================================================================================================================
def ping_traces_resume(mes_id, probe_ids):
    file_path = os.path.join(JSON_DIR, "{0}.json".format(mes_id))
    dst_addr = ""
    src_addr = ""
    avg_min = float('inf')
    std = float('inf')
    rtt_probes_dict = {}
    for probe in probe_ids:
        rtt_probes_dict[probe] = []

    with open(file_path) as f_handler:
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
        # print "np.mean", rtt_probes_dict[key]
        rtt_probes_dict[key].append(np.std(rtt_probes_dict[key]))
        # print "np.std", rtt_probes_dict[key]
        dst_addr = str(json_data[0]["dst_addr"])

    return dst_addr, rtt_probes_dict



def traceroute_traces_resume(mes_id, probe_id):
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
    file_name = "RIPE-Atlas-measurement-{0}-probe-{1}.json".format(mes_id, probe_id)
    file_path = os.path.join(JSON_DIR, file_name)
    frequent_route_list = []
    dst_adr = ""
    src_addr = ""
    hops_number = 0
    with open(file_path) as f_handler:
        json_data = json.load(f_handler)
        if len(json_data) != 0:
            dst_adr = json_data[0]['dst_addr']
            src_addr = json_data[0]["src_addr"]
            for record in json_data:
                exp_date = datetime.fromtimestamp(int(record["timestamp"])).strftime('%Y-%m-%d %H:%M')
                src_addr = record["src_addr"]
                dst_adr = record['dst_addr']
                hop_list = record['result']
                # print hop_list
                hop_ip_list = [retrieve_traversed_ip(hop['result']) for hop in hop_list]
                print exp_date, src_addr, dst_adr, "->".join(hop_ip_list)
                frequent_route_list.append("->".join(hop_ip_list))

    # we can rely the most_common() method to find out the most occurrences of routes
    # The output of most_common() is a list of tuple
    if len(json_data) != 0:
        print Counter(frequent_route_list).most_common(1)[0][0]
        hops_number = len(Counter(frequent_route_list).most_common(1)[0][0].split("->"))
    return src_addr, dst_adr, hops_number
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
    if command == "TRACEROUTE":
        report_name = "{0}_{1}_report.csv".format(command, name)
        with open(report_name, 'wb') as f_handler:
            a = csv.writer(f_handler, dialect='excel', delimiter=";")
            a.writerow(['mesurement id', 'target of traceroute', 'hops_Lab of LISP', 'hops of mPlane'])
            for mes_id in mes_ids:
                output_row = [mes_id]
                src_addr_lisp, dst_addr, hops_number_lisp = traceroute_traces_resume(mes_id, probe_ids[0])
                src_addr_mplane, dst_addr, hops_number_mplane = traceroute_traces_resume(mes_id, probe_ids[1])
                output_row.append(dst_addr)
                output_row.append(hops_number_lisp)
                output_row.append(hops_number_mplane)
                a.writerow(output_row)

    if command == "PING":
        report_name = os.path.join(ATLAS_FIGURES_AND_TABLES, "{0}_{1}_report.csv".format(command, name))
        with open(report_name, 'wb') as f_handler:
            a = csv.writer(f_handler, dialect='excel', delimiter=";")
            a.writerow(
                [
                    'mesurement id',
                    'Destination',
                    'avg(min RTT) from LISP-Lab',
                    'avg(min RTT) from mPlane',
                    'avg(min RTT) from FranceIX',
                    'avg(min RTT) from rmd',
                    'variace from LISP-Lab',
                    'variace from mPlane',
                    'variace from FranceIX',
                    'variace from rmd']
            )
            for mes_id in mes_ids:
                output_row = [mes_id]
                dst_addr, rtt_probes_dict = ping_traces_resume(mes_id, probe_ids)
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
                output_row.append(dst_addr)
                output_row.append(avg_min_lispLab)
                output_row.append(avg_min_mPlane)
                output_row.append(avg_min_FranceIX)
                output_row.append(avg_min_rmd)
                output_row.append(std_lispLab)
                output_row.append(std_mPlane)
                output_row.append(std_FranceIX)
                output_row.append(std_rmd)
                a.writerow(output_row)


if __name__ == "__main__":
    # TRACEROUT_V4_MES_IDS = ['2841000', '2841002', '2841004', '2841006']

    PING_V4_MES_IDS = []
    PROBE_IDS = ['22341', '13842', '6118', '16958']
    # generate_report(TRACEROUT_V4_MES_IDS, PROBE_IDS, "TRACEROUTE", "IPv4")
    mes_id_record_file = os.path.join(ATLAS_CONDUCT_MEASUREMENTS,
                                      '4_probes_to_alexa_top100', '4_top100_measurement_ids_ping.txt')
    with open(mes_id_record_file) as f_handler:
        PING_V4_MES_IDS = f_handler.readlines()
    # 去掉跟在measurement id后面的换行符
    PING_V4_MES_IDS = [i.strip() for i in PING_V4_MES_IDS]
    print PING_V4_MES_IDS
    generate_report(PING_V4_MES_IDS, PROBE_IDS, "PING", "IPv4")

    # TRACEROUT_V6_MES_IDS = ['6002', '6007', '6017', '6018', '6019', '6020', '6021', '6022']
    # PING_V6_MES_IDS = ['2017', '2019', '2020', '2022']
    # generate_report(TRACEROUT_V6_MES_IDS, PROBE_IDS, "TRACEROUTE", "IPv6")
    # generate_report(PING_V6_MES_IDS, PROBE_IDS, "PING", "IPv6")



