#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import time
import requests
import pandas as pd


class StockRequest:
    def __init__(self):
        self.dateTimp = str(int(time.time()*1000)) 
        t = '85d28de63e47f8f25f268fba6aad231c1ec43eb0'
        t = 'bf75ab4bcea18c79de253cb841f2b27e248d8948'
        self.header = {
            'cookie':'xq_is_login=1;xq_a_token=' + t,
            'User-Agent': 'Xueqiu iPhone 13.6.5'
        }
    
    #获取机构持仓比例
    def requestORGFor(self,ts_code):
        if ts_code == None:
            return {}
        ts_code_arr = ts_code.split(".", 1)
        ts_code_symbol=ts_code_arr[1]+ts_code_arr[0]
        url="http://stock.xueqiu.com/v5/stock/f10/cn/org_holding/detail.json?count=50&symbol="+ts_code_symbol
        r = requests.get(url,headers=self.header)
        
        response = r.json()
        code=response['error_code']
        if code != 0:
            print("获取基金异常")
            return {}
        chicang=response['data']
        if not len(chicang) > 0:
            return {}
        temp={}
        #基金持仓
        jijin_org=chicang['fund_items']
        if len(jijin_org) == 0:
            temp['jijin_ORG']=0.0
        else:
            temp['jijin_ORG']=jijin_org[0]["to_float_shares_ratio"]
            
        #社保持仓
        temp['shebao_ORG']=0.0
        if 'social_items' in list(chicang.keys()):
            shebao_org=chicang['social_items']  
            if len(shebao_org) == 0:
                temp['shebao_ORG']=0.0
            else:
                temp['shebao_ORG']=shebao_org[0]["to_float_shares_ratio"]  
                    
        #其他持仓，包含香港中央结算
        temp['hk_ORG']=0.0
        if 'other_items' in list(chicang.keys()):
            other_org=chicang['other_items']
            if len(other_org) == 0:
                temp['hk_ORG']=0.0
            else:
                for dic in other_org:
                    if "香港中央结算有限公司" in list(dic.values()):
                        temp['hk_ORG']=dic["held_num"] 
                        break 
                    else:
                        temp['hk_ORG']=0.0    
        #外资持仓比例
        temp['qfii_ORG']=0.0
        if 'qfii_items' in list(chicang.keys()):
            qfii_org=chicang['qfii_items']
            if len(qfii_org) == 0:
                temp['qfii_ORG']=0.0
            else:
                temp['qfii_ORG']=qfii_org[0]["to_float_shares_ratio"]  
            return  temp    






    def requestXueQiuDaily(self,ts_code):
        if ts_code == None:
            return {}

        ts_code_arr = ts_code.split(".", 1)
        ts_code_symbol=ts_code_arr[1]+ts_code_arr[0]
        
        url="https://stock.xueqiu.com/v5/stock/chart/kline.json?period=day&type=before&count=-365&symbol="+ts_code_symbol+"&begin="+self.dateTimp
        r = requests.get(url,headers=self.header)
        response = r.json()
        code=response['error_code']
        if code != 0:
            print("获取日K异常")
            return []
        stock_daily=response['data']
        if len(list(stock_daily.keys()))<=0:
            print("不存在K线")
            return []
            
        column = stock_daily['column']
        item= stock_daily['item']
        
        df=pd.DataFrame(item,columns=column)
        
        df=df.drop(['volume_post','amount_post'],axis=1)
        # 涨跌金额
        df.rename(columns={'timestamp':'trade_date','volume':'vol','chg':'pct_chg','turnoverrate':'huanshou'},inplace=True)
        df['trade_date'] = df['trade_date'].apply(lambda x: datetime.datetime.fromtimestamp(int(x)/1000).strftime("%Y%m%d") )
        aaa = df.to_dict('records')
        data = sorted(aaa,key = lambda e:e.__getitem__('trade_date'), reverse=True)
        return data
    
    #股票基础信息
    def requestXueQiuBaseInfo(self,ts_code):
        if ts_code == None:
            return {}
        ts_code_arr = ts_code.split(".", 1)
        ts_code_symbol=ts_code_arr[1]+ts_code_arr[0]
        
        url="https://stock.xueqiu.com/v5/stock/quote.json?symbol="+ts_code_symbol+"&extend=detail"
        r = requests.get(url,headers=self.header)
        response = r.json()
        code=response['error_code']
        if code != 0:
            print("获取基础信息异常")
            return []
        stock_data=response['data']
        if len(list(stock_data.keys()))<=0:
            print("获取基础信息异常")
            return []
            
        quote = stock_data['quote']
        # 总市值
        total_mv= quote['market_capital']/100000000
        # 流通市值
        circ_mv= quote['float_market_capital']/100000000

        limit_up = quote['limit_up']#涨停价
        current = quote['current']
        status = quote['status']


        limit_status = 0 #是否涨停
        if limit_up!=None and current>=limit_up:
            limit_status=1
          
        trade_time = quote['time']
        d = datetime.datetime.fromtimestamp(trade_time/1000)
        a = d.strftime("%Y-%m-%d")
        return {"total_mv":total_mv,"circ_mv":circ_mv,"limit_status":limit_status,"trade_date":a,"status":status}
       
    
 
    
    def requestAmountInflow(self,ts_code):

        amountInflow={"net_mf_amount":"0万","buy_elg_amount":"0万","buy_elg_percent":"0%"}

        if ts_code == None:
            return amountInflow

        if "BJ" in ts_code:
            return amountInflow
            
        ts_code_arr = ts_code.split(".", 1)
        ts_code_symbol=ts_code_arr[1]+ts_code_arr[0]

        url="https://stock.xueqiu.com/v5/stock/capital/distribution.json?symbol="+ts_code_symbol
        r = requests.get(url,headers=self.header)
        response = r.json()
        code=response['error_code']
        if code != 0:
            print("获取资金流入异常 %s" %(ts_code))
            return amountInflow
        stock_data=response['data']
        if len(list(stock_data.keys()))<=0:
            return amountInflow
        #资金净流入
        net_inflow = stock_data["net_inflow"]
        amountInflow['net_mf_amount'] = str(round(float(net_inflow/10000),2))+"万"
        
        distribution = stock_data["distribution"]
        if distribution ==None:
            return amountInflow
        if not 'buy' in distribution.keys() :
            return amountInflow

        buy=distribution['buy']
        xlarge=buy['xlarge']
        large=buy['large']
        medium=buy['xlarge']
        small=buy['xlarge']
        
        #特大单金额
        amountInflow['buy_elg_amount']=str(round(float(xlarge/10000),2))+"万"
        #特大单金额占比
        if xlarge > 10000 and (xlarge+large+medium+small) > 10000:
            buy_elg_percent= round(float((xlarge)/(xlarge+large+medium+small)),2) * 100
            amountInflow['buy_elg_percent']= "%.2f%%" % (buy_elg_percent)
        else:
            amountInflow['buy_elg_percent']= "0%"
        return amountInflow
        
        
    
    #股票板块信息
    def requestBankuaiDaily(self,ts_code):
        
        hy_dic={"hy":"","hy2":"","hy3":""}

        if ts_code == None:
            return hy_dic
        ts_code_arr = ts_code.split(".", 1)
        ts_code_symbol=ts_code_arr[0]
        
        headers={
            'cookie':'v=A5HXHYWXl6LoBfu37zzS0SP-pJcr_gVwr3KphHMmjdh3Gr7Mu04VQD_CuVgA; escapename=Mr_Yangwd; ticket=10e15e469f4f3a1970c65d5116e7e10f; u_name=Mr_Yangwd; user=MDpNcl9ZYW5nd2Q6Ok5vbmU6NTAwOjQ5MTkxNDIyNzo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxMDEsNDA7MiwxLDQwOzMsMSw0MDs1LDEsNDA7OCwwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMSw0MDsxMDIsMSw0MDoyNTo6OjQ4MTkxNDIyNzoxNjQ0MzM2ODM3Ojo6MTU1MzczOTU0MDo0MDIzNjM6MDoxOTM4YzAwOTg5MGY2OTJkMjA3ZTgyM2U1ZmZmMDFkNGI6OjA%3D; user_status=0; userid=481914227',
            'User-Agent': 'EQHexinFee/10.90.90 (iPhone; iOS 15.3; Scale/3.00)'
        };
        url="http://basic.10jqka.com.cn/mapp/"+ts_code_symbol+"/company_base_info.json"
        r = requests.get(url,headers=headers)
        response = r.json()
        code=response['status_code']
        if code != 0:
            print("获取板块异常")
            return hy_dic
        stock_info=response['data']
        if len(list(stock_info.keys()))<=0:
            return hy_dic
          
        hy_info = stock_info['industry']
        if len(list(hy_info.keys()))<=0:
            return hy_dic
        
        if "hy" in list(hy_info.keys()):
            hy_dic['hy'] = hy_info['hy']
        if "hy2" in list(hy_info.keys()):
            hy_dic['hy2'] = hy_info['hy2']
        if "hy3" in list(hy_info.keys()):
            hy_dic['hy3'] = ""
    
        return hy_dic
    
    
    @classmethod
    def requestTongHuaShunBK(self,bk_code):
        headers = {
            'User-Agent': '%E5%90%8C%E8%8A%B1%E9%A1%BA/7 CFNetwork/1331.0.7 Darwin/21.4.0',
            'Accept': '*/*'            
        }
        URL = "http://zx.10jqka.com.cn/indval/getstocks?blockcode="+bk_code
        # print(URL)
        r = requests.get(URL,headers=headers)
        response = r.json()
        code=response['errorcode']
        if code != 0:
            print(response)
            return
        
        result=response['result']
        if not len(result.keys())>0:
            print(response)
            return
        
        count=result['count']
        data=result['data']
        allStock=[]
        for item in data:
            stockcode = item['stockcode']
            allStock.append(stockcode)
        return allStock
    
    
