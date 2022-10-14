#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pprint import pprint
from StockGet import StockGet
import pandas as pd
import numpy as np

if __name__ == '__main__':
    si = StockGet()

    find_str = None
    ref = si.db_basicfind(find_str)
    if ref == None:
        print('Not found stock list')
        exit()

    #all_stocks = si.stock_list
    all_stocks = [
        {'ts_code':'600654.SH'},
        {'ts_code':'300370.SZ'},
        {'ts_code':'301268.SZ'},
        {'ts_code':'001236.SZ'},
        {'ts_code':'603237.SH'},
        {'ts_code':'688332.SH'},
        {'ts_code':'688375.SH'}
    ]

    for index,stock_info in enumerate(all_stocks):
        ts_code = stock_info['ts_code']

        ref = si.col_bonus_ori.find_one({ "ts_code": ts_code })
        if ref == None:
            continue
        df_ref = pd.DataFrame(ref['items'])
        df_ref_len = len(df_ref.index)

        ts_code_arr = ts_code.split(".", 1)
        ts_code_symbol = ts_code_arr[1]+ts_code_arr[0]
        url = bonus_url +ts_code_symbol
        ret, resp = si.req_url_retry(url, 3)
        data = resp['data']
        df = pd.DataFrame(data['items'])
        df_len = len(df.index)

        index_none = []
        for i in range(df_ref_len):
            d = df_ref.loc[i, 'ashare_ex_dividend_date']
            dividend_year = df_ref.loc[i, 'dividend_year']
            if d == d and d != None: # not nan
                continue
            for j in range(df_len):
                new_d = df.loc[j, 'ashare_ex_dividend_date']
                if df.loc[j, 'dividend_year'] == dividend_year:
                    if new_d == new_d and new_d != None: # not nan
                        print(ts_code, 'null ex_date has same item', dividend_year, new_d)
                        index_none.append(i)
        df_ref = df_ref.drop(index_none)

        df_new = pd.concat([df, df_ref]).sort_values(by='ashare_ex_dividend_date', ascending=False).drop_duplicates().reset_index(drop=True)
        df_new_len = len(df_new.index)

        if len(index_none) != 0:
            print(ts_code)
            print(df_new)
            print()

        aaa = df_new.to_dict('records')
        data = sorted(aaa,key = lambda e:e.__getitem__('ashare_ex_dividend_date'), reverse=True)

