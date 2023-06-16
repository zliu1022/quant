#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import akshare as ak
import datetime
import pandas as pd

today_str = datetime.datetime.now().strftime('%Y-%m-%d')
today_dt= datetime.datetime.strptime(today_str,'%Y-%m-%d')
akfile_str = 't_akshare_codelist_' + today_str + '.csv'

def get_codelist():
    global akfile_str

    df = ak.stock_zh_a_spot_em() 
    print('Get {} codes'.format(len(df.index)))

    df.to_csv(akfile_str, index=False, sep=',', header=True, na_rep='')
    print('save to {}'.format(akfile_str))

def query_code(ts_code):
    global akfile_str
    df = pd.read_csv(akfile_str, dtype={'代码': str})

    columns_to_drop = ['序号', '60日涨跌幅']
    df = df.drop(columns=columns_to_drop)

    columns_to_rename = {
        '代码': 'ak_code', 
        '名称': 'name', 
        '今开':'open', 
        '昨收':'prev_close', 
        '最高':'high', '最低':'low', 
        '成交量':'volume',          # 手, 即100股
        '成交额':'amount',          # 元
        '最新价': 'p_cur',          # 当前价格,收盘变成close
        '涨跌额': 'p_chg',          # p_cur - prev_close
        '涨跌幅': 'p_chg_perc',     # p_chg/prev_close * 100.0
        '振幅':   'p_range',        # (high - low)/ prev_close
        '量比':   'volume_ratio',
        '换手率': 'turnover_rate',
        '市盈率-动态': 'pe',        # Price-to-Earnings Ratio - Forward, 股票的市场价格与每股收益 (每股利润) 之间的比率
        '市净率':      'pb',        # Price-to-Book Ratio, 股票的市场价格与每股净资产 (每股账面价值) 之间的比率
        '总市值': 'mktvalue',       # market_capitalization
        '流通市值': 'cir_mktvalue', # circulating_market_cap
        '涨速':      'p_chg_speed',
        '5分钟涨跌': 'p_chg_5min',
        '年初至今涨跌幅': 'year_to_now_chg_perc'
    }
    df = df.rename(columns=columns_to_rename)

    new_order = [
        'ak_code', 'name', 'mktvalue', 'cir_mktvalue', 'pe', 'pb',
        'p_cur', 'open', 'low', 'high', 'prev_close',
        'p_chg', 'p_chg_perc', 'p_range',
        'p_chg_speed', 'p_chg_5min', 'year_to_now_chg_perc',
        'amount', 'volume', 'volume_ratio', 'turnover_rate',
        ]
    df = df.reindex(columns=new_order)

    keys = df.iloc[0].keys()
    ind = []
    for i in range(len(df.index)):
        item = df.iloc[i]
        if item.ak_code == '603160':
            ind.append(i)
        if item.ak_code == '601919':
            ind.append(i)

    print(ind)
    for k in keys:
        print('{:20}'.format(k), end='')
        for i in range(len(ind)):
            item = df.iloc[ind[i]]
            if k == 'name':
                print(' {:9}'.format(item[k]), end='')
            elif k == 'mktvalue' or k == 'cir_mktvalue' or k == 'amount':
                print(' {:>9}'.format(str(round(item[k]/100000000.0,1))), end='')
            else:
                print(' {:>9}'.format(item[k]), end='')
        print()

if __name__ == '__main__':
    #get_codelist()
    query_code('601919')

