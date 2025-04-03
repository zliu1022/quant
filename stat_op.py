#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from prettytable import PrettyTable

# 连接到MongoDB
client = MongoClient('localhost', 27017)  # 根据您的实际情况修改
db = client['stk1']
b_collection = db['20200301_20250331_1.55']
basic_collection = db['basic']

# 功能1：找到指定字段的最大Top10、最小Top10对应的文档，并打印信息
def function1():
    fields = ['profit_accum', 'profit_accum_norm', 'sell_counts', 'max_buy_count', 'max_cost', 'avg_mm_days']
    limit_num = 10
    print("\n字段Top文档：\n")
    for field in fields:
        query = {}

        print(f"字段：{field} 的Top {limit_num} 文档：")
        table = PrettyTable()
        table.field_names = ["ts_code", "name", field]

        if field == 'profit_accum' or field == 'profit_accum_norm':
            query['max_cost'] = {'$lte': 500000}  # 增加max_cost筛选条件

        # 排除name中包含“退”、“N”、“ST”的文档
        exclude_patterns = ["退", "N", "ST"]
        regex_pattern = f".*({'|'.join(exclude_patterns)}).*"
        query['name'] = {'$not': {'$regex': regex_pattern}}

        # 对于avg_mm_days字段，排除None值
        if field == 'avg_mm_days':
            query[field] = {'$ne': None}

        top_docs = b_collection.find(query).sort(field, -1).limit(limit_num)
        print_docs(top_docs, field)

def print_docs(docs_cursor, sort_field):
    table = PrettyTable()
    table.field_names = ["ts_code", "name", "industry", "profit_accum", "profit_accum_norm", "sell_counts", "max_buy_count", "max_cost", "avg_mm_days"]

    for doc in docs_cursor:
        ts_code = doc.get('ts_code')

        table.add_row([
            ts_code,
            doc.get('name', ''),
            doc.get('industry', ''),
            doc.get('profit_accum', ''),
            doc.get('profit_accum_norm', ''),
            doc.get('sell_counts', ''),
            doc.get('max_buy_count', ''),
            doc.get('max_cost', ''),
            doc.get('avg_mm_days', '')
        ])
    print(table)

# 功能2：对全部文档的指定字段进行求和
def function2():
    fields = ['profit_accum', 'profit_accum_norm', 'max_cost', 'cur_profit', 'norm_cur_profit', 'cur_cost']
    print("\n字段求和：\n")
    table = PrettyTable()
    table.field_names = ["字段", "总和"]

    # 排除name中包含“退”、“N”、“ST”的文档
    exclude_patterns = ["退", "N", "ST"]
    regex_pattern = f"({'|'.join(exclude_patterns)})"

    for field in fields:
        total = b_collection.aggregate([
            # 增加筛选条件，排除name中包含指定字符串的文档
            {'$match': {'name': {'$not': {'$regex': regex_pattern}}}},
            {'$group': {'_id': None, 'total': {'$sum': f'${field}'}}}
        ])
        total_value = next(total, {}).get('total', 0)
        table.add_row([field, total_value])

    print(table)

# 功能3：根据指定的ts_code列表，对这些文档的指定字段进行求和
def function3():
    ts_code_list = [
        "000425", "002273", "002475", 
        "300911",
        "002508", # 老板电器，厨卫电器，881174
        "600580", # 卧龙电驱，电机，881277
        #"300896", # 爱美客，美容护理，881182
        "600177", # 雅戈尔，服装家纺，881136
        "002202", # 金风科技，风电设备，881280
        #"603195", # 公牛集团，家居用品，881139
        "600061", # 国投资本，多元金融，881283
        "601939" # 建设银行，银行，881155
        ]
    fields = ['profit_accum', 'profit_accum_norm', 'max_cost']
    print("\n指定ts_code列表的文档字段求和：\n")
    table = PrettyTable()
    table.field_names = ["字段", "总和"]

    for field in fields:
        total = b_collection.aggregate([
            {'$match': {'$or': [{'ts_code': {'$regex': f'^{code}'}} for code in ts_code_list]}},
            {'$group': {'_id': None, 'total': {'$sum': f'${field}'}}}
        ])
        total_value = next(total, {}).get('total', 0)
        table.add_row([field, total_value])

    print(table)

#function1()
function2()
function3()
