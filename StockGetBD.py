#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import akshare as ak
from pymongo import MongoClient

import datetime
import os
from pprint import pprint
import numpy as np

today_str = datetime.datetime.now().strftime('%Y-%m-%d')
today_dt= datetime.datetime.strptime(today_str,'%Y-%m-%d')

def get_bdlist_ori(col):
    #df_new = pd.read_csv('t_akshare_board.csv', dtype={'代码': str}) # 从文件读取，调试使用
    df_new = ak.stock_board_concept_name_ths()
    if df_new.empty:
        print('Error: ak.stock_board_concept_name_ths empty')
        return

    print('board list')
    print(df_new)

    # 日期列变为字符串，None也变成字符串
    df_new['日期'] = df_new['日期'].astype(str)
    # 先按'代码' 列排序，'代码' 列相同，将根据 '概念名称' 列的值进行排序
    # 为了后续去重，比较时便于查看
    df_new.sort_values(by=['代码', '概念名称'], inplace=True)
    df_new.reset_index(drop=True, inplace=True)

    col.drop()
    data = df_new.to_dict('records')
    col.insert_many(data)

# test case, 为了测试df比较函数，随意删除df中的数据
def do_new_remove():
    # Randomly delete a row from df_new_modified
    random_index = np.random.choice(df_new.index, 1, replace=False)
    print('drop df_new', random_index)
    df_new = df_new.drop(random_index)
    random_index = np.random.choice(df_cur.index, 1, replace=False)
    print('drop df_cur', random_index)
    df_cur = df_cur.drop(random_index)

def check_dup(df_new):
    # 检查df_new是否存在重复, 重复了也不知道怎么处理
    df_duplicated = df_new[df_new.duplicated('代码', keep=False)]
    if len(df_duplicated.index)>0:
        print('Info: df_new duplicated')
        print(df_duplicated)
        print()

def compare_df(df_new, df_cur):
    df_new.set_index('代码', inplace=True)
    df_cur.set_index('代码', inplace=True)

    df_name_new = df_new.drop(columns=['成分股数量'])
    df_name_cur = df_cur.drop(columns=['成分股数量'])
    df_name_all = pd.merge(df_name_cur, df_name_new, left_index=True, right_index=True, how='outer', suffixes=('_cur', '_new'))
    df_name_diff = df_name_all[df_name_all['概念名称_cur'] != df_name_all['概念名称_new']]

    df_diff_new = df_name_diff[(df_name_diff['概念名称_cur'].isna()) & (df_name_diff['概念名称_new'].notna())]
    if len(df_diff_new.index)>0:
        print('new')
        print(df_diff_new)
        print()

    df_diff_remove = df_name_diff[(df_name_diff['概念名称_cur'].notna()) & (df_name_diff['概念名称_new'].isna())]
    if len(df_diff_remove.index)>0:
        print('remove')
        print(df_diff_remove)
        print()

    df_diff_namechg = df_name_diff[(df_name_diff['概念名称_cur'].notna()) & (df_name_diff['概念名称_new'].notna())]
    if len(df_diff_namechg.index)>0:
        print('name change')
        print(df_diff_namechg)
        print()

    df_all = pd.merge(df_cur, df_new, left_index=True, right_index=True, how='outer', suffixes=('_cur', '_new'))
    df_all = df_all.drop(df_name_diff.index)
    df_diff_num = df_all[df_all['成分股数量_cur'] != df_all['成分股数量_new']]
    df_diff_num = df_diff_num.drop(columns=['概念名称_new'])
    if len(df_diff_num.index)>0:
        print('number change', len(df_diff_num.index))
        #with pd.option_context('display.max_rows', None):
        print(df_diff_num)
        print()

    return df_diff_new, df_diff_remove, df_diff_namechg, df_diff_num

# 仅仅针对2个df，都只有'代码'列，进行对比
def compare_df_v2(df_new, df_cur):
    df_new = df_new.drop(columns=['序号', '名称', '现价', '涨跌幅', '涨跌', '涨速',  '换手', '量比', '振幅', '成交额', '流通股', '流通市值', '市盈率'])
    df_cur = df_cur.drop(columns=['序号', '名称', '现价', '涨跌幅', '涨跌', '涨速',  '换手', '量比', '振幅', '成交额', '流通股', '流通市值', '市盈率'])

    df_name_all = pd.merge(df_cur, df_new, left_index=True, right_index=True, how='outer', suffixes=('_cur', '_new'))
    df_name_diff = df_name_all[df_name_all['代码_cur'] != df_name_all['代码_new']]

    df_diff_new = df_name_diff[(df_name_diff['代码_cur'].isna()) & (df_name_diff['代码_new'].notna())]
    if len(df_diff_new.index)>0:
        print('new')
        print(df_diff_new)

    df_diff_remove = df_name_diff[(df_name_diff['代码_cur'].notna()) & (df_name_diff['代码_new'].isna())]
    if len(df_diff_remove.index)>0:
        print('remove')
        print(df_diff_remove)

    return df_diff_new, df_diff_remove

def compare_bdlist(col_ori, col):
    # col_ori 是从网络拿到的原始数据
    # col 则是目前使用的数据
    ref = col_ori.find()
    df_new = pd.DataFrame(ref)
    if df_new.empty:
        print('Info: no new data in col_ori')
        return

    ref = col.find()
    df_cur = pd.DataFrame(ref)
    if df_cur.empty:
        # 如果cur是空，直接从col_ori覆盖过去即可
        return

    # 删除不参与比较的列，并认为代码是唯一不会改变的
    df_new = df_new.drop(columns=['_id', '日期', '网址'])
    df_new.sort_values(by=['代码', '概念名称'], inplace=True)
    df_cur = df_cur.drop(columns=['_id', '日期', '网址'])
    df_cur.sort_values(by=['代码', '概念名称'], inplace=True)

    check_dup(df_new)

    return compare_df(df_new, df_cur)

def update_bdlist(col_ori, col):
    data = df_new.to_dict('records')
    col.insert_many(data)
    print("board list update", len(df_diff.index))

def get_bdinfo_ori(col, symbol, bdname):
    try:
        df_new = ak.stock_board_cons_ths(symbol=symbol)
    except Exception as e:
        print("Error: get_bdinfo_ori {} {}".format(symbol, e)) 
        return

    # 新数据去重
    dup_codes = df_new[df_new.duplicated('代码', keep=False)][['代码', '名称']]
    if not dup_codes.empty:
        print(f"{symbol} {bdname} dup\n {dup_codes}")
    df_new.drop_duplicates(subset='代码', keep='first', inplace=True)

    # 和数据库中旧的数据比较
    data_old = list(col.find({'板块代码': symbol}))
    df_cur = pd.DataFrame(data_old)
    df_cur.drop(columns=['_id', '板块代码'], inplace=True)
    df_new = df_new.sort_values(by='代码').reset_index(drop=True)
    df_cur = df_cur.sort_values(by='代码').reset_index(drop=True)
    # Find new and removed codes
    new_codes = df_new[~df_new['代码'].isin(df_cur['代码'])][['代码', '名称']]
    removed_codes = df_cur[~df_cur['代码'].isin(df_new['代码'])][['代码', '名称']]
    if not new_codes.empty:
        print(f"{symbol} {bdname} new\n {new_codes}")
    if not removed_codes.empty:
        print(f"{symbol} {bdname} removed\n {removed_codes}")

    df_new['板块代码'] = symbol
    data = df_new.to_dict("records")
    col.delete_many({'板块代码': symbol})
    col.insert_many(data)

def save_update_info_to_db(col_updateinfo):
    update_time = pd.Timestamp.now().strftime("%Y-%m-%d")
    data = {"update_time": update_time}
    col_updateinfo.update_one( { }, { '$set': data }, upsert=True )
    print("update time", update_time)

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
    client = MongoClient(port=27017)
    db = client.ak_board
    col_updateinfo = db.updateinfo
    col_bdlist_ori = db.bdlist_ori
    col_bdlist = db.bdlist
    col_bdinfo_ori = db.bdinfo_ori
    col_bdinfo = db.bdinfo

    # get board list new -> ori
    #get_bdlist_ori(col_bdlist_ori)

    # get board info new -> ori
    #ret = get_bdinfo_ori(col_bdinfo, "302035", "人工智能")

    df_bdlist = pd.DataFrame(list(col_bdlist.find())) # 获取板块信息
    for i, row in df_bdlist.iterrows():
        symbol = row["代码"]
        bdname = row["概念名称"]
        ret = get_bdinfo_ori(col_bdinfo_ori, symbol, bdname)

    save_update_info_to_db(col_updateinfo)
    quit()

    # compare ori with current
    result = compare_bdlist(col_bdlist_ori, col_bdlist)
    if result is not None:
        df_diff_new, df_diff_remove, df_diff_namechg, df_diff_num = result
    else:
        print("compare_bdlist returned None")

    # update bdlist_ori -> cur
    # db.bdlist.drop()
    # db.bdlist_ori.find().forEach(function(doc) { db.bdlist.insertOne(doc); });
    if result is not None and len(df_diff_remove.index) == 0:
        col_bdlist.drop()
        data = list(db.bdlist_ori.find({}))
        db.bdlist.insert_many(data)
        pass

    # replace bdinfo ori -> cur
    # db.bdinfo.drop()
    # db.bdinfo_ori.find().forEach(function(doc) { db.bdinfo.insertOne(doc); });

