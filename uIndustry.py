#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
from pprint import pprint
import sys
from uCode import tscode

if __name__ == '__main__':
    sq = StockQuery()

    if len(sys.argv) == 2:
        industry = sys.argv[1]
    else:
        print('./uXX industry')
        print('industry -> code_list')
        industry = '铅锌'

    df = sq.query_industry_df(industry)
    print(df)
    df_mv = sq.query_mktvalue_industry(industry)
    print(df_mv)
    quit()

    for i, row in df.iterrows():
        code = row['ts_code']
        name = row['name']
        print(code, name)

        for i, row in df_mv.iterrows():
            arr = row['mv']
            for i in arr:
                if i['ts_code'] == code:
                    print('    ', row['start_date'], row['end_date'], i['mktvalue'])

