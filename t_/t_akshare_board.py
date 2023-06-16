#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import akshare as ak
import datetime
import pandas as pd
import os

today_str = datetime.datetime.now().strftime('%Y-%m-%d')
today_dt= datetime.datetime.strptime(today_str,'%Y-%m-%d')
akboardfile_str = 't_ak_board_' + today_str + '.csv'

def get_board():
    global akboardfile_str

    df = ak.stock_board_concept_name_ths()
    print('Get {} boards'.format(len(df.index)))

    df.to_csv(akboardfile_str, index=False, sep=',', header=True, na_rep='')
    print('save to {}'.format(akboardfile_str))

def get_board_detail(code):
    f_str = 't_akbd_' + code + '.csv'
    if os.path.exists(f_str):
        print("文件存在")
        return
    try:
        df = ak.stock_board_cons_ths(symbol=code)
    except Exception as e:
        print(f"Error: ak.stock_board_cons_ths {str(e)}")
        return
    print('Get {}'.format(len(df.index)))
    df.to_csv(f_str, index=False, sep=',', header=True, na_rep='')
    print('save to {}'.format(f_str))

def query_board():
    global akboardfile_str
    df = pd.read_csv(akboardfile_str, dtype={'代码': str})

    columns_to_rename = {
        '代码':     'ak_code', 
        '日期':     'date', 
        '概念名称': 'name', 
        '成分股数量':'num', 
        '网址':     'url', 
    }
    df = df.rename(columns=columns_to_rename)

    new_order = [
        'ak_code', 'date', 'name', 'num', 'url'
        ]
    df = df.reindex(columns=new_order)

    return df


if __name__ == '__main__':
    #get_board()
    df_board = query_board()
    for i in range(len(df_board.index)):
        item = df_board.iloc[i]
        print('{:10} {:10} {:10} {}'.format(item['ak_code'], item['name'], item['num'], item['url']))
        get_board_detail(item['ak_code'])

