#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient()
    db = client.ak_board
    col_bd = db.boardinfo
    col_detail = db.boarddetails

    result = col_detail.find({'代码': '831087'})
    print(result[0].keys())
    print(result[0]['代码'], result[0]['名称'], result[0]['市盈率'], result[0]['流通市值'])
    for item in result:
        ref = col_bd.find({'代码': item['板块代码']})
        for i in ref:
            print(i['代码'], i['概念名称'], i['成分股数量'], i['网址'])

