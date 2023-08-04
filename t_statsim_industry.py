#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

filename = "all-20200101-20230717-industry.csv"
print(f'get data from {filename}')
df = pd.read_csv(filename)

# Calculate the sum and mean of 'norm_accum_profit' and 'norm_cur_profit' within each industry
industry_stats = df.groupby('industry').agg({'norm_accum_profit': ['sum', 'mean'], 'norm_cur_profit': ['sum', 'mean']})
industry_stats.columns = ['_'.join(col).strip() for col in industry_stats.columns.values]

# Add the industry counts to the dataframe
industry_counts = df['industry'].value_counts()
industry_stats['company_count'] = industry_counts

stats_accum = industry_stats.sort_values('norm_accum_profit_mean', ascending=False)
stats_cur   = industry_stats.sort_values('norm_cur_profit_mean', ascending=False)

stats_accum_top10 = stats_accum.head(10)[ ['company_count', 'norm_accum_profit_sum', 'norm_accum_profit_mean', 'norm_cur_profit_sum', 'norm_cur_profit_mean'] ]
stats_cur_top10 = stats_cur.head(10)[ ['company_count', 'norm_accum_profit_sum', 'norm_accum_profit_mean', 'norm_cur_profit_sum', 'norm_cur_profit_mean'] ]

print(f'stats accum profit mean top10 分行业累计利润的企业平均 top 10')
print(stats_accum_top10)
print(f'stats cur profit mean top10   分行业当前计利润的企业平均 top 10')
print(stats_cur_top10)

