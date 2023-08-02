#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
from pprint import pprint
import sys

def drop_bd_useless(df_cur):
    df_new = df_cur.drop(columns=['_id', '序号', '现价', '涨跌幅', '涨跌', '涨速', '换手', '量比', '振幅', '成交额', '流通股'])
    return df_new

def tscode(sq, ts_code):
    bd_code_list = []

    # 从basic获取 'name': '立讯精密', 'industry': '元器件', 'list_status': 'L', 'list_date': '20100915'
    basic = sq.query_basic(ts_code)

    # 从bdinfo获取该code对应的board
    df_ref = sq.query_bd_tscode(ts_code.split('.')[0])
    print(ts_code, df_ref.iloc[0]['名称'], 'pe', df_ref.iloc[0]['市盈率'], basic[0]['industry'])
    for index, row in df_ref.iterrows():
        bd_code = row['板块代码']
        bd_code_list.append(bd_code)

        # 查询板块名字
        df = sq.query_bdlist(bd_code)
        print("    ", bd_code, df.iloc[0]['概念名称'])
    print()
    return bd_code_list

def convert_circulating_market_value(value):
    if '亿' in value:
        return float(value.replace('亿', '')) * 1e8
    else:
        return float(value)

if __name__ == '__main__':
    sq = StockQuery()

    if len(sys.argv) == 2:
        ts_code = sys.argv[1]
    else:
        print('./uXX ts_code')
        print('code -> industry, board -> code_list')
        ts_code = '002475.SZ'

    bd_code_list = tscode(sq, ts_code)

    for bd_code in bd_code_list:
        # 查板块名字
        df = sq.query_bdlist(bd_code)

        # 查板块含的股票
        df_ref = sq.query_bd_bdcode(bd_code)
        print(bd_code, df.iloc[0]['概念名称'], len(df_ref.index))

        if len(df_ref.index) > 100:
            continue

        df_ref = drop_bd_useless(df_ref)
        df_ref['流通市值(数值)'] = df_ref['流通市值'].apply(convert_circulating_market_value)
        df_sorted = df_ref.sort_values(by='流通市值(数值)', ascending=False)
        df_sorted.drop('流通市值(数值)', axis=1, inplace=True)

        print(df_sorted.head(3))
        print(df_sorted.tail(3))
        print()
