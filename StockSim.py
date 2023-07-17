#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Utils import create_buy_table
from Utils import RecTime
import pandas as pd
from StockRecover import recover_price_forward
import numpy as np
from datetime import datetime
import math
from dateutil.relativedelta import relativedelta
from pprint import pprint

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
        #if df.index[i] < start_date:
        #if df.loc[i, 'date'] < start_date:
        if df.iloc[i]['date'] < start_date:
            continue
        #if df.index[i] >= start_date and len(arr_firstmin) == 0:
        #if df.iloc[i]['date'] >= start_date and len(arr_firstmin) == 0:
        if df.date[i] >= start_date and len(arr_firstmin) == 0:
            #print('df.index[i] == start_date')
            #cur_min = (df.low[i] + df.high[i])/2.0
            cur_min = (df['low'].iloc[i] + df['high'].iloc[i])/2.0

            s_date = df.index[i]

            arr_firstmin.append(cur_min)
            arr_sfirst_date.append(df.date[i])
            #print('first', df.low[i], ' -> cur_firstmin', df.index[i])
            continue

        # update min
        if df.low[i] < cur_min:

            if cur_min == 99999.0:
                cur_min = (df.low[i] + df.high[i])/2.0
                arr_firstmin.append(cur_min)

                arr_sfirst_date.append(df.date[i])
                s_date = df.index[i]
                #print('first', df.low[i], ' -> cur_firstmin', df.index[i])
            else:
                cur_min = df.low[i]
                s_date = df.date[i]
                #print('df.low[i] ', df.low[i], ' -> cur_min', s_date)
            continue

        if (df.high[i]-cur_min)/cur_min >= chg_perc:
            cur_max = df.high[i]
            e_date = df.date[i]
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

    #rt.show_ms()
    return df, total_num, max_dec_perc, max_dec_days

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
        print('{} {} month-summary {} {} {:4d} {:4.1f} {:3d} {:7.1f}% {:8d} {:8.1f} {:8.1f} {:8.1f} {:8.1f}'.format(
            new_date, end_date,
            win_or_loss,
            ts_code, num, avg_amount/100000000, ret['inc_num'], ret['max_dec_perc'], ret['max_dec_days'],
            ret['profit'], ret['max_cost'], ret['cur_hold'], ret['cur_qty']))
        print()

    print('all month summary report (single code)')
    print('{} - {} inc_exp_perc {:.1f}% interval {:.1f}%'.format(
        start_date, end_date,
        chg_perc*100, interval*100
        ))

    print_stat_month(ts_code, df_stat, df_forw)

    rt.show_ms()
    return df_stat

def print_stat_month(ts_code, df_stat, df_forw):
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
        ), end=' ')

    print('min_profit_ratio {:.1f}%'.format(round((df_stat[df_stat.status=='lost'].profit / df_stat[df_stat.status=='lost'].max_cost).min()*100, 2)))
    print('max_hold_price   {:.2f} x {:.1f} cur_price {:.2f} - {:.2f}'.format(
        round(df_stat[df_stat.cur_qty==df_stat.cur_qty.max()].cur_hold.max()/df_stat.cur_qty.max(),2),
        df_stat.cur_qty.max(),
        df_forw.iloc[len(df_forw.index)-1].low, df_forw.iloc[len(df_forw.index)-1].high
        ))

    df_tmp = df_stat[(df_stat.status=='win') | (df_stat.status=='loss')]
    df_tmp = 300000/df_tmp.max_cost*df_tmp.profit
    if df_tmp.count() != 0:
        avg_profit = df_tmp.sum()/df_tmp.count()
    else:
        avg_profit = 0.0
    print('average_profit   {:.1f} {:.2f}%'.format(avg_profit, round(avg_profit/300000*100,2) ))
    print()

    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None, 'display.max_colwidth', -1):  # more options can be specified also
        print(df_stat)

    return

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
        print('item_chg.dec_perc {:.3f} mid_ret {} dec_perc {}'.format(item_chg.dec_perc, mid_ret, dec_perc))
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
        if not (d == d and d != None): # nan means still hold, not sold
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

    last_index = df_forw.index[-1]
    if cur_qty==0:
        cur_p = np.inf
    else:
        cur_p = round(cur_hold/cur_qty,2)
    ret = {
        'profit':      round(profit,2),
        'inc_num':     inc_num, 
        'max_dec_perc':round(max_dec_perc,2), 
        'max_dec_days':max_dec_days, 
        'max_cost':    round(max_cost,2), 
        'profit_ratio': round(profit/max_cost, 2),
        'cur_hold':    round(cur_hold,2),
        'cur_qty':     cur_qty,
        'cur_p':       cur_p,
        'cur_lowp':    df_forw.loc[last_index, 'low'],
        'cur_highp':   df_forw.loc[last_index, 'high']
    }
    #rt.show_ms()
    return ret

def sim_chg(sq, code_list, start_date, end_date, chg_perc, interval):
    rt = RecTime()
    df_stat    = pd.DataFrame()

    for item in code_list:
        ts_code = item['ts_code']

        ret = sq.check_bad_bonus(ts_code)
        if ret != 0:
            continue

        df_amount = sq.stat_amount(ts_code, start_date, end_date, 0)
        num = int(df_amount[0]['num'])
        avg_amount = float(df_amount[0]['avg_amount'])/100000000.0
        print('{} {} {:.1f} {} {:3d} {:,.1f}'.format(ts_code, item['name'], item['mktvalue'], item['date'], num, avg_amount))

        ret = sim_chg_single(sq, ts_code, start_date, end_date, chg_perc, interval)

        df_item = pd.DataFrame([ret])
        df_item.insert(loc=0, column='ts_code', value=ts_code)
        df_stat = pd.concat([df_stat, df_item]).reset_index(drop=True)

        win_or_loss = 'draw'
        if ret['profit'] > 0.0:
            win_or_loss = 'win '
        elif ret['profit'] < 0.0:
            win_or_loss = 'lost'
        print('          win  ts_code   days  amt num max_dec% dec_days profit   maxcost  curhold   curqty    cur_p  cur_lowp   cur_highp')
        print('summary   {} {} {:4d} {:4.1f} {:3d} {:7.1f}% {:8d} {:6.1f} {:8.1f} {:8.1f} {:8.1f} {:8.1f} {:8.1f} {:8.1f}'.format(
            win_or_loss,
            ts_code, num, avg_amount/100000000, ret['inc_num'], ret['max_dec_perc'], ret['max_dec_days'],
            ret['profit'], ret['max_cost'], ret['cur_hold'], ret['cur_qty'],
            ret['cur_p'], ret['cur_lowp'], ret['cur_highp']
            ))
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

def sim_chg_monthly(sq, ts_code, start_date, end_date, chg_perc, interval):
    rt = RecTime()
    df_stat    = pd.DataFrame()

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

    print('summary report (all codes)')
    print('all-summary {} - {} inc_exp_perc {:.1f}% interval {:.1f}%'.format(
        start_date, end_date,
        chg_perc*100, interval*100
        ))

    rt.show_s()
    return

if __name__ == '__main__':
    '''
    def sim_chg(ts_code, start_date, end_date, chg_perc, interval):
        def sim_chg_single(sq, ts_code, start_date, end_date, chg_perc, interval):
            def sim_single_chg_forw(df_forw, start_date, end_date, chg_perc, interval):
    def sim_chg_monthly(ts_code, start_date, end_date, chg_perc, interval):
        def sim_chg_monthly_single(sq, ts_code, start_date, end_date, chg_perc, interval):
            def sim_single_chg_forw(df_forw, start_date, end_date, chg_perc, interval):
    '''

    start_date = '20200101'
    end_date   = '20230602'
    chg_perc   = 0.55
    interval   = 0.03

    ts_code    = '002475.SZ'
    draw_example(ts_code, start_date, end_date, chg_perc)
    sim_chg_monthly(sq, ts_code, start_date, end_date, chg_perc, interval)

    quit()

    ts_code    = None       # all stocks
    if ts_code == None:
        title_str = 'stat-{:.1f}%-{}-mv1000'.format(chg_perc*100, interval)
    else:
        title_str = 'stat-{}-{:.1f}%-{}'.format(ts_code, chg_perc*100, interval)

    if ts_code == None:
        code_list = sq.query_basic(None)
        v1 = 1000.0
        v2 = np.inf
        code_list = sq.select_mktvalue(v1, v2)
        print('Found {:4d}'.format(len(ref)))
    else:
        code_list = [{'ts_code':ts_code}]

    df_stat = sim_chg(code_list, start_date, end_date, chg_perc, interval)
    draw_stat_chg(df_stat, title_str)
    df_stat.to_csv(title_str + '.csv', index=False)

