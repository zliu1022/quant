#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
import matplotlib.pyplot as plt
from time import time
import numpy as np
from datetime import datetime
import sys
from Utils import RecTime
from StockRecover import recover_price_forward
from StockRecover import recover_price_backward
from StockSim import stat_chg, sim_chg, sim_chg_monthly

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

        title_str = ts_code + ' ' + str(df.index[0]) + '-' + str(df.index[day_len-1])
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
    import seaborn as sns
    sns.set(style='whitegrid')

    fig = plt.figure(figsize=(12.8,6.4))
    ax1 = fig.add_axes([0.1, 0.3,  0.85, 0.65])
    ax2 = fig.add_axes([0.1, 0.05, 0.85, 0.2])

    # https://www.w3schools.com/colors/colors_names.asp
    ax1.plot(df_day.date, df_day.high, linewidth=1, alpha=0.5, color='orangered', label='high')
    ax1.plot(df_day.date, df_day.low,  linewidth=1, color='lightgreen',  label='low')

    first_x = datetime.strptime(df_chg.index[0], '%Y%m%d')
    for i in range(len(df_chg.index)):
        arr_x, arr_y = [], []
        arr_incx, arr_incy = [], []

        # 绘制第一次买入->最低价
        arr_x.append(df_chg.index[i])
        arr_y.append(df_chg.firstmin.iloc[i])
        arr_x.append(df_chg.min_date.iloc[i])
        arr_y.append(df_chg['min'].iloc[i])
        ax1.plot(arr_x, arr_y, linestyle='dotted', linewidth=1, color='royalblue')

        # 绘制第一次买入日期和价格
        cur_x = datetime.strptime(df_chg.index[i], '%Y%m%d')
        ax1.text((cur_x-first_x).days*0.65+10, arr_y[0]*1+0.5, arr_x[0]+" {:.3f}".format(arr_y[0]), ha='left', rotation=20, fontsize=7, color='gray')

        # 绘制最低价买入日期和价格
        min_x = datetime.strptime(df_chg.min_date.iloc[i], '%Y%m%d')
        ax1.text((min_x-first_x).days*0.65, arr_y[1]*1-0.5, arr_x[1]+" {:.3f}".format(arr_y[1]), ha='left', rotation=20, fontsize=7, color='gray')

        arr_incx.append(df_chg.min_date.iloc[i])
        arr_incy.append(df_chg['min'].iloc[i])
        arr_incx.append(df_chg.max_date.iloc[i])
        arr_incy.append(df_chg['max'].iloc[i])

        # 最后一次买入未卖出，设置时间为20500101
        if arr_incx[1] != '20500101':
            # 绘制最低价->最高价
            ax1.plot(arr_incx, arr_incy, linestyle='dotted', linewidth=1.5, color='red')
            max_x = datetime.strptime(df_chg.max_date.iloc[i], '%Y%m%d')
            # 绘制最高价卖出日期和价格
            ax1.text((max_x-first_x).days*0.65, arr_incy[1]*1+0.5, arr_incx[1]+" {:.3f}".format(arr_incy[1]), ha='left', rotation=20, fontsize=7, color='gray')

        ax1.plot(df_chg.min_date.iloc[i], df_chg['min'].iloc[i], 'o', c='r', markersize=1.1)

    ax1.set(xlabel='', ylabel='price',
        title=ts_code)
    leg = ax1.legend(loc='upper right', frameon=False)

    ax2.bar(df_day.date, df_day.amount, alpha=0.5, width=0.6, label='amount')
    ax2.set(xlabel='date', ylabel='amount')
    leg2 = ax2.legend(loc='upper right', frameon=False)

    arr_ticks = []
    day_len = len(df_day.index)

    index_date = datetime.strptime(df_day.date[0], '%Y%m%d')
    arr_ticks.append(df_day.date[0])

    for i in range(day_len):
        cur_date = datetime.strptime(df_day.date[i], '%Y%m%d')
        if (cur_date-index_date).days > 87 and cur_date.day<=3:
            arr_ticks.append(df_day.date[i])
            index_date = cur_date

    ax1.axes.xaxis.set_ticks(arr_ticks)
    ax2.axes.xaxis.set_ticks(arr_ticks)

    title_str = ts_code + '_' + df_day.date[0] + '_' + df_day.date[day_len-1] + '_' + str(chg_perc)
    #plt.savefig(title_str + '.png', dpi=150)
    plt.show()
    plt.close()
    return

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

def draw_example(ts_code, start_date, end_date, chg_perc):
    rt = RecTime()
    sq = StockQuery()
    sd = StockDraw()

    df_day   = sq.query_day_code_date_df(ts_code, start_date, end_date)
    df_bonus = sq.query_bonus_code_df(ts_code)
    #df = df_day.drop(columns=['open', 'close'])
    df = df_day

    # 前复权
    df_forw = recover_price_forward(df, df_bonus)

    # 统计上涨 0.1 幅度下，次数、最大下跌幅度、最大下跌天数
    df_chg, total_num, max_dec_perc, max_dec_days = stat_chg(df_forw, start_date, chg_perc)
    print('{} total_num {} max_dec_perc -{:.1f}% max_dec_days {:3d}'.format(ts_code, total_num, max_dec_perc, max_dec_days))
    print('df_chg')
    print(df_chg)
    print()

    draw_price_amount_withchg(ts_code, df_forw, df_chg, chg_perc)

    # 后复权
    df_back = recover_price_backward(df, df_bonus) # example, normally will not use backward

    # 不复权、前复权、后复权合并到一张图上
    df = df.drop(columns=['amount', 'volume', 'turnoverrate', 'open', 'close'])
    df_back = df_back.drop(columns=['amount', 'volume', 'turnoverrate', 'open', 'close'])
    df_forw = df_forw.drop(columns=['amount', 'volume', 'turnoverrate', 'open', 'close'])

    df_back = df_back.rename(columns={'high': 'high_back', 'low': 'low_back'})
    df_forw = df_forw.rename(columns={'high': 'high_forw', 'low': 'low_forw'})

    df_tmp = df.merge(    df_forw, left_on='date', right_on='date')
    #df_tmp = df_tmp.merge(df_back, left_on='date', right_on='date')

    sd.draw_df(ts_code+'-merge', df_tmp)

    rt.show_s()

if __name__ == '__main__':
    sq = StockQuery()
    # 20240802: ./StockDraw.py 002475.SZ 1.55 0.03 运行成功，并核对了前复权数据
    if len(sys.argv) == 4:
        start_date = '20201013'
        end_date   = '20250826'
        ts_code  = sys.argv[1]        # 002475.SZ
        chg_perc = float(sys.argv[2]) # 0.55
        interval = float(sys.argv[3]) # 0.03
        draw_example(ts_code, start_date, end_date, chg_perc)
        #sim_chg_monthly(sq, ts_code, start_date, end_date, chg_perc, interval)
        quit()
  
    ts_code    = None       # all stocks
    start_date = '20200101'
    end_date   = '20230602'
    chg_perc   = 0.55
    interval   = 0.03

    if ts_code == None:
        title_str = 'stat-{:.1f}%-{}-mv1000'.format(chg_perc*100, interval)
    else:
        title_str = 'stat-{}-{:.1f}%-{}'.format(ts_code, chg_perc*100, interval)

    if ts_code == None:
        code_list = sq.query_basic(None)
        '''
        v1 = 1000.0
        v2 = np.inf
        code_list = sq.select_mktvalue(v1, v2)
        print('Found {:4d}'.format(len(ref)))
        '''
    else:
        code_list = [{'ts_code':ts_code}]

    df_stat = sim_chg(sq, code_list, start_date, end_date, chg_perc, interval)
    draw_stat_chg(df_stat, title_str)
    #df_stat.to_csv(title_str + '.csv', index=False)


