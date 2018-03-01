# -*- coding: utf-8 -*-
# The function of this script: try some new methods
__author__ = 'yueli'
from config.config import *
import numpy as np
import pandas as pd

FILE_A = os.path.join(ATLAS_TRACES, 'json2csv', '5_probes_to_alexa_top510', 'ping_v4', '5_probes_to_alexa_top510_avg.csv')
FILE_B = os.path.join(ATLAS_TRACES, 'json2csv', 'Low_reliability_verification', 'ping_v4', 'Low_reliability_verification_avg.csv')

dest_list_a = []
dest_list_b = []
with open(FILE_A) as f_a:
    next(f_a)
    for line in f_a:
        if line.split(';')[2] == 'LIP6':
            if (line.split(';')[3:].count('-1.0')/7.20) > 50:
                dest_list_a.append((line.split(';')[1], line.split(';')[3:].count('-1.0')/7.20))

print 'dest_list_a'
print dest_list_a

# with open(FILE_B) as f_b:
#     next(f_b)
#     for line in f_b:
#         if line.split(';')[2] == 'LIP6':
#             if (line.split(';')[3:].count('-1.0')/0.48) > 0:
#                 dest_list_a.append((line.split(';')[1], line.split(';')[3:].count('-1.0')/0.48))
#
# print 'dest_list_b'
# print dest_list_b

print "Difference:"
# print list(set(dest_list_a) - set(dest_list_b))