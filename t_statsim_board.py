#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import pandas as pd
from pprint import pprint

df_all_code = pd.read_csv("all-20200101-20230717.csv")

client = MongoClient('mongodb://localhost:27017/')
db = client.ak_board
col_bdinfo = db.bdinfo
col_bdlist = db.bdlist

df_all_bd = pd.DataFrame(columns=['board_code', 'name', 'num', 'norm_accum_profit', 'norm_cur_profit', 'count'])

for index, row in df_all_code.iterrows():
    code = row['code']
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

# 还可以另外一种遍历
# 先遍历板块 bdlist
#ref = db.bdlist.find()
# 再找板块对应的 code, bdinfo
#ref = db.bdinfo.find({'板块代码': board_code})
# 再到df_all_code 里面找
