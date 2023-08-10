#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

#filename = "all-20200101-20230717-industry.csv"
#filename = "mv100-5000-20200101-op_days.csv"
#filename = "mv30-300-20200101-op_days.csv"
filename = "mv0-inf-20200101-op_days.csv"

print(f'get data from {filename}')
df = pd.read_csv(filename)

# Calculate the sum and mean of 'norm_accum_profit' and 'norm_cur_profit' within each industry
#industry_stats = df.groupby('industry').agg({'norm_accum_profit': ['sum', 'mean'], 'norm_cur_profit': ['sum', 'mean']})

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
industry_counts = (df['industry'].value_counts() / 6).round(0)
industry_stats['company_count'] = industry_counts

stats_accum = industry_stats.sort_values('norm_accum_profit_mean', ascending=False)
stats_cur   = industry_stats.sort_values('norm_cur_profit_mean', ascending=False)

num = 10
#stats_accum_top10 = stats_accum.head(10)[ ['company_count', 'norm_accum_profit_sum', 'norm_accum_profit_mean', 'norm_cur_profit_sum', 'norm_cur_profit_mean'] ]
#stats_cur_top10 = stats_cur.head(10)[ ['company_count', 'norm_accum_profit_sum', 'norm_accum_profit_mean', 'norm_cur_profit_sum', 'norm_cur_profit_mean'] ]
stats_accum_top10 = stats_accum.head(num)[ ['company_count', 'norm_accum_profit_mean', 'norm_cur_profit_mean', 'sell_counts_mean', 'avg_mm_days_mean'] ]
stats_cur_top10   = stats_cur.head(num)  [ ['company_count', 'norm_accum_profit_mean', 'norm_cur_profit_mean', 'sell_counts_mean', 'avg_mm_days_mean'] ]

print()
print(f'stats accum profit mean top{num} 分行业累计利润的企业平均 top{num}')
print(stats_accum_top10)
print()
print(f'stats cur profit mean top{num}   分行业当前计利润的企业平均 top{num}')
print(stats_cur_top10)

