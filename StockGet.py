#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import snowtoken
from datetime import datetime, timedelta
import threading
import requests
import time
from pymongo import MongoClient
from pprint import pprint
import pandas as pd
import tushare as ts
import sys

class StockGet:
    def __init__(self):
        self.today_str = datetime.now().strftime('%Y%m%d')
        self.today_dt= datetime.strptime(self.today_str,'%Y%m%d')

        dayline_str = '20160101'
        #dayline_str = self.today_str
        self.dateTimp = str(int(datetime.timestamp(datetime.strptime(dayline_str, '%Y%m%d'))*1000))

        client = MongoClient(port=27017)
        db = client.stk1

        self.col_basic = db.basic
        self.col_bonus = db.bonus
        self.col_day = db.day
        self.col_token = db.token

        self.stock_list = []
        
        t = self.updateToken(5)
        self.header = {
            'cookie':'xq_is_login=1;xq_a_token=' + t,
            'User-Agent': 'Xueqiu iPhone 13.6.5'
        }

        self.func_name = ''
        return

    def updateToken(self, valid_days):
        ref = self.col_token.find_one()
        if ref == None:
            t = snowtoken.get_snowtoken()
            new_dic = {'token':t, 'date':self.today_str}
            self.col_token.insert_one(new_dic)
            print('new token', t)
        else:
            token_date = datetime.strptime(ref['date'],'%Y%m%d')
            date_len = self.today_dt - token_date
            if date_len.days <= valid_days:
                t = ref['token']
                print('token in', date_len.days, 'days', t)
            else:
                t = snowtoken.get_snowtoken()
                print('token expired, update', t)
                new_dic = {'token':t, 'date':self.today_str}
                newvalues = { "$set": new_dic}    
                self.col_token.update_one({'_id' : ref.get('_id')}, newvalues)
        return t

    # go-to-market days
    def get_stock_trade_days(self,list_date):
        list_date_temp = datetime.strptime(list_date,'%Y%m%d')
        date_len = self.today_dt-list_date_temp
        return date_len.days

    def find_eof_digit(self, s, pos):
        i=0
        while s[pos+1+i].isdigit() or s[pos+1+i]=='.':
            i+=1
        return i

    # bonus plan2digit
    # ex: 10送4股转4股派1元，流通A股股东10转5.149022股,B股股东10转1.5股(实施方案)
    def plan2digit(self, s):
        base, free, new, bonus = 0,0,0,0

        free_pos =  s.find('送')
        if free_pos != -1:
            free_gu_pos =  s.find('股', free_pos)
            if free_gu_pos != -1:
                free = s[free_pos+1:free_gu_pos]
                
                d_pos = free.find('转') #10送6转增4股(实施方案)
                if d_pos != -1:
                    free = free[0:d_pos]
            else:
                print('bonus plan error: 送 without 股', s)

        new_pos =  s.find('转')
        if new_pos != -1:
            new_gu_pos =  s.find('股', new_pos)
            if new_gu_pos != -1:
                if s[new_pos+1] == '增':
                    new = s[new_pos+2:new_gu_pos]
                else:
                    new = s[new_pos+1:new_gu_pos]
            else:
                d_num = self.find_eof_digit(s, new_pos)
                if d_num == 0:
                    print('bonus plan error: 转 without 股 and no digit follow', s)
                else:
                    new = s[new_pos+1:new_pos+1+d_num]

        bonus_pos =  s.find('派')
        if bonus_pos != -1:
            bonus_gu_pos =  s.find('元', bonus_pos)
            if bonus_gu_pos != -1:
                bonus = s[bonus_pos+1:bonus_gu_pos]
            else:
                print('bonus plan error: 派 without 元', s)

        if free_pos == -1 and new_pos == -1 and bonus_pos == -1:
            print('bonus plan error: not find 送转派', s)
        else:
            if free_pos == -1: free_pos = 100
            if new_pos == -1:  new_pos = 100
            if bonus_pos == -1: bonus_pos = 100
            base = s[0:min( free_pos, new_pos, bonus_pos)]

            if base != '10': #流通股股东每10股
                d_pos = base.find('股东')
                if d_pos != -1:
                    base = base[d_pos+2:]
                else:
                    d_pos = base.find('股')
                    if d_pos != -1:
                        base = base[0:d_pos]
                    else:
                        print('bonus plan error: unknown base', s)

        return base, free, new, bonus

    def req_basic(self):
        ts.set_token('0603f0a6ce3d7786d607e65721594ed0d1c23b41d6bc82426d7e4674')
        self.pro = ts.pro_api()
        df = singleObjc.pro.stock_basic(exchange='',fields='ts_code,symbol,name,industry,list_date,list_status,delist_date')
        #all_stocks = df.rename(columns={'industry': 'hy'}).to_dict('records')
        all_stocks = df.to_dict('records')
        ret = col.insert_many(all_stocks)

    def req_bonus(self, all_stocks):
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

            ret, resp = self.req_url_retry(url, 3)
            if ret != 0:
                err_day.append(stock_info)
                continue

            code = resp['error_code']
            if code != 0:
                print("Get bonus error", ts_code_symbol, code)
                err_day.append(stock_info)
                continue

            data = resp['data']

            year_arr = []
            base_arr = []
            free_arr = []
            new_arr = []
            bonus_arr = []
            date_arr = []
            for x in data['items']:
                y = x['dividend_year']
                d = x['ashare_ex_dividend_date']
                s = x['plan_explain']

                pos = y.find('年')
                year_arr.append(y[0:pos])

                base, free, new, bonus = self.plan2digit(s)
                base_arr.append(base)
                free_arr.append(free)
                new_arr.append(new)
                bonus_arr.append(bonus)

                if d != None:
                    date_str = datetime.strftime(datetime.fromtimestamp(d/1000), '%Y%m%d')
                    date_arr.append(date_str)
                else: #has plan but no date yet
                    date_arr.append('00000000')
                
            #print('data -> pd', ts_code_symbol, len(data['items']), data.keys())
            df = pd.DataFrame(data['items'])
            if len(data['items']) != 0:# some new stock has no dividend info
                df.insert(0, 'bonus', bonus_arr)
                df.insert(0, 'new', new_arr)
                df.insert(0, 'free', free_arr)
                df.insert(0, 'base', base_arr)
                df.insert(0, 'date', date_arr)
                df.insert(0, 'year', year_arr)
                df = df.drop(['ashare_ex_dividend_date', 'equity_date', 'cancle_dividend_date'],axis=1)
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

    def req_day(self, all_stocks):
        req_days = 365*5+10
        err_day = []

        for index,stock_info in enumerate(all_stocks):
            ret = 0
            ts_code = stock_info['ts_code']
            list_days = self.get_stock_trade_days(stock_info['list_date'])# #获取股票上市时长

            if ts_code == None:
                print('ts_code == None')
                continue
            ts_code_arr = ts_code.split(".", 1)
            ts_code_symbol=ts_code_arr[1]+ts_code_arr[0]

            ref = self.col_day.find_one({ "ts_code": ts_code })
            if ref != None:
                print('find', ts_code)
                stk_days = len(ref['day'])
                last_date = ref['day'][0]['date']
                early_date = ref['day'][stk_days-1]['date']

                last_dateTimp = str(int(datetime.timestamp(datetime.strptime(last_date, '%Y%m%d')+timedelta(days=1))*1000))
                new_req_days = self.get_stock_trade_days(last_date)
                print(last_date, '-', early_date)
                print('try to get', last_date, new_req_days, 'days')

                url="https://stock.xueqiu.com/v5/stock/chart/kline.json?period=day&type=none&count="+str(new_req_days)+"&symbol="+ts_code_symbol+"&begin="+last_dateTimp
            else:
                url="https://stock.xueqiu.com/v5/stock/chart/kline.json?period=day&type=none&count="+str(req_days)+"&symbol="+ts_code_symbol+"&begin="+self.dateTimp
            print(url)

            ret, resp = self.req_url_retry(url, 3)
            if ret != 0:
                err_day.append(stock_info)
                continue

            code = resp['error_code']
            if code != 0:
                print("Get day kline error", ts_code_symbol, code)
                err_day.append(stock_info)
                continue

            stock_daily = resp['data']
            if len(stock_daily['item']) == 0:
                print("No kline, maybe restday", ts_code_symbol)
                continue
            df = pd.DataFrame(stock_daily['item'], columns=stock_daily['column'])
            df = df.drop(['volume_post','amount_post'],axis=1)
            df.rename(columns={'timestamp':'date'}, inplace=True)
            df['date'] = df['date'].apply(lambda x: datetime.fromtimestamp(int(x)/1000).strftime("%Y%m%d") )

            aaa = df.to_dict('records')
            data = sorted(aaa,key = lambda e:e.__getitem__('date'), reverse=True)

            all_trade_daily = []
            for index,item in enumerate(data):
                all_trade_daily.append(item)
            all_trade_daily = sorted(all_trade_daily,key = lambda e:e.__getitem__('date'), reverse=True)

            if ref != None:
                dt1={
                    'day':{ '$each': all_trade_daily, '$sort':{'date':-1} }
                }
                new_dic = {}
                new_dic.update(dt1)
                newvalues = { "$push": new_dic}
                self.col_day.update_one({ "ts_code": ts_code }, newvalues)
                self.col_day.update_one({ "ts_code": ts_code }, {"$set":{'list_days':list_days}})
            else:
                new_dic = stock_info
                dt1={
                    'day':all_trade_daily,
                    'list_days':list_days
                }
                new_dic.update(dt1)
                self.col_day.insert_one(new_dic)
                    
        return err_day

    def req_url_retry(self, url, retry):
        start_t = time.time()
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
            end_t = time.time()
            #print('req_url_retry cost {:5.2f}s'.format(end_t - start_t))
            return 0, resp

        end_t = time.time()
        print('req_url_retry cost {:5.2f}s'.format(end_t - start_t))
        return 1, {}

    def func_req(self,all_stocks):
        start_t = time.time()
        req_func = self.map_req(self.func_name)
        err_stock = req_func(all_stocks)
        if len(err_stock)>0:
            print(threading.current_thread().name, 'Error', len(err_stock), err_stock)
        end_t = time.time()
        print('{} cost {:.2f}s'.format(threading.current_thread().name, end_t - start_t))

    def get_stocks(self, thread_num):
        if len(self.stock_list) == 0: return []

        #stock_arr = list_split(self.stock_list[0:1], thread_num)
        stock_arr = list_split(self.stock_list, thread_num)

        threads = []  
        for index,small_codes_array in enumerate(stock_arr):
            thre = threading.Thread(target=self.func_req, args=(small_codes_array,))   # 创建一个线程
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

    def req_default(self):
        return

    def map_req(self, name):
        req_name = "req_" + str(name)
        fun = getattr(self, req_name, self.req_default)
        return fun

    def set_func(self, name):
        self.func_name = name
 
def list_split(items,n):
    return [items[i:i+n] for i in range(0, len(items), n)]

if __name__ == '__main__':

    if len(sys.argv)!=2:
        print('update_stock [basic|bonus|day]')
        quit()

    si = StockGet()
    if sys.argv[1] == 'basic':
        si.req_basic()
        quit()

    if sys.argv[1] == 'bonus' or sys.argv[1] == 'day':
        si.set_func(sys.argv[1])

    #ref = si.db_basicfind('002475.SZ')
    ref = si.db_basicfind(None)
    if ref == None:
        print('Not found stock list')
        exit()

    start_t = time.time()
    threads = si.get_stocks(240)
    for i in threads:
        i.join()
    end_t = time.time()

    print('total cost {:5.2f}s'.format(end_t - start_t))
