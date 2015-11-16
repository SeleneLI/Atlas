__author__ = 'yueli'
# -*- coding: utf-8 -*-
# 这个script用来模拟产生一系列measurement id，并把它们存在一个txt文档里

import os
import sys
from config.config import *

# 由于产生实验的时候measurement id“基本上”是连续的，所以用循环来产生，只要存储的时候剔除掉不是自己做实验的id即可
def produce_measurement_id():
    list_measurement_id = []
    # 在 https://atlas.ripe.net/measurements/?mine=3&status=&kind=&af=&age=&search=&order=#tab-mine 上想实际下载
    # 编号 2841000 到 2841100 的 measurement
    for i in range (2841000, 2841100, 2):
        # 因为50个不同dest而产生的100组ping和traceroute实验得measurement id基本连续，除了2841073这个id号
        if i != 2841073:
            list_measurement_id.append(i)

    return list_measurement_id

if __name__ == "__main__":
    subfolder_name = '4_probes_to_alexa_top50'
    file_name = '4_probes_to_alexa_top50_ping_measurement_ids_complete.txt'
    results = produce_measurement_id()
    file = os.path.join(ATLAS_CONDUCT_MEASUREMENTS, subfolder_name, file_name)
    f = open(file, 'w')
    for id in results:
        f.write(str(id)+'\n')
    f.close()
    print produce_measurement_id()
    print len(produce_measurement_id())