#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 价格下降幅度dec_perc_price
# 期望单位成本下降幅度exp_dec_perc_cost_unit
# 期望卖出倍数exp_sell_inc_perc
# 每次卖出比例sell_perc

import sys
import pandas as pd

def qty_lowcost(buy_price, exp_dec_perc_cost_unit, cost_accum_prev, qty_accum_prev):
    # 如果原来没有持有成本，直接返回最低买入数量
    if qty_accum_prev == 0:
        return 100
    cost_unit_prev = cost_accum_prev / qty_accum_prev

    # Compute the target cost unit
    cost_unit_target = cost_unit_prev * (1 - exp_dec_perc_cost_unit)
    numerator = (cost_unit_target * qty_accum_prev) - cost_accum_prev
    denominator = buy_price - cost_unit_target
    if denominator == 0:
        buy_qty_new = 100.0  # Avoid division by zero
    else:
        buy_qty_new = numerator / denominator
    # If buy_qty_new is less than 100, set it to 100
    if buy_qty_new < 100:
        buy_qty_new = 100.0
    # Round down to the nearest multiple of 100
    buy_qty = int(buy_qty_new // 100) * 100
    if buy_qty < 100:
        buy_qty = 100
    #print(f'buy_qty {buy_qty_new} -> {buy_qty}')
    return buy_qty

def buy_sell_seq(max_steps, prev_data, parameters):
    # Initialize variables
    price_prev = prev_data.get('price', 0)
    profit_prev = prev_data.get('profit', 0)
    cost_accum_prev = prev_data.get('remain_cost', 0)
    qty_accum_prev = prev_data.get('remain_qty', 0)
    if qty_accum_prev == 0:
        cost_unit_prev = 0
    else:
        cost_unit_prev = cost_accum_prev / qty_accum_prev

    # Initialize parameters
    dec_perc_price = parameters.get('dec_perc_price', 0)
    exp_dec_perc_cost_unit = parameters.get('exp_dec_perc_cost_unit', 0)
    exp_sell_inc_perc = parameters.get('exp_sell_inc_perc', 0)
    sell_perc = parameters.get('sell_perc', 0)

    # Initialize lists to store each column of the table
    No = []
    price_list = []
    buy_price_list = []
    buy_qty_list = []
    qty_accum_list = []
    cost_cur_list = []
    cost_accum_list = []
    cost_unit_list = []
    dec_perc_cost_unit_list = []
    exp_sell_price_list = []
    exp_sell_qty_list = []
    exp_profit_list = []
    remain_qty_list = []
    remain_cost_accum_list = []
    remain_profit_list = []

    for n in range(1, max_steps+1):
        No.append(n)
        if n == 1:
            # At step 1, initialize values
            price = price_prev
        else:
            # Price decreases by dec_perc_price
            price = price_prev * (1 - dec_perc_price)

        buy_price = price
        buy_qty = qty_lowcost(buy_price, exp_dec_perc_cost_unit, cost_accum_prev, qty_accum_prev)
        cost_cur = buy_price * buy_qty
        qty_accum = qty_accum_prev + buy_qty
        cost_accum = cost_accum_prev + cost_cur
        cost_unit = cost_accum / qty_accum
        if cost_unit_prev == 0:
            dec_perc_cost_unit = 0.0
        else:
            dec_perc_cost_unit = (cost_unit_prev - cost_unit) / cost_unit_prev

        exp_sell_price = price * exp_sell_inc_perc
        ori_exp_sell_qty = qty_accum * sell_perc
        exp_sell_qty = int(ori_exp_sell_qty// 100) * 100
        #print(f'exp_sell_qty {ori_exp_sell_qty} -> {exp_sell_qty}')
        exp_profit = exp_sell_price * exp_sell_qty - cost_accum * (exp_sell_qty/qty_accum) + profit_prev

        remain_qty = qty_accum - exp_sell_qty
        remain_cost_accum = cost_accum * (1 - exp_sell_qty/qty_accum)
        remain_profit = remain_qty*exp_sell_price*exp_sell_inc_perc - remain_cost_accum

        # Append to lists
        price_list.append(round(price, 2))
        buy_price_list.append(round(buy_price, 2))
        buy_qty_list.append(round(buy_qty, 0))
        qty_accum_list.append(round(qty_accum, 0))
        cost_cur_list.append(round(cost_cur, 1))
        cost_accum_list.append(round(cost_accum, 1))
        cost_unit_list.append(round(cost_unit, 1))
        dec_perc_cost_unit_list.append(round(dec_perc_cost_unit * 100, 2))  # Percentage
        exp_sell_price_list.append(round(exp_sell_price, 2))
        exp_sell_qty_list.append(round(exp_sell_qty, 0))
        exp_profit_list.append(round(exp_profit, 1))

        remain_qty_list.append(round(remain_qty, 1))
        remain_cost_accum_list.append(round(remain_cost_accum, 1))
        remain_profit_list.append(round(remain_profit, 1))

        # Update previous variables for next iteration
        price_prev = price
        cost_accum_prev = cost_accum
        qty_accum_prev = qty_accum
        cost_unit_prev = cost_unit

    data = {
        'No': No,
        'Price': price_list,
        'Buy_P': buy_price_list,
        'Buy_Q': buy_qty_list,
        'Q_Accum': qty_accum_list,
        'C_Cur': cost_cur_list,
        'C_Accum': cost_accum_list,
        'C_Unit': cost_unit_list,
        'Dec_C%': dec_perc_cost_unit_list,
        'Sell_P': exp_sell_price_list,
        'Sell_Q': exp_sell_qty_list,
        'Profit': exp_profit_list,
        'Rm_Q': remain_qty_list,
        'Rm_C': remain_cost_accum_list,
        'Rm_Prft': remain_profit_list
    }

    cur_data = {
        'price':      round(price* (1 - dec_perc_price), 2),
        'profit': round(exp_profit,1),
        'remain_qty':   round(remain_qty,0),
        'remain_cost':   round(remain_cost_accum,1)
    }
    return data, cur_data

if __name__ == '__main__':
    # 15次，价格跌幅 3%，买入后成本预期降幅 1.5%，期望卖出价格涨幅 1.55
    #./buy_sell_seq 15 0.03 0.015 1.55
    if len(sys.argv) == 6:
        loops = int(sys.argv[1])                # 循环次数
        max_steps = int(sys.argv[2])                # 买入次数
        dec_perc_price = float(sys.argv[3])         # 买入价格跌幅
        exp_dec_perc_cost_unit = float(sys.argv[4]) # 买入后成本预期降幅
        exp_sell_inc_perc = float(sys.argv[5])      # 期望卖出价格涨幅

        # 每次卖出的比例%
        sell_perc = 0.5

        print(f'重复{loops}次：下跌{max_steps}x{dec_perc_price*100}% 后，上涨{exp_sell_inc_perc}, 卖掉{sell_perc*100}%')
    else:
        sys.exit(1)
        
    prev_data = {
        'price':       100,
        'profit':      0,
        'remain_qty':  0,
        'remain_cost': 0
    }
    parameters = {
        'dec_perc_price':         dec_perc_price,
        'exp_dec_perc_cost_unit': exp_dec_perc_cost_unit,
        'exp_sell_inc_perc':      exp_sell_inc_perc,
        'sell_perc':              sell_perc
    }

    for _ in range(loops):
        data, cur_data = buy_sell_seq(max_steps, prev_data, parameters)
        print(pd.DataFrame(data))
        print(cur_data)
        #print('--------------------')

        prev_data = cur_data
        parameters = {
            'dec_perc_price':         dec_perc_price,
            'exp_dec_perc_cost_unit': exp_dec_perc_cost_unit * 1.1,
            'exp_sell_inc_perc':      exp_sell_inc_perc,
            'sell_perc':              sell_perc
        }

