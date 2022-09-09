#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pprint import pprint
from StockQuery import StockQuery
import matplotlib.pyplot as plt

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
    sq = StockQuery()
    sd = StockDraw()

    amount = 2000000000
    ref = sq.query_day_amount(amount)

    for item in ref:
        ts_code = item['_id']['ts_code']
        amount = item['amount']
        num = item['num']
        if num > 500:
            print('%s %3d %.1f' % (ts_code, num, amount))

            day = sq.query_day_code_date(ts_code, '20220101', '20220908')
            sd.draw(day)
            print()
            quit()

