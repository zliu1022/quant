#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import plotly.express as px
import pandas as pd

# 创建数据框
'''
df = pd.DataFrame({
    'X': [2.71]*8,
    'Y': [4.44, 4.45, 4.46, 4.47, 4.48, 4.49, 4.50, 4.51],
    'Z1': [986938, 976596, 903714, 902443, 901288, 900282, 738542, 673040],
    'Z2': [44581, 40482, 37672, 36619, 35450, 34630, 25506, 16129]
})
'''
df = pd.read_csv("bs_table_cost_price.csv")
df['profit_margin'] = df['profit'] / df['accum_cost']
df['delta_34'] = abs(df['next_buy_price'] - 34)

#filtered_df = df
#filtered_df = df[df['accum_cost'] < 1000000]
#filtered_df = df[(df['accum_cost'] > 0) & (df['accum_cost'] <= 1000000)]
#filtered_df = df[(df['accum_cost'] > 700000) & (df['accum_cost'] <= 900000)]
filtered_df = df[(df['accum_cost'] > 700000) & (df['accum_cost'] <= 800000)]

filtered_df = filtered_df[filtered_df['profit'] > 0]

filtered_df = filtered_df[filtered_df['profit_margin'] >= 0.02829] # 22620/799500=2.8%
#filtered_df = filtered_df[filtered_df['profit_margin'] >= 0.0195]

filtered_df = filtered_df[ filtered_df['delta_34'] < 0.1 ]

print(filtered_df)

# 创建3D散点图
fig = px.scatter_3d(filtered_df, x='cost_perc', y='price_perc', z='accum_cost', color='profit')
#fig = px.scatter_3d(filtered_df, x='cost_perc', y='price_perc', z='profit')
fig.update_traces(marker=dict(size=3))

fig.show()

