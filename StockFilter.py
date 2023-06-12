#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
from Utils import RecTime
import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient

client = MongoClient(port=27017)
db = client.stk1
db.drop_collection('mktvalue')
col_mktvalue = db.mktvalue

def filter_mktvalue(start_date, end_date):
    rt = RecTime()
    df_stat    = pd.DataFrame()

    sq = StockQuery()
    ref = sq.query_basic(None)
    #print('Found {:4d}'.format(len(ref)))

    for item in ref:
        ts_code = item['ts_code']
        ret = sq.check_bad_bonus(ts_code)
        if ret != 0:
            continue

        ref = sq.query_basic(ts_code)
        #print(ref[0].items())
        info=ref[0]

        ref = sq.query_day_code_date(ts_code, start_date, end_date)
        # 日线数据第一个最近, 得到最近一天和次近一天
        if ref == None:
            print('{} {} {} {} null'.format(ts_code, info['name'], info['industry'], info['list_date']))
            continue

        d0 = ref[0]
        if d0['turnoverrate'] == 0:
            print('{} {} {} {} turnoverrate==0'.format(ts_code, info['name'], info['industry'], info['list_date']))
            continue
        mktvalue = round((d0['volume']/(d0['turnoverrate']/100.0) * d0['close']) / 100000000.0, 2)
        print('{} {} {} {} {:.2f} 亿元 ({})'.format(ts_code, info['name'], info['industry'], info['list_date'], mktvalue, d0['date']))

        new_dic = {
            'ts_code':ts_code, 
            'name':   info['name'],
            'mktvalue':mktvalue, 
            'date':d0['date']
            }
        col_mktvalue.insert_one(new_dic)

        df_item = pd.DataFrame([{
                'ts_code':     ts_code,
                'name':        info['name'],
                'industry':    info['industry'],
                'list_date':   info['list_date'],
                'mktvalue':    mktvalue
            }])
        df_stat = pd.concat([df_stat, df_item]).reset_index(drop=True)

    title_str = 'mktvalue'
    df_stat.to_csv(title_str + '.csv', index=False)

    rt.show_s()
    return df_stat

def draw_mktvalue_fromfile():
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np

    df_stat    = pd.DataFrame()

    title_str = 'mktvalue'

    #df_stat.to_csv(title_str + '.csv', index=False)
    df_stat = pd.read_csv(title_str + '.csv')
    column = df_stat.mktvalue

    bins = [0, 10, 20, 50, 100, 200, 500, 1000, np.inf]  # 定义分组范围
    grouped_data = pd.cut(column, bins) # 对数据进行分组
    counts = grouped_data.value_counts() # 计算每个范围内的数量
    print("分组统计结果：")
    print(counts)

    fig = plt.figure()
    ax1 = fig.add_axes([0.1, 0.1,  0.8, 0.8])
    ax1.hist(column, bins=500, log=True)
    ax1.set_title(title_str)
    plt.savefig(title_str + '.png', dpi=150)
    plt.show()

# 筛选指定条件的code，存储到单独的collection中，后续通过不同条件select出来
if __name__ == '__main__':
    start_date = '20200101'
    end_date   = '20200115'
    #filter_mktvalue(start_date, end_date)

    draw_mktvalue_fromfile()
