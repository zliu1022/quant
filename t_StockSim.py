#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockSim import sim_chg
from StockSim import sim_chg_monthly
import StockDraw
import sys
from StockQuery import StockQuery
import numpy as np
from StockDraw import draw_stat_chg
from StockDraw import draw_example

if __name__ == '__main__':
    #ts_code    = '688223.SH' # 晶科能源
    #ts_code    = '000590.SZ' # 启迪药业
    #ts_code    = '000610.SZ' # 西安旅游
    #ts_code    = '600519.SH' # 茅台
    #ts_code    = '002241.SZ' # 歌尔
    #ts_code    = '002273.SZ' # 水晶
    #ts_code    = '000425.SZ' # 徐工

    #ts_code    = '838030.BJ' # 德众汽车
    #ts_code    = '000001.SZ' # 平安
    #ts_code    = '000055.SZ' # 方大集团
    #ts_code    = '001218.SZ' # 丽臣实业

    #ts_code    = '000501.SZ' # 武商集团
    #ts_code    = '601186.SH' # 中国铁建

    #ts_code    = '002317.SZ' # 众生药业
    #ts_code    = '002528.SZ' # 英飞拓

    #ts_code    = '002456.SZ' # 欧菲光

    sq = StockQuery()
    start_date = '20200101'
    end_date   = '20230602'

    if len(sys.argv) == 4:
        ts_code  = sys.argv[1]
        chg_perc = float(sys.argv[2])
        interval = float(sys.argv[3])
        draw_example(ts_code, start_date, end_date, chg_perc)
        sim_chg_monthly(sq, ts_code, start_date, end_date, chg_perc, interval)
        quit()

    ts_code    = None       # all stocks
    chg_perc   = 0.55
    interval   = 0.03

    if ts_code == None:
        title_str = 'stat-{:.1f}%-{}-mv1000'.format(chg_perc*100, interval)
    else:
        title_str = 'stat-{}-{:.1f}%-{}'.format(ts_code, chg_perc*100, interval)

    if ts_code == None:
        v1 = 5000.0
        v2 = np.inf
        code_list = sq.select_mktvalue(v1, v2)
        #code_list = sq.query_basic(None)
        print('Found {:4d}'.format(len(code_list)))
    else:
        code_list = [{'ts_code':ts_code}]

    df_stat = sim_chg(sq, code_list, start_date, end_date, chg_perc, interval)
    draw_stat_chg(df_stat, title_str)
    df_stat.to_csv(title_str + '.csv', index=False)

