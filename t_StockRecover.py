#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
from StockRecover import recover_price_forward

if __name__ == '__main__':
    sq = StockQuery()

    # 检查复权数据，amount不复权
    ts_code    = '002475.SZ'
    start_date = '20220711'
    end_date   = '20220714' # bonus 中的日期是 20220713

    df_day   = sq.query_day_code_date_df(ts_code, start_date, end_date)
    print(df_day)
    df_bonus = sq.query_bonus_code_df(ts_code)
    df_forw  = recover_price_forward(df_day, df_bonus)
    print(df_forw)

