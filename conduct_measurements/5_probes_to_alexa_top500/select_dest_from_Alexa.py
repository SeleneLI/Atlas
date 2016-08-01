# -*- coding: utf-8 -*-
# 本script功能：
# 提供开启 RIPE Atlas 上 ping 和 traceroute 的实验
# 5 个 probes，编号分别为 22341, 13842, 16958 and anchor 6118
# destination 是 Alexa top 150, http://www.alexa.com/topsites
# !!注意!! 因为有些网站不允许被 ping，因而每爬一个网址都可先 ping 一下，确定对方有回复才记录下来成为实验开启的正式 destination
#!/usr/bin/python

# RIPE Atlas API demo
# Ping measurement can be configured and created using this script

import csv
import time
import socket
import subprocess

# To record the codes execution time
start_time = time.time()

# ==========================================Section: constant variable declaration======================================
# How many websites want to be finally stored
SITE_NB = 510
# Top 1 million websites file downloaded from Alexa
ALEXA_TOP_SITE_F = 'top_1m_Alexa.csv'
# In which file to store the successfully ping and traceroute websites
EXP_INPUT_F = 'exp_input.csv'



if __name__ == "__main__":
    # Ref: http://stackoverflow.com/questions/29911507/reading-first-n-lines-of-a-csv-into-a-dictionary
    # 讲述了如何读取 CSV 文件的前 N 行的例子
    PARSE = True
    target_site_l = []
    if PARSE == True:
        with open(EXP_INPUT_F, 'w') as out_csvfile:
            spamewriter = csv.writer(out_csvfile, dialect='excel', delimiter=';')
            spamewriter.writerow(['Site name', 'Site IP'])

            with open(ALEXA_TOP_SITE_F, 'r') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                for row in spamreader:
                    site_name = row[1].decode('utf-8')
                    site_ip = ''
                    try:
                        site_ip = socket.gethostbyname(site_name)
                        print "Processing ", site_name, site_ip
                        cmd = "ping -c 3 {0}".format(site_ip)
                        output = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]
                        if "bytes from" in output.decode('utf-8'):
                            target_site_l.append([site_name, site_ip])
                            spamewriter.writerow([site_name, site_ip])
                        else:
                            print site_name, site_ip, "is Offline"
                        if len(target_site_l) == SITE_NB:
                            print SITE_NB, "sites have been retrieved. Stop now"
                            break
                    except:
                        print site_name, ': unknown host! Skipped'

    # convert each URL into Unicode
    with open(EXP_INPUT_F, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            print "row", row

    # print len(target_site_l), target_site_l


    print (time.time() - start_time)/60.0, "minutes are used to execute the codes"







