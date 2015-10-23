#!/usr/bin/python

# RIPE Atlas API demo
# Given a measurement id, fetch the results of the measurement and store them in a local file


import requests
import os
import sys


AUTH = "%s/auth" % os.environ['PWD'] # put the KEY in file named 'auth' under current folder

def main(argv):

    requests.packages.urllib3.disable_warnings() #disable urllib3 warnings

    if len(argv) != 1:
        print "Usage: python fetch_result.py #id"
        exit()
    
    measure_id = argv[-1]

    # read key from auth file
    if not os.path.exists(AUTH):
        raise CredentialsNotFound(authfile)
    auth = open(AUTH)
    key = auth.readline()[:-1]
    auth.close()
    
    url = "https://atlas.ripe.net/api/v1/measurement/%s/result/" % int(measure_id)
    params = {"key": key}
    headers = {"Accept": "application/json"}
    results = requests.get(url=url, params=params, headers=headers)

    file = '%s/%s.json' % (os.environ['PWD'], measure_id)
    f = open(file, 'w')
    f.write(results.text)
    f.close()
     
if __name__ == "__main__":
    main(sys.argv[1:])