#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
from Utils import RecTime
import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient
from StockDraw import recover_price_forward

client = MongoClient(port=27017)
db = client.stk1
db.drop_collection('mktvalue')
col_mktvalue = db.mktvalue

def filter_single_example():
    sq = StockQuery()

    ts_code    = '002475.SZ'

    ref = sq.query_day_code(ts_code)

    # 获取日线数据的真实开始、结束日期
    start_date = ref[len(ref)-1]['date']
    end_date = ref[0]['date']

    #format dict_keys(['date', 'volume', 'open', 'high', 'low', 'close', 'chg', 'percent', 'turnoverrate', 'amount'])
    # 对每一个日线数据进行说明
    for i in range(2):
        for k in ref[0].keys():
            d = ref[i][k]
            if k == 'amount':
                print(k, '      成交金额', d, '元', round(d/100000000,2), '亿元')
            elif k == 'volume':
                print(k, '      成交量', d, '股', round(d/100/10000,2), '手')
            elif k == 'turnoverrate':
                print(k, '换手率', d, '%', '成交量/流通股数，推算流通股：', round(ref[i]['volume']/(d/100)/100000000, 2), '亿股，自由流通股比流通股少一些')
            elif k == 'percent':
                print(k, '     变化率', d, '%', '今天close和昨天close相比变化百分比，推算昨天close：', round(ref[i]['close']/(1+d/100), 2))
            elif k == 'chg':
                print(k, '         价格变化', d, '今天close和昨天close相比较，变化数值，推算昨天close：', ref[i]['close'] + d)
            else:
                print(k, ref[i][k])
        print()
    print()

    # 日线数据第一个最近, 得到最近一天和次近一天
    d0 = ref[0]
    d1 = ref[1]

    # 下面是一个常人容易想到的筛选方式
    # 一个是验证下符合下面的股票不存在，另一个验证我的想法就是价格的波动和这些都没有关系
    '''
    涨幅3到5%:        OK, 蜡烛线有各种阶梯数据，考虑收盘数据作为对比
    量比＞1:          OK, 量比指分钟级别成交股票数量相比于5天平均值，可以考虑按天               从日线计算得到5日均线;需要思考从日线的量能否看出有大单,有大单是否就会涨
    换手率5到10%:     OK
    市值50到200亿:    OK, 采用换手率来反推
    成交量持续放大:   OK, 指成交的股票数量
    价格历史新高:     OK, 复权后的历史最高价格，也考虑收盘价
    热点题材板块:     NOK                                                                       哪里可以获取热点题材
    分时价格涨速超过上证指数: 可以修正为日涨速，就是涨幅百分比；                                上证指数怎么获得
    下午出现当日新高: NOK, 也就是high这个点出现在下午，这个日线没有
    '''

    '涨幅：delta_close,  delta_high,  delta_low, delta_avgp'
    delta_close = d0['close'] - d1['close']
    delta_high  = d0['high']  - d1['high']
    delta_low   = d0['low']   - d1['low']
    delta_avgp  = d0['amount']/d0['volume'] - d1['amount']/d1['volume']
    print('delta_close {:.2f}'.format(delta_close))
    print('delta_high  {:.2f}'.format(delta_high))
    print('delta_low   {:.2f}'.format(delta_low))
    print('delta_avgp  {:.2f}'.format(delta_avgp))

    '量比：ratio_amount, ratio_volume'
    ratio_amount = d0['amount'] / d1['amount']
    ratio_volume = d0['volume'] / d1['volume']
    print('ratio_amount  {:.2f}'.format(ratio_amount))
    print('ratio_volume  {:.2f}'.format(ratio_volume))

    '市值'
    d0_mktvalue = d0['volume']/(d0['turnoverrate']/100) * d0['close']
    d1_mktvalue = d1['volume']/(d1['turnoverrate']/100) * d1['close']
    print('d0_mktvalue  {:.2f} 亿元'.format(d0_mktvalue/100000000))
    print('d1_mktvalue  {:.2f} 亿元'.format(d1_mktvalue/100000000))
    print()

    # 检查复权数据，amount不复权
    df_day   = sq.query_day_code_date_df(ts_code, start_date, end_date)
    df_bonus = sq.query_bonus_code_df(ts_code)
    df_forw  = recover_price_forward(df_day, df_bonus)
    df_stat = df_forw.agg({
        'open': ['min','max','average'],
        'high': ['min','max','average'],
        'low': ['min','max','average'],
        'close': ['min','max','average']
        })
    print('{:.2f}'.format(df_stat['close']['max']))
    print('{:.2f}'.format(df_stat['close']['average']))

    ref = sq.query_basic(ts_code)
    print(len(ref))
    print(ref[0].keys())
    print(ref[0].items())
    for item in ref:
        ts_code = item['ts_code']
        list_date = item['list_date']
        if list_date < start_date:
            sq.check_day(ts_code, start_date, end_date)
        else:
            sq.check_day(ts_code, list_date, end_date)
    print()


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

    filter_single_example()

    #filter_mktvalue(start_date, end_date)
    #draw_mktvalue_fromfile()
