#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
from pprint import pprint

def drop_bd_useless(df_cur):
    df_new = df_cur.drop(columns=['_id', '序号', '现价', '涨跌幅', '涨跌', '涨速', '换手', '量比', '振幅', '成交额', '流通股', '流通市值'])
    return df_new

def tscode(sq, ts_code):
    df_ref = sq.query_bd_tscode(ts_code.split('.')[0])
    #df_ref = drop_bd_useless(df_ref)
    print(ts_code, df_ref.iloc[0]['名称'], 'pe', df_ref.iloc[0]['市盈率'])
    for index, row in df_ref.iterrows():
        bd_code = row['板块代码']
        df = sq.query_bdlist(bd_code)
        print("    ", bd_code, df.iloc[0]['概念名称'])
    print()

if __name__ == '__main__':
    sq = StockQuery()

    ts_code = "000060.SZ"
    tscode(sq, ts_code)

    bd_code = "301582"
    #bd_code = "300248"
    df = sq.query_bdlist(bd_code)
    print(bd_code, df.iloc[0]['概念名称'])
    df_ref = sq.query_bd_bdcode(bd_code)
    df_ref = drop_bd_useless(df_ref)
    pprint(df_ref)
    quit()

    bd_code_list = [
        "300809", #小金属概念
        "301511", # 金属镍
        "301577", #金属铜
        "301582", #金属锌
        "302174", #钴
        "308864"  #金属
    ]
    for bd_code in bd_code_list:
        df = sq.query_bdlist(bd_code)
        print(bd_code, df.iloc[0]['概念名称'])

        df_ref = sq.query_bd_bdcode(bd_code)
        df_ref = drop_bd_useless(df_ref)
        pprint(df_ref)
        print()
