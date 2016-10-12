# -*- coding: utf-8 -*-
__author__ = 'yueli'
'''In this python script, we plan to define some globl variables'''


import os
from pylab import *
import json
from datetime import datetime
import numpy as np
import csv
from collections import Counter
import re
import math
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st
from scipy.stats import pearsonr
import collections
from pandas.tools.plotting import autocorrelation_plot
import scipy as sp
import scipy.stats


# 读取 环境变量 Atlas 目录下的各个文件夹
# 上述 环境变量 定义在 工作目录下 .profile中 (也有可能定义在 .bashprofile中)
try:
    # $HOME/Documents/Codes/Atlas/analyze_traces
    ATLAS_ANALYZE_TRACES = os.environ['ATLAS_ANALYZE_TRACES']
    # $HOME/Documents/Codes/Atlas/conduct_measurements
    ATLAS_CONDUCT_MEASUREMENTS = os.environ['ATLAS_CONDUCT_MEASUREMENTS']
    # $HOME/Documents/Codes/Atlas/figures_and_tables
    ATLAS_FIGURES_AND_TABLES = os.environ['ATLAS_FIGURES_AND_TABLES']
    # $HOME/Documents/Codes/Atlas/plot
    ATLAS_PLOT = os.environ['ATLAS_PLOT']
    # $HOME/Documents/Codes/Atlas/traces
    ATLAS_TRACES = os.environ['ATLAS_TRACES']
    # $HOME/Documents/Codes/Atlas/Wenqin_codes
    ATLAS_WENQIN_CODES = os.environ['ATLAS_WENQIN_CODES']
    # $HOME/Documents/Codes/Atlas/auth
    ATLAS_AUTH = os.environ['ATLAS_AUTH']

except KeyError:

    print "Environment variable is not properly defined or " \
          "the definition about this variable is not taken into account."
    print "If every environment variable is well defined, restart Pycharm to try again!"


# # probe id和此probe的IP地址间的对应关系
# PROBE_NAME_ID_DICT = {
#
#     "FranceIX": "6118",
#     "mPlane": "13842",
#     "rmd": "16958",
#     "LISP-Lab": "22341"
# }
#
# # probe id和此probe的IP地址间的对应关系
# PROBE_ID_NAME_DICT = {
#
#     "6118": "FranceIX",
#     "13842": "mPlane",
#     "16958": "rmd",
#     "22341": "LISP-Lab"
# }

# probe id和此probe的IP地址间的对应关系
PROBE_ID_IPv4_DICT = {
    "132.227.120.130": "22341",
    "37.49.234.132": "6118",
    "137.194.165.62": "13842",
    "153.16.38.64": "2403",
    "81.56.47.149": "2848"
}
PROBE_ID_IPv6_DICT = {
    "2a03:9180:2:128::84e3:7882": "22341",
    "2a00:a4c0:2:1::132": "6118",
    "2001:660:330f:a4:a2f3:c1ff:fec4:5d2e": "13842",
    "2610:d0:2121::64": "2403",
    "2a01:e35:1382:f950:220:4aff:fee0:2770": "2848"
}

PROBE_ID_NAME_DICT = {

    "6118"  : "FranceIX",
    "13842" : "mPlane",
    "2403" : "LIP6",
    "22341" : "LISP-Lab",
    "2848": "home"
}

RTT_TYPE_ID_DICT = {
    "min": 0,
    "avg": 1,
    "max": 2
}

# probe id和此probe的IP地址间的对应关系
PROBE_NAME_COLUMN_DICT = {

    "FranceIX": 4,
    "mPlane": 3,
    "rmd": 5,
    "LISP-Lab": 2
}

# 实验中出现的 geo 的list
GEO_LIST = ['Europe', 'America', 'Asia']

# Plot part

font = {
    'fontname'   : 'Times New Roman',
    'color'      : 'k',
    'fontsize'   : 60
       }

fontText = {
    'fontname'   : 'Times New Roman',
    'color'      : 'k',
    'fontsize'   : 40
       }

font3D = {
    'fontname'   : 'Times New Roman',
    'color'      : 'k',
    'fontsize'   : 52
       }