#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
from pprint import pprint
import sys
from uCode import tscode

if __name__ == '__main__':
    sq = StockQuery()

    industry = '铅锌'
    mv_min = 0
    mv_max = 99999
    if len(sys.argv) == 2:
        industry = sys.argv[1]
    elif len(sys.argv) == 4:
        industry = sys.argv[1]
        mv_min = float(sys.argv[2])
        mv_max = float(sys.argv[3])
    else:
        print('./uXX industry')
        print('industry -> code_list')

    df = sq.query_industry_df(industry)
    df_mv = sq.query_mktvalue_industry(industry)
    '''
    print(df)
    print(df_mv)
    quit()
    '''

    for i, row in df.iterrows():
        code = row['ts_code']
        name = row['name']
        print(code, name)

        for i, row in df_mv.iterrows():
            arr = row['mv']
            for i in arr:
                if i['ts_code'] == code and i['mktvalue'] < mv_max and i['mktvalue'] > mv_min:
                    print('    ', row['start_date'], row['end_date'], i['mktvalue'])

