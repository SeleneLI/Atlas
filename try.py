__author__ = 'yueli'

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.tools.plotting import autocorrelation_plot

def difference_calculator_mean_var(target_dict, ref_probe):
    dict_mean = {}
    dict_var = {}
    for key in target_dict.keys():
        if key != ref_probe:
            dict_mean[key] = np.mean(abs(np.matrix(target_dict[key]) - np.matrix(target_dict[ref_probe])).tolist()[0])
            dict_var[key] = np.var(abs(np.matrix(target_dict[key]) - np.matrix(target_dict[ref_probe])).tolist()[0])

    return dict_mean, dict_var

if __name__ == "__main__":
    simulated_dict = {'31.13.76.102': {'LISP-Lab': [163.7450633333, 161.801375, 162.7511183333],
                      'mPlane': [150.0483333333, 144.6703333333, 143.2673333333],
                      'FranceIX': [129.097423, 129.014165, 128.961054],
                      'rmd': [17.0287633333, 17.338855, 17.146705]},
                      '74.125.136.190': {'LISP-Lab': [163.7450633333, 161.801375, 162.7511183333],
                      'mPlane': [150.0483333333, 144.6703333333, 143.2673333333],
                      'FranceIX': [129.097423, 129.014165, 128.961054],
                      'rmd': [17.0287633333, 17.338855, 17.146705]}
    }



    dict_probe_dest_mean = {}
    dict_probe_dest_var = {}
    for key_dest in simulated_dict.keys():
        dict_mean_temp, dict_var_temp = difference_calculator_mean_var(simulated_dict[key_dest], 'FranceIX')
        for key_probe in dict_mean_temp.keys():
            print "key_probe:", key_probe
            if key_probe not in dict_probe_dest_mean.keys():
                dict_probe_dest_mean[key_probe] = {}
                dict_probe_dest_mean[key_probe][key_dest] = dict_mean_temp[key_probe]
                dict_probe_dest_var[key_probe] = {}
                dict_probe_dest_var[key_probe][key_dest] = dict_var_temp[key_probe]
            else:
                dict_probe_dest_mean[key_probe][key_dest] = dict_mean_temp[key_probe]
                dict_probe_dest_var[key_probe][key_dest] = dict_var_temp[key_probe]


    print "dict_probe_dest_mean =", dict_probe_dest_mean
    print "dict_probe_dest_var =", dict_probe_dest_var