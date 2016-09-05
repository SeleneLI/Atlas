#!/usr/bin/python

# RIPE Atlas API demo
# Ping measurement can be configured and created using this script

import json
import csv
import requests
import os
import sys
import time
import calendar
import math
from config.config import *

# AUTH = "%s/auth" % os.environ['PWD'] # put the KEY in file named 'auth' under current folder
AUTH = os.path.join(os.path.dirname(__file__), "auth")

MEASUREMENT_NAME = '5_probes_to_alexa_top500'
MES_ID_PING_V4_FILE = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, MEASUREMENT_NAME, '{0}_ping_v4_measurement_ids_complete.txt'.format(MEASUREMENT_NAME))
MES_ID_PING_V6_FILE = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, MEASUREMENT_NAME, '{0}_ping_v6_measurement_ids_complete.txt'.format(MEASUREMENT_NAME))
MES_ID_TRACEROUTE_V4_FILE = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, MEASUREMENT_NAME, '{0}_traceroute_v4_measurement_ids_complete.txt'.format(MEASUREMENT_NAME))
MES_ID_TRACEROUTE_V6_FILE = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, MEASUREMENT_NAME, '{0}_traceroute_v6_measurement_ids_complete.txt'.format(MEASUREMENT_NAME))

STRAT_TIME = '2016-09-08 00:00:00'
STOP_TIME = '2016-09-22 23:59:59'

def ping_v4(target, mes_id_file):
    requests.packages.urllib3.disable_warnings() #disable urllib3 warnings
    # Measurement definition
    #target = 'www.enst.fr'
    description = 'Ping_v4 to %s from probe 22341, 2403, 13842, 2848 and anchor 6118' % target
    af = 4 # can be IPv4 or IPv6
    type = 'ping'
    resolve_on_probe = False # Set to 'true' if you want the probe to resolve your target instead of the RIPE Atlas servers.
    is_oneoff = False # Set this to 'true' to make this measurement a one-off.
    is_public = True # Set true so that the measurement and results are visible to others
    interval = 1800 # default value is 240 seconds; In normal (not one-off) measurements, this value represents the number of seconds between measurements by a single probe.
    # if it's of one-off measurement, why there would be a interval?
    # 60sec is the minimum interval, any value smaller than 60 will cause 400 bad request
    packets = 3 # defualt 3, number of ping packets sent in each ping meaasurement, must between 1 to 16
    size = 48 # unkonwn default value; the size of ping request; must between 1 and 2048
    #Probe description
    probe_count = 5 # probe numbers
    probe_selec = 'probes'
    # can be
    #area: WW, West, North-Central, South-Central, North-East, South-East
    #country: ISO two-letter country code, https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    #prefix: e.g. 193.6.0/8, rumor is that it's not working with prefix option
    #asn: e.g. 147
    #probes: comma-separated list of integers as the value, e.g. "1,2,3"
    #msm (re-use the probes in an existing measurement by specifying the id): e.g. 2310237
    probe_selec_value = '22341, 2403, 13842, 2848, 6118'
    tag_include = ["system-ipv4-works", "system-anchor"]
    tag_exclude = ["system-ipv4-doesnt-work", "system-ipv6-doesnt-work",]
    # there are two types of tags: system assigened ones, see https://atlas.ripe.net/docs/probe-tags/
    # and user assigned ones, see https://atlas.ripe.net/probes/

    start_time = calendar.timegm(time.strptime('{0}'.format(STRAT_TIME), '%Y-%m-%d %H:%M:%S'))
    stop_time =  calendar.timegm(time.strptime('{0}'.format(STOP_TIME), '%Y-%m-%d %H:%M:%S'))

    data = {"definitions": [{ "target": target,
                               "description": description,
                               "type": type,
                               "af": af,
                               "is_oneoff": is_oneoff,
                               "resolve_on_probe": resolve_on_probe,
                               "is_public": is_public,
                               "interval": interval,
                               "packets": packets,
                               "size": size}],
            "probes": [{ "requested": probe_count,
                         "type": probe_selec,
                         "value": probe_selec_value}],
            "start_time": start_time,
            "stop_time": stop_time
    }

    # read key from auth file
    # if not os.path.exists(AUTH):
    #     raise CredentialsNotFound(authfile)
    auth = open(AUTH)
    key = auth.readline()[:-1]
    auth.close()

    # create measurement
    url = "https://atlas.ripe.net/api/v1/measurement/"
    params = {"key": key}
    headers = {"Content-Type": "application/json",
              "Accept": "application/json"}
    results = requests.post(url=url, params=params, headers=headers, data=json.dumps(data))
    print results.url
    print results.status_code
    results.raise_for_status()
    measure_id = int(results.json()["measurements"][0])
    print("Measurement #%s created, please wait the result (it may be long)" % (measure_id))
    mes_id_file.write(str(measure_id)+'\n')

def ping_v6(target, mes_id_file):
    requests.packages.urllib3.disable_warnings() #disable urllib3 warnings
    # Measurement definition
    #target = 'www.enst.fr'
    description = 'Ping_v6 to %s from probe 22341, 2403, 13842, 2848 and anchor 6118' % target
    af = 6 # can be IPv4 or IPv6
    type = 'ping'
    resolve_on_probe = False # Set to 'true' if you want the probe to resolve your target instead of the RIPE Atlas servers.
    is_oneoff = False # Set this to 'true' to make this measurement a one-off.
    is_public = True # Set true so that the measurement and results are visible to others
    interval = 1800 # default value is 240 seconds; In normal (not one-off) measurements, this value represents the number of seconds between measurements by a single probe.
    # if it's of one-off measurement, why there would be a interval?
    # 60sec is the minimum interval, any value smaller than 60 will cause 400 bad request
    packets = 3 # defualt 3, number of ping packets sent in each ping meaasurement, must between 1 to 16
    size = 48 # unkonwn default value; the size of ping request; must between 1 and 2048
    #Probe description
    probe_count = 5 # probe numbers
    probe_selec = 'probes'
    # can be
    #area: WW, West, North-Central, South-Central, North-East, South-East
    #country: ISO two-letter country code, https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    #prefix: e.g. 193.6.0/8, rumor is that it's not working with prefix option
    #asn: e.g. 147
    #probes: comma-separated list of integers as the value, e.g. "1,2,3"
    #msm (re-use the probes in an existing measurement by specifying the id): e.g. 2310237
    probe_selec_value = '22341, 2403, 13842, 2848, 6118'
    tag_include = ["system-ipv4-works", "system-anchor"]
    tag_exclude = ["system-ipv4-doesnt-work", "system-ipv6-doesnt-work",]
    # there are two types of tags: system assigened ones, see https://atlas.ripe.net/docs/probe-tags/
    # and user assigned ones, see https://atlas.ripe.net/probes/

    start_time = calendar.timegm(time.strptime('{0}'.format(STRAT_TIME), '%Y-%m-%d %H:%M:%S'))
    stop_time =  calendar.timegm(time.strptime('{0}'.format(STOP_TIME), '%Y-%m-%d %H:%M:%S'))

    data = {"definitions": [{ "target": target,
                               "description": description,
                               "type": type,
                               "af": af,
                               "is_oneoff": is_oneoff,
                               "resolve_on_probe": resolve_on_probe,
                               "is_public": is_public,
                               "interval": interval,
                               "packets": packets,
                               "size": size}],
            "probes": [{ "requested": probe_count,
                         "type": probe_selec,
                         "value": probe_selec_value}],
            "start_time": start_time,
            "stop_time": stop_time
    }

    # read key from auth file
    # if not os.path.exists(AUTH):
    #     raise CredentialsNotFound(authfile)
    auth = open(AUTH)
    key = auth.readline()[:-1]
    auth.close()

    # create measurement
    url = "https://atlas.ripe.net/api/v1/measurement/"
    params = {"key": key}
    headers = {"Content-Type": "application/json",
              "Accept": "application/json"}
    results = requests.post(url=url, params=params, headers=headers, data=json.dumps(data))
    print results.url
    print results.status_code
    results.raise_for_status()
    measure_id = int(results.json()["measurements"][0])
    print("Measurement #%s created, please wait the result (it may be long)" % (measure_id))
    mes_id_file.write(str(measure_id)+'\n')


def traceroute_v4(target, mes_id_file):
    requests.packages.urllib3.disable_warnings() #disable urllib3 warnings
    # Measurement definition
    #target = 'www.enst.fr'
    description = 'Traceroute_v4 to %s from probe 22341, 2403, 13842, 2848 and anchor 6118' % target
    af = 4 # can be IPv4 or IPv6
    type = 'traceroute'
    resolve_on_probe = False # Set to 'true' if you want the probe to resolve your target instead of the RIPE Atlas servers.
    is_oneoff = False # Set this to 'true' to make this measurement a one-off.
    is_public = True # Set true so that the measurement and results are visible to others
    interval = 3600 # default value is 240 seconds; In normal (not one-off) measurements, this value represents the number of seconds between measurements by a single probe.
    # if it's of one-off measurement, why there would be a interval?
    # 60sec is the minimum interval, any value smaller than 60 will cause 400 bad request
    packets = 3 # defualt 3, number of ping packets sent in each ping meaasurement, must between 1 to 16
    size = 48 # unkonwn default value; the size of ping request; must between 1 and 2048
    #Probe description
    probe_count = 5 # probe numbers
    probe_selec = 'probes'
    # can be
    #area: WW, West, North-Central, South-Central, North-East, South-East
    #country: ISO two-letter country code, https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    #prefix: e.g. 193.6.0/8, rumor is that it's not working with prefix option
    #asn: e.g. 147
    #probes: comma-separated list of integers as the value, e.g. "1,2,3"
    #msm (re-use the probes in an existing measurement by specifying the id): e.g. 2310237
    probe_selec_value = '22341, 2403, 13842, 2848, 6118'
    tag_include = ["system-ipv4-works", "system-anchor"]
    tag_exclude = ["system-ipv4-doesnt-work", "system-ipv6-doesnt-work",]
    # there are two types of tags: system assigened ones, see https://atlas.ripe.net/docs/probe-tags/
    # and user assigned ones, see https://atlas.ripe.net/probes/

    start_time = calendar.timegm(time.strptime('{0}'.format(STRAT_TIME), '%Y-%m-%d %H:%M:%S'))
    # should be a >= 10 mins interval between stop and start time
    stop_time =  calendar.timegm(time.strptime('{0}'.format(STOP_TIME), '%Y-%m-%d %H:%M:%S'))

    protocol="ICMP"

    data = {"definitions": [{ "target": target,
                               "description": description,
                               "type": type,
                               "af": af,
                               "is_oneoff": is_oneoff,
                               "resolve_on_probe": resolve_on_probe,
                               "is_public": is_public,
                               "interval": interval,
                               "protocol": protocol,
                               "packets": packets,
                               "gap_limit": 24,     # To set how many non-responding hops traceroute should try
                               "size": size}],
            "probes": [{ "requested": probe_count,
                         "type": probe_selec,
                         "value": probe_selec_value}],
            "start_time": start_time,
            "stop_time": stop_time
    }

    # read key from auth file
    # if not os.path.exists(AUTH):
    #     raise CredentialsNotFound(authfile)
    auth = open(AUTH)
    key = auth.readline()[:-1]
    auth.close()

    # create measurement
    url = "https://atlas.ripe.net/api/v1/measurement/"
    params = {"key": key}
    headers = {"Content-Type": "application/json",
              "Accept": "application/json"}
    results = requests.post(url=url, params=params, headers=headers, data=json.dumps(data))
    print results.url
    print results.status_code
    results.raise_for_status()
    measure_id = int(results.json()["measurements"][0])
    print("Measurement #%s created, please wait the result (it may be long)" % (measure_id))
    mes_id_file.write(str(measure_id)+'\n')

def traceroute_v6(target, mes_id_file):
    requests.packages.urllib3.disable_warnings() #disable urllib3 warnings
    # Measurement definition
    #target = 'www.enst.fr'
    description = 'Traceroute_v6 to %s from probe 22341, 2403, 13842, 2848 and anchor 6118' % target
    af = 6 # can be IPv4 or IPv6
    type = 'traceroute'
    resolve_on_probe = False # Set to 'true' if you want the probe to resolve your target instead of the RIPE Atlas servers.
    is_oneoff = False # Set this to 'true' to make this measurement a one-off.
    is_public = True # Set true so that the measurement and results are visible to others
    interval = 3600 # default value is 240 seconds; In normal (not one-off) measurements, this value represents the number of seconds between measurements by a single probe.
    # if it's of one-off measurement, why there would be a interval?
    # 60sec is the minimum interval, any value smaller than 60 will cause 400 bad request
    packets = 3 # defualt 3, number of ping packets sent in each ping meaasurement, must between 1 to 16
    size = 48 # unkonwn default value; the size of ping request; must between 1 and 2048
    #Probe description
    probe_count = 5 # probe numbers
    probe_selec = 'probes'
    # can be
    #area: WW, West, North-Central, South-Central, North-East, South-East
    #country: ISO two-letter country code, https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    #prefix: e.g. 193.6.0/8, rumor is that it's not working with prefix option
    #asn: e.g. 147
    #probes: comma-separated list of integers as the value, e.g. "1,2,3"
    #msm (re-use the probes in an existing measurement by specifying the id): e.g. 2310237
    probe_selec_value = '22341, 2403, 13842, 2848, 6118'
    tag_include = ["system-ipv4-works", "system-anchor"]
    tag_exclude = ["system-ipv4-doesnt-work", "system-ipv6-doesnt-work",]
    # there are two types of tags: system assigened ones, see https://atlas.ripe.net/docs/probe-tags/
    # and user assigned ones, see https://atlas.ripe.net/probes/

    start_time = calendar.timegm(time.strptime('{0}'.format(STRAT_TIME), '%Y-%m-%d %H:%M:%S'))
    # should be a >= 10 mins interval between stop and start time
    stop_time =  calendar.timegm(time.strptime('{0}'.format(STOP_TIME), '%Y-%m-%d %H:%M:%S'))

    protocol="ICMP"

    data = {"definitions": [{ "target": target,
                               "description": description,
                               "type": type,
                               "af": af,
                               "is_oneoff": is_oneoff,
                               "resolve_on_probe": resolve_on_probe,
                               "is_public": is_public,
                               "interval": interval,
                               "protocol": protocol,
                               "packets": packets,
                               "gap_limit": 24,     # To set how many non-responding hops traceroute should try
                               "size": size}],
            "probes": [{ "requested": probe_count,
                         "type": probe_selec,
                         "value": probe_selec_value}],
            "start_time": start_time,
            "stop_time": stop_time
    }

    # read key from auth file
    # if not os.path.exists(AUTH):
    #     raise CredentialsNotFound(authfile)
    auth = open(AUTH)
    key = auth.readline()[:-1]
    auth.close()

    # create measurement
    url = "https://atlas.ripe.net/api/v1/measurement/"
    params = {"key": key}
    headers = {"Content-Type": "application/json",
              "Accept": "application/json"}
    results = requests.post(url=url, params=params, headers=headers, data=json.dumps(data))
    print results.url
    print results.status_code
    results.raise_for_status()
    measure_id = int(results.json()["measurements"][0])
    print("Measurement #%s created, please wait the result (it may be long)" % (measure_id))
    mes_id_file.write(str(measure_id)+'\n')



if __name__ == "__main__":
    # # When you want to try with a small scall of website, use the command below
    # target_site_v4_l = ['193.51.224.185', '140.205.220.96']
    # target_site_v6_l = ['2001:4860:b002::68', '2607:f0d0:1002:51::4']

    # When you want to try the whole scale of website, use the command below

    target_site_v4_l = []
    target_site_v6_l = []
    # exp_input = 'top_510_websites_fr.csv'
    exp_input = 'xak.csv'
    with open(exp_input) as exp_handler:
        reader = csv.reader(exp_handler, delimiter=';')
        next(reader)
        for csv_line in map(list, reader):
            target_site_v4_l.append(csv_line[1])
            # print len(csv_line), csv_line
            print len([i for i in csv_line if i != '']), [i for i in csv_line if i != ''] # To remove null element in list
            if len([i for i in csv_line if i != '']) > 4:
                target_site_v6_l.append(csv_line[4])

    print "target_site_v4_l:", target_site_v4_l
    print "target_site_v6_l", target_site_v6_l

    # with open(MES_ID_PING_V4_FILE, 'w') as ping_v4_file, open(MES_ID_PING_V6_FILE, 'w') as ping_v6_file, \
    #         open(MES_ID_TRACEROUTE_V4_FILE, 'w') as traceroute_v4_file, open(MES_ID_TRACEROUTE_V6_FILE, 'w') as traceroute_v6_file:
    #     target_site_l = [str(e) for e in target_site_v4_l]
    #     for target in target_site_v4_l:
    #         try:
    #             ping_v4(target, ping_v4_file)
    #         except requests.exceptions.HTTPError:
    #             print "Due to ping_v4, cannot launch mesurement for {0}".format(target)
    #         try:
    #             traceroute_v4(target, traceroute_v4_file)
    #         except requests.exceptions.HTTPError:
    #             print "Due to traceroute_v4, cannot launch mesurement for {0}".format(target)
    #
    #     for target in target_site_v6_l:
    #         try:
    #             ping_v6(target, ping_v6_file)
    #         except requests.exceptions.HTTPError:
    #             print "Due to ping_v6, cannot launch mesurement for {0}".format(target)
    #         try:
    #             traceroute_v6(target, traceroute_v6_file)
    #         except requests.exceptions.HTTPError:
    #             print "Due to traceroute_v6, cannot launch mesurement for {0}".format(target)