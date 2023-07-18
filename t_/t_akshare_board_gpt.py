#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import akshare as ak
from pymongo import MongoClient

import datetime
import os

today_str = datetime.datetime.now().strftime('%Y-%m-%d')
today_dt= datetime.datetime.strptime(today_str,'%Y-%m-%d')

def convert_date_injson(data):
    #{'日期': datetime.date(2023, 6, 9), '概念名称': '算力租赁', '成分股数量': 39, '网址': 'http://q.10jqka.com.cn/gn/detail/code/309068/', '代码': '309068'}
    #转换为：
    #{'日期': '2023-06-09', '概念名称': '算力租赁', '成分股数量': 39, '网址': 'http://q.10jqka.com.cn/gn/detail/code/309068/', '代码': '309068'}
    converted_data = []
    for record in data:
        if record['日期'] is not None:
            try:
                record['日期'] = record['日期'].strftime('%Y-%m-%d')
            except Exception as e:
                print('Error: convert date{}'.format(e))
                print(record)
                print()
                continue
        converted_data.append(record)
    return converted_data

def save_sector_info_to_db(col_board):
    #df = pd.read_csv('t_akshare_board.csv', dtype={'代码': str}) # 从文件读取，调试使用
    df = ak.stock_board_concept_name_ths()

    existing = list(col_board.find({}, {'代码': 1}))
    if not existing:
        data = df.to_dict('records')
        data = convert_date_injson(data)
        col_board.insert_many(data)
        print("板块信息已成功保存到数据库 new", len(df.index))
        return

    # 将数据框中的板块代码列与现有记录中的代码进行比较，找到不同的内容
    df_diff = pd.merge(df, pd.DataFrame(existing), on='代码', how='left', indicator=True)
    df_diff = df_diff[df_diff['_merge'] == 'left_only']

    print('diff', len(df_diff.index))
    print(df_diff)

    # 转换为字典列表
    data = df_diff.drop(['_merge'], axis=1).to_dict('records')
    data = convert_date_injson(data)

    # 执行更新操作
    if data:
        col_board.update_many(
            {'代码': {'$in': [r['代码'] for r in data]}},
            {'$set': data},
            upsert=True
        )
    print("板块信息已成功保存到数据库 update", len(df_diff.index))

def save_stock_list_to_db(col, symbol):
    try:
        df = ak.stock_board_cons_ths(symbol=symbol)
    except Exception as e:
        print("Error: save_stock_list_to_db {} {}".format(symbol, e))
        return

    df['板块代码'] = symbol
    data = df.to_dict("records")
    col.insert_many(data)
    print("股票列表信息已成功保存到数据库 {} {}".format(symbol, len(df.index)))

def save_update_info_to_db(col_updateinfo):
    update_time = pd.Timestamp.now().strftime("%Y-%m-%d")
    data = {"update_time": update_time}
    col_updateinfo.update_one( { }, { '$set': data }, upsert=True )

    print("更新信息已成功保存到数据库。", update_time)

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
    '''
    #get_board()
    df_board = query_board()
    for i in range(len(df_board.index)):
        item = df_board.iloc[i]
        print('{:10} {:10} {:10} {}'.format(item['ak_code'], item['name'], item['num'], item['url']))
        get_board_detail(item['ak_code'])
    '''

    client = MongoClient(port=27017)
    db = client.ak_board
    col_name = 'boardinfo'
    col_name = 'boarddetails'
    col_updateinfo = db.updateinfo

    '''
    col_board      = db[col_name]
    if col_name not in db.list_collection_names():
        print('create collection {}'.format(col_name))
        db.create_collection(col_name)

    col_board_list = db[col_name]
    if col_name not in db.list_collection_names():
        print('create collection {}'.format(col_name))
        db.create_collection(col_name)
    
    save_sector_info_to_db(col_board)

    df_sector_info = pd.DataFrame(list(col_board.find())) # 获取板块信息

    # 遍历板块信息，获取板块具体包含的股票信息并存储到数据库
    for _, row in df_sector_info.iterrows():
        symbol = row["代码"]
        save_stock_list_to_db(col_board_list, symbol)
    '''

    # 保存更新信息到数据库
    save_update_info_to_db(col_updateinfo)

