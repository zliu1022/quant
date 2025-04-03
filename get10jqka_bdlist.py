#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
import os
import sys
import pymongo
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

def resp_bdlist(html_content):
    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找目标表格
    tables = soup.find_all('table', {'class': 'm-table m-pager-table'})

    ret_doc = []
    operations = []
    # 确保表格存在
    for table in tables:
        # 查找表头后面的所有行
        trs = table.find_all('tr')
        # 通常第一个<tr>是表头，所以从第二个开始
        for tr in trs[1:]:
            tds = tr.find_all('td')
            if len(tds) >= 2:
                # 提取第二列中的<a>标签
                td2 = tds[1]
                a_tag = td2.find('a')
                if a_tag and 'href' in a_tag.attrs:
                    name = a_tag.get_text(strip=True)
                    url = a_tag['href']
                    # 使用正则表达式从URL中提取code
                    match = re.search(r'/code/(\d+)/', url)
                    if match:
                        code = match.group(1)
                        data = {
                            'name': name,
                            'code': code,
                            'url': url
                        }
                        # 将数据插入MongoDB，若已存在则更新
                        operations.append(UpdateOne(
                            {'code': code},   # 查询条件
                            {'$set': data},    # 更新内容
                            upsert=True        # 如果不存在则插入
                        ))
                        ret_doc.append(data)
                        print(f"已处理板块：{name}，代码：{code}")
                    else:
                        print('no match')
                else:
                    print('no a_tag or href')
            else:
                print(f'len(tds) >= 2 no match {len(tds)}')

    return ret_doc, operations

def get_bdlist_one(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    ret_doc, operations = resp_bdlist(html_content)
    return ret_doc, operations

def get_bdlist():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["stk1"]
    collection = db["bd_10jqka"]
    collection.create_index([('code', pymongo.ASCENDING)], unique=True)

    directory = '.cache'
    for filename in os.listdir(directory):
        if filename.startswith('bdlist') and filename.endswith('.html'):
            file_path = os.path.join(directory, filename)
            print(f"正在处理文件：{file_path}")
            ret_doc, operations = get_bdlist_one(file_path)

            if operations:
                try:
                    collection.bulk_write(operations, ordered=False)
                    print(f"已成功插入 {len(operations)} 条记录。")
                except BulkWriteError as bwe:
                    print("批量写入出现错误，详情如下：")
                    for error in bwe.details['writeErrors']:
                        print(f"错误索引 {error['index']}: {error['errmsg']}")


if __name__ == '__main__':
    if len(sys.argv) == 1: 
        get_bdlist()
    elif len(sys.argv) == 2: 
        file_path = sys.argv[1]
        get_bdlist_one(file_path)
    else:
        print("./get10jqka_bdlist.py:           解析.cache目录下全部bdlist*.html")
        print("./get10jqka_bdlist.py file_path: 解析文件")
        sys.exit(1)

