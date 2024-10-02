#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
from pprint import pprint
from Utils import RecTime
from StockRecover import recover_price_forward

def find_highest_day(sq, ts_code):
    rt = RecTime()
    df_day = sq.query_day_code_df(ts_code)
    if df_day.empty:
        return None
    df_bonus = sq.query_bonus_code_df(ts_code)
    if df_bonus.empty:
        return None

    df = df_day
    df_forw = recover_price_forward(df, df_bonus)
    if df_forw.empty:
        return None

    #highest_day      = max(df_day, key=lambda x: x['high'])
    #highest_day_forw = max(df_forw, key=lambda x: x['high'])
    highest_day = df_day.loc[df['high'].idxmax()]
    highest_day_forw = df_forw.loc[df['high'].idxmax()]
    #rt.show_ms()
    return highest_day, highest_day_forw

if __name__ == '__main__':
    sq = StockQuery()


    arr_ts_code = ['002475.SZ', '600519.SH', '000425.SZ', '002273.SZ', '002456.SZ', '000002.SZ', '600054.SH', '603199.SH', '600497.SH', '002033.SZ']

    for ts_code in arr_ts_code:
        ret = sq.query_basic(ts_code)
        print(ts_code, ret[0]['name'], end=' ')

        '''
        ret = sq.query_highest_day(ts_code)
        print(ret['date'], ret['high'])

        # 直接在原始价格中，找最大值
        ret = sq.find_highest_day(ts_code)
        print(ret['date'], ret['high'])
        '''

        # 在前复权价格中，找最大值
        ret, ret_forw = find_highest_day(sq, ts_code)
        print(ret['date'], ret['high'], end=' ')
        print(ret_forw['date'], ret_forw['high'])
    quit()

    start_date = '20230101'
    end_date   = '20230201'
    ret = sq.query_bonus_date(start_date, end_date)
    pprint(ret[0])

    ts_code    = '831445.BJ'
    start_date = '20210101'
    end_date   = '20230201'
    ret = sq.query_bonus_code_date(ts_code, start_date, end_date)
    pprint(ret[0])

