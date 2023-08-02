#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
from pprint import pprint
import sys
from uCode import tscode

if __name__ == '__main__':
    sq = StockQuery()

    if len(sys.argv) == 2:
        industry_code = sys.argv[1]
    else:
        print('./uXX industry_code')
        print('industry -> code_list -> board_list')
        industry_code = '铅锌'

    df = sq.query_industry_df(industry_code)

    for index, row in df.iterrows():
        code = row['ts_code']
        name = row['name']
        tscode(sq, code)

