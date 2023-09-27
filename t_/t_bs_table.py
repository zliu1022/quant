#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy  as np

def create_buy_table(interval=0.025, inc_perc=1.1, dec_buy_ratio=5, base_price=100.0):
    num = round(1/interval) + 1

    a = pd.DataFrame({'dec_perc':np.arange(num)*interval}) # 下跌幅度，似乎和 stat_chg 的dec有理解差异
    a.insert(1, 'cur_price',   (1-a.dec_perc) * base_price) # 根据下跌计算的当前价格
    a.insert(2, 'buy_qty',     np.round(np.exp2(np.arange(num)/dec_buy_ratio))*100) # 买入数量
    a.insert(3, 'acum_qty',    a.buy_qty.cumsum()) # hold qty, 累计的、持有数量
    a.insert(4, 'sell_price',  a.cur_price*inc_perc) # 卖出价格
    a.insert(5, 'acum_cost', (a.cur_price*a.buy_qty).cumsum()) # hold cost 持有成本
    a.insert(6, 'profit',      a.sell_price*a.acum_qty-a.acum_cost)

    return a

def bs_table_v1(cost_perc = 0.032, price_perc = 0.0477, row = 10):
    unit_cost      = [100]
    next_buy_price = [100]
    buy_qty        = [100]
    accum_cost     = [100 * 100]  # next_buy_price * buy_qty
    accum_qty      = [100]

    for i in range(1, row):
        unit_cost.append(np.floor(unit_cost[-1] * (1 - cost_perc)*100)/100)
        next_buy_price.append(np.floor(next_buy_price[-1] * (1 - price_perc)*100)/100)

        #new_accum_qty = np.round((accum_cost[-1] - accum_qty[-1] * next_buy_price[-1]) / (unit_cost[-1] - next_buy_price[-1]) / 100) * 100
        new_accum_qty = np.floor((accum_cost[-1] - accum_qty[-1] * next_buy_price[-1]) / (unit_cost[-1] - next_buy_price[-1]) / 100) * 100
        accum_qty.append(new_accum_qty)
        buy_qty.append(new_accum_qty - accum_qty[-2])
        new_accum_cost = sum(np.array(next_buy_price) * np.array(buy_qty))
        accum_cost.append(new_accum_cost)

    a = pd.DataFrame({
        'unit_cost':      unit_cost,
        'next_buy_price': next_buy_price,
        'buy_qty':        buy_qty,
        'accum_cost':     accum_cost,
        'accum_qty':      accum_qty
    })
    return a

def bs_table_v2(first_buy_price=100, first_buy_qty=100, last_accum_cost=0, last_accum_qty=0, cost_perc = -0.032, price_perc = -0.0477, chg_perc=0.55, row = 10):
    chg_mid_perc = (1+chg_perc) ** 0.5

    df = pd.DataFrame()

    df.at[0, 'next_buy_price'] = first_buy_price
    df.at[0, 'buy_qty']        = first_buy_qty
    df.at[0, 'unit_cost']      = df.at[0, 'next_buy_price']
    df.at[0, 'accum_cost'] = df.at[0, 'next_buy_price'] * df.at[0, 'buy_qty'] + last_accum_cost
    df.at[0, 'accum_qty']  = df.at[0, 'buy_qty'] + last_accum_qty

    df.at[0, 'sell_price']  = np.floor(df.at[0, 'next_buy_price'] * (1+chg_perc)*100)/100
    df.at[0, 'profit']      = np.floor(df.at[0, 'sell_price'] * df.at[0, 'accum_qty'] - df.at[0, 'accum_cost'])

    df.at[0, 'sell_price1']  = np.floor(df.at[0, 'next_buy_price'] * (chg_mid_perc)*100)/100
    df.at[0, 'profit1']      = np.floor(df.at[0, 'sell_price1'] * df.at[0, 'accum_qty']/2 - df.at[0, 'accum_cost']/2)
    df.at[0, 'sell_price2']  = np.floor(df.at[0, 'sell_price1'] * (chg_mid_perc)*100)/100
    df.at[0, 'profit2']      = np.floor(df.at[0, 'sell_price2'] * df.at[0, 'accum_qty']/2 - df.at[0, 'accum_cost']/2)

    for i in range(1, row):
        df.at[i, 'unit_cost'] = np.floor(df.at[i-1, 'accum_cost']/df.at[i-1, 'accum_qty'] * (1+cost_perc) *100)/100
        df.at[i, 'next_buy_price'] = np.floor(df.at[i-1, 'next_buy_price'] * (1+price_perc) *100)/100

        df.at[i, 'accum_qty']  = np.floor((df.at[i-1, 'accum_cost'] - df.at[i-1, 'accum_qty'] * df.at[i, 'next_buy_price']) / (df.at[i, 'unit_cost'] - df.at[i, 'next_buy_price']) / 100) * 100
        df.at[i, 'buy_qty']    = df.at[i, 'accum_qty'] - df.at[i-1, 'accum_qty']
        df.at[i, 'accum_cost'] = sum(df['next_buy_price'][:i+1] * df['buy_qty'][:i+1])
        df.at[i, 'sell_price'] = np.floor(df.at[i, 'next_buy_price'] * (1+chg_perc) *100)/100
        df.at[i, 'profit']     = np.floor(df.at[i, 'sell_price'] * df.at[i, 'accum_qty'] - df.at[i, 'accum_cost'])

        df.at[i, 'sell_price1']  = np.floor(df.at[i, 'next_buy_price'] * (chg_mid_perc)*100)/100
        df.at[i, 'profit1']      = np.floor(df.at[i, 'sell_price1'] * df.at[i, 'accum_qty']/2 - df.at[i, 'accum_cost']/2)
        df.at[i, 'sell_price2']  = np.floor(df.at[i, 'sell_price1'] * (chg_mid_perc)*100)/100
        df.at[i, 'profit2']      = np.floor(df.at[i, 'sell_price2'] * df.at[i, 'accum_qty']/2 - df.at[i, 'accum_cost']/2)

    df['buy_qty']    = df['buy_qty'].astype(int)
    df['accum_qty']  = df['accum_qty'].astype(int)
    df['accum_cost'] = df['accum_cost'].astype(int)
    df['profit'] = df['profit'].astype(int)
    df['profit1'] = df['profit1'].astype(int)
    df['profit2'] = df['profit2'].astype(int)
    return df

if __name__ == '__main__':
    #df = create_buy_table(interval=0.05, inc_perc=1.15)
    #df = bs_table_v1(cost_perc = 0.032, price_perc = 0.0477, row = 10)
    df = bs_table_v1(cost_perc = 0.032, price_perc = 0.0477, row = 10)
    print(df.head(3))
    print()

    last_df = pd.DataFrame()
    last_df.at[0, 'next_buy_price'] = 100
    last_df.at[0, 'buy_qty']        = 100
    last_df.at[0, 'unit_cost']      = 100
    last_df.at[0, 'accum_cost']     = 0
    last_df.at[0, 'accum_qty']      = 0
    print(last_df)

    df = bs_table_v2(cost_perc = -0.032, price_perc = -0.0477, row = 10)
    print(df)
    print()
    print(df.iloc[0]['profit'])  # line no
    print(df.iloc[-1]['profit'])  # line no
    print(df.loc[9]['profit'])  # index
    print()
