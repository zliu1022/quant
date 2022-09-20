#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
import matplotlib.pyplot as plt
from time import time
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

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

def draw_price_amount(df_day):
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
    ax2.plot(df_day.amount, color = 'blue')
    #ax2.hist(df_day.amount, facecolor = 'blue', edgecolor = 'orange') # 100,000,000
    #ax = plt.gca()
    ax1.axes.xaxis.set_ticks([])
    ax2.axes.xaxis.set_ticks([])
    plt.show()

# Recover Price Backward, first date price is baseline
# input: df, df_bonus
# return: df_back
def recover_price_backward(df_in, df_bonus):
    df = df_in.copy()
    first_date = df.index[0]
    for i in range(day_len):
        #print('{} {:7.2f} {:7.2f}'.format(df.index[i], df.low[i], df.high[i]), end='')

        # 后复权，则以开始日价格为基准，除权日晚于开始日, 早于当前日，当日价格需要复权
        # 开始日 <= 除权日 <= 当前日，除权日当日也需要复权
        ret = df_bonus[df_bonus.index>=first_date]
        ret = ret[ret.index<=df.index[i]]
        if ret.empty == True:
            #print()
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
        #print(' -> {:7.2f} {:7.2f}'.format(low, high))

    #df_back = df.copy()
    #sd.draw_df(ts_code+'-back', df_back)
    return df

# forward recover ex-dividend, baseline is last date price
# input: df, df_bonus
# return: df_back
def recover_price_forward(df_in, df_bonus):
    df = df_in.copy()
    last_date = df.index[day_len-1]
    for i in range(day_len):
        #print('{} {:7.2f} {:7.2f}'.format(df.index[i], df.low[i], df.high[i]), end='')
        ret = df_bonus[df_bonus.index<=last_date]
        ret = ret[ret.index>df.index[i]]
        if ret.empty == True:
            #print()
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
        #print(' -> {:7.2f} {:7.2f}'.format(low, high))

    #df_forw = df.copy()
    #sd.draw_df(ts_code+'-forw', df_forw)
    return df

# stat change percentage
# input: df(forward recover ex-dividend), start_date, chage percentage
# output: 
#   array: first_min,first_min_date, min,max,min_date,max_date
def stat_chg(df, start_date, chg_perc):
    arr_min,arr_max,arr_sdate,arr_edate = [],[],[],[]
    cur_min,cur_max = 99999.0, 0.0
    s_date,e_date = 'yyyymmdd', 'yyyymmdd'

    arr_firstmin = []
    arr_sfirst_date = []

    day_len = len(df.index)
    for i in range(day_len):
        #print('{} {:7.2f} {:7.2f}'.format(df.index[i], df.low[i], df.high[i]), end=' ')
        if df.index[i] < start_date:
            continue
        if df.index[i] >= start_date and len(arr_firstmin) == 0:
            #print('df.index[i] == start_date')
            cur_min = (df.low[i] + df.high[i])/2.0
            s_date = df.index[i]

            arr_firstmin.append(cur_min)
            arr_sfirst_date.append(df.index[i])
            #print('first', df.low[i], ' -> cur_firstmin', df.index[i])
            continue

        # update min
        if df.low[i] < cur_min:
            if cur_min == 99999.0:
                cur_min = (df.low[i] + df.high[i])/2.0
                arr_firstmin.append(cur_min)

                arr_sfirst_date.append(df.index[i])
                s_date = df.index[i]
                #print('first', df.low[i], ' -> cur_firstmin', df.index[i])
            else:
                cur_min = df.low[i]
                s_date = df.index[i]
                #print('df.low[i] ', df.low[i], ' -> cur_min', s_date)
            continue

        if (df.high[i]-cur_min)/cur_min >= chg_perc:
            cur_max = df.high[i]
            e_date = df.index[i]
            #print('df.high[i] ', df.high[i], ' -> cur_max', e_date)
            #print()

            arr_min.append(cur_min)
            arr_max.append(cur_max)
            arr_sdate.append(s_date)
            arr_edate.append(e_date)

            cur_min,cur_max = 99999.0, 0.0
            s_date,e_date = 'yyyymmdd', 'yyyymmdd'
            continue
        #print()

    if len(arr_firstmin) != len(arr_min):
        arr_min.append(cur_min)
        arr_sdate.append(s_date)
        arr_max.append(np.nan)
        arr_edate.append('20500101')

    arr_len = len(arr_min)
    for i in range(arr_len):
        minfirst_date = datetime.strptime(arr_sfirst_date[i], '%Y%m%d')
        min_date = datetime.strptime(arr_sdate[i], '%Y%m%d')
        max_date = datetime.strptime(arr_edate[i], '%Y%m%d')
        print('{} {} {} {:2d} {:2d} {:7.2f} {:7.2f} {:7.2f}  {:7.2f}% {:7.2f}%'.format(
            arr_sfirst_date[i], arr_sdate[i], arr_edate[i], 
            (min_date-minfirst_date).days, (max_date-min_date).days,
            arr_firstmin[i], arr_min[i], arr_max[i], 
            (arr_firstmin[i]-arr_min[i])/arr_firstmin[i]*100,
            (arr_max[i]-arr_min[i])/arr_min[i]*100
        ))

    df = pd.DataFrame(index=arr_sfirst_date)
    df.insert(0, 'firstmin', arr_firstmin)
    df.insert(1, 'min', arr_min)
    df.insert(2, 'max', arr_max)
    df.insert(3, 'min_date', arr_sdate)
    df.insert(4, 'max_date', arr_edate)
    return df

if __name__ == '__main__':
    s_time = time()

    sq = StockQuery()
    sd = StockDraw()

    ts_code = '002460.SZ'
    ts_code = '601012.SH'

    df_day = sq.query_day_code_date_df(ts_code, '20220701', '20220917')
    #draw_price_amount(df_day)
    df_bonus = sq.query_bonus_code_df(ts_code)

    df = df_day.drop(columns=['open', 'close', 'amount'])
    day_len = len(df.index)

    df_forw = recover_price_forward(df, df_bonus)
    df_back = recover_price_backward(df, df_bonus)

    '''
    df_back = df_back.rename(columns={'high': 'high_back', 'low': 'low_back'})
    df_forw = df_forw.rename(columns={'high': 'high_forw', 'low': 'low_forw'})
    df_tmp = df.merge(df_back, left_on='date', right_on='date')
    df_tmp = df_tmp.merge(df_forw, left_on='date', right_on='date')
    sd.draw_df(ts_code+'-merge', df_tmp)
    '''

    start_date = '20220101'
    end_date   = '20220920'
    amount     = 1000000000
    ref = sq.stat_day_amount(start_date, end_date, amount)

    for item in ref:
        ts_code = item['_id']['ts_code']
        avg_amount = item['avg_amount']
        num = item['num']
        if num > 85:
            print('%s %3d %.1f' % (ts_code, num, avg_amount))

            df_day = sq.query_day_code_date_df(ts_code, start_date, end_date)
            df_bonus = sq.query_bonus_code_df(ts_code)
            df_forw = recover_price_forward(df_day, df_bonus)

            chg_perc = 0.1
            start_date = '20220101'
            end_date   = '20220918'

            start_d = datetime.strptime(start_date, '%Y%m%d')
            end_d = datetime.strptime(end_date, '%Y%m%d')
            print('{} - {}'.format(start_date, end_date))
            df_chg = stat_chg(df_forw, start_date, chg_perc)
            print()
            '''
            start_d = datetime.strptime(start_date, '%Y%m%d')
            end_d = datetime.strptime(end_date, '%Y%m%d')
            for i in range(end_d.month - start_d.month):
                new_d = start_d + relativedelta(months=i)
                new_date = datetime.strftime(new_d, '%Y%m%d')
                print('{} - {}'.format(new_date, end_date))
                df_chg = stat_chg(df_forw, new_date, chg_perc)
                print()
            '''

    e_time = time()
    print('StockDraw cost %.2f s' % (e_time - s_time))

