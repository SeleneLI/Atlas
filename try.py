__author__ = 'yueli'

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.tools.plotting import autocorrelation_plot


def periodicity_verified_autocorr(sig,lags):
        n = len(sig)
        print "n:", n
        x = np.array([float(sig) for sig in sig])
        print "x:", x
        result = [np.correlate(x[i:]-x[i:].mean(),x[:n-i]-x[:n-i].mean())[0]\
            /(x[i:].std()*x[:n-i].std()*(n-i)) \
            for i in range(1,lags+1)]
        print "result:", result

        plt.plot(np.arange(1, lags+1), result,'red')
        # plt.xlim(1, len(np.arange(1, lags+1))/2)
        plt.xlabel("Order from 1 to n/2-1")
        plt.ylabel("Auto-\ncorrelation")
        plt.show()

        return result

if __name__ == "__main__":
    series = [10, 11, 12, 10.1, 11.1, 12.1, 9.9, 10.9, 11.9, 10.05]
    s_ping = [0.816, 0.682, 0.596, 0.743, 0.725, 0.692, 0.770, 0.623, 0.746, 0.689, 0.747, 0.607, 0.641, 0.756, 0.708, 0.713, 0.663, 0.779, 0.775, 0.721, 0.715, 0.721, 0.701, 0.588, 0.740, 0.715, 0.818, 0.675, 0.691, 0.530, 0.711, 0.589, 0.718]
    s = pd.Series(s_ping)
    autocorrelation_plot(s)
    plt.show()