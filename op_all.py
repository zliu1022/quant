#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient, ASCENDING, UpdateOne
from StockOp_v1 import StockOp, show_stat
from Utils import RecTime
from pprint import pprint

if __name__ == '__main__':
    start_date = '20200301'
    end_date   = '20250331'
    chg_perc   = 1.55
    interval   = 0.03

    client = MongoClient('mongodb://localhost:27017/')  # Adjust the connection string as needed
    db = client['stk1']
    collection_basic = db['basic']

    collection_name = f"{start_date}_{end_date}_{chg_perc}"
    collection_stat = db[collection_name]
    collection_stat.create_index('ts_code', unique=True)

    documents = collection_basic.find().sort('ts_code', ASCENDING)

    bulk_operations = []
    begin_status = False
    rt = RecTime()
    for doc in documents:
        ts_code = doc['ts_code']
        print(doc['ts_code'], doc['name'], doc['industry'], end=' ')
        so = StockOp(ts_code)
        df_stat = so.Op(chg_perc, interval=interval, start_date=start_date, end_date=end_date, debug=0)
        if df_stat is None:
            continue
        ret_stat = show_stat(ts_code, start_date, end_date, chg_perc, interval, df_stat)
        ret_cur = so.show_cur()

        ret_stat['name'] = doc['name']
        ret_stat['industry'] = doc['industry']
        ret_stat['cur_profit'] = ret_cur['cur_profit']
        ret_stat['norm_cur_profit'] = ret_cur['norm_cur_profit']
        ret_stat['cur_cost'] = ret_cur['cur_cost']

        bulk_operations.append(
            UpdateOne(
                {'ts_code': ret_stat['ts_code']},  # 查询条件，根据 ts_code 匹配
                {'$set': ret_stat},  # 更新内容，直接设置为新的数据
                upsert=True  # 如果不存在则插入
            )
        )
    rt.show_s()

    if bulk_operations:
        # 批量更新到数据库
        result = collection_stat.bulk_write(bulk_operations)
        print(f"Bulk write result: {len(result.bulk_api_result)}")
    else:
        print("No operations to perform.")
