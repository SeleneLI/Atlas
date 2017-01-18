#!/usr/bin/python

# RIPE Atlas API demo
# Ping measurement can be configured and created using this script

from ripe.atlas.cousteau import AtlasStopRequest
from config.config import *

# ATLAS_STOP_API_KEY = ""
# AUTH = "%s/auth" % os.environ['PWD'] # put the KEY in file named 'auth' under current folder
AUTH = os.path.join(os.path.dirname(__file__), "auth_stop")

MEASUREMENT_NAME = '5_probes_to_alexa_top510'
MES_ID_PING_V4_FILE = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, MEASUREMENT_NAME, '{0}_ping_v4_measurement_ids_complete.txt'.format(MEASUREMENT_NAME))
MES_ID_PING_V6_FILE = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, MEASUREMENT_NAME, '{0}_ping_v6_measurement_ids_complete.txt'.format(MEASUREMENT_NAME))
MES_ID_TRACEROUTE_V4_FILE = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, MEASUREMENT_NAME, '{0}_traceroute_v4_measurement_ids_complete.txt'.format(MEASUREMENT_NAME))
MES_ID_TRACEROUTE_V6_FILE = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, MEASUREMENT_NAME, '{0}_traceroute_v6_measurement_ids_complete.txt'.format(MEASUREMENT_NAME))

MES_ID_PING_V4_FILE_RUN = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, MEASUREMENT_NAME, '{0}_ping_v4_measurement_ids_stop.txt'.format(MEASUREMENT_NAME))
MES_ID_PING_V6_FILE_RUN = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, MEASUREMENT_NAME, '{0}_ping_v6_measurement_ids_stop.txt'.format(MEASUREMENT_NAME))
MES_ID_TRACEROUTE_V4_FILE_RUN = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, MEASUREMENT_NAME, '{0}_traceroute_v4_measurement_ids_stop.txt'.format(MEASUREMENT_NAME))
MES_ID_TRACEROUTE_V6_FILE_RUN = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, MEASUREMENT_NAME, '{0}_traceroute_v6_measurement_ids_stop.txt'.format(MEASUREMENT_NAME))

# Doesn't work if we use auth_file !!!!
# # read key from auth file
# # if not os.path.exists(AUTH):
# #     raise CredentialsNotFound(authfile)
# auth = open(AUTH)
# ATLAS_STOP_API_KEY = auth.readline()[:-1]
# auth.close()
# print type(ATLAS_STOP_API_KEY), ATLAS_STOP_API_KEY

# Stop the experiment request by using its measurement id
def stop_exp(msm_id_list, stop_file):
    with open(stop_file, 'w') as f_stop:
        for measurement_id in msm_id_list:

            atlas_request = AtlasStopRequest(msm_id = measurement_id, key = "fbae8ef7-d73e-413a-af8e-9d709dcc1148")

            (is_success, response) = atlas_request.create()
            if is_success:
                f_stop.write(str(measurement_id) + '\n')
            print is_success
            print response


if __name__ == "__main__":

    ping_v4_msm_id_list = []
    ping_v6_msm_id_list = []
    traceroute_v4_msm_id_list = []
    traceroute_v6_msm_id_list = []

    with open(MES_ID_PING_V4_FILE) as ping_v4_file, open(MES_ID_PING_V6_FILE) as ping_v6_file, \
            open(MES_ID_TRACEROUTE_V4_FILE) as traceroute_v4_file, open(MES_ID_TRACEROUTE_V6_FILE) as traceroute_v6_file:

        for line in ping_v4_file:
            ping_v4_msm_id_list.append(int(line.strip()))
        for line in ping_v6_file:
            ping_v6_msm_id_list.append(int(line.strip()))
        for line in traceroute_v4_file:
            traceroute_v4_msm_id_list.append(int(line.strip()))
        for line in traceroute_v6_file:
            traceroute_v6_msm_id_list.append(int(line.strip()))

    print ping_v4_msm_id_list
    print ping_v6_msm_id_list
    print traceroute_v4_msm_id_list
    print traceroute_v6_msm_id_list

    # stop_exp(ping_v4_msm_id_list, MES_ID_PING_V4_FILE_RUN)
    # stop_exp(ping_v6_msm_id_list, MES_ID_PING_V6_FILE_RUN)
    stop_exp(traceroute_v4_msm_id_list, MES_ID_TRACEROUTE_V4_FILE_RUN)
    # stop_exp(traceroute_v6_msm_id_list, MES_ID_TRACEROUTE_V6_FILE_RUN)

