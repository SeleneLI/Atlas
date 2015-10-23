#!/usr/bin/python
#visualize ping measuremnt result in 3d
import json
import os
import sys
import time
import calendar
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import itertools
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

MODE = ['avg', 'min', 'max', 'loss']
MODE_LABEL = {'avg': 'Avg. RTT (ms)',
              'min': 'Min. RTT(ms)',
              'max': 'Max. RTT(ms)',
              'loss': 'Packet loss %'}

def read_at_raw(file):
    at_raw = json.load(open(file, 'r'))
    at_prob_rtt = {}
    for mes in at_raw:
        prob_id = mes['prb_id']
        if prob_id not in at_prob_rtt:
            at_prob_rtt[prob_id] = {'src_ip': mes['from'],
                                    'time': [],
                                    'avg': [],
                                    'min':[],
                                    'max':[],
                                    'loss':[]}
        epoch_time = mes['timestamp']
        utc_string = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(epoch_time))
        mdate_time = mdates.strpdate2num('%Y-%m-%d %H:%M:%S')(utc_string)
        at_prob_rtt[prob_id]['time'].append(mdate_time)
        at_prob_rtt[prob_id]['min'].append(mes['min'])
        at_prob_rtt[prob_id]['avg'].append(mes['avg'])
        at_prob_rtt[prob_id]['max'].append(mes['max'])
        if mes['sent'] == 0:
            at_prob_rtt[prob_id]['loss'].append(100)
        else:
            at_prob_rtt[prob_id]['loss'].append((1-float(mes['rcvd'])/mes['sent'])*100)
    return at_prob_rtt


def main(argv):
    if len(argv) >2:
        print "Usage: python plot_ping.py mode #id or python plot_ping #id (defaut mode is avg)"
        exit()

    if len(argv) == 2:
        mode = argv[0]
        if mode not in MODE:
            print "mode %s not recognized, set to default mode 'avg', all possible modes are %s" % (mode, MODE)
            mode = 'avg'
    else:
        mode = 'avg'
    measure_id = argv[-1]
    filename = measure_id + '.json'

    if not os.path.isfile(filename):
        print"Measurement results for #%s doesn't exist." % measure_id
        exit()

    trace_dict = read_at_raw(filename)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    y_lable = []
    yi=1
    for probe in trace_dict:
        ax.plot(xs=trace_dict[probe]['time'], ys=[yi]*len(trace_dict[probe]['time']),zs=trace_dict[probe][mode], ls='-', color='black', marker='None')
        y_lable.append(probe)
        yi += 1
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=60))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.set_yticklabels(y_lable)
    ax.set_ylabel('Probe ID', fontsize=16)
    ax.set_xlabel('Time', fontsize=16)
    ax.set_zlabel(MODE_LABEL[mode], fontsize=16)
    plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])


