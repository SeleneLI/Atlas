# -*- coding: utf-8 -*-
# This script can do：
# Get top 510 ping-able website IPv4 addresses from top_1m_Alexa.csv

import csv
import time
import socket
import subprocess
from geoip import geolite2

# To record the codes execution time
start_time = time.time()

# ==========================================Section: constant variable declaration======================================
# How many websites want to be finally stored
SITE_NB = 510
# Top 1 million websites file downloaded from Alexa
ALEXA_TOP_SITE_F = 'top_1m_Alexa.csv'
# In which file to store the successfully ping and traceroute websites
EXP_INPUT_F = 'top_{0}_websites_IPv4.csv'.format(SITE_NB)



if __name__ == "__main__":
    # Ref: http://stackoverflow.com/questions/29911507/reading-first-n-lines-of-a-csv-into-a-dictionary
    # 讲述了如何读取 CSV 文件的前 N 行的例子
    PARSE = True
    target_site_l = []
    dict_country = {}
    dict_continent = {}
    if PARSE == True:
        with open(EXP_INPUT_F, 'w') as out_csvfile:
            spamewriter = csv.writer(out_csvfile, dialect='excel', delimiter=';')
            spamewriter.writerow(['Site name', 'Site IP', 'Country', 'Continent'])

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
                            match = geolite2.lookup(site_ip)
                            if match is not None:
                                country = match.country
                                continent = match.continent
                                target_site_l.append([site_name, site_ip, country, continent])
                                spamewriter.writerow([site_name, site_ip, country, continent])
                                if country not in dict_country.keys():
                                    dict_country[country] = 1
                                else:
                                    dict_country[country] += 1
                                if continent not in dict_continent.keys():
                                    dict_continent[continent] = 1
                                else:
                                    dict_continent[continent] += 1
                            else:
                                print "Don't find the country/continent of", site_name, site_ip
                        else:
                            print site_name, site_ip, "is Offline"
                        if len(target_site_l) == SITE_NB:
                            print SITE_NB, "sites have been retrieved. Stop now"
                            break
                    except:
                        print site_name, ': unknown host! Skipped'

    # # convert each URL into Unicode
    # with open(EXP_INPUT_F, 'r') as csvfile:
    #     spamreader = csv.reader(csvfile, delimiter=',')
    #     for row in spamreader:
    #         print "row", row

    # print len(target_site_l), target_site_l

    print "dict_country:", dict_country
    print "dict_continent:", dict_continent
    print (time.time() - start_time)/60.0, "minutes are used to execute the codes"







