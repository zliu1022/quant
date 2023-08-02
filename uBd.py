#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
from pprint import pprint
import sys
from uCode import tscode

if __name__ == '__main__':
    sq = StockQuery()

    if len(sys.argv) == 2:
        bd_code = sys.argv[1]
    else:
        print('./uXX industry_code')
        print('industry -> code_list -> board_list')
        bd_code = '301582'

    # name, url, num ...
    df = sq.query_bdlist(bd_code)
    df_bd = df.iloc[0]
    print(df_bd['概念名称'], df_bd['代码'])

    df = sq.query_bd_bdcode(bd_code)

    for index, row in df.iterrows():
        code = row['代码']
        name = row['名称']
        pe = row['市盈率']
        mktvalue = row['流通市值']
        #print(code, name, pe, mktvalue)
        tscode(sq, code)

