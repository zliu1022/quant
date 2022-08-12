#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockSingle import StockSingle
from StockRequest import StockRequest
import datetime
import threading
import requests
import time

from pymongo import MongoClient
from random import randint
from pprint import pprint

import pandas as pd
import numpy as np

def RD(N,D=3):   return np.round(N,D)        #四舍五入取3位小数
def ABS(S):      return np.abs(S)            #返回N的绝对值

class StockInfo:
    def __init__(self):
        client = MongoClient(port=27017)
        db = client.stk1

        self.col_bonus = db.bonus
        self.col_baseinfo = db.baseinfo
        self.col_day = db.day

        self.dateTimp = str(int(time.time()*1000))
        t = 'bf75ab4bcea18c79de253cb841f2b27e248d8948'
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

    #近N日振幅是否小于20%
    def isWaveLow20ForDateCount(self,close,count,sourceData,percent=0.8):        # #如果存在大于当日价格的，则是非新高，所以数值要取非
        df1 = pd.DataFrame(sourceData)
        if len(df1)<=count+20:
            return 0
        close_max = df1[1:count+1].close.max()
        close_min = df1[1:count+1].close.min()
        if close_min >= (close_max*percent):
            return 1
        return 0

    def isLimitUpOrDown(self,ts_code,close,last_close,percent):
        mark_pect = 0.1
        if ts_code.startswith("300") or ts_code.startswith("688"):
            mark_pect = 0.2 #
        if ts_code.startswith("*S"):
            mark_pect = 0.05 #
        if ts_code.endswith("BJ"):
            mark_pect = 0.3 #
        if close >= last_close:
            #涨
            limit_close = RD(last_close*(1+mark_pect),2) #四舍五入保留两位小数
            limit_close_price = RD(last_close*mark_pect,2) #四舍五入保留两位小数
            limit_percent= RD(float(limit_close_price/last_close)*100,2)
            if close == limit_close and percent == limit_percent:
                return 1
            else:
                return 0
        else:
            #跌
            limit_close = RD(last_close*(1-mark_pect),2) #四舍五入保留两位小数
            limit_close_price = RD(last_close*mark_pect,2) #四舍五入保留两位小数
            limit_percent= RD(float(limit_close_price/last_close)*100,2)

            if close == limit_close and ABS(percent) == ABS(limit_percent):
                return -1
            else:
                return 0


    def isNewHighForDateCount(self,close,count,sourceData):        # #如果存在大于当日价格的，则是非新高，所以数值要取非
        df1 = pd.DataFrame(sourceData)
        close_max = df1[0:count].close.max()
        if close >= close_max:
            return 1
        return 0

    #获取股票上市时长
    def get_stock_trade_days(self,list_date):
        list_date_temp = datetime.datetime.strptime(list_date,'%Y%m%d')
        date_len=self.today_dt-list_date_temp
        return date_len.days

    def initDailyItem(self,item):
        temp=item
        '''
        temp['isYearHigh']=0
        temp['is20High']=0
        temp['is60High']=0
        temp['is120High']=0
        temp['is20Wave']= -100
        temp['avail_5']= -100
        temp['avail_20']= -100
        temp['avail_60']= -100
        temp['avail_250']=-100
        temp['net_mf_amount']="0万"
        temp['buy_elg_amount']="0万"
        temp['buy_elg_percent']="0%"
        '''
        return temp

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
            '''
            url = "https://stock.xueqiu.com/v5/stock/quote.json?symbol="+ts_code_symbol+"&extend=detail"
            ret, resp = self.req_url(url)
            if ret != 0:
                err.append(stock_info)
                continue
            else:
                code=resp['error_code']
            '''

            '''
            url = "https://stock.xueqiu.com/v5/stock/f10/cn/bonus.json?&symbol=" +ts_code_symbol
            ret, resp = self.req_url(url)
            if ret != 0:
                err.append(stock_info)
                continue
            else:
                code=resp['error_code']
            '''

            #stock_daily=self.xueqiu.requestXueQiuDaily(ts_code)
            url="https://stock.xueqiu.com/v5/stock/chart/kline.json?period=day&type=before&count=-3&symbol="+ts_code_symbol+"&begin="+self.dateTimp
            begin_t = time.time()
            ret, resp = self.req_url(url)
            end_t = time.time()
            print('req_url cost {:5.2f}s'.format(end_t - start_t))

            if ret != 0:
                err.append(stock_info)
                continue
            else:
                code = resp['error_code']
                if code != 0:
                    print("获取日K异常")
                    err.append(stock_info)
                    continue

                stock_daily = resp['data']
                if len(list(stock_daily.keys()))<=0:
                    print("不存在K线")
                    err.append(stock_info)
                    continue

                # begin of requestXueQiuDaily
                column = stock_daily['column']
                item= stock_daily['item']
                print('item= stock_daily[item]')
                pprint(item)
                print()

                #?
                df = pd.DataFrame(item,columns=column)
                df = df.drop(['volume_post','amount_post'],axis=1)

                # 涨跌金额
                #df.rename(columns={'timestamp':'trade_date','volume':'vol','chg':'pct_chg','turnoverrate':'huanshou'}, inplace=True)
                df.rename(columns={'timestamp':'trade_date'}, inplace=True)

                #?
                df['trade_date'] = df['trade_date'].apply(lambda x: datetime.datetime.fromtimestamp(int(x)/1000).strftime("%Y%m%d") )
                print('item to pandas DataFrame, drop volume_post and amount_post, rename and change timestamp to trade_date')
                print(df)
                print()

                #?
                aaa = df.to_dict('records')
                print('df.to_dict(records)')
                pprint(aaa)
                print()

                #?
                data = sorted(aaa,key = lambda e:e.__getitem__('trade_date'), reverse=True)
                print('sorted trade_date')
                pprint(data)
                print()

                # end of requestXueQiuDaily

                list_date_days = self.get_stock_trade_days(stock_info['list_date'])# #获取股票上市时长
                # begin of get_stock_trade
                #stock_daily=self.xueqiu.requestXueQiuDaily(ts_code)
                stock_daily = data

                all_trade_daily = []
                data_count = len(stock_daily)

                if data_count == 0:
                    print(("获取异常 %s" %(ts_code)))
                    err.append(stock_info)
                    continue
            
                print('data_count ==', data_count)
                if data_count == 1:
                    item = self.initDailyItem(stock_daily[0])

                    #?
                    trade_date = self.stringFromconvertDateType(stock_daily[0]['trade_date'],'%Y%m%d','%Y-%m-%d')#当天交易日期
                    all_trade_daily.append(item)

                else:
                    max_len = len(stock_daily)
                    for index,item in enumerate(stock_daily):
                        item=self.initDailyItem(item)
                        close=item['close']

                        '''
                        if index == 0 : 
                            item.update(amount)

                        if index<3 and len(stock_daily)>=255:    
                            item['avail_5']= close/stock_daily[5]['close']-1
                            item['avail_20']= close/stock_daily[20]['close']-1
                            item['avail_60']= close/stock_daily[60]['close']-1
                            item['avail_250']= close/stock_daily[250]['close']-1
                            item['is20High'] = self.isNewHighForDateCount(close,20,stock_daily)
                            item['is20Wave'] = self.isWaveLow20ForDateCount(close,20,stock_daily,0.8)

                        if index<20 and list_date_days>250:   
                            item['isYearHigh'] = self.isNewHighForDateCount(close,250,stock_daily)

                        if index<6 and list_date_days>250:    
                            if index <= max_len-2:
                                last_close = stock_daily[index+1]['close']
                                percent=item['percent']
                                item['limit_status']= self.isLimitUpOrDown(ts_code,close,last_close,percent)
                        '''
                
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

                stock_local_info = self.col_day.find_one({ "ts_code": ts_code })

                print('stock_local_info')
                pprint(stock_local_info)
                print()
                if stock_local_info != None:#本地数据库存在code
                    dt1={
                        'trade_daily':trade_kline,
                        'list_date_days':list_date_days,
                        'trade_date':trade_date,
                    }

                    new_dic = {}
                    new_dic.update(dt1)
                    print('new_dic')
                    pprint(new_dic)
                    print()

                    newvalues = { "$set": new_dic}    
                    self.col_day.update_one({ "ts_code": ts_code }, newvalues)
                    print('update_one')
                    print()
                else:
                    dt1={
                        'trade_daily':trade_kline,
                        'list_date_days':list_date_days,
                        'trade_date':trade_date
                    }
                    #本地数据库不存在code
                    stock_local_info = stock_info
                    stock_local_info.update(dt1)
                    print('stock_local_info')
                    pprint(stock_local_info)
                    print()

                    self.col_day.insert_one(stock_local_info)
                    print('insert_one')
                    print()
                    
            #amount = self.xueqiu.requestAmountInflow(ts_code)
            '''
            if "BJ" in ts_code:
                continue
            url="https://stock.xueqiu.com/v5/stock/capital/distribution.json?symbol="+ts_code_symbol
            ret, resp = self.req_url(url)
            if ret != 0:
                err.append(stock_info)
                continue
            else:
                code=resp['error_code']
            '''

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
 
today_mt_string= datetime.datetime.now().strftime('%Y%m%d')

#将数组分割成8个数组 并行操作

def list_split(items,n):
    return [items[i:i+n] for i in range(0, len(items), n)]

def stock_daily_update(all_stock_count,stocks):
    bi = StockInfo()
    size_array_stosks =list_split(stocks,240)
    threads = bi.getAllStockAvail(size_array_stosks,all_stock_count)
    return threads
    
if __name__ == '__main__':
    print('testing mongodb')
    print('insert daily line or update daily line')
    print()
    print('use following command to check:')
    print('show dbs')
    print('use stk1')
    print('show collections')
    print('db.day.find({\'ts_code\': \'002475.SZ\'})')
    print('db.basic.find({\'ts_code\': \'002475.SZ\'})')
    print()
    
    client = MongoClient(port=27017)
    db = client.stk1

    col = db.basic
    # 从tushare获取全部stock列表
    '''
    singleObjc = StockSingle()
    df = singleObjc.pro.stock_basic(exchange='',fields='ts_code,symbol,name,industry,list_date,list_status')
    all_stocks = df.rename(columns={'industry': 'hy'}).to_dict('records')
    ret = col.insert_many(all_stocks)
    quit()
    '''

    ref = col.find_one( {'ts_code':'002475.SZ'} )
    if ref == None:
        print('Can\'t find ts_code:002475.SZ')
        exit()
    print('find ts_code:002475.SZ in collection basic')
    #print(ref)
    print()

    all_stocks = []
    all_stocks.append(ref)
    #print(type(all_stocks), all_stocks)
    
    all_stock_count = len(all_stocks)
    all_stocks = [item for item in all_stocks if item['list_date'] <= today_mt_string]
    print(("最新交易日期 ----- %s  股票数量： %s 个" %(today_mt_string, len(all_stocks))))

    size_array_stosks = list_split(all_stocks, 480)

    start_t = time.time()
    threads_arr = []
    for index,stocks in enumerate(size_array_stosks):
        threads = stock_daily_update(all_stock_count,stocks)
        threads_arr.append(threads)
    for i in threads_arr:
        for j in i:
            j.join()
    end_t = time.time()

    print('total cost {:5.2f}s'.format(end_t - start_t))

