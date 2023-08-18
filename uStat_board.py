#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import pandas as pd
from pprint import pprint

client = MongoClient('mongodb://localhost:27017/')
db = client.ak_board
col_bdinfo = db.bdinfo
col_bdlist = db.bdlist

filename = "mv30-300-20200101-op_days.csv"
#filename = "mv100-5000-20200101-op_days.csv"
#filename = "mv0-inf-20200101-op_days.csv"

print(f'get data from {filename}')
df_all_code = pd.read_csv(filename)

df_all_bd = pd.DataFrame(columns=['board_code', 'name', 'num', 'norm_accum_profit', 'norm_cur_profit', 'count'])

def stat_board_from_code():
    for index, row in df_all_code.iterrows():
        code = row['ts_code']
        symbol = code.split('.')[0]
        result = col_bdinfo.find({'代码': symbol})

        for document in result:
            board_code = document['板块代码']

            # 如果这个板块代码已经在结果中，就更新它，否则就添加一行新的数据
            index_to_update = df_all_bd[df_all_bd['board_code'] == board_code].index
            if len(index_to_update) == 0:
                ret = col_bdlist.find({'代码': board_code})
                ret_list = list(ret)[0]
                name = ret_list['概念名称']
                num = ret_list['成分股数量']
                new_row = {
                    'board_code': board_code,
                    'name':name,
                    'num':num,
                    'norm_accum_profit': row['norm_accum_profit'],
                    'norm_cur_profit': row['norm_cur_profit'],
                    'count': 1
                }
                df_all_bd = df_all_bd.append(new_row, ignore_index=True)
            elif len(index_to_update) == 1:
                df_all_bd.at[index_to_update[0], 'norm_accum_profit'] += row['norm_accum_profit']
                df_all_bd.at[index_to_update[0], 'norm_cur_profit'] += row['norm_cur_profit']
                df_all_bd.at[index_to_update[0], 'count'] += 1
            else:
                print(f'find several same board {board_code}')

    df_all_bd['norm_accum_profit'] = df_all_bd['norm_accum_profit'].astype(float)
    df_all_bd['norm_cur_profit'] = df_all_bd['norm_cur_profit'].astype(float)
    df_all_bd['count'] = df_all_bd['count'].astype(int)

    df_all_bd['norm_accum_mean_profit'] = df_all_bd['norm_accum_profit'] / df_all_bd['count']
    df_all_bd['norm_cur_mean_profit'] = df_all_bd['norm_cur_profit'] / df_all_bd['count']

    print(df_all_bd)
    if not df_all_bd.empty:
        df_all_bd.to_csv("all-20200101-20230717-board.csv", index=False)

def get_board_name(board_code):
    global col_bdlist
    ret = col_bdlist.find({'代码': board_code})
    ret_list = list(ret)[0]
    name = ret_list['概念名称']
    num = ret_list['成分股数量']
    return name, num

def update_board_one_code(board_code, df_code):
    row = df_code.iloc[0].to_dict()
    global df_all_bd
    # 如果这个板块代码已经在结果中，就更新它，否则就添加一行新的数据
    index_to_update = df_all_bd[df_all_bd['board_code'] == board_code].index
    if len(index_to_update) == 0:
        name, num = get_board_name(board_code)
        new_row = {
            'board_code': board_code,
            'name':name,
            'num':num,
            'norm_accum_profit': row['norm_accum_profit'],
            'norm_cur_profit': row['norm_cur_profit'],
            'count': 1
        }
        df_all_bd = df_all_bd.append(new_row, ignore_index=True)
    elif len(index_to_update) == 1:
        df_all_bd.at[index_to_update[0], 'norm_accum_profit'] += row['norm_accum_profit']
        df_all_bd.at[index_to_update[0], 'norm_cur_profit'] += row['norm_cur_profit']
        df_all_bd.at[index_to_update[0], 'count'] += 1
    else:
        print(f'find several same board {board_code}')

# 还可以另外一种遍历,先遍历板块 bdlist, 再找板块对应的 code, bdinfo
# 这两种应该会不一样, 比如板块中有的股票代码，被bad_bonus之类剔除了
# 再到df_all_code 里面找
def stat_board_from_board():
    '''
    ref = col_bdlist.find()
    df_bdlist = pd.DataFrame(ref)
    df_bdlist = df_bdlist.drop(columns=['_id', '日期', '网址'])
    print(df_bdlist.head())
    print()
    '''
    ref = col_bdinfo.find()
    df_bdinfo = pd.DataFrame(ref)
    df_bdinfo = df_bdinfo.drop(columns=['_id', '序号', '现价', '涨跌幅', '涨跌', '涨速', '换手', '量比', '振幅', '成交额', '流通股', '流通市值'])
    df_bdinfo = df_bdinfo.drop_duplicates(subset=['代码', '板块代码'])

    df_all_code["ts_code"] = df_all_code["ts_code"].apply(lambda x: x.split('.')[0])

    for i, row in df_bdinfo.iterrows():
        board_code = row['板块代码']
        code = row['代码']
        df_code = df_all_code[df_all_code.ts_code==code]
        if df_code.empty:
            continue
        update_board_one_code(board_code, df_code)

    df_all_bd['norm_accum_profit'] = df_all_bd['norm_accum_profit'].astype(float)
    df_all_bd['norm_cur_profit'] = df_all_bd['norm_cur_profit'].astype(float)
    df_all_bd['count'] = df_all_bd['count'].astype(int)

    df_all_bd['norm_accum_mean_profit'] = df_all_bd['norm_accum_profit'] / df_all_bd['count']
    df_all_bd['norm_cur_mean_profit'] = df_all_bd['norm_cur_profit'] / df_all_bd['count']

    bd_accum = df_all_bd.sort_values('norm_accum_mean_profit', ascending=False)
    bd_cur = df_all_bd.sort_values('norm_cur_mean_profit', ascending=False)
    print('norm_accum_mean_profit')
    print(bd_accum.head(10))
    print('norm_cur_mean_profit')
    print(bd_cur.head(10))
    '''
    if not df_all_bd.empty:
        df_all_bd.to_csv("all-20200101-20230725-board-fromcode.csv", index=False)
    '''

if __name__ == '__main__':
    stat_board_from_board()

