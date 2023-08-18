#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

# 读取文件，删除后续都用不到的列
filename="mv-all-20200101-op_days.csv"
df = pd.read_csv(filename)
df.drop(columns=['profit_accum', 'profit_cur'], inplace=True)

# 删除时间段不足6次的ts_code, 也可以不删除, 平均后也会打印出次数供判断
ts_code_counts = df['ts_code'].value_counts()
valid_ts_codes = ts_code_counts[ts_code_counts == 6].index
df = df[df['ts_code'].isin(valid_ts_codes)]

# 删除mv变化大于50%, 可以保留，供判断
df['mv_diff'] = abs( (df['mv'] - df['mv_ori']) / df['mv_ori'])
df = df[df['mv_diff'] <= 0.5]

# 排序
df_accum = df.sort_values(by=['norm_accum_profit', 'mv_diff'], ascending=[False, True])
df_cur   = df.sort_values(by=['norm_cur_profit', 'mv_diff'], ascending=[False, True])

print('完整6次时间段、mv变化小于50%, accum 和 cur')
print(df_accum.head(10))
print()
print(df_cur.head(10))
print()

#### 下面是平均 ####

# 求平均
df_stats = (
    df.groupby('ts_code')
    .agg({
        'ts_code':           ['size'], # 添加计数列统计
        'norm_accum_profit': ['mean'],
        'norm_cur_profit':   ['mean'],
        'sell_counts':       ['mean'],
        'avg_mm_days':       ['mean']
    })
    .round({
        ('sell_counts', 'mean'): 1,
        ('norm_accum_profit', 'mean'): 0,
        ('norm_cur_profit', 'mean'): 0,
        ('avg_mm_days', 'mean'): 0,
    })
)
df_stats.columns = ['_'.join(col).strip() for col in df_stats.columns.values]

# 在加上name和industry
name_industry_df = df[['ts_code', 'name', 'industry']].drop_duplicates(subset='ts_code')
name_industry_df.set_index('ts_code', inplace=True)
df_stats = df_stats.join(name_industry_df)

# 不同排序方式
df_accum = df_stats.sort_values(by=['norm_accum_profit_mean', 'sell_counts_mean'], ascending=[False, False])
df_cur   = df_stats.sort_values(by=['norm_cur_profit_mean',   'sell_counts_mean'], ascending=[False, False])

print('按code平均')
print(df_accum.head(10))
print()
print(df_cur.head(10))
print()
