#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pprint import pprint

import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

import random
from time import time
from backtest import BackTest

if __name__ == '__main__':
    ts_code = '002475.SZ'

    s_time = time()
    bt = BackTest()
    bt.set_code(ts_code)
    e_time = time()
    print('BackTest cost %.2f s' % (e_time - s_time))

    start_date = '20220712'
    end_date = '20220713'
    bt.push({'cost': 10, 'qty': 10})
    bt.show()
    bt.pop(8.5)
    bt.show()
    print()
 
    bt.buy({'cost': 10, 'qty': 10})
    bt.show()
    bt.sell({'cost': 8.5, 'qty': 5})
    bt.show()
    print()

    # use fft to get freq of dayline
    y_low = fft(bt.low_list)
    y_high = fft(bt.high_list)

    l = len(y_high)
    f_list = np.arange(0, l, 1)
    xf = fftfreq(3226, 1.0/2.0)[:3226//2]

    plt.plot(bt.date_list, bt.low_list)
    plt.show()
    plt.plot(f_list, np.abs(y_high))
    plt.show()
    plt.plot(xf[10:l-10:10], np.abs(y_high)[10:l-10:10])
    plt.grid()
    plt.show()
