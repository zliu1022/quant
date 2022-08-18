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
        self.today_str = datetime.datetime.now().strftime('%Y%m%d')
        self.today_dt= datetime.datetime.strptime(self.today_str,'%Y%m%d')

        client = MongoClient(port=27017)
        db = client.stk1

        self.col_basic = db.basic
        self.col_bonus = db.bonus
        self.col_baseinfo = db.baseinfo
        self.col_day = db.day

        ref = db.token.find_one()
        if ref == None:
            print('no token in db')
            t = snowtoken.get_snowtoken()
            new_dic = {'token':t, 'date':self.today_str}
            db.token.insert_one(new_dic)
        else:
            token_date = datetime.datetime.strptime(ref['date'],'%Y%m%d')
            date_len = self.today_dt - token_date
            if date_len.days <3:
                print('get token in', date_len.days, 'days in db')
                t = ref['token']
            else:
                print('update token in db')
                t = snowtoken.get_snowtoken()
                new_dic = {'token':t, 'date':self.today_str}
                newvalues = { "$set": new_dic}    
                db.token.update_one({'_id' : ref.get('_id')}, newvalues)

        #t = '28ed0fb1c0734b3e85f9e93b8478033dbc11c856'
        self.header = {
            'cookie':'xq_is_login=1;xq_a_token=' + t,
            'User-Agent': 'Xueqiu iPhone 13.6.5'
        }

        self.stock_list = []
        return

    def stringFromconvertDateType(self,date,oldType,newType):
        temp_string=""
        if isinstance(date,str):
            temp_date = datetime.datetime.strptime(date,oldType)
            temp_string = temp_date.strftime(newType)
        else:
            temp_string = date.strftime(newType)
        return temp_string

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

            start_t = time.time()
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

                    if d != None:
                        date_str = time.strftime('%Y%m%d', time.localtime(d/1000))
                        date_arr.append(date_str)
                    else:
                        print('d error', ts_code_symbol)
                        date_arr.append('00000000')
                    
                df = pd.DataFrame(data['items'])
                df.insert(0, 'bonus', bonus_arr)
                df.insert(0, 'new', new_arr)
                df.insert(0, 'base', base_arr)
                df.insert(0, 'date', date_arr)
                df.insert(0, 'year', year_arr)

                # some new stock has no dividend info
                if len(data['items']) != 0:
                    df = df.drop(['ashare_ex_dividend_date', 'equity_date', 'cancle_dividend_date'],axis=1)

                print('data -> pd', ts_code_symbol, len(data['items']), data.keys())
                print(df)
                aaa = df.to_dict('records')
                data = sorted(aaa,key = lambda e:e.__getitem__('date'), reverse=True)

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

        return err_day

    def req_url_retry(self, url, retry):
        ori = retry - 1
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

            if retry != ori:
                print('retry', ori-retry, 'times', url)
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
        print('{} cost {:.2f}s'.format(threading.current_thread().name, end_t - start_t))


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
            if ref != None:
                self.stock_list = []
                for x in ref:
                    self.stock_list.append(x)
        else:
            ref = self.col_basic.find_one({ 'ts_code': code })
            if ref != None:
                self.stock_list = []
                self.stock_list.append(ref)
        return ref
 
def list_split(items,n):
    return [items[i:i+n] for i in range(0, len(items), n)]

if __name__ == '__main__':
    si = StockInfo()

    #ref = si.db_basicfind('002475.SZ')
    ref = si.db_basicfind(None)

    if ref == None:
        print('Not found stock list')
        exit()
    print('Found stock list')
    all_stocks = si.stock_list
    all_stock_count = len(all_stocks)

    all_stocks = [item for item in all_stocks if item['list_date'] <= si.today_str]
    print('all stock', all_stock_count)
    print(("list_data <= %s %s" %(si.today_str, len(all_stocks))))

    stock_arr = list_split(all_stocks, 480)

    start_t = time.time()
    threads_arr = []
    for index,stock in enumerate(stock_arr):
        stock_arr = list_split(stock, 240)
        threads = si.getAllStockAvail(stock_arr, all_stock_count)
        threads_arr.append(threads)
    for i in threads_arr:
        for j in i:
            j.join()
    end_t = time.time()

    print('total cost {:5.2f}s'.format(end_t - start_t))

