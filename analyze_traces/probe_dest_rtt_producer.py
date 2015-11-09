# -*- coding: utf-8 -*-
# 本script功能：
# 对 $HOME/Documents/Codes/Atlas/traces/Produced_traces 中存储的各实验下的 measurement_id.json 文件进行 .csv 转化
__author__ = 'yueli'

from config.config import *
import numpy as np
import re
import math_tool as math_tool


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
TARGET_TRACES_PATH = os.path.join(ATLAS_TRACES, EXPERIMENT_NAME)
PING_MEASUREMENT_ID_LIST = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, EXPERIMENT_NAME, '4_probes_to_alexa_top100_measurement_ids_ping.txt')

# ======================================================================================================================
# 此函数负责从 PING_MEASUREMENT_ID_LIST 的txt文档中逐一读出 measurement_id，
# 并转化成路径文件名的方式作为 probe_dest_rtt_csv_producer 的input (在此处调用 probe_dest_rtt_csv_producer )
def json_file_finder(file_string):
    # 首先对 file_string 进行判断，如果 file_string 本来就是
    # $HOME/Documents/Codes/Atlas/traces/Produced_traces/EXPERIMENT_NAME/measurement_id.json 则无需转化，
    # 直接调用 probe_dest_rtt_csv_producer
    # 如果 file_string == PING_MEASUREMENT_ID_LIST，则需打开文件继续处理
    if re.match(r'.json', file_string):
        return file_string
    else:
        # 开文件继续处理
        json_file = file_string

    return json_file


# ======================================================================================================================
# 此函数负责把 measurement_id.json 的文件转化成4个 probe_dest_rtt.csv 文件，
# 存在 $HOME/Documents/Codes/Atlas/traces/json2csv/EXPERIMENT_NAME/*destination*/下
def probe_dest_rtt_csv_producer(target_file):
