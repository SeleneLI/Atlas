# -*- coding: utf-8 -*-
# The function of this script: try some new methods
__author__ = 'yueli'



import matplotlib.pyplot as plt

advance_purchase_list = [1, 2.5, 1, 5, 36]
print advance_purchase_list
print max(advance_purchase_list)
# plt.hist(advance_purchase_list, max(advance_purchase_list), normed=1)
plt.bar(range(len(advance_purchase_list)), advance_purchase_list)
plt.show()