#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from buy_sell_seq import buy_sell_seq
import sys

def buy_sell_dec_range(para):
    dec_perc_price_begin = para.get('dec_perc_begin')
    dec_perc_price_end = para.get('dec_perc_end')
    perc_interval = para.get('perc_interval')
    limit_min_price = para.get('limit_min_price')
    exp_dec_cost_min = para.get('exp_dec_cost_min')
    exp_dec_cost_max = para.get('exp_dec_cost_max')

    # Initialize parameter ranges
    dec_perc_price_values = np.arange(dec_perc_price_begin, dec_perc_price_end + perc_interval, perc_interval)

    # Results storage
    results = []

    # Fixed parameters
    exp_sell_inc_perc = 1.245  # Example value
    sell_perc         = 0.5  # Example value
    prev_data = {
        'price': 100,
        'profit': 0,
        'remain_qty': 0,
        'remain_cost': 0
    }

    for dec_perc_price in dec_perc_price_values:
        # Avoid log of zero or negative numbers
        try:
            max_steps = np.ceil(np.log(limit_min_price) / np.log(1 - dec_perc_price))
        except ValueError:
            continue  # Skip invalid values where log is undefined
        if max_steps <= 0:
            continue  # Skip non-positive steps

        exp_dec_perc_cost_unit_start = exp_dec_cost_min * dec_perc_price
        exp_dec_perc_cost_unit_end   = exp_dec_cost_max * dec_perc_price
        exp_dec_perc_cost_unit_values = np.arange(exp_dec_perc_cost_unit_start, exp_dec_perc_cost_unit_end + 0.1*perc_interval, perc_interval)
        exp_dec_perc_cost_unit_values = np.round(exp_dec_perc_cost_unit_values, 5)  # Round to avoid floating point issues

        for exp_dec_perc_cost_unit in exp_dec_perc_cost_unit_values:
            parameters = {
                'dec_perc_price': dec_perc_price,
                'exp_dec_perc_cost_unit': exp_dec_perc_cost_unit,
                'exp_sell_inc_perc': exp_sell_inc_perc,
                'sell_perc': sell_perc
            }
            
            data, cur_data = buy_sell_seq(int(max_steps), prev_data, parameters)
            profit = cur_data['profit']
            max_cost = cur_data['max_cost']

            results.append({
                'max_steps': int(max_steps),
                'dec_perc_price': float(dec_perc_price),
                'exp_dec_perc_cost_unit': float(exp_dec_perc_cost_unit),
                'profit': float(profit),
                'max_cost': float(max_cost)
            })

    return results

# max_cost < 1,000,000 时 max_profit
def find_max_profit(results, limit_max_cost):
    # Convert results to NumPy arrays for processing
    dec_perc_price_array = np.array([r['dec_perc_price'] for r in results])
    exp_dec_perc_cost_unit_array = np.array([r['exp_dec_perc_cost_unit'] for r in results])
    profit_array = np.array([r['profit'] for r in results])
    max_cost_array = np.array([r['max_cost'] for r in results])
    max_steps_array = np.array([r['max_steps'] for r in results])

    # Filter results where max_cost < 1,000,000
    valid_indices = np.where(max_cost_array < limit_max_cost)
    valid_profits = profit_array[valid_indices]
    valid_dec_perc_price = dec_perc_price_array[valid_indices]
    valid_exp_dec_perc_cost_unit = exp_dec_perc_cost_unit_array[valid_indices]
    valid_max_steps = max_steps_array[valid_indices]
    valid_max_cost = max_cost_array[valid_indices]

    # Find the maximum profit and corresponding parameters
    max_profit_index = np.argmax(valid_profits)
    profit = valid_profits[max_profit_index]
    optimal_dec_perc_price = valid_dec_perc_price[max_profit_index]
    optimal_exp_dec_perc_cost_unit = valid_exp_dec_perc_cost_unit[max_profit_index]
    max_max_steps = valid_max_steps[max_profit_index]
    max_cost = valid_max_cost[max_profit_index]

    data = {
        'profit': profit,
        'max_cost':   max_cost,
        'max_max_steps': max_max_steps,
        'dec_perc_price': optimal_dec_perc_price,
        'exp_dec_perc_cost_unit': optimal_exp_dec_perc_cost_unit
    }
    return data

# profit > 0 时 min_cost
def find_min_cost(results):
    # Convert results to NumPy arrays for processing
    dec_perc_price_array = np.array([r['dec_perc_price'] for r in results])
    exp_dec_perc_cost_unit_array = np.array([r['exp_dec_perc_cost_unit'] for r in results])
    profit_array = np.array([r['profit'] for r in results])
    max_cost_array = np.array([r['max_cost'] for r in results])
    max_steps_array = np.array([r['max_steps'] for r in results])

    # Filter results where profit > 0
    valid_indices = np.where(profit_array > 0)
    valid_profits = profit_array[valid_indices]
    valid_dec_perc_price = dec_perc_price_array[valid_indices]
    valid_exp_dec_perc_cost_unit = exp_dec_perc_cost_unit_array[valid_indices]
    valid_max_steps = max_steps_array[valid_indices]
    valid_max_cost = max_cost_array[valid_indices]

    # Find the minimu cost and corresponding parameters
    if len(valid_profits) !=0:
        index = np.argmin(valid_max_cost)
        profit = valid_profits[index]
        optimal_dec_perc_price = valid_dec_perc_price[index]
        optimal_exp_dec_perc_cost_unit = valid_exp_dec_perc_cost_unit[index]
        max_max_steps = valid_max_steps[index]
        max_cost = valid_max_cost[index]

        data = {
            'profit': profit,
            'max_cost':   max_cost,
            'max_max_steps': max_max_steps,
            'dec_perc_price': optimal_dec_perc_price,
            'exp_dec_perc_cost_unit': optimal_exp_dec_perc_cost_unit
        }
        return data
    return None

def draw_range(results):
    dec_perc_price_array = np.array([r['dec_perc_price'] for r in results])
    exp_dec_perc_cost_unit_array = np.array([r['exp_dec_perc_cost_unit'] for r in results])
    profit_array = np.array([r['profit'] for r in results])
    max_cost_array = np.array([r['max_cost'] for r in results])

    valid_indices = np.where(max_cost_array < limit_max_cost)
    profit_array = profit_array[valid_indices]
    dec_perc_price_array = dec_perc_price_array[valid_indices]
    exp_dec_perc_cost_unit_array = exp_dec_perc_cost_unit_array[valid_indices]
    max_cost_array = max_cost_array[valid_indices]

    # Plotting Profit
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(121, projection='3d')
    ax.scatter(dec_perc_price_array, exp_dec_perc_cost_unit_array, profit_array, c=profit_array, cmap='viridis')
    ax.set_xlabel('dec_perc_price')
    ax.set_ylabel('exp_dec_perc_cost_unit')
    ax.set_zlabel('profit')
    ax.set_title('Profit vs Parameters')

    # Plotting Max Cost
    ax2 = fig.add_subplot(122, projection='3d')
    ax2.scatter(dec_perc_price_array, exp_dec_perc_cost_unit_array, max_cost_array, c=max_cost_array, cmap='plasma')
    ax2.set_xlabel('dec_perc_price')
    ax2.set_ylabel('exp_dec_perc_cost_unit')
    ax2.set_zlabel('max_cost')
    ax2.set_title('Max Cost vs Parameters')

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    perc_interval = 0.001
    limit_min_price = 0.5       # 按照下跌到 20%的原价来测算
    limit_max_cost = 1_000_000  # 最大投入限制
    exp_dec_cost_min = 0.5      # 买入后持有成本下降是价格下降幅度的下限
    exp_dec_cost_max = 0.9      # 买入后持有成本下降是价格下降幅度的上限

    if len(sys.argv) == 3:
        begin = float(sys.argv[1])
        end   = float(sys.argv[2])
    else:
        begin = 0.047 # max_cost < 1,000,000 ，刚好开始 profit > 0
        end   = 0.09

    print(f'最大投入 {limit_max_cost}万')
    print(f'到达价格跌幅，买入并使得持有成本下降，持有成本下降是价格下降幅度的范围 {exp_dec_cost_min} {exp_dec_cost_max}')
    print(f'买入后，价格最低会跌到原价的 {limit_min_price*100:>3.0f}%')
    para = {
        'dec_perc_begin': begin,
        'dec_perc_end': end,
        'perc_interval': perc_interval,
        'limit_min_price': limit_min_price,
        'exp_dec_cost_min': exp_dec_cost_min,
        'exp_dec_cost_max': exp_dec_cost_max
    }
    ret = buy_sell_dec_range(para)
    max_data = find_max_profit(ret, limit_max_cost) # 寻找最大投入范围内，最高的盈利
    min_data = find_min_cost(ret)   # 寻找不亏本情况下，最低的投入

    print(f"                        profit  max_cost max_steps dec_perc_price exp_dec_perc_cost_unit")
    print(f"投入小于100w，最大盈利 ", end='')
    print(f"{max_data['profit']:>7} {max_data['max_cost']:>10,} {max_data['max_max_steps']:>8} {max_data['dec_perc_price']:>14.5f} {max_data['exp_dec_perc_cost_unit']:>22.5f}")
    print(f"盈利>0的最小投入成本   ", end='')
    print(f"{min_data['profit']:>7} {min_data['max_cost']:>10,} {min_data['max_max_steps']:>8} {min_data['dec_perc_price']:>14.5f} {min_data['exp_dec_perc_cost_unit']:>22.5f}")
    print('dec_perc_price 价格下降幅度，下降到这个位置就买入')
    print('exp_dec_perc_cost_uni 买入后，成本下降幅度的期望')

    draw_range(ret)

