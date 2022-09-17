#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
        df = df_day
        #df = df_day.drop(columns=['open', 'close', 'chg', 'percent', 'turnoverrate', 'volume', 'amount'])
        #df = df.sort_values(by='date')
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
    ts_code = '601012.SH'

    df_day = sq.query_day_code_date_df(ts_code, '20220101', '20220908')
    df_day = df_day.sort_values(by='date')

    '''
    fig, axs = plt.subplots(2, 1)
    axs[0].plot(df_day.high)
    axs[0].plot(df_day.low)
    axs[1].plot(df_day.amount, color = 'orange')
    '''

    from matplotlib.gridspec import GridSpec
    fig = plt.figure(constrained_layout=True)
    gs = GridSpec(3, 1, figure=fig)
    ax1 = fig.add_subplot(gs[0:2, 0])
    ax2 = fig.add_subplot(gs[2, 0])
    ax1.plot(df_day.high)
    ax1.plot(df_day.low)
    ax2.plot(df_day.amount, color = 'orange')
    #ax = plt.gca()
    ax1.axes.xaxis.set_ticks([])
    ax2.axes.xaxis.set_ticks([])
    plt.show()
    quit()

    df = df_day.drop(columns=['open', 'close', 'chg', 'percent', 'turnoverrate', 'volume', 'amount'])
    df = df.sort_values(by='date')
    df_ori = df.copy()
    day_len = len(df.index)
    sd.draw_df(ts_code+'-ori', df_ori)

    print(df_ori)
    print()

    df_bonus = sq.query_bonus_code_df(ts_code)
    print(df_bonus)
    print()

    # Recover Price Backward, first date price is baseline
    # input: df, df_bonus
    # return: df_back
    first_date = df.index[0]
    for i in range(day_len):
        print('{} {:7.2f} {:7.2f}'.format(df.index[i], df.low[i], df.high[i]), end='')

        # 后复权，则以开始日价格为基准，除权日晚于开始日, 早于当前日，当日价格需要复权
        # 开始日 <= 除权日 <= 当前日，除权日当日也需要复权
        ret = df_bonus[df_bonus.index>=first_date]
        ret = ret[ret.index<=df.index[i]]
        if ret.empty == True:
            print()
            continue
        bonus_len = len(ret.index)
        #print(' {:2d} ex-d'.format(bonus_len), end='')

        high = df.high[i]
        low = df.low[i]
        for j in range(bonus_len):
            base = float(ret.base[j])
            free = float(ret.free[j])
            new = float(ret.new[j])
            bonus = float(ret.bonus[j])

            high = round((high * (base+free+new) + bonus)/base, 2)
            low = round((low * (base+free+new) + bonus)/base, 2)

        df.high[i] = high
        df.low[i] = low
        print(' -> {:7.2f} {:7.2f}'.format(low, high))

    df_back = df.copy()
    #sd.draw_df(ts_code+'-back', df_back)
    df_back = df_back.rename(columns={'high': 'high_back', 'low': 'low_back'})

    df = df_ori.copy()

    # forward recover ex-dividend, baseline is last date price
    # input: df, df_bonus
    # return: df_back
    last_date = df.index[day_len-1]
    for i in range(day_len):
        print('{} {:7.2f} {:7.2f}'.format(df.index[i], df.low[i], df.high[i]), end='')
        ret = df_bonus[df_bonus.index<=last_date]
        ret = ret[ret.index>df.index[i]]
        if ret.empty == True:
            print()
            continue

        high = df.high[i]
        low = df.low[i]
        bonus_len = len(ret.index)
        for j in range(bonus_len):
            base = float(ret.base[j])
            free = float(ret.free[j])
            new = float(ret.new[j])
            bonus = float(ret.bonus[j])

            high = round((high * base - bonus)/(base + free + new), 2)
            low = round((low * base - bonus)/(base + free + new), 2)

        df.high[i] = high
        df.low[i] = low
        print(' -> {:7.2f} {:7.2f}'.format(low, high))

    df_forw = df.copy()
    sd.draw_df(ts_code+'-forw', df_forw)

    df_forw = df_forw.rename(columns={'high': 'high_forw', 'low': 'low_forw'})

    #df_tmp = df_ori.merge(df_back, left_on='date', right_on='date')
    df_tmp = df_ori.merge(df_forw, left_on='date', right_on='date')
    sd.draw_df(ts_code+'-merge', df_tmp)

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

