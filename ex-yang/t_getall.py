#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockSingle import StockSingle
from StockRequest import StockRequest
import datetime
import threading
import requests
import time

class StockTestBaseInfo:
    def __init__(self):
        self.dateTimp = str(int(time.time()*1000))
        t = 'bf75ab4bcea18c79de253cb841f2b27e248d8948'
        self.header = {
            'cookie':'xq_is_login=1;xq_a_token=' + t,
            'User-Agent': 'Xueqiu iPhone 13.6.5'
        }
        return

    def req_all(self, all_stocks):
        err = []

        for index,stock_info in enumerate(all_stocks):
            ret = 0
            ts_code = stock_info['ts_code']

            if ts_code == None:
                print('ts_code == None')
                continue
            ts_code_arr = ts_code.split(".", 1)
            ts_code_symbol=ts_code_arr[1]+ts_code_arr[0]

            #base_info = self.xueqiu.requestXueQiuBaseInfo(ts_code)#基础信息
            url = "https://stock.xueqiu.com/v5/stock/quote.json?symbol="+ts_code_symbol+"&extend=detail"
            ret, response = self.req_url(url)
            if ret != 0:
                err.append(stock_info)
                continue
            else:
                code=response['error_code']

            url = "https://stock.xueqiu.com/v5/stock/f10/cn/bonus.json?&symbol=" +ts_code_symbol
            ret, response = self.req_url(url)
            if ret != 0:
                err.append(stock_info)
                continue
            else:
                code=response['error_code']

            #stock_daily=self.xueqiu.requestXueQiuDaily(ts_code)
            url="https://stock.xueqiu.com/v5/stock/chart/kline.json?period=day&type=before&count=-365&symbol="+ts_code_symbol+"&begin="+self.dateTimp
            ret, response = self.req_url(url)
            if ret != 0:
                err.append(stock_info)
                continue
            else:
                code=response['error_code']

            #amount = self.xueqiu.requestAmountInflow(ts_code)
            if "BJ" in ts_code:
                continue
            url="https://stock.xueqiu.com/v5/stock/capital/distribution.json?symbol="+ts_code_symbol
            ret, response = self.req_url(url)
            if ret != 0:
                err.append(stock_info)
                continue
            else:
                code=response['error_code']

        return err

    def req_url(self, url):
        try:
            r = requests.get(url, headers=self.header)
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
            return 1, {}
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
            return 2, {}
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
            return 3, {}
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)
            return 4, {}

        resp = r.json()
        return 0, resp

    def funcaaaaa(self,all_stocks,all_stock_count,singleObjc):
        start_t = time.time()

        err_stock = self.req_all(all_stocks)

        if len(err_stock)>0:
            print(threading.current_thread().name, 'Error 1st', len(err_stock))
            err_stock = self.req_all(err_stock)
            if len(err_stock)>0:
                print(threading.current_thread().name, 'Error 2nd', err_stock)

        end_t = time.time()
        print('{} done {:.2f}s'.format(threading.current_thread().name, end_t - start_t))


    def getAllStockAvail(self,size_array_codes,all_stock_count,singleObjc): 
        threads = []  
        for index,small_codes_array in enumerate(size_array_codes):
            thre = threading.Thread(target=self.funcaaaaa, args=(small_codes_array,all_stock_count,singleObjc))   # 创建一个线程
            threads.append(thre)
            thre.start()  # 运行线程
        return threads
 
today_mt_string= datetime.datetime.now().strftime('%Y%m%d')

#将数组分割成8个数组 并行操作

def list_split(items,n):
    return [items[i:i+n] for i in range(0, len(items), n)]

def stock_daily_update(all_stock_count,singleObjc,stocks):
    bi = StockTestBaseInfo()
    size_array_stosks =list_split(stocks,240)
    threads = bi.getAllStockAvail(size_array_stosks,all_stock_count,singleObjc)
    return threads
    
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
    
    all_stock_count = len(all_stocks)
    all_stocks = [item for item in all_stocks if item['list_date'] <= today_mt_string]
    print(("最新交易日期 ----- %s  股票数量： %s 个" %(today_mt_string,len(all_stocks))))

    all_stocks = all_stocks[0:3]

    size_array_stosks =list_split(all_stocks, 1)

    start_t = time.time()
    threads_arr = []
    for index,stocks in enumerate(size_array_stosks):
        threads = stock_daily_update(all_stock_count,singleObjc,stocks)
        threads_arr.append(threads)
    for i in threads_arr:
        for j in i:
            j.join()
    end_t = time.time()

    print('total cost {:5.2f}s'.format(end_t - start_t))

