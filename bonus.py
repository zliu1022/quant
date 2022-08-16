#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import snowtoken

import datetime
import threading
import requests
import time

from pymongo import MongoClient
from pprint import pprint

import pandas as pd

class StockInfo:
    def __init__(self):
        client = MongoClient(port=27017)
        db = client.stk1

        self.col_basic = db.basic
        self.col_bonus = db.bonus
        self.col_baseinfo = db.baseinfo
        self.col_day = db.day

        #self.dateTimp = str(int(time.time()*1000))
        time_str = '20200618'
        self.dateTimp = str(int(time.mktime(time.strptime(time_str, '%Y%m%d'))*1000))

        #t = snowtoken.get_snowtoken()
        t = '28ed0fb1c0734b3e85f9e93b8478033dbc11c856'
        self.header = {
            'cookie':'xq_is_login=1;xq_a_token=' + t,
            'User-Agent': 'Xueqiu iPhone 13.6.5'
        }

        self.today_String = datetime.datetime.now().strftime('%Y-%m-%d')
        self.today_dt= datetime.datetime.strptime(self.today_String,'%Y-%m-%d')
        return

    def stringFromconvertDateType(self,date,oldType,newType):
        temp_string=""
        if isinstance(date,str):
            temp_date = datetime.datetime.strptime(date,oldType)
            temp_string = temp_date.strftime(newType)
        else:
            temp_string = date.strftime(newType)
        return temp_string

    #获取股票上市时长
    def get_stock_trade_days(self,list_date):
        list_date_temp = datetime.datetime.strptime(list_date,'%Y%m%d')
        date_len=self.today_dt-list_date_temp
        return date_len.days

    def plan2digit(self, s):
        base, new, bonus = 0,0,0
        zhuan_pos = s.find('转')
        gu_pos =    s.find('股')
        pai_pos =   s.find('派')
        yuan_pos =  s.find('元')
        if zhuan_pos != -1:
            new = s[zhuan_pos+1:gu_pos]
            if pai_pos != -1:
                bonus = s[pai_pos+1:yuan_pos]
                if zhuan_pos < pai_pos:
                    base = s[0:zhuan_pos]
                else:
                    base = s[0:pai_pos]
            else:
                bonus = 0
        else:
            if pai_pos != -1:
                bonus = s[pai_pos+1:yuan_pos]
                base = s[0:pai_pos]
            else:
                base = 0
            new = 0
        return base, new, bonus


    def req_all(self, all_stocks):
        err_day = []

        for index,stock_info in enumerate(all_stocks):
            ret = 0
            ts_code = stock_info['ts_code']

            if ts_code == None:
                print('ts_code == None')
                continue
            ts_code_arr = ts_code.split(".", 1)
            ts_code_symbol=ts_code_arr[1]+ts_code_arr[0]

            url = "https://stock.xueqiu.com/v5/stock/f10/cn/bonus.json?&symbol=" +ts_code_symbol
            print(url)
            begin_t = time.time()
            ret, resp = self.req_url_retry(url, 3)
            end_t = time.time()
            print('req_url_retry cost {:5.2f}s'.format(end_t - start_t))

            if ret != 0:
                err_day.append(stock_info)
                continue
            else:
                code = resp['error_code']
                if code != 0:
                    print("获取日K异常")
                    err_day.append(stock_info)
                    continue

                data = resp['data']

                year_arr = []
                base_arr = []
                new_arr = []
                bonus_arr = []
                date_arr = []
                for x in data['items']:
                    y = x['dividend_year']
                    d = x['ashare_ex_dividend_date']
                    s = x['plan_explain']

                    pos = y.find('年')
                    year_arr.append(y[0:pos])

                    base, new, bonus = self.plan2digit(s)
                    base_arr.append(base)
                    new_arr.append(new)
                    bonus_arr.append(bonus)

                    date_str = time.strftime('%Y%m%d', time.localtime(d/1000))
                    date_arr.append(date_str)
                    
                df = pd.DataFrame(data['items'])
                df.insert(0, 'bonus', bonus_arr)
                df.insert(0, 'new', new_arr)
                df.insert(0, 'base', base_arr)
                df.insert(0, 'date', date_arr)
                df.insert(0, 'year', year_arr)
                #, 'bonus_date':[], 'base':[], 'new':[], 'bonus':[]})
                print('data -> pd')
                print(df)
                aaa = df.to_dict('records')
                data = sorted(aaa,key = lambda e:e.__getitem__('date'), reverse=True)

                # data -> pd
                # items[x].dividend_year -> year
                # items[x].equity_date or ashare_ex_dividend_date -> date
                # items[x].plan_explain -> base, new, bonus

                ref = self.col_bonus.find_one({ "ts_code": ts_code })

                if ref != None:
                    new_dic = {}
                    new_dic.update({'items':data})
                    newvalues = { "$set": new_dic}    
                    self.col_bonus.update_one({ "ts_code": ts_code }, newvalues)
                else:
                    new_dic = { "ts_code": ts_code }
                    new_dic.update({'items':data})
                    self.col_bonus.insert_one(new_dic)

                '''
                df = df.drop(['volume_post','amount_post'],axis=1)
                df.rename(columns={'timestamp':'trade_date'}, inplace=True)
                df['trade_date'] = df['trade_date'].apply(lambda x: datetime.datetime.fromtimestamp(int(x)/1000).strftime("%Y%m%d") )
                aaa = df.to_dict('records')
                data = sorted(aaa,key = lambda e:e.__getitem__('trade_date'), reverse=True)

                # begin of get_stock_trade
                stock_daily = data

                all_trade_daily = []
                data_count = len(stock_daily)

                if data_count == 0:
                    print(("获取异常 %s" %(ts_code)))
                    err_day.append(stock_info)
                    continue
            
                print('data_count ==', data_count)
                if data_count == 1:
                    item = stock_daily[0]

                    #?
                    trade_date = self.stringFromconvertDateType(stock_daily[0]['trade_date'],'%Y%m%d','%Y-%m-%d')#当天交易日期
                    all_trade_daily.append(item)

                else:
                    max_len = len(stock_daily)
                    for index,item in enumerate(stock_daily):
                        all_trade_daily.append(item)
                
                    all_trade_daily = sorted(all_trade_daily,key = lambda e:e.__getitem__('trade_date'), reverse=True)
                    trade_date = self.stringFromconvertDateType(all_trade_daily[0]['trade_date'],'%Y%m%d','%Y-%m-%d')#当天交易日期

                print('trade_date', trade_date)
                print('all_trade_daily')
                pprint(all_trade_daily)
                print()
                # end of get_stock_trade

                # inside funcaaaaa
                trade_kline = all_trade_daily

                stock_local_info = self.col_bonus.find_one({ "ts_code": ts_code })

                print('stock_local_info')
                pprint(stock_local_info)
                print()
                if stock_local_info != None:#本地数据库存在code
                    dt1={
                        'trade_daily':trade_kline,
                        'trade_date':trade_date,
                    }

                    new_dic = {}
                    new_dic.update(dt1)
                    print('new_dic')
                    pprint(new_dic)
                    print()

                    newvalues = { "$set": new_dic}    
                    self.col_bonus.update_one({ "ts_code": ts_code }, newvalues)
                    print('update_one')
                    print()
                else:
                    dt1={
                        'trade_daily':trade_kline,
                        'trade_date':trade_date
                    }
                    #本地数据库不存在code
                    stock_local_info = stock_info
                    stock_local_info.update(dt1)
                    print('stock_local_info')
                    pprint(stock_local_info)
                    print()

                    self.col_bonus.insert_one(stock_local_info)
                    print('insert_one')
                    print()
                '''
                    
        return err_day

    def req_url_retry(self, url, retry):
        while retry:
            try:
                retry = retry - 1
                r = requests.get(url, headers=self.header)
                r.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                print ("Http Error:",errh)
                continue
            except requests.exceptions.ConnectionError as errc:
                print ("Error Connecting:",errc)
                continue
            except requests.exceptions.Timeout as errt:
                print ("Timeout Error:",errt)
                continue
            except requests.exceptions.RequestException as err:
                print ("OOps: Something Else",err)
                continue
            resp = r.json()
            return 0, resp

        return 1, {}

    def func_req(self,all_stocks,all_stock_count):
        start_t = time.time()

        err_stock = self.req_all(all_stocks)

        if len(err_stock)>0:
            print(threading.current_thread().name, 'Error 1st', len(err_stock))
            err_stock = self.req_all(err_stock)
            if len(err_stock)>0:
                print(threading.current_thread().name, 'Error 2nd', err_stock)

        end_t = time.time()
        print('{} done {:.2f}s'.format(threading.current_thread().name, end_t - start_t))


    def getAllStockAvail(self,size_array_codes,all_stock_count): 
        threads = []  
        for index,small_codes_array in enumerate(size_array_codes):
            thre = threading.Thread(target=self.func_req, args=(small_codes_array,all_stock_count))   # 创建一个线程
            threads.append(thre)
            thre.start()  # 运行线程
        return threads

    def db_basicfind(self, code):
        if code == None:
            ref = self.col_basic.find()
        else:
            ref = self.col_basic.find_one({ 'ts_code': code })
        return ref
 
today_str = datetime.datetime.now().strftime('%Y%m%d')
t_str = time.strftime('%Y%m%d', time.localtime(time.time()))

def list_split(items,n):
    return [items[i:i+n] for i in range(0, len(items), n)]

def daily_update(all_stock_count,stock):
    bi = StockInfo()
    stock_arr =list_split(stock, 240)
    threads = bi.getAllStockAvail(stock_arr, all_stock_count)
    return threads
    
if __name__ == '__main__':
    si = StockInfo()

    #ref = si.db_basicfind('002475.SZ')
    ref = si.db_basicfind(None)
    if ref == None:
        print('Can\'t find ts_code:002475.SZ')
        exit()
    print('find in collection basic')
    print()

    all_stocks = []
    for x in ref:
        all_stocks.append(x)

    all_stock_count = len(all_stocks)
    all_stocks = [item for item in all_stocks if item['list_date'] <= today_str]
    print(("最新交易日期 ----- %s  股票数量： %s 个" %(today_str, len(all_stocks))))

    stock_arr = list_split(all_stocks, 480)

    start_t = time.time()
    threads_arr = []
    for index,stock in enumerate(stock_arr):
        stock_arr =list_split(stock, 240)
        threads = si.getAllStockAvail(stock_arr, all_stock_count)
        threads_arr.append(threads)
    for i in threads_arr:
        for j in i:
            j.join()
    end_t = time.time()

    print('total cost {:5.2f}s'.format(end_t - start_t))


