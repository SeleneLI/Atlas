# -*- coding: utf-8 -*-
# 本script功能：
# 为分析Atlas的 traces 而写。基于Atlas/traces/json2csv/5_probes_to_alexa_top500/ping_v4/5_probes_to_alexa_top500_avg.csv等files
# 针对不同probes ping 同一目的地，可以计算各自的平均值(mean)和方差(variance)；
# 针对不同probes traceroute 同一目的地，可以计算各自的最常用路径的跳数(hops)
__author__ = 'yueli'

from config.config import *
import math_tool as math_tool
import csv
import numpy as np
import glob
import json
import pprint
from rtt.localutils import pathtools
import difflib
from geoip import geolite2

# ==========================================Section: constant variable declaration======================================

# 需要 generate ping report 还是 traceroute report，写 'PING' 或 'TRACEROUTE'
GENERATE_TYPE = 'ping'  # 'ping' or 'traceroute'
IP_VERSION = 'v4'  # 'v6'
RTT_TYPE = 'avg'    # 'avg' or 'min' or 'max'，当 GENERATE_TYPE = 'TRACEROUTE' 时忽略此变量，什么都不用更改
MES_ID_TYPE = 'txt'     # 'list' or 'txt'
MES_ID_LIST = ['6964405']    # 只有当 MES_ID_TYPE = 'list' 时，此参数才有用。即指定处理哪几个实验
CALCULATE_TYPE = 'median'   # 'mean' or 'median'
REF_RTT_PROBE = 6118
COMPARED_RTT_PROBE = 22341

# EXPERIMENT_NAME 为实验起个名字，会作为存储和生成trace的子文件夹名称
EXPERIMENT_NAME = '5_probes_to_alexa_top510'
# The .csv tables we need to base on
JSON2CSV_FILE = os.path.join(ATLAS_TRACES, 'json2csv', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION),'{0}_{1}.csv'.format(EXPERIMENT_NAME,RTT_TYPE))
JSON2CSV_FILE_NO_RESPONSE = os.path.join(ATLAS_TRACES, 'json2csv', EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION), '{0}_{1}_no_response.csv'.format(EXPERIMENT_NAME, RTT_TYPE))

# The folder path, where we will store the filtered .csv tables
FILTERED_TRACE_PATH = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE, IP_VERSION))

DEST_FILE = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, EXPERIMENT_NAME, 'top_510_websites_fr.csv')
TRACEROUTE_REPORT = os.path.join(ATLAS_FIGURES_AND_TABLES, EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE,IP_VERSION), '{0}_{1}_report'.format(GENERATE_TYPE,IP_VERSION))

# ==========================================Section: functions declaration======================================
# Get the probes_list from JSON2CSV_FILE
# input = JSON2CSV_FILE
# output = ['mPlane', 'FranceIX', 'LISP-Lab']
def get_probes():
    probes_list = []
    with open(JSON2CSV_FILE) as f_handler:
        next(f_handler)
        for line in f_handler:
            probes_list.append(line.split(";")[2].strip())

    return list(set(probes_list))


# Get the Country & Continent from file to a dictionary
# "/Users/yueli/Documents/Codes/Atlas/conduct_measurements/5_probes_to_alexa_top500/top_510_websites_fr.csv"
# input = .csv file
# output =
"""
    {'dest': ['country', 'continent'],
     'dest': ['country', 'continent'],
     ...
     'dest': ['country', 'continent']}
"""
def get_country_continent():
    dest_country_continent = {}
    try:
        os.stat(DEST_FILE)
    except:
        print "The .csv file where to get Country & Continent doesn' exist !!", DEST_FILE

    with open(DEST_FILE) as f_handler:
        next(f_handler)
        for line in f_handler:
            dest_country_continent[line.split(";")[1].strip()] = [line.split(";")[2].strip(), line.split(";")[3].strip()]
            if len(line.split(";")) > 4:
                dest_country_continent[line.split(";")[4].strip()] = [line.split(";")[5].strip(), line.split(";")[6].strip()]

    print "len(dest_country_continent.keys())", len(dest_country_continent.keys())
    return dest_country_continent




# Judge whether all the probes receive RTT.
# To filter the destation in the following case, caused by probe_2:
"""
    dest    probe_1    [RTT, RTT, ..., RTT]
    dest    probe_2    [-1, -1, ..., -1]
    dest    probe_3    [RTT, RTT, ..., RTT]
"""
# input = {'FranceIX':[RTT, RTT, ..., RTT], 'mPlane':[-1, -1, ..., -1], 'LISP-Lab':[RTT, RTT, ..., RTT]}
# output = True or False
def all_probes_have_rtt(dest_probes_rtt_dict):
    result = True
    if not dest_probes_rtt_dict:
        result = False
    for probe in dest_probes_rtt_dict.keys():
        if list(set(dest_probes_rtt_dict[probe]))[0] == '-1': # 因为当整个list都为-1时,最后会得到[-1],仅有一个元素且为-1
             return False
    return result # when input dict is empty, return False



# Clean the RTT series received by all probes.
# To remove the RTT in a dedicated experiment round in the following case:
"""
input =
    dest    probe_1    [RTT, RTT, RTT, RTT, -1,  RTT]
    dest    probe_2    [RTT, -1,  RTT, RTT, RTT, RTT]
    dest    probe_3    [RTT, RTT, RTT, RTT, RTT, RTT]

output =
    dest    probe_1    [RTT, RTT, RTT, RTT]
    dest    probe_2    [RTT, RTT, RTT, RTT]
    dest    probe_3    [RTT, RTT, RTT, RTT]
"""
def clean_rtt_series(dest_probes_rtt_dict):
    index = []
    for probe in dest_probes_rtt_dict.keys():
        index.extend([i for i, x in enumerate(dest_probes_rtt_dict[probe]) if x == '-1.0'])

    # index.sort()    # Let the index to remove is sorted from small to big
    # reversed_index = [i for i in reversed(index)]   # Remove the element with a high index to ensure the order don' change

    clean_dest_probes_rtt_dict = {}
    for probe in dest_probes_rtt_dict.keys():
        clean_dest_probes_rtt_dict[probe] = [rtt for i, rtt in enumerate(dest_probes_rtt_dict[probe]) if i not in index]

    return clean_dest_probes_rtt_dict



# input = JSON2CSV_FILE
# output = {
#           ('mes_id','dest'): [RTT, RTT, ..., RTT],
#           ('mes_id','dest'): [RTT, RTT, ..., RTT],
#           ('mes_id','dest'): [RTT, RTT, ..., RTT],
#           ...
#           ('mes_id','dest'): [RTT, RTT, ..., RTT]
#           }
def get_clean_traces():
    temp_probes_list = []
    dest_probes_rtt_dict = {}
    probes_rtt_dict = {}
    m_id_list = []


    with open(JSON2CSV_FILE) as json2csv_file:
        next(json2csv_file)
        line = next(json2csv_file)
        first_line = [element.strip() for element in line.split(";")]
        print "first_line:", first_line
        dest = first_line[1]
        m_id = first_line[0]
        probe = first_line[2]

        probes_rtt_dict[probe] = first_line[3:]

        for line in json2csv_file:
            tmp_list = [element.strip() for element in line.split(";")]
            current_m_id = tmp_list[0]
            current_dest = tmp_list[1]
            probe = tmp_list[2]

            if m_id != current_m_id:
            # if dest != current_dest:

                if all_probes_have_rtt(probes_rtt_dict): # if probes_rtt_dict is not empty and has no RTT with all -1
                    dest_probes_rtt_dict[(m_id, dest)] = clean_rtt_series(probes_rtt_dict)
                    m_id_list.append(m_id)
                    # update m_id and dest value
                    # print "dest", dest
                    # print dest_probes_rtt_dict[dest]
                # else:
                #     print "Bad dest:", dest

                dest = current_dest
                m_id = current_m_id

                # Intialize probes_rtt_dict
                probes_rtt_dict = {}

                temp_probes_list.append(probe)

            probes_rtt_dict[probe] = tmp_list[3:]

        if all_probes_have_rtt(probes_rtt_dict):
            dest_probes_rtt_dict[(m_id, dest)] = clean_rtt_series(probes_rtt_dict)
            m_id_list.append(m_id)
        else:
            print "Bad dest:", dest

    print "len(dest_probes_rtt_dict.keys())", len(dest_probes_rtt_dict.keys())
    print "len(m_id_list):", m_id_list
    print dest_probes_rtt_dict.keys()
    return dest_probes_rtt_dict




def generate_report(dest_probes_rtt_dict):
    try:
        os.stat(FILTERED_TRACE_PATH)
    except:
        os.makedirs(FILTERED_TRACE_PATH)

    clean_file = os.path.join(FILTERED_TRACE_PATH, '{0}_{1}_report_{2}_{3}.csv'.format(GENERATE_TYPE,IP_VERSION,RTT_TYPE,CALCULATE_TYPE))

    # probes_list = get_probes()
    probes_list = PROBE_ID_NAME_DICT.values()
    dest_country_continent = get_country_continent()

    with open(clean_file, 'wb') as f_handler:
        csv_writter = csv.writer(f_handler, delimiter=';')
        csv_title = ['mesurement id', 'Destination']
        csv_title.extend(
            ["{0}({1} RTT) from {2}".format(CALCULATE_TYPE, RTT_TYPE, probe_name) for probe_name in probes_list])
        csv_title.extend(
            ["variance from {1}".format(RTT_TYPE, probe_name) for probe_name in probes_list])
        csv_title.extend(['Country', 'Continent'])
        csv_writter.writerow(csv_title)
        for key, value in dest_probes_rtt_dict.iteritems():
            # print key
            csv_row = []
            current_m_id, current_dest = key[0], key[1]
            csv_row.append(current_m_id)
            csv_row.append(current_dest)
            rtts = []
            for probe in probes_list:
                rtt_tmp = [float(element) for element in value[probe]]
                rtts.append(rtt_tmp)

            if CALCULATE_TYPE == 'mean':
                csv_row.extend([np.mean(element) for element in rtts])
            elif CALCULATE_TYPE == 'median':
                csv_row.extend([np.median(element) for element in rtts])
            else:
                print "CALCULATE_TYPE should be 'mean' or 'median' !! Retry "
            csv_row.extend([np.var(element) for element in rtts])

            try:
                csv_row.extend(dest_country_continent[key[1]])
                csv_writter.writerow(csv_row)
            except:
                print "The following measurement_id and IPv6 are not in top_510_websites_fr.csv:"
                print current_m_id
                print key[1]



# ==========================================Section: Traceroute analysis============================================
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


def process_traceroute(json_traces_folder, hop_number=True):

    files = glob.glob(json_traces_folder)

    hops_count_dict = {}

    for trace_p in files:
        with open(trace_p, 'r') as f_handler:
            json_data = json.load(f_handler)
            if len(json_data) != 0:
                for index, record in enumerate(json_data):
                    msm_id = record['msm_id']
                    prb_id = record['prb_id']
                    dst_addr = record['dst_addr']
                    hop_list = record['result']
                    hop_ip_list = [retrieve_traversed_ip(hop['result']) for hop in hop_list if 'result' in hop.keys()]
                    '''
                    {"af":4,"dst_addr":"144.160.155.43","dst_name":"144.160.155.43","endtime":1482584785,
                    "from":"217.70.181.250","fw":4740,"group_id":6963985,"lts":486,"msm_id":6963985,
                    "msm_name":"Traceroute","paris_id":4,"prb_id":3141,"proto":"ICMP",
                    "result":[{"error":"connect failed: Network is unreachable","hop":1}],
                    "size":48,"src_addr":"217.70.181.250",
                    "timestamp":1482584785,"type":"traceroute"}
                    '''
                    ## frequent_route_list.append("->".join(hop_ip_list))
                    ## we can rely the most_common() method to find out the most occurrences of routes
                    ## The output of most_common() is a list of tuple
                    ##     print Counter(frequent_route_list).most_common(1)[0][0]
                    ## hops_number = len(Counter(frequent_route_list).most_common(1)[0][0].split("->"))
                    # print msm_id, dst_addr, prb_id, "->".join(hop_ip_list)
                    if (msm_id, dst_addr) in hops_count_dict.keys():
                        if prb_id not in hops_count_dict[(msm_id, dst_addr)].keys():
                            hops_count_dict[(msm_id, dst_addr)][prb_id] = ["->".join(hop_ip_list)]
                        else:
                             hops_count_dict[(msm_id, dst_addr)][prb_id].append("->".join(hop_ip_list))
                    else:
                        hops_count_dict[(msm_id, dst_addr)] = {}
                        hops_count_dict[(msm_id, dst_addr)][prb_id] = ["->".join(hop_ip_list)]
            else:
                # print "!!!!!!!!!!!!!!!!!", trace_p, " is empty !!!!!!!!!!!!!!!!!"
                pass

    for key, value in hops_count_dict.iteritems():
        for prb_id, hop_ip_list in value.iteritems():
            if hop_number:
                hops_number = len(Counter(hop_ip_list).most_common(1)[0][0].split("->"))
            else:
                hops_number = Counter(hop_ip_list).most_common(1)[0][0].split("->")
            value[prb_id] = hops_number

    # pprint.pprint(hops_count_dict)
    return hops_count_dict



def ip_to_as(json_traces_folder):
    dest_probe_ipList = process_traceroute(json_traces_folder, False)
    dest_probe_asList = {}
    dest_probe_countryList = {}

    for dest in dest_probe_ipList.keys():
        print "dest ==>", dest
        dest_probe_asList[dest] = {}
        dest_probe_countryList[dest] = {}
        for probe in dest_probe_ipList[dest].keys():

            if probe == REF_RTT_PROBE:
                # Full AS-path
                # dest_probe_asList[dest][probe] = [pathtools.ip2asn.lookup(ip) for ip in dest_probe_ipList[dest][probe]]
                # AS-path removing 'None', 'Invalid IP address' and the consecutively same ones
                dest_probe_asList[dest][probe] = []
                dest_probe_countryList[dest][probe] = []
                for ip in dest_probe_ipList[dest][probe]:
                    as_current = pathtools.ip2asn.lookup(ip)
                    if len(dest_probe_asList[dest][probe]) == 0:
                        if (as_current != 'Invalid IP address') and (as_current != None):
                            dest_probe_asList[dest][probe].append(as_current)
                            print "ip ==>", ip
                            dest_probe_countryList[dest][probe].append(find_IP_geolocation(ip))

                    elif (as_current != dest_probe_asList[dest][probe][-1]) and (as_current !=  None) and (as_current != 'Invalid IP address'):
                        dest_probe_asList[dest][probe].append(as_current)
                        print "ip ==>", ip
                        dest_probe_countryList[dest][probe].append(find_IP_geolocation(ip))
            elif probe == COMPARED_RTT_PROBE:
                # Full AS-path
                # dest_probe_asList[dest][probe] = [pathtools.ip2asn.lookup(ip) for ip in dest_probe_ipList[dest][probe]]
                # AS-path removing 'None', 'Invalid IP address' and the consecutively same ones
                dest_probe_asList[dest][probe] = []
                dest_probe_countryList[dest][probe] = []
                for ip in dest_probe_ipList[dest][probe]:
                    as_current = pathtools.ip2asn.lookup(ip)
                    if len(dest_probe_asList[dest][probe]) == 0:
                        if (as_current != 'Invalid IP address') and (as_current != None):
                            dest_probe_asList[dest][probe].append(as_current)
                            print "ip ==>", ip
                            dest_probe_countryList[dest][probe].append(find_IP_geolocation(ip))
                    elif (as_current != dest_probe_asList[dest][probe][-1]) and (as_current !=  None) and (as_current != 'Invalid IP address'):
                        dest_probe_asList[dest][probe].append(as_current)
                        print "ip ==>", ip
                        dest_probe_countryList[dest][probe].append(find_IP_geolocation(ip))

    print "dest_probe_asList ==>"
    pprint.pprint(dest_probe_asList)
    print "dest_probe_countryList ==>"
    pprint.pprint(dest_probe_countryList)

    ref_index = 0
    com_index = 0
    both_index = 0
    for dest in dest_probe_countryList.keys():
        if ('US' in dest_probe_countryList[dest][REF_RTT_PROBE]) and ('US' not in dest_probe_countryList[dest][COMPARED_RTT_PROBE]):
            ref_index += 1
        elif ('US' not in dest_probe_countryList[dest][REF_RTT_PROBE]) and ('US' in dest_probe_countryList[dest][COMPARED_RTT_PROBE]):
            com_index += 1
        elif ('US' not in dest_probe_countryList[dest][REF_RTT_PROBE]) and ('US' not in dest_probe_countryList[dest][COMPARED_RTT_PROBE]):
            both_index += 1

    print "ref_index =", ref_index
    print "com_index =", com_index
    print "both_index =", both_index

    return dest_probe_asList, dest_probe_countryList


def common_path_calculator(json_traces_folder):
    dest_probe_as_list, dest_probe_countryList = ip_to_as(json_traces_folder)
    common_path_dict = {}
    for dest in dest_probe_as_list.keys():
        as_path_1 = dest_probe_as_list[dest][REF_RTT_PROBE]
        as_path_2 = dest_probe_as_list[dest][COMPARED_RTT_PROBE]
        as_path_1_reverse = as_path_1[::-1]
        as_path_2_reverse = as_path_2[::-1]
        index = 0
        print dest
        while as_path_1_reverse[index] == as_path_2_reverse[index]:
            index += 1
            if index == min(len(as_path_1_reverse), len(as_path_2_reverse)):
                break

        print "To", dest, "common hops =", index
        common_path_dict[dest] = (index, len(as_path_1_reverse), len(as_path_2_reverse), dest_probe_countryList[dest][REF_RTT_PROBE], dest_probe_countryList[dest][COMPARED_RTT_PROBE])

    mean_common_hops = mean([i[0] for i in common_path_dict.values()])

    print "mean_common_hops ==>"
    print mean_common_hops

    print "common_path_dict ==>"
    print common_path_dict

    return common_path_dict


def similarity_calculator(json_traces_folder):
    dest_probe_as_list, dest_probe_countryList = ip_to_as(json_traces_folder)
    similarity_dict = {}
    for dest in dest_probe_as_list.keys():
        as_path_1 = dest_probe_as_list[dest][REF_RTT_PROBE]
        as_path_2 = dest_probe_as_list[dest][COMPARED_RTT_PROBE]
        sm = difflib.SequenceMatcher(None, as_path_1, as_path_2)
        similarity_dict[dest] = sm.ratio()

    print "Avg similarity", mean(similarity_dict.values())
    return similarity_dict


def generate_report_as(target_dict):
    with open("xxx.csv", 'w') as f_handler:
        csv_writter = csv.writer(f_handler, delimiter=';')
        title_line = ['measurement_id','destination','common_hops_num','FranceIX_hops_num','LISP-Lab_hops_num','FranceIX_country_path','LISP-Lab_country_path','Country','Continent']
        csv_writter.writerow(title_line)

        dest_country_continent = get_country_continent()

        for key, value in target_dict.iteritems():
            csv_row = []
            for id in key:
                csv_row.append(id)
            for number in value:
                csv_row.append(number)

            csv_row.extend(dest_country_continent[key[1]])

            csv_writter.writerow(csv_row)


def find_IP_geolocation(ip):
    match = geolite2.lookup(ip)

    if match is not None:
        country = match.country
        continent = match.continent
    else:
        country = '/'
        continent = '/'

    print country
    print continent

    return country




def generate_report_traceroute(dest_probes_rtt_dict):

    try:
        os.stat(FILTERED_TRACE_PATH)
    except:
        os.makedirs(FILTERED_TRACE_PATH)

    clean_file = os.path.join(FILTERED_TRACE_PATH, '{0}_{1}_report.csv'.format(GENERATE_TYPE,IP_VERSION))

    # probes_list = get_probes()
    probes_list = PROBE_ID_NAME_DICT.values()

    dest_country_continent = get_country_continent()

    with open(clean_file, 'wb') as f_handler:
        csv_writter = csv.writer(f_handler, delimiter=';')
        csv_title = ['mesurement id', 'Destination']
        csv_title.extend(
            ["hop numbers from {0}".format(probe_name) for probe_name in probes_list])
        csv_title.extend(['Country', 'Continent'])
        csv_writter.writerow(csv_title)

        for key, value in dest_probes_rtt_dict.iteritems():
            # pprint.pprint(value)
            csv_row = []
            current_m_id, current_dest = key[0], key[1]
            csv_row.append(current_m_id)
            csv_row.append(current_dest)
            hops = []
            for probe in probes_list:
                for prb_id, prb_name in PROBE_ID_NAME_DICT.iteritems():
                    print "prb_name:", prb_name
                    print "probe:", probe
                    print "prb_id:", type(prb_id)
                    print "value.keys()", value.keys()
                    if prb_name == probe:
                        if int(prb_id) in [int(i) for i in value.keys()]:
                            # rtt_tmp = [float(element) for element in value[int(prb_id)]]
                            hops.append(value[int(prb_id)])
                        else:
                            hops.append('/') # for a traceroute having no result
            csv_row.extend(hops)

            try:
                csv_row.extend(dest_country_continent[key[1]])
                csv_writter.writerow(csv_row)
            except:
                print "The following measurement_id and IPv6 are not in top_510_websites_fr.csv:"
                print current_m_id
                print key[1]






# ==========================================Section: main function declaration======================================

if __name__ == "__main__":
    # print get_probes()
    # dict_target = {'MR_1': [2, 5, 5, -1, 3],
    #               'MR_2': [1, -1, 1, 5, 2]}
    # print all_probes_have_rtt(dict_target)

    # print clean_rtt_series(dict_target)

    # print get_clean_traces().keys()[0]

    generate_report(get_clean_traces())

    # JSON_TRACES_FOLDER = os.path.join("..", "traces", "Produced_traces", EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE, IP_VERSION), "*.json")

    # JSON_TRACES_FOLDER = os.path.join("..", "traces", "Produced_traces", EXPERIMENT_NAME, '{0}_{1}'.format(GENERATE_TYPE, IP_VERSION), "6964414.json")
    # generate_report_traceroute(process_traceroute(JSON_TRACES_FOLDER))
    # process_traceroute(JSON_TRACES_FOLDER, False)
    # ip_to_as(JSON_TRACES_FOLDER)
    # print similarity_calculator(JSON_TRACES_FOLDER)

    # generate_report_as(common_path_calculator(JSON_TRACES_FOLDER))



