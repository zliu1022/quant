#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

# Load the data
df = pd.read_csv('./all-20200101-20230717.csv')

# Create a dictionary for industry name translations
industry_translation = {
    "计算机应用": "Computer Applications",
    "养殖业": "Animal Husbandry",
    "通信设备": "Communication Equipment",
    "种植业": "Planting Industry",
    "石油开采": "Oil Extraction",
    "家用电器": "Household Appliances",
    "其他电子": "Other Electronics",
    "软件服务": "Software Services",
    "IT设备": "IT Equipment",
    "化工原料": "Chemical Raw Materials"
}

# Apply the translations to the dataframe
df['industry'] = df['industry'].replace(industry_translation)

# Count the number of companies in each industry
industry_counts = df['industry'].value_counts()

# Calculate the sum and mean of 'norm_accum_profit' and 'norm_cur_profit' within each industry
industry_stats = df.groupby('industry').agg(
    {'norm_accum_profit': ['sum', 'mean'], 'norm_cur_profit': ['sum', 'mean']}
)

# Flatten the column index
industry_stats.columns = ['_'.join(col).strip() for col in industry_stats.columns.values]

# Add the industry counts to the dataframe
industry_stats['company_count'] = industry_counts

# Select the top 30 industries by 'norm_accum_profit_mean'
industry_stats_top30 = industry_stats.sort_values('norm_accum_profit_mean', ascending=False).head(30)

# Reorder the columns
industry_stats_top30 = industry_stats_top30[
    ['company_count', 'norm_accum_profit_sum', 'norm_accum_profit_mean', 'norm_cur_profit_sum', 'norm_cur_profit_mean']
]

# Print the dataframe
print(industry_stats_top30)

