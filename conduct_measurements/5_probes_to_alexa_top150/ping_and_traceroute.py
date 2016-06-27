# -*- coding: utf-8 -*-
# 本script功能：
# 提供开启 RIPE Atlas 上 ping 和 traceroute 的实验
# 5 个 probes，编号分别为 22341, 13842, 16958 and anchor 6118
# destination 是 Alexa top 150, http://www.alexa.com/topsites
# !!注意!! 因为有些网站不允许被 ping，因而每爬一个网址都可先 ping 一下，确定对方有回复才记录下来成为实验开启的正式 destination
#!/usr/bin/python

# RIPE Atlas API demo
# Ping measurement can be configured and created using this script

import json
import requests
import urllib2
import csv
import itertools
import os
import sys
import time
import calendar
import math
from config.config import *
import socket



if __name__ == "__main__":
    # Ref: http://stackoverflow.com/questions/29911507/reading-first-n-lines-of-a-csv-into-a-dictionary
    # 讲述了如何读取 CSV 文件的前 N 行的例子
    SITE_NB = 150
    PARSE = True
    ALEXA_TOP_SITE_F = 'top-1m.csv'
    EXP_INPUT_F = 'exp_input.csv'
    target_site_l = []
    if PARSE == True:
        with open(EXP_INPUT_F, 'w') as out_csvfile:
            spamewriter = csv.writer(out_csvfile, delimiter=',')
            with open(ALEXA_TOP_SITE_F, 'r') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                for row in spamreader:
                    site_name = row[1].decode('utf-8')
                    site_ip = ''
                    try:
                        site_ip = socket.gethostbyname(site_name)
                        target_site_l.append([site_name, site_ip])
                        spamewriter.writerow([site_name, site_ip])
                        if len(target_site_l) == SITE_NB:
                            print SITE_NB, "sites have been retrieved. Stop now"
                            break
                    except:
                        print site_name, ': unknown host! Skipped'


    # convert each URL into Unicode
    with open(EXP_INPUT_F, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            print row

    # print len(target_site_l), target_site_l






