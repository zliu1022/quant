#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

filename = "mv30-300-20200101-op_days.csv"
#filename = "mv100-5000-20200101-op_days.csv"
#filename = "mv0-inf-20200101-op_days.csv"

print(f'get data from {filename}')
df = pd.read_csv(filename)

normal_counts = 6

# 部分code缺大片的day数据，导致没有6个周期，删除这些
date_counts = df.groupby('ts_code')['start_date'].count()
invalid = date_counts[date_counts != normal_counts].index

df_err = pd.DataFrame()
for ts_code in invalid:
    rows = df[df['ts_code'] == ts_code]
    #print(rows)
    df_err = df_err.append(rows)
#print(df_err)
df = df.drop(df_err.index)

#industry_stats = df.groupby('industry').agg({'norm_accum_profit': ['sum', 'mean'], 'norm_cur_profit': ['sum', 'mean'], 'sell_counts':['sum','mean'],'avg_mm_days':['sum','mean']})
industry_stats = (
    df.groupby('industry')
    .agg({
        'norm_accum_profit': ['sum', 'mean'],
        'norm_cur_profit': ['sum', 'mean'],
        'sell_counts': ['sum', 'mean'],
        'avg_mm_days': ['sum', 'mean']
    })
    .round({
        ('sell_counts', 'sum'): 1,
        ('sell_counts', 'mean'): 1,
        ('norm_accum_profit', 'sum'): 0,
        ('norm_accum_profit', 'mean'): 0,
        ('norm_cur_profit', 'sum'): 0,
        ('norm_cur_profit', 'mean'): 0,
        ('avg_mm_days', 'sum'): 0,
        ('avg_mm_days', 'mean'): 0,
    })
)
industry_stats.columns = ['_'.join(col).strip() for col in industry_stats.columns.values]

# Add the industry counts to the dataframe
industry_counts = (df['industry'].value_counts() / normal_counts).round(0)
industry_stats['company_count'] = industry_counts

stats_accum = industry_stats.sort_values('norm_accum_profit_mean', ascending=False)
stats_cur   = industry_stats.sort_values('norm_cur_profit_mean', ascending=False)

num = 3 
stats_accum_top = stats_accum.head(num)[ ['company_count', 'norm_accum_profit_mean', 'norm_cur_profit_mean', 'sell_counts_mean', 'avg_mm_days_mean'] ]
stats_cur_top   = stats_cur.head(num)  [ ['company_count', 'norm_accum_profit_mean', 'norm_cur_profit_mean', 'sell_counts_mean', 'avg_mm_days_mean'] ]

print()
print(f'stats accum profit mean top{num} 分行业累计利润的企业平均 top{num}')
print(stats_accum_top)
print()
print(f'stats cur profit mean top{num}   分行业当前计利润的企业平均 top{num}')
print(stats_cur_top)

