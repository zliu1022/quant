#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
from StockDraw import recover_price_forward

if __name__ == '__main__':
    sq = StockQuery()

    ts_code    = '002475.SZ'
    #start_date = '20220101'
    #end_date   = '20230526'

    ref = sq.query_day_code(ts_code)
    start_date = ref[len(ref)-1]['date']
    end_date = ref[0]['date']
    #format dict_keys(['date', 'volume', 'open', 'high', 'low', 'close', 'chg', 'percent', 'turnoverrate', 'amount'])
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

    d0 = ref[0]
    d1 = ref[1]
    '''
    涨幅3到5%:        OK
    量比＞1:          OK
    换手率5到10%:     OK
    市值50到200亿:    OK
    成交量持续放大:   OK
    价格历史新高:     复权OK，求历史最高价格OK, 需要看是哪个价格open/close/high/low
    热点题材板块:     NOK, 哪里可以获取热点题材
    分时价格涨速超过上证指数: 可以修正为日涨速
    下午出现当日新高: NOK
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
    print(df_stat['close']['max'])
    print(df_stat['close']['average'])
