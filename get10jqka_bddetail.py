#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
import os
import sys
import pymongo
from pymongo import UpdateOne, ReturnDocument
from pymongo.errors import BulkWriteError

def resp_bddetail(html_content):
    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')

    div_board = soup.find_all('div', {'class': 'board-hq'})
    h3_tag = div_board[0].find('h3')
    span_tag = h3_tag.find('span')
    bdcode = span_tag.get_text(strip=True)

    # 查找目标表格
    tables = soup.find_all('table', {'class': 'm-table m-pager-table'})

    ret_doc = []
    # 确保表格存在
    for table in tables:
        # 查找表头后面的所有行
        trs = table.find_all('tr')
        # 通常第一个<tr>是表头，所以从第二个开始
        for tr in trs[1:]:
            tds = tr.find_all('td')
            if len(tds) >= 3:
                # 提取第二列中的<a>标签
                td2 = tds[2] #和bdlist的区别1
                a_tag = td2.find('a')
                if a_tag and 'href' in a_tag.attrs:
                    name = a_tag.get_text(strip=True)
                    url = a_tag['href']
                    # 使用正则表达式从URL中提取code
                    match = re.search(r'/(\d+)', url) #和bdlist的区别2
                    if match:
                        code = match.group(1)
                        data = {
                            'name': name,
                            'code': code,
                            'url': url
                        }
                        # 将数据插入MongoDB，若已存在则更新
                        ret_doc.append(data)
                        #print(f"已处理板块：{name}，代码：{code} {url}")
                    else:
                        print('no match')
                else:
                    print('no a_tag or href')
            else:
                print(f'len(tds) >= 2 no match {len(tds)}')

    return ret_doc, bdcode

def get_bddetail_one(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    ret_doc, bdcode = resp_bddetail(html_content)
    return ret_doc, bdcode

def get_bddetail():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["stk1"]
    collection = db["bd_10jqka"]
    collection.create_index([('code', pymongo.ASCENDING)], unique=True)

    directory = '.cache'
    for filename in os.listdir(directory):
        if filename.startswith('bd_') and filename.endswith('.html'):
            file_path = os.path.join(directory, filename)
            print(f"正在处理文件：{file_path}")
            newdata, bdcode = get_bddetail_one(file_path)

            olddoc = collection.find_one({'code': bdcode})
            olddata = olddoc.get('list', [])

            # Convert old_list to a dictionary indexed by 'code'
            old_dict = {item['code']: item for item in olddata}
            new_dict = {item['code']: item for item in newdata}
            
            # Merge the two dictionaries
            merged_dict = old_dict.copy()
            merged_dict.update(new_dict)  # This overwrites old items with new ones if 'code' matches
            
            # Convert the merged dictionary back to a list
            merged_list = list(merged_dict.values())
            
            # Update the 'list' field with the merged data
            result = collection.update_one(
                {'code': bdcode},
                {'$set': {'list': merged_list}}
            )

            if result.modified_count > 0:
                print(f"The document with code {bdcode} has been updated successfully.")
            else:
                print(f"No changes were made to the document with code {bdcode}.")

if __name__ == '__main__':
    if len(sys.argv) == 2: 
        file_path = sys.argv[1]
        get_bddetail_one(file_path)
    elif len(sys.argv) == 1: 
        get_bddetail()
    else:
        print("./get10jqka_bddetail.py:           解析.cache目录下全部bdlist*.html")
        print("./get10jqka_bddetail.py file_path: 解析文件")
        sys.exit(1)

