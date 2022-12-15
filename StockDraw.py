#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
import matplotlib.pyplot as plt
from time import time
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from Utils import create_buy_table
from Utils import RecTime
import math
import sys

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
        print('draw_df')
        print(df.columns)
        #df = df_day.drop(columns=['open', 'close', 'chg', 'percent', 'turnoverrate', 'volume', 'amount'])
        df = df.sort_values(by='date')

        day_len = len(df.index)

        #plt.figure()
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

def draw_price_amount_withchg(ts_code, df_day, df_chg, chg_perc):
    plt.style.use('seaborn-whitegrid')

    fig = plt.figure(figsize=(12.8,6.4))
    ax1 = fig.add_axes([0.1, 0.3,  0.85, 0.65])
    ax2 = fig.add_axes([0.1, 0.05, 0.85, 0.2])

    # https://www.w3schools.com/colors/colors_names.asp
    ax1.plot(df_day.index, df_day.high, linewidth=1, alpha=0.5, color='orangered', label='high')
    ax1.plot(df_day.index, df_day.low,  linewidth=1, color='lightgreen',  label='low')

    first_x = datetime.strptime(df_chg.index[0], '%Y%m%d')
    for i in range(len(df_chg.index)):
        arr_x, arr_y = [], []
        arr_incx, arr_incy = [], []

        arr_x.append(df_chg.index[i])
        arr_x.append(df_chg.min_date[i])
        arr_y.append(df_chg.firstmin[i])
        arr_y.append(df_chg['min'][i])
        ax1.plot(arr_x, arr_y, linestyle='dotted', linewidth=1, color='royalblue')

        cur_x = datetime.strptime(df_chg.index[i], '%Y%m%d')
        ax1.text((cur_x-first_x).days*0.65, arr_y[0]*1+0.5, arr_x[0], ha='left', rotation=20, fontsize=7, color='gray')

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

    for i in range(day_len):
        cur_date = datetime.strptime(df_day.index[i], '%Y%m%d')
        if (cur_date-index_date).days > 87 and cur_date.day<=3:
            arr_ticks.append(df_day.index[i])
            index_date = cur_date

    ax1.axes.xaxis.set_ticks(arr_ticks)
    ax2.axes.xaxis.set_ticks(arr_ticks)

    title_str = ts_code + '_' + df_day.index[0] + '_' + df_day.index[day_len-1] + '_' + str(chg_perc)
    #plt.savefig(title_str + '.png', dpi=150)
    plt.show()
    plt.close()
    return

# Recover Price Backward, first date price is baseline
# input: df, df_bonus
# return: df_back
def recover_price_backward(df_in, df_bonus):
    rt = RecTime()
    df = df_in.copy()
    day_len = len(df.index)
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
    rt.show_ms()
    return df

# forward recover ex-dividend, baseline is last date price
# input: df, df_bonus
# return: df_back
def recover_price_forward(df_in, df_bonus):
    rt = RecTime()

    df = df_in.copy()
    day_len = len(df.index)
    if day_len == 0:
        return df
    if df_bonus.empty == True:
        return df

    last_date = df.index[day_len-1]
    #print('recover_price_forward {} - {}'.format(df.index[0], last_date))
    for i in range(day_len):
        #print('{} {:9.2f} {:9.2f}'.format(df.index[i], df.low[i], df.high[i]), end='')
        ret = df_bonus[df_bonus.index<=last_date]
        ret = ret[ret.index>df.index[i]]
        if ret.empty == True:
            #print()
            continue

        high = df.high[i]
        low = df.low[i]
        bonus_len = len(ret.index)
        #print(' {:2d} ex-d'.format(bonus_len), end='')
        for j in range(bonus_len):
            base = float(ret.base[j])
            free = float(ret.free[j])
            new = float(ret.new[j])
            bonus = float(ret.bonus[j])

            high = (high * base - bonus)/(base + free + new)
            low = (low * base - bonus)/(base + free + new)

        df.high[i] = math.floor(high*100)/100
        df.low[i] = math.ceil(low*100)/100
        #print(' -> {:9.3f} {:9.3f}'.format(df.low[i], df.high[i]))

    rt.show_ms()
    return df

# 统计上涨 chg_perc 幅度下，次数、最大下跌幅度、最大下跌天数
# stat change percentage
# input: df(forward recover ex-dividend), start_date, chage percentage
# output: 
#   array: first_min,first_min_date, min,max,min_date,max_date
def stat_chg(df, start_date, chg_perc):
    rt = RecTime()

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

    rt.show_ms()
    return df, total_num, max_dec_perc, max_dec_days

def draw_stat_chg(df_stat, title_str):
    len_df_stat = len(df_stat.index)
    bins_num = 100
    print(df_stat)

    fig = plt.figure()
    ax1 = fig.add_axes([0.05, 0.05,  0.4, 0.4]) # left-bottom
    ax2 = fig.add_axes([0.05, 0.55,  0.4, 0.4]) # left-top
    ax3 = fig.add_axes([0.55, 0.55,  0.4, 0.4]) # right-top
    ax4 = fig.add_axes([0.55, 0.05,  0.4, 0.4]) # right-bottom

    ax1.hist(df_stat.max_dec_perc, bins=bins_num)
    #ax1.hist(df_stat.max_dec_perc, bins=80, histtype='stepfilled', alpha=0.3, density=True, edgecolor='black')
    ax1.set_title('max_dec_perc')

    ax2.hist(df_stat.profit, bins=bins_num)
    ax2.set_title('profit')

    ax3.hist(df_stat.inc_num, bins=bins_num)
    ax3.set_title('inc_num')

    ax4.hist(df_stat.max_cost, bins=bins_num)
    ax4.set_title('max_cost')

    plt.savefig(title_str + '.png', dpi=150)
    plt.show()

def sim_chg_monthly_single(sq, ts_code, start_date, end_date, chg_perc, interval):
    rt = RecTime()
    df_stat    = pd.DataFrame()

    df_day   = sq.query_day_code_date_df(ts_code, start_date, end_date)
    start_date = df_day.index[0]
    end_date = df_day.index[len(df_day)-1]
    df_bonus = sq.query_bonus_code_df(ts_code)
    df_forw  = recover_price_forward(df_day, df_bonus)

    # 针对每一个股票，开始时间不同，再计算 chg
    start_d = datetime.strptime(start_date, '%Y%m%d')
    end_d = datetime.strptime(end_date, '%Y%m%d')
    for i in range(end_d.month - start_d.month + (end_d.year - start_d.year) * 12):
        new_d = start_d + relativedelta(months=i)
        new_date = datetime.strftime(new_d, '%Y%m%d')

        print('{} - {}'.format(new_date, end_date))

        df_amount = sq.stat_amount(ts_code, new_date, end_date, 0)
        num = int(df_amount[0]['num'])
        avg_amount = float(df_amount[0]['avg_amount'])

        ret = sim_single_chg_forw(df_forw, new_date, end_date, chg_perc, interval)
        if ret['max_cost'] == 0:
            ret['max_cost'] = 1

        win_or_loss = 'draw'
        if ret['profit'] > 0.0:
            win_or_loss = 'win'
        elif ret['profit'] < 0.0:
            win_or_loss = 'lost'

        df_item = pd.DataFrame([{
                'ts_code':     ts_code,
                's_date':      new_date,
                'e_date':      end_date,
                'status':      win_or_loss,
                'days':        num,
                'amt':         round(avg_amount/100000000,3),
                'num':         ret['inc_num'],
                'max_dec':     round(ret['max_dec_perc'],1),
                'dec_days':    ret['max_dec_days'],
                'profit':      round(ret['profit'],1),
                'max_cost':    round(ret['max_cost'],1),
                'cur_hold':    round(ret['cur_hold'],1),
                'cur_qty':     ret['cur_qty'],
                'profit_ratio':round(ret['profit']/ret['max_cost'],2)
            }])
        df_stat = pd.concat([df_stat, df_item]).reset_index(drop=True)

        print('                            win  ts_code   days  amt num max_dec% dec_days profit  maxcost  curhold  curqty')
        print('{} {} m-summary {} {} {:4d} {:4.1f} {:3d} {:7.1f}% {:8d} {:8.1f} {:8.1f} {:8.1f} {:8.1f}'.format(
            new_date, end_date,
            win_or_loss,
            ts_code, num, avg_amount/100000000, ret['inc_num'], ret['max_dec_perc'], ret['max_dec_days'],
            ret['profit'], ret['max_cost'], ret['cur_hold'], ret['cur_qty']))
        print()

    print('summary report')
    print('{} - {} inc_exp_perc {:.1f}% interval {:.1f}%'.format(
        start_date, end_date,
        chg_perc*100, interval*100
        ))
    print_stat(ts_code, df_stat)
    print()

    print('min_profit_ratio {:.1f}%'.format(round((df_stat[df_stat.status=='lost'].profit / df_stat[df_stat.status=='lost'].max_cost).min()*100, 2)))
    print('max_hold_price   {:.2f} x {:.1f} cur_price {:.2f} - {:.2f}'.format(
        round(df_stat[df_stat.cur_qty==df_stat.cur_qty.max()].cur_hold.max()/df_stat.cur_qty.max(),2),
        df_stat.cur_qty.max(),
        df_forw.iloc[len(df_forw.index)-1].low, df_forw.iloc[len(df_forw.index)-1].high
        ))
    df_tmp = df_stat[(df_stat.status=='win') | (df_stat.status=='loss')]
    df_tmp = 300000/df_tmp.max_cost*df_tmp.profit
    avg_profit = df_tmp.sum()/df_tmp.count()
    print('average_profit   {:.1f} {:.2f}%'.format(avg_profit, round(avg_profit/300000*100,2) ))
    print()

    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None, 'display.max_colwidth', -1):  # more options can be specified also
        print(df_stat)

    rt.show_ms()
    return df_stat

def print_stat(ts_code, df_stat):
    stat_agg = df_stat.agg({
        'max_cost':    ['sum','min','max','average'], # 最大投入的成本
        'profit':      ['sum','min','max','average'], # 获利
        'profit_ratio':['sum','min','max','average'], 
        'cur_hold':    ['sum','min','max','average'], # 当前持有成本
        'cur_qty':     ['sum','min','max','average']  # 当前持有数量
        })

    df_p = df_stat['profit']
    print('range-summary', ts_code, 
        'win', df_p[df_p>0].count(), 'loss', df_p[df_p<0].count(), 'draw', df_p[df_p==0].count(),
        end=' ')

    print('avg_cost {:,.0f} avg_profit {:,.0f} {:.1f}% avg_hold {:,.0f} avg_qty {:,.0f}'.format(
        stat_agg.max_cost['average'], stat_agg.profit['average'],
        stat_agg.profit_ratio['average'],
        stat_agg.cur_hold['average'],
        stat_agg.cur_qty['average'],
        ), end=' ')
    print('max_max_cost {:,.0f} min_profit {:,.0f}'.format(
        stat_agg.max_cost['max'], stat_agg.profit['min']
        ))
    return

def f2exp10(f_num):
    # f_num 是浮点数，返回：小数点后有效数字个数，转成10的次方
    str_ivl = str(f_num)
    len_after_dot = len(str_ivl) - str_ivl.find('.') -1
    m_10 = 10 ** len_after_dot
    return len_after_dot,m_10

def step_num(dec_input, interval, m_10):
    # 求整除 interval，最接近dec_input 的数
    mid_ret = math.floor(dec_input/100/interval)
    dec_output = math.floor((mid_ret*interval+0.000001)*m_10)/m_10
    return dec_output, mid_ret

def sim_chg_single(sq, ts_code, start_date, end_date, chg_perc, interval):
    rt = RecTime()

    df_day   = sq.query_day_code_date_df(ts_code, start_date, end_date)
    df_bonus = sq.query_bonus_code_df(ts_code)
    df_forw  = recover_price_forward(df_day, df_bonus)
    ret = sim_single_chg_forw(df_forw, start_date, end_date, chg_perc, interval)

    rt.show_ms()
    return ret

def sim_single_chg_forw(df_forw, start_date, end_date, chg_perc, interval):
    rt = RecTime()

    len_after_dot, m_10 = f2exp10(interval)
    df_chg, inc_num, max_dec_perc, max_dec_days = stat_chg(df_forw, start_date, chg_perc)
    print('{} - {}'.format(start_date, end_date))
    print(df_chg)

    profit = 0
    max_cost = 0.0
    cur_hold = 0.0
    cur_qty  = 0.0
    for i in range(len(df_chg.index)):
        item_chg = df_chg.loc[df_chg.index[i]]

        df_buy_table = create_buy_table(base_price=item_chg.firstmin, interval=interval, inc_perc=1+chg_perc)

        dec_perc, mid_ret = step_num(item_chg.dec_perc, interval, m_10)
        df_buy_item = df_buy_table[round(df_buy_table['dec_perc'], len_after_dot)==dec_perc]
        print('item_chg.dec_perc {} mid_ret {} dec_perc {}'.format(item_chg.dec_perc, mid_ret, dec_perc))
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None, 'display.max_colwidth', -1):  # more options can be specified also
            print(df_buy_table[round(df_buy_table['dec_perc'], len_after_dot)<=(dec_perc+interval)])
        try:
            hold_qty  = float(df_buy_item.acum_qty)
        except:
            print(df_buy_item.acum_qty)
            print('Error', chg_perc, interval, m_10, len_after_dot, mid_ret, round(mid_ret,6), dec_perc)
            print(item_chg)
            print()
            print(df_buy_table)
            hold_qty = 0
            quit()

        hold_cost = float(df_buy_item.acum_cost)
        d = item_chg.inc_perc
        if not (d == d and d != None): # nan
            if hold_cost > max_cost: max_cost = hold_cost
            cur_hold = hold_cost
            cur_qty  = hold_qty
            continue

        sell_exp_price = item_chg['min'] * (1+chg_perc)
        cur_profit = hold_qty * sell_exp_price - hold_cost
        print('{:6.0f} x {:7.2f} - {:9.1f} = {:9.1f}'.format(hold_qty, sell_exp_price, hold_cost, cur_profit))

        if hold_cost > max_cost: max_cost = hold_cost
        profit += cur_profit
        cur_hold = 0.0
        cur_qty  = 0.0

    ret = {
        'profit':      profit,
        'inc_num':     inc_num, 
        'max_dec_perc':max_dec_perc, 
        'max_dec_days':max_dec_days, 
        'max_cost':    max_cost, 
        'cur_hold':    cur_hold,
        'cur_qty':    cur_qty
    }
    
    rt.show_ms()
    return ret

def sim_chg(ts_code, start_date, end_date, chg_perc, interval):
    rt = RecTime()
    df_stat    = pd.DataFrame()
    sq = StockQuery()

    if ts_code == None:
        ref = sq.query_basic(None)
    else:
        ref = [{'ts_code':ts_code}]
    print('Found {:4d}'.format(len(ref)))

    for item in ref:
        ts_code = item['ts_code']
        ret = sq.check_bad_bonus(ts_code)
        if ret != 0:
            continue

        num = 0
        avg_amount = 0
        print('{} {:3d} {:,.1f}'.format(ts_code, num, avg_amount))

        ret = sim_chg_single(sq, ts_code, start_date, end_date, chg_perc, interval)

        df_item = pd.DataFrame([{
                'ts_code':     ts_code,
                'inc_num':     ret['inc_num'],
                'max_dec_perc':round(ret['max_dec_perc'],2),
                'max_dec_days':ret['max_dec_days'],
                'max_cost':    ret['max_cost'],
                'profit':      ret['profit'],
                'profit_ratio':ret['profit']/ret['max_cost'],
                'cur_hold':    ret['cur_hold'],
                'cur_qty':    ret['cur_qty']
            }])
        df_stat = pd.concat([df_stat, df_item]).reset_index(drop=True)

        win_or_loss = 'draw'
        if ret['profit'] > 0.0:
            win_or_loss = 'win '
        elif ret['profit'] < 0.0:
            win_or_loss = 'lost'
        print('          win  ts_code   days  amt num max_dec% dec_days profit   maxcost  curhold   curqty')
        print('summary   {} {} {:4d} {:4.1f} {:3d} {:7.1f}% {:8d} {:6.1f} {:8.1f} {:8.1f} {:8.1f}'.format(
            win_or_loss,
            ts_code, num, avg_amount/100000000, ret['inc_num'], ret['max_dec_perc'], ret['max_dec_days'],
            ret['profit'], ret['max_cost'], ret['cur_hold'], ret['cur_qty']))
        print()
        #if len(df_stat.index)>=10: break

    print('summary report')
    print('{} - {} inc_exp_perc {:.1f}% interval {:.1f}%'.format(
        start_date, end_date,
        chg_perc*100, interval*100
        ))

    print_stat(None, df_stat)
    rt.show_ms()
    return df_stat

def sim_chg_monthly(ts_code, start_date, end_date, chg_perc, interval):
    rt = RecTime()
    df_stat    = pd.DataFrame()
    sq = StockQuery()

    if ts_code == None:
        ref = sq.query_basic(None)
    else:
        ref = [{'ts_code':ts_code}]
    print('Found {:4d}'.format(len(ref)))

    for item in ref:
        ts_code = item['ts_code']
        ret = sq.check_bad_bonus(ts_code)
        if ret != 0:
            continue

        print('{}'.format(ts_code))

        df_stat = sim_chg_monthly_single(sq, ts_code, start_date, end_date, chg_perc, interval)
        print()

    print('summary report')
    print('{} - {} inc_exp_perc {:.1f}% interval {:.1f}%'.format(
        start_date, end_date,
        chg_perc*100, interval*100
        ))

    rt.show_s()
    return

def draw_example(ts_code, start_date, end_date, chg_perc):
    rt = RecTime()
    sq = StockQuery()
    sd = StockDraw()

    df_day   = sq.query_day_code_date_df(ts_code, start_date, end_date)
    df_bonus = sq.query_bonus_code_df(ts_code)
    df = df_day.drop(columns=['open', 'close'])

    # 前复权
    df_forw = recover_price_forward(df, df_bonus)

    # 统计上涨 0.1 幅度下，次数、最大下跌幅度、最大下跌天数
    #chg_perc = 0.35
    df_chg, total_num, max_dec_perc, max_dec_days = stat_chg(df_forw, start_date, chg_perc)
    print('{} {} -{:.1f}% {:3d}'.format(ts_code, total_num, max_dec_perc, max_dec_days))
    print(df_chg)
    draw_price_amount_withchg(ts_code, df_forw, df_chg, chg_perc)

    # 后复权
    df_back = recover_price_backward(df, df_bonus) # example, normally will not use backward

    # 不复权、前复权、后复权合并到一张图上
    df_back = df_back.rename(columns={'high': 'high_back', 'low': 'low_back'})
    df_forw = df_forw.rename(columns={'high': 'high_forw', 'low': 'low_forw'})
    df_tmp = df.merge(    df_back, left_on='date', right_on='date')
    df_tmp = df_tmp.merge(df_forw, left_on='date', right_on='date')
    df_tmp = df_tmp.drop(columns=['amount', 'amount_x', 'amount_y'])
    #sd.draw_df(ts_code+'-merge', df_tmp)

    rt.show_s()

if __name__ == '__main__':
    if len(sys.argv) == 4:
        start_date = '20190902'
        end_date   = '20221125'
        ts_code  = sys.argv[1]
        chg_perc = float(sys.argv[2])
        interval = float(sys.argv[3])
        #draw_example(ts_code, start_date, end_date, chg_perc)
        sim_chg_monthly(ts_code, start_date, end_date, chg_perc, interval)
        quit()

    #ts_code    = '688223.SH' # 晶科能源
    #ts_code    = '000590.SZ' #
    #ts_code    = '000610.SZ' #
    ts_code    = '002475.SZ' # 立讯
    start_date = '20190902'
    end_date   = '20221231'
    draw_example(ts_code, start_date, end_date, 0.35)
    quit()

    ts_code    = '002475.SZ' # 立讯
    #ts_code    = '600519.SH' # 茅台
    #ts_code    = '002241.SZ' # 歌尔
    #ts_code    = '002273.SZ' # 水晶
    #ts_code    = '000425.SZ' # 徐工

    #ts_code    = '838030.BJ' # 德众汽车
    #ts_code    = '000001.SZ' # 平安
    #ts_code    = '000055.SZ' # 方大集团
    #ts_code    = '001218.SZ' # 丽臣实业

    #ts_code    = '000501.SZ' #
    #ts_code    = '601186.SH' #

    #ts_code    = '000610.SZ' #
    #ts_code    = '002317.SZ' #
    #ts_code    = '002528.SZ' #

    #ts_code    = None
    start_date = '20190901'
    end_date   = '20221231'
    chg_perc   = 0.35
    interval   = 0.05

    '''
    if ts_code == None:
        title_str = 'stat-{:.1f}%-{}'.format(chg_perc*100, interval)
    else:
        title_str = 'stat-{}-{:.1f}%-{}'.format(ts_code, chg_perc*100, interval)
    df_stat = sim_chg(ts_code, start_date, end_date, chg_perc, interval)
    draw_stat_chg(df_stat, title_str)
    df_stat.to_csv(title_str + '.csv', index=False)
    '''
    sim_chg_monthly(ts_code, start_date, end_date, chg_perc, interval)
