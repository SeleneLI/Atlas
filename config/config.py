# -*- coding: utf-8 -*-
__author__ = 'yueli'
'''In this python script, we plan to define some globl variables'''


import os

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


