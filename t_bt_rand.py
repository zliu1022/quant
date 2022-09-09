#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pprint import pprint

import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

import random
from time import time

from BackTest import BackTest

if __name__ == '__main__':
    ts_code = '603005.SH'

    s_time = time()
    bt = BackTest()
    bt.set_code(ts_code)
    e_time = time()
    print('BackTest cost %.2f s' % (e_time - s_time))

    # review dayline and show bonus
    start_date = '20220501'
    end_date = '20220531'
    run_num = 10

    rev = 0.0 #revenue
    rev_list = []
    rev_ratio = 0.0
    rev_ratio_list = []

    s_time = time()
    for _ in range(0, run_num):
        bt.clear_hold()
        bt.set_cash(10000)
        bt.run(start_date, end_date)

        rev = bt.cash + bt.mkt_cost - bt.ori_cash
        rev_ratio = (bt.mkt_cost-bt.total_cost) / bt.max_cost
        rev_list.append(rev)
        rev_ratio_list.append(rev_ratio)
        print()
    e_time = time()
    print('Run cost %.2f s each cost %.2f s' % ( (e_time - s_time), (e_time - s_time)/float(run_num)))

    rev_arr = np.array(rev_list)
    print('avg %.2f' % np.average(rev_arr))
    print('mean %.2f' % np.mean(rev_arr))
    print('std %.2f' % np.std(rev_arr))
    print('var %.2f' % np.var(rev_arr))
    print()

    rev_ratio_arr = np.array(rev_ratio_list)
    print('avg %.1f%%'  % (100.0*np.average(rev_ratio_arr)))
    print('mean %.1f%%' % (np.mean(rev_ratio_arr)*100.0))
    print('std %.1f%%'  % (np.std(rev_ratio_arr)*100.0))
    print('var %.1f%%'  % (np.var(rev_ratio_arr)*100.0))
    print()
