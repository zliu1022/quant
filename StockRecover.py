#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Utils import RecTime
import math

# Recover Price Backward, first date price is baseline
# input: df, df_bonus
# return: df_back
def recover_price_backward(df_in, df_bonus):
    rt = RecTime()
    df = df_in.copy()
    day_len = len(df.index)
    first_date = df.index[0]
    for i in range(day_len):
        #print('{} {:7.2f} {:7.2f}'.format(df.index[i], df.low[i], df.high[i]), end='')

        # 后复权，则以开始日价格为基准，除权日晚于开始日, 早于当前日，当日价格需要复权
        # 开始日 <= 除权日 <= 当前日，除权日当日也需要复权
        ret = df_bonus[df_bonus.index>=first_date]
        ret = ret[ret.index<=df.index[i]]
        if ret.empty == True:
            #print()
            continue
        bonus_len = len(ret.index)
        #print(' {:2d} ex-d'.format(bonus_len), end='')

        high = df.high[i]
        low = df.low[i]
        for j in range(bonus_len):
            base = float(ret.base[j])
            free = float(ret.free[j])
            new = float(ret.new[j])
            bonus = float(ret.bonus[j])

            high = round((high * (base+free+new) + bonus)/base, 2)
            low = round((low * (base+free+new) + bonus)/base, 2)

        df.high[i] = high
        df.low[i] = low
        #print(' -> {:7.2f} {:7.2f}'.format(low, high))

    #df_back = df.copy()
    #sd.draw_df(ts_code+'-back', df_back)
    rt.show_ms()
    return df

# forward recover ex-dividend, baseline is last date price
# input: df, df_bonus
# return: df_back
# 对 open,close,high,low 进行复权，对amount交易金额, volume交易股数不复权
# bonus中的日期就是这天的开盘价已经经过除权调整，所以前复权会修改这个日期前一天的价格
# 例如：bonus中002475.SZ 日期 2022-7-13，前复权不动7-13数据，7-12数据会修改
def recover_price_forward(df_in, df_bonus):
    rt = RecTime()

    df = df_in.copy()
    day_len = len(df.index)
    if day_len == 0:
        return df
    if df_bonus.empty == True:
        return df

    last_date = df.index[day_len-1]
    #print('recover_price_forward {} - {}'.format(df.index[0], last_date))
    #print('date          open      low       high     close  no.    ->      open       low      high     close')
    for i in range(day_len):
        ret = df_bonus[df_bonus.index<=last_date]
        ret = ret[ret.index>df.index[i]]
        if ret.empty == True:
            #print('{} {:9.2f} {:9.2f} {:9.2f} {:9.2f}'.format(df.index[i], df.open[i], df.low[i], df.high[i], df.close[i]), end='')
            #print()
            continue
        #print(ret)

        #print('{} {:9.2f} {:9.2f} {:9.2f} {:9.2f}'.format(df.index[i], df.open[i], df.low[i], df.high[i], df.close[i]), end='')

        high = df.high[i]
        low = df.low[i]
        p_open = df.open[i]
        close = df.close[i]
        bonus_len = len(ret.index)
        #print(' {:2d} ex-d'.format(bonus_len), end='')

        for j in range(bonus_len):
            base = float(ret.base[j])
            free = float(ret.free[j])
            new = float(ret.new[j])
            bonus = float(ret.bonus[j])

            high = (high * base - bonus)/(base + free + new)
            low = (low * base - bonus)/(base + free + new)
            p_open = (p_open * base - bonus)/(base + free + new)
            close = (close * base - bonus)/(base + free + new)

        # 截取小数点用的方式竟然还不一样，应该是错了，ceil是取更大的值，floor是取更小的值, 修改为四舍五入
        '''
        df.high[i] = math.floor(high*100)/100
        df.low[i] = math.ceil(low*100)/100
        df.open[i] = math.ceil(p_open*100)/100
        df.close[i] = math.ceil(close*100)/100
        '''
        df.high[i] = round(high*100)/100
        df.low[i] = round(low*100)/100
        df.open[i] = round(p_open*100)/100
        df.close[i] = round(close*100)/100
        #print(' -> {:9.3f} {:9.3f} {:9.3f} {:9.3f}'.format(df.open[i], df.low[i], df.high[i], df.close[i]))

    rt.show_ms()
    return df

if __name__ == '__main__':
    exit()

