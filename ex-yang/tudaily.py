#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockTushare import StockTushare
from StockSingle import StockSingle
import datetime

today_mt_string= datetime.datetime.now().strftime('%Y%m%d')

#将数组分割成8个数组 并行操作

def list_split(items,n):
    return [items[i:i+n] for i in range(0, len(items), n)]

def stock_daily_update(all_stock_count,singleObjc,stocks):

    tushareObj=StockTushare()
    size_array_stosks =list_split(stocks,150)
    tushareObj.getAllStockAvail(size_array_stosks,all_stock_count,singleObjc)
    
def stock_BK_update():
    tushareObj=StockTushare()
    tushareObj.updateBK()

if __name__ == '__main__':
    #更新本地数据库
    #1、获取最新股票库和交易数据

    singleObjc = StockSingle()
    df = singleObjc.pro.stock_basic(exchange='',fields='ts_code,symbol,name,industry,list_date,list_status')
    all_stocks = df.rename(columns={'industry': 'hy'}).to_dict('records')
    # stock_BK_update()
    # exit(0)
    
    all_stocks = [item for item in all_stocks if item['list_date'] <= today_mt_string]
    print(("最新交易日期 ----- %s  股票数量： %s 个" %(today_mt_string,len(all_stocks))))
    all_stock_count = len(all_stocks)
    index_stock_count = 0

    size_array_stosks =list_split(all_stocks, 240)
    for index,stocks in enumerate(size_array_stosks):
        stock_daily_update(all_stock_count,singleObjc,stocks)

  
