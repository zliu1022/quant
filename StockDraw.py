#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pprint import pprint
from StockQuery import StockQuery
import matplotlib.pyplot as plt
from time import time

class StockDraw:
    def __init__(self):
        return

    def draw(self, day):
        day = day[::-1]
        date_list = [ x['date'] for x in day]
        low_list = [ x['low'] for x in day]
        high_list = [ x['low'] for x in day]

        plt.plot(date_list, low_list)
        plt.grid()
        plt.show()
        return

if __name__ == '__main__':
    s_time = time()
    sq = StockQuery()
    sd = StockDraw()

    start_date = '20220101'
    end_date = '20220901'
    amount = 2000000000
    ref = sq.stat_day_amount(start_date, end_date, amount)

    for item in ref:
        ts_code = item['_id']['ts_code']
        amount = item['amount']
        num = item['num']
        if num > 160:
            print('%s %3d %.1f' % (ts_code, num, amount))
            day = sq.query_day_code_date(ts_code, '20220101', '20220908')

            e_time = time()
            print('draw cost %.2f s' % (e_time - s_time))
            sd.draw(day)
            print()
            quit()

