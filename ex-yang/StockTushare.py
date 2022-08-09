# -*- coding:utf-8 -*-
import sys,os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,BASE)
from StockSingle import StockSingle
from StockRequest import StockRequest
from pymongo import MongoClient
from threading import Thread
import datetime
import time
import pandas as pd
import numpy as np; 


def RD(N,D=3):   return np.round(N,D)        #四舍五入取3位小数 
def ABS(S):      return np.abs(S)            #返回N的绝对值

ROOT_PATH=os.path.abspath(os.path.dirname(os.getcwd()))
the_day = '20210820'  #截至计算时间

class StockTushare:
    def __init__(self):
        self.u_index=0
        #使用之前先输入token，可以从个人主页上复制出来，
        #每次调用数据需要先运行该命令
        singleObjc = StockSingle()
        self.pro = singleObjc.pro
        self.today_String = datetime.datetime.now().strftime('%Y-%m-%d')
        self.today_dt= datetime.datetime.strptime(self.today_String,'%Y-%m-%d')
        self.today_mt_string= datetime.datetime.now().strftime('%Y%m%d')
        self.today_mt=datetime.datetime.strptime(self.today_mt_string, '%Y%m%d')   
        self.lastyear_date=self.today_mt-datetime.timedelta(days=365)
        self.lastyear_date_str=datetime.datetime.strftime(self.lastyear_date, '%Y%m%d')  
        self.client = MongoClient('mongodb://127.0.0.1:27017/')
        self.db = self.client.tushare
        self.stock_basic_aa = self.db['stock_basic_aa']
        self.xueqiu=StockRequest()
        
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
        list_date_temp=datetime.datetime.strptime(list_date,'%Y%m%d')
        date_len=self.today_dt-list_date_temp
        return date_len.days
    
    #是否新高
    def isNewHighForDateCount(self,close,count,sourceData):        # #如果存在大于当日价格的，则是非新高，所以数值要取非
        
        df1 = pd.DataFrame(sourceData)
        close_max = df1[0:count].close.max()
        if close >= close_max:
            return 1
        return 0
    
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
            

    
    def initDailyItem(self,item):
        temp=item
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

        return temp
    
    #检测股票日K线数据
    def get_stock_trade(self,ts_code,list_date_days):
        
        stock_daily=self.xueqiu.requestXueQiuDaily(ts_code)
        all_trade_daily=[]
        data_count=len(stock_daily)

        if data_count == 0:
            print(("获取异常 %s" %(ts_code)))
            return [self.today_String,all_trade_daily]
    
        amount = self.xueqiu.requestAmountInflow(ts_code)

        if data_count == 1:
            item=self.initDailyItem(stock_daily[0])
            item.update(amount)
            trade_date = self.stringFromconvertDateType(stock_daily[0]['trade_date'],'%Y%m%d','%Y-%m-%d')#当天交易日期
            all_trade_daily.append(item)
            return [trade_date,all_trade_daily]
        
        for index,item in enumerate(stock_daily):
            item=self.initDailyItem(item)
            close=item['close']
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
                last_close=stock_daily[index+1]['close']
                percent=item['percent']
                item['limit_status']= self.isLimitUpOrDown(ts_code,close,last_close,percent)
            
            all_trade_daily.append(item)
            
        all_trade_daily = sorted(all_trade_daily,key = lambda e:e.__getitem__('trade_date'), reverse=True)
        trade_date = self.stringFromconvertDateType(all_trade_daily[0]['trade_date'],'%Y%m%d','%Y-%m-%d')#当天交易日期
        return [trade_date,all_trade_daily]
    
    def funcaaaaa(self,all_stocks,all_stock_count,singleObjc):
        
        for index,stock_info in enumerate(all_stocks):  

            start_time_0 = time.time()
            ts_code = stock_info['ts_code']
            ts_status = stock_info['list_status']
            stock_local_info = self.stock_basic_aa.find_one({ "ts_code": ts_code })
            
            base_info = self.xueqiu.requestXueQiuBaseInfo(ts_code)#基础信息
            list_date_days=self.get_stock_trade_days(stock_info['list_date'])# #获取股票上市时长
            trade_info = self.get_stock_trade(ts_code,list_date_days)#获取起始日期到最新一天的交易数据
                
            trade_date =trade_info[0] #当天交易日期
            trade_kline =trade_info[1]
            chicang = None #self.xueqiu.requestORGFor(ts_code)#获取基金持仓 每月请求一次即可
            
            if stock_local_info != None:#本地数据库存在code
                #更新本地 交易K线，上市日期、持仓数据
                dt1={
                    'trade_daily':trade_kline,
                    'list_date_days':list_date_days,
                    'trade_date':trade_date,
                    'status':ts_status,
                    'hy3':""
                }
                
                if not "hy" in stock_local_info.keys():
                    bankuai_info = self.xueqiu.requestBankuaiDaily(ts_code)#新股获取板块信息
                    dt1['hy']=bankuai_info['hy']
                
                new_dic = {}
                new_dic.update(dt1)
                new_dic.update(base_info)

                if chicang!=None:
                    new_dic.update(chicang)
                newvalues = { "$set": new_dic}    
                self.stock_basic_aa.update_one({ "ts_code": ts_code }, newvalues)
            else:
                bankuai_info = self.xueqiu.requestBankuaiDaily(ts_code)#新股获取板块信息
                dt1={
                    'trade_daily':trade_kline,
                    'hy':bankuai_info['hy'],
                    'hy2':bankuai_info['hy2'],
                    'hy3':"",
                    'list_date_days':list_date_days,
                    'trade_date':trade_date
                }
                #本地数据库不存在code
                stock_local_info = stock_info
                stock_local_info.update(dt1)
                stock_local_info.update(base_info)
                if chicang!=None:
                    stock_local_info.update(chicang)
                self.stock_basic_aa.insert_one(stock_local_info)
                
            stop_time_0 = time.time()
            cost_0 = stop_time_0 - start_time_0
            singleObjc.uindex = singleObjc.uindex+1
            singleObjc.haoshi += cost_0
            print("更新 %s %s 第 %s - %s 个 耗时 %s" %(ts_code,stock_info['name'],str(all_stock_count),str(singleObjc.uindex),cost_0))

            if singleObjc.uindex == all_stock_count:
                print("更新完成 总耗时 %s" %(singleObjc.haoshi/20))
                
    def getAllStockAvail(self,size_array_codes,all_stock_count,singleObjc): 
        threads = []  
        for index,small_codes_array in enumerate(size_array_codes):
            thre = Thread(target=self.funcaaaaa, args=(small_codes_array,all_stock_count,singleObjc))   # 创建一个线程
            threads.append(thre)
            thre.start()  # 运行线程
    
   
    def updateBK(self):
        print(" 同花顺数据 ")
        aa = self.pro.ths_index(exchange='A',type='I')
        bb = aa.to_dict(orient='records')
        print(aa)
        print(aa.ts_code.values[0:76])
        print(bb[0])
        
        all_count_1=0
        all_count_2=0
        aaaaaa =[]
        for index,ti_info in enumerate(bb):
            ti_code = ti_info['ts_code']
            ti_name = ti_info['name']
            if index <= 75:
                a = self.pro.ths_member(ts_code=ti_code)
                b = a.to_dict(orient='records')
                all_stocks = [item['code'] for item in b]
                print("%s 二级板块 %s :%s 包含股票数 %s" %(index,ti_name,ti_code,len(all_stocks)))
                a_count=0
                for ts_code in all_stocks:
                    if ts_code in aaaaaa:
                        continue
                    all_count_1+=1
                    aaaaaa.append(ts_code)
                    stock_local_info = self.stock_basic_aa.find_one({ "ts_code": ts_code })
                    if stock_local_info:
                        a_count+=1
                        new_dic = {'hy':ti_name,'hy3':""}                       
                        newvalues = { "$set": new_dic }    
                        self.stock_basic_aa.update_one({ "ts_code": ts_code }, newvalues)
                print("数据库更新完成 %s个" %(a_count))
                time.sleep(0.5)
            else:
                a = self.pro.ths_member(ts_code=ti_code)
                b = a.to_dict(orient='records')
                all_stocks = [item['code'] for item in b]
                print("%s 三级级板块 %s :%s 包含股票数 %s" %(index,ti_name,ti_code,len(all_stocks)))
                all_count_2+=len(all_stocks)

                a_count=0
                for ts_code in all_stocks:
                    stock_local_info = self.stock_basic_aa.find_one({ "ts_code": ts_code })
                    if stock_local_info:
                        a_count+=1
                        new_dic = {'hy2':ti_name,'hy3':""}                       
                        newvalues = { "$set": new_dic }    
                        self.stock_basic_aa.update_one({ "ts_code": ts_code }, newvalues)
                print("数据库更新完成 %s个" %(a_count))
                time.sleep(0.5)
        
        print("所有一级股票数 %s" %(all_count_1))
        print("所有二级股票数 %s" %(all_count_2))
       
           