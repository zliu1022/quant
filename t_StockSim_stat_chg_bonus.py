#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
from StockDraw import draw_example
from StockRecover import recover_price_forward
from StockSim import stat_chg
from StockSim import sim_single_chg_forw
from pprint import pprint
import pandas as pd

def testds_list():
    print('data structure list')
    # trade 记录, chg(change)仅仅记录最低到最高,达到波动要求的改变
    td = [
        {
            'start_date': '2023-01-01',
            'profit': 25.0,
            'buy_records': [
                {'buy_date': '2023-01-01', 'buy_price': 35.0},
                {'buy_date': '2023-02-03', 'buy_price': 45.0},
                {'buy_date': '2023-04-05', 'buy_price': 55.0}
            ]
        },
        {
            'start_date': '2023-01-01',
            'profit': 25.0,
            'buy_records': [
                {'buy_date': '2023-01-01', 'buy_price': 35.0}
            ]
        }
    ]

    print(td[0]['start_date'])                     # 输出: '2023-01-01'
    print(td[1]['buy_records'][0]['buy_date'])     # 输出: '2023-01-01'

    td[0]['profit'] = 30.0
    td[1]['buy_records'][0]['buy_price'] = 40.0

    pprint(td)
    print()
    new_td = {
        'start_date': '2023-01-01',
        'profit': 25.0,
        'buy_records': [
            {'buy_date': '2023-01-01', 'buy_price': 35.0},
            {'buy_date': '2023-02-03', 'buy_price': 45.0}
        ]
    }
    td.append(new_td)
    pprint(td)

def testds_np():
    import numpy as np

    buy_type = np.dtype([
        ('date', 'U10'),
        ('price', float),
        ('qty', float)
    ])

    data_type = np.dtype([
        ('start_date', 'U10'), ('end_date', 'U10'),
        ('profit', float), ('accum_qty', int),
        ('buy_records', buy_type, (3,)),    # 固定为3，可以按照最大个数来定义，没有的数据按照NaN来设置，如果需要灵活，则需要定义成object
        ('min_date', 'U10'), ('min_p', float),
        ('sell_date', 'U10'), ('sell_p', float)
    ])

    data = np.array([
        ('2023-01-01', '2023-06-01',
        180.0, 200,
        [   ('2023-01-01', 35.0, 100),
            ('2023-02-03', 45.0, 100),
            ('2023-04-05', 55.0, 200) ],
        '2023-03-05', 25.0,
        '2023-06-01', 35.0
        )
    ], dtype=data_type)

    print('dtype', data.dtype)
    print()
    print('dtype.names', data.dtype.names) # 结构化数组的属性名称列表
    print()
    print('shape', data.shape) # 返回数组的形状，即每个维度的大小。
    print('size', data.size) #返回数组中的元素总数。
    print('ndim', data.ndim) #返回数组的维度数。
    print('itemsize', data.itemsize) #返回数组中每个元素的字节大小。
    print()
    print('tolist', data.tolist()) #将结构化数组转换为 Python 列表的形式。
    print()
    print('item', data.item()) #将结构化数组视为标量，并返回其 Python 对象表示。
    print()
    pprint(data[0])
    print()
    print(data[0]['start_date'])
    data[0]['start_date'] = '2023-5-15'
    print(data[0]['start_date'])
    print()
    print(data[0]['buy_records'][2])
    print()
    data[0]['buy_records'][2] = ('2023-04-07', 15.0, 500)
    print(data[0]['buy_records'][2])

def testds_pandas():
    import pandas as pd

    # 定义数据
    data = [
        {   'start_date': '2023-01-01',
            'profit': 25.0,
            'buy_records': [
                {'buy_date': '2023-01-01', 'buy_price': 35.0},
                {'buy_date': '2023-02-03', 'buy_price': 45.0},
                {'buy_date': '2023-04-05', 'buy_price': 55.0} ]
        },
        {   'start_date': '2023-01-01',
            'profit': 25.0,
            'buy_records': [
                {'buy_date': '2023-02-03', 'buy_price': 45.0},
                {'buy_date': '2023-04-05', 'buy_price': 55.0} ]
        } ]

    # 将buy_records转换为pandas DataFrame
    df = pd.DataFrame(data)
    print(df)
    print()

    new_data = {
        'start_date': '2023-01-01',
        'profit': 25.0,
        'buy_records': [
            {'buy_date': '2023-02-03', 'buy_price': 45.0},
            {'buy_date': '2023-04-05', 'buy_price': 55.0} ]
        } 
    df = df.append(new_data, ignore_index=True)
    print(df)
    quit()

    # 引用部分数据
    first_buy_date = df.loc[0, 'buy_records'][0]['buy_date']
    first_buy_price = df.loc[0, 'buy_records'][0]['buy_price']

def sim_single(sq, ts_code, start_date, end_date, chg_perc, interval):
    df_day   = sq.query_day_code_date_df(ts_code, start_date, end_date)
    df_bonus = sq.query_bonus_code_df(ts_code)

    for index, row in df_day.iterrows():
        print(index, row['low'], row['high'])
        break

    for row in df_day.itertuples():
        print(row.Index, row.low, row.high)
        break

# 针对code_list，得到chg
# 然后遍历chg, 针对每次chg,查找其时间范围内是否有过XD
# 做这个的目的是为了核对动态除权操作
def stat_chg_bonus(sq, code_list, start_date, end_date, chg_perc, interval):
    for item in code_list:
        ts_code = item['ts_code']

        ret = sq.check_bad_bonus(ts_code)
        if ret != 0:
            continue

        df_day   = sq.query_day_code_date_df(ts_code, start_date, end_date)
        df_bonus = sq.query_bonus_code_df(ts_code)
        if df_day is None:
            continue

        df_forw  = recover_price_forward(df_day, df_bonus)
        df_chg, inc_num, max_dec_perc, max_dec_days = stat_chg(df_forw, start_date, chg_perc)
        chg_len = len(df_chg.index)
        if chg_len == 0:
            print(ts_code, 'chg_len == 0')
            continue

        print(df_chg)

        # 去除最后一行，还在持有，不算chg
        if df_chg.iloc[-1]['max_date'] == '20500101':
            df_chg = df_chg.drop(df_chg.index[-1])
        chg_len = len(df_chg.index)
        max_dec_perc = df_chg['dec_perc'].max()
        if chg_len < 1:
            continue

        # 遍历每一个chg，找其中是否有bonus
        for index, row in df_chg.iterrows():
            s_date = index
            min_date = row['min_date']
            max_date = row['max_date']
            ret = sq.query_bonus_code_date(ts_code, s_date, max_date)
            if len(ret) == 0:
                continue

            len_bonus = len(ret[0]['items'])
            bonus = ret[0]['items']
            if len_bonus > 1:
                print('{} s_date {} {} {} bonus_num {}'.format(ts_code, s_date, min_date, max_date, len_bonus))
                for row in bonus:
                    print(row['date'], row['plan_explain'])
                print()

def print_single(sq, ts_code, start_date, end_date, chg_perc, interval):
    draw_example(ts_code, start_date, end_date, chg_perc)

    df_day   = sq.query_day_code_date_df(ts_code, start_date, end_date) 
    df_bonus = sq.query_bonus_code_df(ts_code)
    print(df_bonus)
    quit()
    df_forw  = recover_price_forward(df_day, df_bonus)
    ret = sim_single_chg_forw(df_forw, start_date, end_date, chg_perc, interval)
    print('hold {} cost {} profit {} dec_perc {}%'.format(
        ret['cur_qty'], ret['max_cost'], ret['profit'], ret['max_dec_perc']
        ))
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None, 'display.max_colwidth', -1):
        print(df_day)
        print()
        print(df_forw)

if __name__ == '__main__':
    #testds_np()
    #testds_pandas()
    #testds_list()

    sq = StockQuery()

    #start_date = '20230101'
    start_date = '20200101'
    end_date   = '20230630'
    chg_perc = 0.55
    interval = 0.03

    # 20230101 - 20230601 期间chg且遇到XD的
    code_list = [
            {'ts_code': '002315.SZ'},
            {'ts_code': '002919.SZ'},
            {'ts_code': '300211.SZ'},
            {'ts_code': '300476.SZ'},
            {'ts_code': '300620.SZ'},
            {'ts_code': '300654.SZ'},
            {'ts_code': '300678.SZ'},
            {'ts_code': '301052.SZ'},
            {'ts_code': '301179.SZ'},
            {'ts_code': '301312.SZ'},
            {'ts_code': '600666.SH'},
            {'ts_code': '688160.SH'}
        ]
    code_list = sq.query_basic(None)
    #stat_chg_bonus(sq, code_list, start_date, end_date, chg_perc, interval)

    # 20200101 - 20230630, 出现过2次chg中含多次XD的，且XD 3次
    code_list = [
            {'ts_code': '002050.SZ'},
            {'ts_code': '002555.SZ'},
            {'ts_code': '601857.SH'},
            {'ts_code': '830799.BJ'}
        ]
    #stat_chg_bonus(sq, code_list, start_date, end_date, chg_perc, interval)

    # 830799.BJ s_date 20200420 20200915 20210519 bonus_num 3
    # 830799.BJ s_date 20210520 20220427 20220615 bonus_num 2
    # 第一个竟然失败了
    # 当时间范围在 20200101 进行前复权时，20210519可以卖出
    # 时间范围到 20200420 时卖出失败
    ts_code = '830799.BJ'
    start_date = '20200408' # 当调节到0408，前面到是出现了次chg, 最后一次还是没卖出
    start_date = '20200420'
    end_date   = '20210519'
    #print_single(sq, ts_code, start_date, end_date, chg_perc, interval)
    start_date = '20210520'
    end_date   = '20220615'
    #print_single(sq, ts_code, start_date, end_date, chg_perc, interval)

    # 数列A，进行 (a * A - b) / c, 得到数列B, 也可能有过多次这个操作
    # 数列B的 B2 = B1 * 1.55, 但对应位置的 A2 < A1 * 1.55
    '''
    601857.SH s_date 20200102 20201029 20210914 bonus_num 3
    20210629 10派0.8742元(实施方案)
    20200922 10派0.8742元(实施方案)
    20200630 10派0.6601元(实施方案)

    601857.SH s_date 20210915 20211129 20230412 bonus_num 3
    20220920 10派2.0258元(实施方案)
    20220628 10派0.9622元(实施方案)
    20210917 10派1.3040元(实施方案)

    601857.SH s_date 20200102 20201029 20210914 bonus_num 3
    20210629 10派0.8742元(实施方案)
    20200922 10派0.8742元(实施方案)
    20200630 10派0.6601元(实施方案)

    601857.SH s_date 20210915 20211129 20230412 bonus_num 3
    20220920 10派2.0258元(实施方案)
    20220628 10派0.9622元(实施方案)
    20210917 10派1.3040元(实施方案)
    '''
    ts_code = '601857.SH'
    start_date = '20200102' # 卖出失败
    end_date   = '20210914'
    #print_single(sq, ts_code, start_date, end_date, chg_perc, interval)
    start_date = '20210915'
    end_date   = '20230412'
    #print_single(sq, ts_code, start_date, end_date, chg_perc, interval)
    start_date = '20200102' # 卖出失败
    end_date   = '20210914'
    #print_single(sq, ts_code, start_date, end_date, chg_perc, interval)
    start_date = '20210915'
    end_date   = '20230412'
    #print_single(sq, ts_code, start_date, end_date, chg_perc, interval)

    '''
    002555.SZ s_date 20200615 20210831 20211029 bonus_num 2
    20210818 10派2元(实施方案)
    20200925 10派3元(实施方案)
    002555.SZ s_date 20211101 20221025 20230130 bonus_num 3
    20220926 10派3.5元(实施方案)
    20220527 10派3.7元(实施方案)
    20211109 10派1.5元(实施方案)
    '''
    ts_code = '002555.SZ'
    start_date = '20200615' # 卖出失败
    end_date   = '20211029'
    #print_single(sq, ts_code, start_date, end_date, chg_perc, interval)
    start_date = '20211101'
    end_date   = '20230130'
    #print_single(sq, ts_code, start_date, end_date, chg_perc, interval)

    '''
    002050.SZ s_date 20200708 20220425 20220610 bonus_num 3
    20220511 10派1.50元(实施方案)
    20210512 10派2.50元(实施方案)
    20200916 10派1元(实施方案)

    002050.SZ s_date 20220728 20221020 20230619 bonus_num 2
    20230609 10派2元(实施方案)
    20220922 10派1.00元(实施方案)
    '''
    # 都成功了
    ts_code = '002050.SZ'
    start_date = '20200708'
    end_date   = '20220610'
    #print_single(sq, ts_code, start_date, end_date, chg_perc, interval)
    start_date = '20220728'
    end_date   = '20230619'
    print_single(sq, ts_code, start_date, end_date, chg_perc, interval)

    ts_code = '002050.SZ'
    start_date = '20200708'
    end_date   = '20220610'
    #sim_single(sq, ts_code, start_date, end_date, chg_perc, interval)

