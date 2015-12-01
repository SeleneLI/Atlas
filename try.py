__author__ = 'yueli'

import matplotlib.pyplot as plt


if __name__ == "__main__":

    l = [2.1, 2.3, 1.8, 4.5, 2.7, 4.7]

    l_int = [int(value) for value in l]
    print "l_int:", l_int


    d = {}

    for x in l_int:
        if x not in d.keys():
            d[x] = 1
        else:
            d[x] += 1

    print d

    x_axis = d.keys()
    y_axis = d.values()

    print x_axis
    print y_axis


    n_groups = len(d.keys())
    indexs = range(n_groups)
    bar_width = 0.35
    y_values = d.values()


    plt.grid(True)

    # plt.xlabel(X_LABEL, fontsize=20)
    # plt.ylabel(Y_LABEL, fontsize=20)
    # plt.title('Percentage of stability for 5 vantage points', fontsize=18)
    plt.xticks([j+ bar_width/2 for j in indexs], d.keys(), fontsize=16)
    plt.xlim(-0.3, n_groups-0.3)
    plt.ylim(0, max(y_values)+1)
    rect = plt.bar(indexs, y_values, bar_width, color='b')
    # autolabel(rect)
    # plt.legend(loc='upper right')


    plt.show()