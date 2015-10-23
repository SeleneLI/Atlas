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

AUTH = "%s/auth" % os.environ['PWD'] # put the KEY in file named 'auth' under current folder

def main(argv):

    requests.packages.urllib3.disable_warnings() #disable urllib3 warnings

    if len(argv) != 1:
        print "Usage: python ping.py www.example.com\nParameter modification should be done within the script.\n"
        exit()

    # Measurement definition
    target = argv[-1]
    #target = 'www.enst.fr'
    description = 'Ping to %s from Anchors' % target
    af = 4 # can be IPv4 or IPv6
    type = 'traceroute'
    resolve_on_probe = True # Set to 'true' if you want the probe to resolve your target instead of the RIPE Atlas servers.
    is_oneoff = False # Set this to 'true' to make this measurement a one-off.
    is_public = True # Set true so that the measurement and results are visible to others

    interval = 900 # default value is 240 seconds; In normal (not one-off) measurements, this value represents the number of seconds between measurements by a single probe.
    # if it's of one-off measurement, why there would be a interval?
    # 60sec is the minimum interval, any value smaller than 60 will cause 400 bad request
    packets = 3 # defualt 3, number of ping packets sent in each ping meaasurement, must between 1 to 16
    size = 48 # unkonwn default value; the size of ping request; must between 1 and 2048

    #Probe description
    probe_count = 149 # probe numbers
    probe_selec = 'area'
    # can be
    #area: WW, West, North-Central, South-Central, North-East, South-East
    #country: ISO two-letter country code, https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    #prefix: e.g. 193.6.0/8, rumor is that it's not working with prefix option
    #asn: e.g. 147
    #probes: comma-separated list of integers as the value, e.g. "1,2,3"
    #msm (re-use the probes in an existing measurement by specifying the id): e.g. 2310237
    probe_selec_value = 'WW'
    tag_include = ["system-ipv4-works","system-anchor"]
    tag_exclude = ["system-ipv4-doesnt-work", "system-ipv6-doesnt-work",]
    # there are two types of tags: system assigened ones, see https://atlas.ripe.net/docs/probe-tags/
    # and user assigned ones, see https://atlas.ripe.net/probes/

    start_time = calendar.timegm(time.strptime('2015-10-21 15:34:00', '%Y-%m-%d %H:%M:%S'))
    stop_time =  calendar.timegm(time.strptime('2015-10-21 15:36:00', '%Y-%m-%d %H:%M:%S'))
    # UTC time to Unix Timestamp; Unix timestamp is the second counts since 1970
    # when

    #start_time = math.ceil(time.time()) # current Unix timestamp
    #stop_time = start_time + 60*180 #ten minutes later
    #in the case of on-off meassurement, passing time parameters will cause 400 bad request

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
                         "value": probe_selec_value,
                         "tags":{"include":tag_include,
                                 "exclude":tag_exclude}}],
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

    # read measurement status
    #url = "https://atlas.ripe.net/api/v1/measurement/%d/" % measure_id
    #params = {"key": key}
    #headers = {"Accept": "application/json"}
    #while True:
    #    results = requests.get(url=url, params=params, headers=headers)
    #    if results.status_code == requests.codes.ok:
    #        status = results.json()["status"]["name"]
    #        if status == "Ongoing" or status == "Specified":
    #            #print "Not yet finished..."
    #            time.sleep(10)
    #        elif status == "Stopped":
    #            break
    #        else:
    #            print "Unknow status: %s" % status
    #            time.sleep(30)
    #    results.raise_for_status()
    ##more often than not results are already available on line but the status won't change....
    #print "Measurement %d finished." % measure_id


if __name__ == "__main__":
    main(sys.argv[1:])