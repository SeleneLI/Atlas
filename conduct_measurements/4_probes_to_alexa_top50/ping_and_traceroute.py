#!/usr/bin/python

# RIPE Atlas API demo
# Ping measurement can be configured and created using this script

import json
import requests
import os
import sys
import time
import calendar
import math
from config.config import *

# AUTH = "%s/auth" % os.environ['PWD'] # put the KEY in file named 'auth' under current folder
AUTH = os.path.join(os.path.dirname(__file__), "auth")

MEASUREMENT_NAME = '4_probes_to_alexa_top50'
MES_ID_PING_FILE = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, MEASUREMENT_NAME, '{0}_ping_measurement_ids_complete.txt'.format(MEASUREMENT_NAME))
MES_ID_TRACEROUTE_FILE = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, MEASUREMENT_NAME, '{0}_traceroute_measurement_ids_complete.txt'.format(MEASUREMENT_NAME))


def ping(target, mes_id_file):
    requests.packages.urllib3.disable_warnings() #disable urllib3 warnings
    # Measurement definition
    #target = 'www.enst.fr'
    description = 'Ping to %s from probe 22341, 13842, 16958 and anchor 6118' % target
    af = 4 # can be IPv4 or IPv6
    type = 'ping'
    resolve_on_probe = False # Set to 'true' if you want the probe to resolve your target instead of the RIPE Atlas servers.
    is_oneoff = False # Set this to 'true' to make this measurement a one-off.
    is_public = True # Set true so that the measurement and results are visible to others
    interval = 600 # default value is 240 seconds; In normal (not one-off) measurements, this value represents the number of seconds between measurements by a single probe.
    # if it's of one-off measurement, why there would be a interval?
    # 60sec is the minimum interval, any value smaller than 60 will cause 400 bad request
    packets = 3 # defualt 3, number of ping packets sent in each ping meaasurement, must between 1 to 16
    size = 48 # unkonwn default value; the size of ping request; must between 1 and 2048
    #Probe description
    probe_count = 4 # probe numbers
    probe_selec = 'probes'
    # can be
    #area: WW, West, North-Central, South-Central, North-East, South-East
    #country: ISO two-letter country code, https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    #prefix: e.g. 193.6.0/8, rumor is that it's not working with prefix option
    #asn: e.g. 147
    #probes: comma-separated list of integers as the value, e.g. "1,2,3"
    #msm (re-use the probes in an existing measurement by specifying the id): e.g. 2310237
    probe_selec_value = '13842, 22341, 16958, 6118'
    tag_include = ["system-ipv4-works", "system-anchor"]
    tag_exclude = ["system-ipv4-doesnt-work", "system-ipv6-doesnt-work",]
    # there are two types of tags: system assigened ones, see https://atlas.ripe.net/docs/probe-tags/
    # and user assigned ones, see https://atlas.ripe.net/probes/

    start_time = calendar.timegm(time.strptime('2015-10-22 10:00:00', '%Y-%m-%d %H:%M:%S'))
    stop_time =  calendar.timegm(time.strptime('2015-10-22 16:00:00', '%Y-%m-%d %H:%M:%S'))

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
    if not os.path.exists(AUTH):
        raise CredentialsNotFound(authfile)
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
    mes_id_file.write(measure_id, '\n')

def traceroute(target, mes_id_file):
    requests.packages.urllib3.disable_warnings() #disable urllib3 warnings
    # Measurement definition
    #target = 'www.enst.fr'
    description = 'Traceroute to %s from probe 22341, 13842, 16958 and anchor 6118' % target
    af = 4 # can be IPv4 or IPv6
    type = 'traceroute'
    resolve_on_probe = False # Set to 'true' if you want the probe to resolve your target instead of the RIPE Atlas servers.
    is_oneoff = False # Set this to 'true' to make this measurement a one-off.
    is_public = True # Set true so that the measurement and results are visible to others
    interval = 1800 # default value is 240 seconds; In normal (not one-off) measurements, this value represents the number of seconds between measurements by a single probe.
    # if it's of one-off measurement, why there would be a interval?
    # 60sec is the minimum interval, any value smaller than 60 will cause 400 bad request
    packets = 3 # defualt 3, number of ping packets sent in each ping meaasurement, must between 1 to 16
    size = 48 # unkonwn default value; the size of ping request; must between 1 and 2048
    #Probe description
    probe_count = 4 # probe numbers
    probe_selec = 'probes'
    # can be
    #area: WW, West, North-Central, South-Central, North-East, South-East
    #country: ISO two-letter country code, https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    #prefix: e.g. 193.6.0/8, rumor is that it's not working with prefix option
    #asn: e.g. 147
    #probes: comma-separated list of integers as the value, e.g. "1,2,3"
    #msm (re-use the probes in an existing measurement by specifying the id): e.g. 2310237
    probe_selec_value = '13842, 22341, 16958, 6118'
    tag_include = ["system-ipv4-works", "system-anchor"]
    tag_exclude = ["system-ipv4-doesnt-work", "system-ipv6-doesnt-work",]
    # there are two types of tags: system assigened ones, see https://atlas.ripe.net/docs/probe-tags/
    # and user assigned ones, see https://atlas.ripe.net/probes/

    start_time = calendar.timegm(time.strptime('2015-10-22 10:00:00', '%Y-%m-%d %H:%M:%S'))
    stop_time =  calendar.timegm(time.strptime('2015-10-22 16:00:00', '%Y-%m-%d %H:%M:%S'))

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
                               "size": size}],
            "probes": [{ "requested": probe_count,
                         "type": probe_selec,
                         "value": probe_selec_value}],
            "start_time": start_time,
            "stop_time": stop_time
    }

    # read key from auth file
    if not os.path.exists(AUTH):
        raise CredentialsNotFound(authfile)
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
    mes_id_file.write(measure_id, '\n')

if __name__ == "__main__":
    target_site_l = [ u'Facebook.com', u'Youtube.com', u'Baidu.com', u'Yahoo.com', u'Amazon.com',
                     u'Wikipedia.org', u'Qq.com', u'Twitter.com', u'Taobao.com', u'Live.com',
                     u'Sina.com.cn', u'Linkedin.com', u'Yahoo.co.jp', u'Weibo.com', u'Ebay.com',
                     u'Yandex.ru', u'Hao123.com', u'Vk.com', u'Bing.com', u'Instagram.com',
                     u'T.co', u'Msn.com', u'Amazon.co.jp',  u'Pinterest.com', u'Aliexpress.com',
                     u'Ask.com', u'Tmall.com', u'Blogspot.com', u'Wordpress.com', u'Reddit.com',
                     u'Apple.com', u'Paypal.com', u'Onclickads.net',  u'Mail.ru', u'Tumblr.com',
                     u'Sohu.com', u'Microsoft.com', u'Imgur.com', u'Xvideos.com', u'Imdb.com',
                      u'Netflix.com', u'Gmw.cn', u'Fc2.com', u'Amazon.de', u'360.cn',
                      u'Alibaba.com', u'Go.com', u'Stackoverflow.com',  u'Ok.ru', u'Craigslist.org',
                      u'Tianya.cn', u'Amazon.co.uk', u'Pornhub.com', u'Rakuten.co.jp', u'Blogger.com',
                      u'Naver.com', u'Amazon.in', u'Espn.go.com', u'Xhamster.com', u'Flipkart.com'
    ]

    with open(MES_ID_PING_FILE, 'w') as ping_file, open(MES_ID_TRACEROUTE_FILE, 'w') as traceroute_file:
        target_site_l = [str(e) for e in target_site_l]
        for target in target_site_l:
            try:
                ping(target, ping_file)
                traceroute(target, traceroute_file)
            except requests.exceptions.HTTPError:
                print "Due to unknown cause, cannot launch mesurement for {0}".format(target)