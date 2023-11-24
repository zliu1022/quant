#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ex.创建数据框
'''
df = pd.DataFrame({
    'X': [2.71]*8,
    'Y': [4.44, 4.45, 4.46, 4.47, 4.48, 4.49, 4.50, 4.51],
    'Z1': [986938, 976596, 903714, 902443, 901288, 900282, 738542, 673040],
    'Z2': [44581, 40482, 37672, 36619, 35450, 34630, 25506, 16129]
})
'''
#df = pd.read_csv("bs_table_cost_price.csv")
df = pd.read_csv("bs_table_cost_price_cp1~5_pp3~7.csv")
df['profit_margin'] = df['profit'] / df['accum_cost']
df['delta_34'] = abs(df['next_buy_price'] - 34)

filtered_df = df
filtered_df = df[df['accum_cost'] < 1000000]
#filtered_df = df[(df['accum_cost'] > 0) & (df['accum_cost'] <= 1000000)]
#filtered_df = df[(df['accum_cost'] > 700000) & (df['accum_cost'] <= 900000)]
filtered_df = df[(df['accum_cost'] > 700000) & (df['accum_cost'] <= 800000)]

filtered_df = filtered_df[filtered_df['profit'] > 0]

#filtered_df = filtered_df[filtered_df['price_perc'] == 4.77 ]

filtered_df = filtered_df[filtered_df['profit_margin'] >= 0.02829] # 22620/799500=2.8%
#filtered_df = filtered_df[filtered_df['profit_margin'] >= 0.0195]

filtered_df = filtered_df[ filtered_df['delta_34'] < 1 ]

print(filtered_df)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

x = filtered_df['cost_perc']
y = filtered_df['price_perc']
z = filtered_df['accum_cost']
p = filtered_df['profit']

ax.scatter(x, y, z, c=p, cmap='viridis')

ax.set_xlabel('Cost Percentage')
ax.set_ylabel('Price Percentage')
ax.set_zlabel('Accumulated Cost')

plt.show()

