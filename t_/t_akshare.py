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

def get_bdlist_ori(col):
    #df_new = pd.read_csv('t_akshare_board.csv', dtype={'代码': str}) # 从文件读取，调试使用
    df_new = ak.stock_board_concept_name_ths()
    if df_new.empty:
        print('Error: ak.stock_board_concept_name_ths empty')
        return

    print(df_new)
    # 替换里面日期为None的列，不知道为什么有None
    #df_new['日期'] = df_new['日期'].fillna("2050-01-01")
    df_new['日期'] = df_new['日期'].astype(str)

    # 先按'代码' 列排序，'代码' 列相同，将根据 '概念名称' 列的值进行排序
    # 为了后续去重，比较时便于查看
    df_new.sort_values(by=['代码', '概念名称'], inplace=True)

    df_new.reset_index(drop=True, inplace=True)

    col.drop()
    data = df_new.to_dict('records')
    col.insert_many(data)

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

def compare_df_v2(df_new, df_cur):
    df_name_all = pd.merge(df_cur, df_new, left_index=True, right_index=True, how='outer', suffixes=('_cur', '_new'))
    print(df_name_all)
    df_name_diff = df_name_all[df_name_all['代码_cur'] != df_name_all['代码_new']]

    print(df_name_diff)

    df_diff_new = df_name_diff[(df_name_diff['代码_cur'].isna()) & (df_name_diff['代码_new'].notna())]
    if len(df_diff_new.index)>0:
        print('new')
        print(df_diff_new)
        print()

    df_diff_remove = df_name_diff[(df_name_diff['代码_cur'].notna()) & (df_name_diff['代码_new'].isna())]
    if len(df_diff_remove.index)>0:
        print('remove')
        print(df_diff_remove)
        print()

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

def save_board_info(col, symbol):
    try:
        df_new = ak.stock_board_cons_ths(symbol=symbol)
    except Exception as e:
        print("Error: save_board_info {} {}".format(symbol, e)) 
        return

    # 对新数据进行排序和去重
    dup_codes = df_new[df_new.duplicated('代码', keep=False)]['代码']
    if not dup_codes.empty:
        print(f"board_code {symbol} Dup codes {dup_codes.values}")
    df_new.drop_duplicates(subset='代码', keep='first', inplace=True)

    # 从数据库中获取旧的数据
    data_old = list(col.find({'板块代码': symbol}))
    df_cur = pd.DataFrame(data_old)
    df_cur.drop(columns=['_id', '板块代码'], inplace=True)

    df_new = df_new.sort_values(by='代码').reset_index(drop=True)
    df_cur = df_cur.sort_values(by='代码').reset_index(drop=True)

    random_index = np.random.choice(df_new.index, 1, replace=False)
    df_new = df_new.drop(random_index)
    random_index = np.random.choice(df_cur.index, 1, replace=False)
    df_cur = df_cur.drop(random_index)

    print('df_new')
    print(df_new)
    print()
    print('df_cur')
    print(df_cur)
    print()

    new_codes = df_new[~df_new['代码'].isin(df_cur['代码'])]['代码']
    removed_codes = df_cur[~df_cur['代码'].isin(df_new['代码'])]['代码']
    if not new_codes.empty:
        print(f"New codes: {new_codes.values}")
    if not removed_codes.empty:
        print(f"Removed codes: {removed_codes.values}")

    df_new = df_new.drop(columns=['序号', '名称', '现价', '涨跌幅', '涨跌', '涨速',  '换手', '量比', '振幅', '成交额', '流通股', '流通市值', '市盈率'])
    df_cur = df_cur.drop(columns=['序号', '名称', '现价', '涨跌幅', '涨跌', '涨速',  '换手', '量比', '振幅', '成交额', '流通股', '流通市值', '市盈率'])

    compare_df_v2(df_new, df_cur)
    quit()

    df_all = pd.concat([df_cur, df_new])
    df_all.drop_duplicates(subset=['代码', '板块代码'], keep='first', inplace=True)
    if len(df_all) > len(df_old):
        print("Info: 新的数据 {} 条".format(len(df_all) - len(df_old)))
    else:
        print("Info: 新数据和老数据相同 {} 条".format(len(df_all)))

    # 将新的数据更新到数据库
    df_all['板块代码'] = symbol
    data = df_all.to_dict("records")
    col.delete_many({'板块代码': symbol})
    col.insert_many(data)

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
    client = MongoClient(port=27017)
    db = client.ak_board
    col_updateinfo = db.updateinfo
    col_bdlist_ori = db.bdlist_ori
    col_bdlist = db.bdlist
    col_bdinfo_ori = db.bdinfo_ori
    col_bdinfo = db.bdinfo

    # get new -> ori
    #get_bdlist_ori(col_bdlist_ori)

    # compare ori with current
    result = compare_bdlist(col_bdlist_ori, col_bdlist)
    if result is not None:
        df_diff_new, df_diff_remove, df_diff_namechg, df_diff_num = result
    else:
        print("compare_bdlist returned None")

    # 增量更新 bdlist_ori -> bdlist
    if result is not None and len(df_diff_remove.index) == 0:
        #col_bdlist.drop()
        #documents = list(db.bdlist_ori.find({}))
        #db.bdlist.insert_many(documents)
        #col_bdlist_ori.rename('bdlist')
        pass

    symbol = "308438"
    save_board_info(col_bdinfo_ori, symbol)

    df_bdlist = pd.DataFrame(list(col_bdlist.find())) # 获取板块信息
    for i, row in df_bdlist.iterrows():
        symbol = row["代码"]
        save_board_info(col_bdinfo_ori, symbol)

        # 检查板块-股票中有没有相同内容重复的
        data = list(col_bdinfo_ori.find())
        df = pd.DataFrame(data)
        df_duplicates = df[df.duplicated(subset=['代码', '板块代码'], keep=False)]
        if not df_duplicates.empty:
            print(f'board code {symbol}')
            print(df_duplicates)
            break

        if i>10:
            break

    save_update_info_to_db(col_updateinfo)

