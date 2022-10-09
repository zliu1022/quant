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

        plt.show()
        #plt.savefig(title_str + '.png', dpi=150)
        return

# obsolete
# use GridSpec to draw subplot
def draw_price_amount(df_day):
    from matplotlib.gridspec import GridSpec

    fig = plt.figure(constrained_layout=True)
    gs = GridSpec(3, 1, figure=fig)
    ax1 = fig.add_subplot(gs[0:2, 0])
    ax2 = fig.add_subplot(gs[2, 0])

    ax1.plot(df_day.high)
    ax1.plot(df_day.low)
    ax2.plot(df_day.amount, color = 'blue')

    ax1.axes.xaxis.set_ticks([])
    ax2.axes.xaxis.set_ticks([])
    plt.show()

def draw_price_amount_withchg(ts_code, df_day, df_chg):
    plt.style.use('seaborn-whitegrid')

    fig = plt.figure(figsize=(12.8,6.4))
    ax1 = fig.add_axes([0.1, 0.3,  0.85, 0.65])
    ax2 = fig.add_axes([0.1, 0.05, 0.85, 0.2])

    # https://www.w3schools.com/colors/colors_names.asp
    ax1.plot(df_day.index, df_day.high, linewidth=1, alpha=0.5, color='orangered', label='high')
    ax1.plot(df_day.index, df_day.low,  linewidth=1, color='lightgreen',  label='low')

    for i in range(len(df_chg.index)):
        arr_x, arr_y = [], []
        arr_incx, arr_incy = [], []

        arr_x.append(df_chg.index[i])
        arr_x.append(df_chg.min_date[i])
        arr_y.append(df_chg.firstmin[i])
        arr_y.append(df_chg['min'][i])
        ax1.plot(arr_x, arr_y, linestyle='dotted', linewidth=1, color='royalblue')

        arr_incx.append(df_chg.min_date[i])
        arr_incy.append(df_chg['min'][i])
        arr_incx.append(df_chg.max_date[i])
        arr_incy.append(df_chg['max'][i])
        ax1.plot(arr_incx, arr_incy, linestyle='dotted', linewidth=1.5, color='red')

        ax1.plot(df_chg.min_date[i], df_chg['min'][i], 'o', c='r', markersize=1.1)

    ax1.set(xlabel='', ylabel='price',
        title=ts_code)
    leg = ax1.legend(loc='upper right', frameon=False)

    ax2.bar(df_day.index, df_day.amount, alpha=0.5, width=0.6, label='amount')
    ax2.set(xlabel='date', ylabel='amount')
    leg2 = ax2.legend(loc='upper right', frameon=False)

    arr_ticks = []
    day_len = len(df_day.index)

    index_date = datetime.strptime(df_day.index[0], '%Y%m%d')
    arr_ticks.append(df_day.index[0])
    first_month = index_date.month + 1

    for i in range(day_len):
        cur_date = datetime.strptime(df_day.index[i], '%Y%m%d')
        if cur_date.month > first_month:
            arr_ticks.append(df_day.index[i])
            first_month = cur_date.month

    ax1.axes.xaxis.set_ticks(arr_ticks)
    ax2.axes.xaxis.set_ticks(arr_ticks)
    #ax2.axes.xaxis.set_ticks([df_day.index[0], df_day.index[round(day_len/2)], df_day.index[day_len-1]])

    title_str = ts_code + ' ' + df_day.index[0] + '-' + df_day.index[day_len-1]
    #plt.savefig(title_str + '.png', dpi=150)
    plt.show()
    return

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
    day_len = len(df.index)
    if day_len == 0:
        return df
    if df_bonus.empty == True:
        return df
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

    total_num = len(arr_min)
    if len(arr_firstmin) != len(arr_min):
        arr_min.append(cur_min)
        arr_sdate.append(s_date)
        arr_max.append(np.nan)
        arr_edate.append('20500101')

    arr_len = len(arr_min)
    max_dec_perc = 0.0
    max_dec_days = 0

    dec_perc, inc_perc = 0.0, 0.0
    arr_dec, arr_inc = [], []
    for i in range(arr_len):
        minfirst_date = datetime.strptime(arr_sfirst_date[i], '%Y%m%d')
        min_date = datetime.strptime(arr_sdate[i], '%Y%m%d')
        max_date = datetime.strptime(arr_edate[i], '%Y%m%d')

        dec_perc = (arr_firstmin[i]-arr_min[i])/arr_firstmin[i]*100
        inc_perc = (arr_max[i]-arr_min[i])/arr_min[i]*100
        arr_dec.append(dec_perc)
        arr_inc.append(inc_perc)

        if dec_perc >= max_dec_perc:
            max_dec_perc = dec_perc
            max_dec_days = (min_date-minfirst_date).days

        '''
        print('{} {} {} {:2d} {:2d} {:7.2f} {:7.2f} {:7.2f}  {:7.2f}% {:7.2f}%'.format(
            arr_sfirst_date[i], arr_sdate[i], arr_edate[i], 
            (min_date-minfirst_date).days, (max_date-min_date).days,
            arr_firstmin[i], arr_min[i], arr_max[i], 
            dec_perc*100,
            inc_perc*100
        ))
        '''
    #print('Total {:3d} Max dec_perc {:7.2f}% {:3d}'.format(total_num ,max_dec_perc*100, max_dec_days))

    df = pd.DataFrame(index=arr_sfirst_date)

    df.insert(0, 'min_date', arr_sdate)
    df.insert(1, 'max_date', arr_edate)

    df.insert(2, 'firstmin', arr_firstmin)
    df.insert(3, 'min', arr_min)
    df.insert(4, 'max', arr_max)

    df.insert(5, 'dec_perc', arr_dec)
    df.insert(5, 'inc_perc', arr_inc)

    '''
    df['firstmin'] = df['firstmin'].map('{:.2f}'.format)
    df['min'] = df['min'].map('{:.2f}'.format)
    df['max'] = df['max'].map('{:.2f}'.format)

    df['dec_perc'] = df['dec_perc'].map('{:.1f}%'.format)
    df['inc_perc'] = df['inc_perc'].map('{:.1f}%'.format)
    '''
    return df, total_num, max_dec_perc, max_dec_days

if __name__ == '__main__':
    s_time = time()

    sq = StockQuery()
    sd = StockDraw()

    #ts_code = '002460.SZ'
    #ts_code = '601012.SH'
    #ts_code = '600153.SH'
    #ts_code = '002475.SZ'
    ts_code = '688223.SH'

    #start_date = '20220101'
    #end_date   = '20220922'
    start_date = '20220101'
    end_date   = '20221231'

    df_day = sq.query_day_code_date_df(ts_code, start_date, end_date)
    df_bonus = sq.query_bonus_code_df(ts_code)
    df = df_day.drop(columns=['open', 'close'])

    df_forw = recover_price_forward(df, df_bonus)
    #df_back = recover_price_backward(df, df_bonus) # example, normally will not use backward
    #draw_price_amount(df_forw) # obselete

    chg_perc = 0.1
    df_chg, total_num, max_dec_perc, max_dec_days = stat_chg(df_forw, start_date, chg_perc)
    draw_price_amount_withchg(ts_code, df_forw, df_chg)
    quit()

    '''
    df_back = df_back.rename(columns={'high': 'high_back', 'low': 'low_back'})
    df_forw = df_forw.rename(columns={'high': 'high_forw', 'low': 'low_forw'})
    df_tmp = df.merge(df_back, left_on='date', right_on='date')
    df_tmp = df_tmp.merge(df_forw, left_on='date', right_on='date')
    sd.draw_df(ts_code+'-merge', df_tmp)
    '''

    amount     = 1 * 10000 * 10000
    ref = sq.stat_day_amount(start_date, end_date, amount)
    print('Found {:4d} >= {}'.format(len(ref), amount))

    for item in ref:
        ts_code = item['_id']['ts_code']
        avg_amount = item['avg_amount']
        num = item['num']
        if num > 30:
            print('%s %3d %.1f' % (ts_code, num, avg_amount))

            df_day = sq.query_day_code_date_df(ts_code, start_date, end_date)
            df_bonus = sq.query_bonus_code_df(ts_code)
            df_forw = recover_price_forward(df_day, df_bonus)

            chg_perc = 0.05
            df_chg, total_num, max_dec_perc, max_dec_days = stat_chg(df_forw, start_date, chg_perc)

            print('{} - {}'.format(start_date, end_date))
            print(df_chg)
            
            if max_dec_perc<=16 and total_num>=10:
                print('summary-good {}({:3d} {:4.1f}) {:3d} {:.1f} {:3d}'.format(ts_code, num, avg_amount/100000000, total_num, max_dec_perc, max_dec_days))
                #draw_price_amount(df_day)
                #sd.draw_df(ts_code+'-forw', df_forw)
                draw_price_amount_withchg(ts_code, df_forw, df_chg)
            else:
                print('summary-bad  {}({:3d} {:4.1f}) {:3d} {:.1f} {:3d}'.format(ts_code, num, avg_amount/100000000, total_num, max_dec_perc, max_dec_days))
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

