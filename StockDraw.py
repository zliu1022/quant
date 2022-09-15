#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pprint import pprint
from StockQuery import StockQuery
import matplotlib.pyplot as plt
from time import time

class StockDraw:
    def __init__(self):
        return

    def draw(self, ts_code, day):
        day = day[::-1]
        day_len = len(day)

        date_list = [ x['date'] for x in day]
        low_list = [ x['low'] for x in day]
        high_list = [ x['high'] for x in day]

        plt.figure()

        plt.plot(date_list, low_list)
        plt.plot(date_list, high_list)

        title_str = ts_code + ' ' + date_list[0] + '-' + date_list[day_len-1]
        font_title = {'family':'verdana','color':'blue','size':10}
        plt.title(title_str, fontdict = font_title, loc = 'center')

        ax = plt.gca()
        #plt.xticks(color='w') # no label, but ticks
        #ax.axes.xaxis.set_visible(False)
        ax.axes.xaxis.set_ticks([])
        #ax.axes.xaxis.set_ticklabels([]) # no label, but ticks

        #plt.show()
        plt.savefig(title_str + '.png', dpi=150)

        return

    def draw_df(self, ts_code, df_day):
        df = df_day.drop(columns=['open', 'close', 'chg', 'percent', 'turnoverrate', 'volume', 'amount'])
        df = df.sort_values(by='date')
        day_len = len(df.index)

        plt.figure()
        df.plot()

        title_str = ts_code + ' ' + df.index[0] + '-' + df.index[day_len-1]
        font_title = {'family':'verdana','color':'blue','size':10}
        plt.title(title_str, fontdict = font_title, loc = 'center')

        ax = plt.gca()
        ax.axes.xaxis.set_ticks([])

        #plt.show()
        plt.savefig(title_str + '.png', dpi=150)
        return

if __name__ == '__main__':
    s_time = time()
    sq = StockQuery()
    sd = StockDraw()

    ts_code = '002460.SZ'
    df_day = sq.query_day_code_date_df(ts_code, '20220101', '20220908')
    df = df_day.drop(columns=['open', 'close', 'chg', 'percent', 'turnoverrate', 'volume', 'amount'])
    df = df.sort_values(by='date')
    df_ori = df.copy()
    day_len = len(df.index)

    df_bonus = sq.query_bonus_code_df(ts_code)

    first_date = df.index[0]
    for i in range(day_len):
        print(df.index[i], df.low[i], df.high[i], end='')
        ret = df_bonus[df_bonus.index>=first_date]
        ret = ret[ret.index<=df.index[i]]
        if ret.empty == True:
            print()
            continue

        high = df.high[i]
        low = df.low[i]
        bonus_len = len(ret.index)
        for j in range(bonus_len):
            base = float(ret.base)
            free = float(ret.free)
            new = float(ret.new)
            bonus = float(ret.bonus)

            high = (high * (base+free+new) + bonus)/base
            low = (low * (base+free+new) + bonus)/base

        print(' -> ', low, high)

    quit()

    start_date = '20220101'
    end_date = '20220901'
    amount = 2000000000
    ref = sq.stat_day_amount(start_date, end_date, amount)

    for item in ref:
        ts_code = item['_id']['ts_code']
        amount = item['amount']
        num = item['num']
        if num > 100:
            print('%s %3d %.1f' % (ts_code, num, amount))
            #day = sq.query_day_code_date(ts_code, '20220101', '20220908')
            #sd.draw(ts_code, day)


            #sd.draw_df(ts_code, df_day)
            print()
            quit()

    e_time = time()
    print('draw cost %.2f s' % (e_time - s_time))

