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

    start_date = '20200101'
    df_mv = sq.query_mktvalue_industry(start_date, industry)

    for i, row in df.iterrows():
        code = row['ts_code']
        name = row['name']

        selected_rows = df_mv.loc[df_mv['ts_code'] == code, 'mktvalue']
        if not selected_rows.empty:
            mv = selected_rows.iloc[0]
        else:
            mv = None  # 或者其他适当的默认值
        print(i, code, name, mv)

