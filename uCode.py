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
    if basic == None:
        basic = sq.query_basic_name(ts_code)
    if basic == None:
        quit()

    ts_code = basic[0]['ts_code']
    industry = basic[0]['industry']
    name = basic[0]['name']

    # 从bdinfo获取该code对应的board
    df_ref = sq.query_bd_tscode(ts_code.split('.')[0])

    # mktvalue
    start_date = "20200101"
    df_mv = sq.query_mktvalue_code(start_date, ts_code)

    '''
    print(basic)
    print(df_ref)
    print(df_mv)
    '''

    print(ts_code, name, 'mv', df_mv.iloc[0]['mktvalue'], 'pe', df_ref.iloc[0]['市盈率'], industry)
    print()

    df_i = sq.query_industry_df(industry)
    print('industry {:10} {}'.format(industry, len(df_i.index)))
    print()

    for index, row in df_ref.iterrows():
        bd_code = row['板块代码']

        # 查板块名字
        df = sq.query_bdlist(bd_code)

        # 查板块含的股票
        df_ref = sq.query_bd_bdcode(bd_code)
        print('{:<6} {:<10} {:>6}'.format(bd_code, df.iloc[0]['概念名称'], len(df_ref.index)))

        continue
        if len(df_ref.index) > 100:
            continue
        df_ref = drop_bd_useless(df_ref)
        df_ref['流通市值(数值)'] = df_ref['流通市值'].apply(convert_circulating_market_value)
        df_sorted = df_ref.sort_values(by='流通市值(数值)', ascending=False)
        df_sorted.drop('流通市值(数值)', axis=1, inplace=True)
        print(df_sorted.head(3))
        print(df_sorted.tail(3))
        print()
    return

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
        print('code -> code detail -> industry, board -> code_list')
        print()
        ts_code = '002475.SZ'
        ts_code = '000425.SZ'

    tscode(sq, ts_code)

