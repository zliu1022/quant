#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy  as np
import sys

import matplotlib.pyplot as plt

import math
def round_up(number):
    #if np.isinf(number): return -1
    if number > 0:
        return math.floor(number + 0.5)
    elif number < 0:
        # 负数的处理方式不同，需要使用math.ceil
        return math.ceil(number - 0.5)
    else:
        return 0

def create_buy_table(interval=0.025, inc_perc=1.1, dec_buy_ratio=5, base_price=100.0):
    num = round(1/interval) + 1 + 10

    a = pd.DataFrame({'dec_perc':np.arange(num)*interval}) # 下跌幅度，似乎和 stat_chg 的dec有理解差异
    a.insert(1, 'cur_price',   (1-a.dec_perc) * base_price) # 根据下跌计算的当前价格
    a.insert(2, 'buy_qty',     np.round(np.exp2(np.arange(num)/dec_buy_ratio))*100) # 买入数量
    a.insert(3, 'acum_qty',    a.buy_qty.cumsum()) # hold qty, 累计的、持有数量
    a.insert(4, 'sell_price',  a.cur_price*inc_perc) # 卖出价格
    a.insert(5, 'accum_cost', (a.cur_price*a.buy_qty).cumsum()) # hold cost 持有成本
    a.insert(6, 'profit',      a.sell_price*a.acum_qty-a.accum_cost)

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

def bs_table_v2(last_df, cost_perc = -0.032, price_perc = -0.0477, chg_perc=0.55, row = 10):
    price_perc = round(price_perc,4)
    cost_perc = round(cost_perc,4)
    last_buy_price = last_df.at[0, 'next_buy_price']
    last_accum_cost = last_df.at[0, 'accum_cost']
    last_accum_qty  = last_df.at[0, 'accum_qty']

    #chg_mid_perc = (1+chg_perc) ** 0.5
    chg_mid_perc = 1.245

    df = pd.DataFrame()

    if last_accum_qty == 0:
        df.at[0, 'next_buy_price'] = last_buy_price
        df.at[0, 'unit_cost']      = df.at[0, 'next_buy_price']
        df.at[0, 'accum_qty']      = last_df.at[0, 'buy_qty']
        df.at[0, 'buy_qty']        = df.at[0, 'accum_qty']
        df.at[0, 'accum_cost']     = df.at[0, 'next_buy_price'] * df.at[0, 'buy_qty']
    else:
        df.at[0, 'next_buy_price'] = np.floor(last_buy_price * (1+price_perc) *100)/100
        df.at[0, 'unit_cost']      = np.floor(last_accum_cost/last_accum_qty * (1+cost_perc) *100)/100

        if df.at[0, 'unit_cost'] == df.at[0, 'next_buy_price']:
            print(df.at[0, 'unit_cost'], df.at[0, 'next_buy_price'])
            return None
        #df.at[0, 'accum_qty']      = np.floor((last_accum_cost - last_accum_qty * df.at[0, 'next_buy_price']) / (df.at[0, 'unit_cost'] - df.at[0, 'next_buy_price']) / 100) * 100
        df.at[0, 'accum_qty']      = np.round((last_accum_cost - last_accum_qty * df.at[0, 'next_buy_price']) / (df.at[0, 'unit_cost'] - df.at[0, 'next_buy_price']) ,-2)
        #df.at[0, 'accum_qty']      = np.ceil((last_accum_cost - last_accum_qty * df.at[0, 'next_buy_price']) / (df.at[0, 'unit_cost'] - df.at[0, 'next_buy_price'])/100)*100
        if df.at[0, 'accum_qty'] <=0: return None

        df.at[0, 'buy_qty']        = df.at[0, 'accum_qty'] - last_accum_qty
        df.at[0, 'accum_cost']     = df.at[0, 'next_buy_price'] * df.at[0, 'buy_qty'] + last_accum_cost

    sell_qty = (df.at[0, 'accum_qty'] / 2) // 100 * 100
    remain_qty = df.at[0, 'accum_qty'] - sell_qty

    df.at[0, 'sell_price']  = np.floor(df.at[0, 'next_buy_price'] * (1+chg_perc)*100)/100
    df.at[0, 'profit']      = np.floor(df.at[0, 'sell_price'] * df.at[0, 'accum_qty'] - df.at[0, 'accum_cost']) + last_df.at[0, 'profit1']

    df.at[0, 'sell_price1']  = np.floor(df.at[0, 'next_buy_price'] * (chg_mid_perc)*100)/100
    df.at[0, 'sell_qty1']    = sell_qty
    df.at[0, 'profit1']      = np.floor(df.at[0, 'sell_price1'] * sell_qty   - df.at[0, 'accum_cost']*sell_qty/df.at[0, 'accum_qty']) + last_df.at[0, 'profit1']
    df.at[0, 'sell_price2']  = np.floor(df.at[0, 'sell_price1'] * (chg_mid_perc)*100)/100
    df.at[0, 'sell_qty2']    = remain_qty
    df.at[0, 'profit2']      = np.floor(df.at[0, 'sell_price2'] * remain_qty - df.at[0, 'accum_cost']*remain_qty/df.at[0, 'accum_qty'])

    for i in range(1, row):
        df.at[i, 'next_buy_price'] = np.floor(df.at[i-1, 'next_buy_price'] * (1+price_perc) *100)/100
        df.at[i, 'unit_cost']      = np.floor(df.at[i-1, 'accum_cost']/df.at[i-1, 'accum_qty'] * (1+cost_perc) *100)/100

        if df.at[i, 'unit_cost'] == df.at[i, 'next_buy_price']:
            print(df.at[i, 'unit_cost'], df.at[i, 'next_buy_price'])
            return None
        #df.at[i, 'accum_qty']      = np.floor((df.at[i-1, 'accum_cost'] - df.at[i-1, 'accum_qty'] * df.at[i, 'next_buy_price']) / (df.at[i, 'unit_cost'] - df.at[i, 'next_buy_price']) / 100) * 100
        #df.at[i, 'accum_qty']      = np.round((df.at[i-1, 'accum_cost'] - df.at[i-1, 'accum_qty'] * df.at[i, 'next_buy_price']) / (df.at[i, 'unit_cost'] - df.at[i, 'next_buy_price']), -2 )
        df.at[i, 'accum_qty']      = round_up((df.at[i-1, 'accum_cost'] - df.at[i-1, 'accum_qty'] * df.at[i, 'next_buy_price']) / (df.at[i, 'unit_cost'] - df.at[i, 'next_buy_price'])/100.0)*100
        #df.at[i, 'accum_qty']      = np.ceil((df.at[i-1, 'accum_cost'] - df.at[i-1, 'accum_qty'] * df.at[i, 'next_buy_price']) / (df.at[i, 'unit_cost'] - df.at[i, 'next_buy_price'])/100)*100
        if df.at[i, 'accum_qty'] <=0: return None

        df.at[i, 'buy_qty']        = df.at[i, 'accum_qty'] - df.at[i-1, 'accum_qty']
        df.at[i, 'accum_cost']     = df.at[i, 'next_buy_price'] * df.at[i, 'buy_qty'] + df.at[i-1, 'accum_cost']

        df.at[i, 'sell_price'] = np.floor(df.at[i, 'next_buy_price'] * (1+chg_perc) *100)/100

        sell_qty = (df.at[i, 'accum_qty'] / 2) // 100 * 100
        remain_qty = df.at[i, 'accum_qty'] - sell_qty

        df.at[i, 'sell_price1']  = np.floor(df.at[i, 'next_buy_price'] * (chg_mid_perc)*100)/100
        df.at[i, 'sell_qty1']    = sell_qty
        df.at[i, 'sell_price2']  = np.floor(df.at[i, 'sell_price1'] * (chg_mid_perc)*100)/100
        df.at[i, 'sell_qty2']    = remain_qty

        if last_accum_qty == 0:
            df.at[i, 'profit']       = np.floor(df.at[i, 'sell_price'] * df.at[i, 'accum_qty'] - df.at[i, 'accum_cost'])
            df.at[i, 'profit1']      = np.floor(df.at[i, 'sell_price1'] * sell_qty   - df.at[i, 'accum_cost']*sell_qty/df.at[i, 'accum_qty'])
            df.at[i, 'profit2']      = np.floor(df.at[i, 'sell_price2'] * remain_qty - df.at[i, 'accum_cost']*remain_qty/df.at[i, 'accum_qty'])
        else:
            df.at[i, 'profit']     = np.floor(df.at[i, 'sell_price'] * df.at[i, 'accum_qty'] - df.at[i, 'accum_cost']) + last_df.at[0, 'profit']

            df.at[i, 'profit1']      = np.floor(df.at[i, 'sell_price1'] * sell_qty   - df.at[i, 'accum_cost']*sell_qty/df.at[i, 'accum_qty']) + last_df.at[0, 'profit1']
            df.at[i, 'profit2']      = np.floor(df.at[i, 'sell_price2'] * remain_qty - df.at[i, 'accum_cost']*remain_qty/df.at[i, 'accum_qty'])

    df['buy_qty']    = df['buy_qty'].astype(int)
    df['accum_qty']  = df['accum_qty'].astype(int)
    df['accum_cost'] = df['accum_cost'].astype(int)
    df['profit']     = df['profit'].astype(int)
    df['sell_qty1']  = df['sell_qty1'].astype(int)
    df['profit1']    = df['profit1'].astype(int)
    df['sell_qty2']  = df['sell_qty2'].astype(int)
    df['profit2']    = df['profit2'].astype(int)
    return df

if __name__ == '__main__':
    # 第一类买表：分次买入，以第一次买入为梯度，买入量为指数，1次卖出
    df1 = create_buy_table(interval=0.03, inc_perc=1.55)
    #print(df1.head(23))
    print('{:.2f} {:.0f} {:.0f}'.format(df1.loc[22, 'cur_price'], df1.loc[22, 'accum_cost'], df1.loc[22, 'profit']))

    # 第二类买表：分次买入，以上一次买入为梯度，压低持有成本来确定买入量，2次卖出
    #df = bs_table_v1(cost_perc = 0.032, price_perc = 0.0477, row = 10)
    #print(df.head(3))
    #print()

    first_df = pd.DataFrame()
    first_df.at[0, 'next_buy_price'] = 100
    first_df.at[0, 'buy_qty']        = 100
    first_df.at[0, 'accum_cost']     = 0
    first_df.at[0, 'accum_qty']      = 0
    first_df.at[0, 'profit1']        = 0
    #print(first_df)

    #df = bs_table_v2(first_df, cost_perc = -0.032, price_perc = -0.0477, row = 50)
    #df = bs_table_v2(first_df, cost_perc = -0.0291, price_perc = -0.0477, row = 50)
    #df2 = df
    #print(df.head(23))

    # 为了单独核对某个参数的输出
    # 4.69/100 传入函数后，变成0.04690000004，导致误差
    # 2.83, 4.69 存在极值 743k 14k
    '''
    u = 2.83 #2.91
    v = 4.69 #4.77
    df2 = bs_table_v2(first_df, cost_perc = -1*u/100, price_perc = -1*v/100, row = 50)
    if df2 is None: quit()
    abs_difference = abs(df2['next_buy_price'] - 34)
    min_diff_row = abs_difference.idxmin()
    print(min_diff_row)
    print('{:.2f} {:.2f} {:.2f} {:.0f} {:.0f}'.format(u, v, df2.loc[min_diff_row, 'next_buy_price'], df2.loc[min_diff_row, 'accum_cost'], df2.loc[min_diff_row, 'profit']))
    print(df2)
    quit()
    '''

    data_arr = []
    #for u in np.arange(1.41, 3.7, 0.01):
    for u in np.arange(1, 5, 0.01): # center: 3.2%
        u = round(u,4)
        print(u)
        #for v in np.arange(3.8, 5.7, 0.01):
        for v in np.arange(3, 7, 0.01): # center: 4.77%
            v = round(v,4)
            if u == v: continue
            df2 = bs_table_v2(first_df, cost_perc = -1*u/100, price_perc = -1*v/100, row = 50)
            if df2 is None: 
                print('df2 is None u = ', u, 'v = ', v)
                continue
            abs_difference = abs(df2['next_buy_price'] - 34)
            min_diff_row = abs_difference.idxmin()
            #print(min_diff_row)
            #print('{:.2f} {:.2f} {:.2f} {:.0f} {:.0f}'.format(u, v, df2.loc[min_diff_row, 'next_buy_price'], df2.loc[min_diff_row, 'accum_cost'], df2.loc[min_diff_row, 'profit']))
            data_arr.append(( u, v, df2.loc[min_diff_row, 'accum_cost'], df2.loc[min_diff_row, 'profit'], df2.loc[min_diff_row, 'next_buy_price'] ))

    columns = ['cost_perc', 'price_perc', 'accum_cost', 'profit', 'next_buy_price']
    df_draw = pd.DataFrame(data_arr, columns=columns)
    df_draw.to_csv("./bs_table_cost_price.csv", index=False)

    quit()
    print()

    df1['profit_rate'] = (df1['profit'] / df1['accum_cost']) * 100
    df2['profit_rate'] = (df2['profit'] / df2['accum_cost']) * 100

    df1.loc[35:, 'cur_price'] = None
    df1.loc[42:, 'accum_cost'] = None
    df1.loc[35:, 'profit_rate'] = None

    df1 = df1.iloc[:23, :]
    df2 = df2.iloc[:23, :]

    plt.figure()
    plt.scatter(df1.index, df1['cur_price'],      color='blue', label='buy_price_v1', s=10)
    plt.scatter(df2.index, df2['next_buy_price'], color='red',  label='buy_price_v2', s=10)
    plt.axhline(y=0, color='orange', linestyle='--', label='Y=0')
    #plt.xticks(ticks=range(0, 101, 5))
    plt.gca().xaxis.set_minor_locator(plt.MultipleLocator(5))
    plt.grid(which='both', axis='x')
    plt.grid(which='both', axis='y')
    plt.legend()
    plt.title('buy num - buy price')
    plt.xlabel('num')
    plt.ylabel('price')
    plt.show()

    plt.scatter(df1.index, df1['accum_cost'],  color='blue', label='accum_cost_v1', s=10)
    plt.scatter(df2.index, df2['accum_cost'], color='red',  label='accum_cost_v2',  s=10)
    plt.axhline(y=0, color='orange', linestyle='--', label='Y=0')
    plt.gca().xaxis.set_minor_locator(plt.MultipleLocator(5))
    plt.grid(which='both', axis='x')
    plt.grid(which='both', axis='y')
    plt.legend()
    plt.title('buy num - accum cost')
    plt.xlabel('num')
    plt.ylabel('accum cost')
    plt.show()

    df1 = df1.iloc[:31, :]
    df2 = df2.iloc[:31, :]
    fig, ax1 = plt.subplots()
    # Plotting accum_cost and accum_cost as bar chart on the left y-axis
    ax1.set_xlabel('buy num')
    ax1.set_ylabel('accum_cost', color='tab:blue')
    ax1.bar(df1.index, df1['accum_cost'], width=0.2, color='tab:red',  label='accum_cost_v1')
    ax1.bar(df2.index + 0.2, df2['accum_cost'], width=0.2, color='tab:blue', alpha=0.6, label='accum_cost_v2')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.axhline(0, color='blue', linestyle='--', linewidth=1)

    # Creating a secondary y-axis to plot the profit_rate
    ax2 = ax1.twinx()
    ax2.set_ylabel('Profit Rate (%)', color='tab:red')
    ax2.plot(df1.index, df1['profit_rate'], color='tab:orange', marker='o', markersize=1, label='profit_rate_v1')
    ax2.plot(df2.index, df2['profit_rate'], color='tab:green',  marker='s', markersize=1, linestyle='--', label='profit_rate_v2')
    ax2.tick_params(axis='y', labelcolor='tab:red')
    ax2.axhline(0,   color='blue', linestyle='--', linewidth=1, label='Y=0')
    ax2.axhline(-25, color='blue', linestyle='--', linewidth=1, label='Y=-25')

    # Adding title and legend
    plt.title('buy num - accum_cost and profit_ratio')
    fig.tight_layout()
    ax1.legend(loc='lower left', bbox_to_anchor=(0, 0))
    ax2.legend(loc='lower left', bbox_to_anchor=(0, 0.15))
    plt.grid(True)

    plt.show()

    quit()
    plt.gca().invert_xaxis()  # Invert x-axis

    last_df = pd.DataFrame()
    last_df.at[0, 'next_buy_price'] = 100
    last_row = int(sys.argv[1])
    ret_list = []
    for i in range(1, 5):
        sell_qty = (df.iloc[last_row]['accum_qty'] / 2) // 100 * 100
        remain_qty = df.iloc[last_row]['accum_qty'] - sell_qty

        print(last_df.at[0, 'next_buy_price'], '->', df.iloc[last_row]['next_buy_price'], '->', df.iloc[last_row]['sell_price1'], '*', sell_qty, 'profit1', df.iloc[last_row]['profit1'], 'profit2', df.iloc[last_row]['profit2'])
        ret_list.append(last_df.at[0, 'next_buy_price'])
        ret_list.append(df.iloc[last_row]['next_buy_price'])
        ret_list.append(df.iloc[last_row]['sell_price1'])

        last_df.at[0, 'next_buy_price'] = df.iloc[last_row]['next_buy_price']

        last_df.at[0, 'accum_qty']      = remain_qty
        last_df.at[0, 'accum_cost']     = df.iloc[last_row]['accum_cost'] * (remain_qty/df.iloc[last_row]['accum_qty'])

        last_df.at[0, 'sell_price']      = df.iloc[last_row]['sell_price']
        last_df.at[0, 'profit']      = df.iloc[last_row]['profit']
        last_df.at[0, 'sell_price1']      = df.iloc[last_row]['sell_price1']
        last_df.at[0, 'profit1']      = df.iloc[last_row]['profit1']
        last_df.at[0, 'sell_price2']      = df.iloc[last_row]['sell_price2']
        last_df.at[0, 'profit2']      = df.iloc[last_row]['profit2']

        print(last_df)

        if last_df.at[0, 'accum_qty']<100:
            print('accum_qty<100')
            break
        if last_df.at[0, 'next_buy_price']<10:
            print('next_buy_price<27')
            break
        df = bs_table_v2(last_df, cost_perc = -0.032, price_perc = -0.0477, row = 20)
        print(df.head(last_row+1))
        print()

    print()
    print(ret_list)
