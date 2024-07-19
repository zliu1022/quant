#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import SnowToken
from datetime import datetime, timedelta
import threading
import requests
import time
from pymongo import MongoClient, ASCENDING
from pprint import pprint
import pandas as pd
import tushare as ts
import sys

basic_token = '0603f0a6ce3d7786d607e65721594ed0d1c23b41d6bc82426d7e4674'
bonus_url   = "https://stock.xueqiu.com/v5/stock/f10/cn/bonus.json?&symbol="
day_url     = "https://stock.xueqiu.com/v5/stock/chart/kline.json?period=day&type=none&count="

class StockGet:
    def __init__(self):
        self.today_str = datetime.now().strftime('%Y%m%d')
        self.today_dt= datetime.strptime(self.today_str,'%Y%m%d')
        self.this_year = self.today_dt.year

        dayline_str = '20160101'
        #dayline_str = self.today_str
        self.dateTimp = str(int(datetime.timestamp(datetime.strptime(dayline_str, '%Y%m%d'))*1000))

        client = MongoClient(port=27017)
        db = client.stk1

        self.col_basic = db.basic
        self.col_bonus_ori = db.bonus_ori # from network, concat db and drop_duplicates
        self.col_bonus = db.bonus         # transform from bonus_ori
        self.col_day = db.day
        self.col_token = db.token

        db.drop_collection('bad_bonus')
        self.col_bad_bonus = db.bad_bonus

        self.stock_list = []
        
        t = self.updateToken(1)
        self.header = {
            'cookie':'xq_is_login=1;xq_a_token=' + t + ';u=1119975455;',
            'User-Agent': 'Xueqiu iPhone 13.6.5'
        }

        self.func_name = ''
        return

    def updateToken(self, valid_days):
        print('Check token', datetime.strftime(datetime.now(), '%Y-%m-%d'))
        ref = self.col_token.find_one()
        if ref == None:
            t = SnowToken.get_snowtoken()
            new_dic = {'token':t, 'date':self.today_str}
            self.col_token.insert_one(new_dic)
            print('new token', t)
        else:
            token_date = datetime.strptime(ref['date'],'%Y%m%d')
            date_len = self.today_dt - token_date
            if date_len.days <= valid_days:
                t = ref['token']
                print('token got', date_len.days, 'days ago', t, 'still valid')
            else:
                t = SnowToken.get_snowtoken()
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

    # ex: 10送4股转4股派1元，流通A股股东10转5.149022股,B股股东10转1.5股(实施方案)
    def plan2digit(self, s):
        ret = 0
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
                print('Error: bonus plan 送 without 股', s)
                ret = 1

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
                    print('Error: bonus plan 转 without 股 and no digit follow', s)
                    ret = 2
                else:
                    new = s[new_pos+1:new_pos+1+d_num]

        bonus_pos =  s.find('派')
        if bonus_pos != -1:
            bonus_gu_pos =  s.find('元', bonus_pos)
            if bonus_gu_pos != -1:
                bonus = s[bonus_pos+1:bonus_gu_pos]
            else:
                print('Error: bonus plan: 派 without 元', s)
                ret = 3

        if free_pos == -1 and new_pos == -1 and bonus_pos == -1:
            print('Error: bonus plan: not find 送转派', s)
            ret = 4
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
                        print('Error: bonus plan: unknown base', s)
                        ret = 5

        return ret, base, free, new, bonus

    def bonus2df(self, ts_code, data):
        year_arr = []
        base_arr = []
        free_arr = []
        new_arr = []
        bonus_arr = []
        date_arr = []

        # debug use
        #print('bonus2df: dividend_year(报告期)           ashare_date(除权除息日) equity_date(股权登记日) plan_explain(分红方案)')
        for x in data['items']:
            try:
                y = x['dividend_year']              # 报告期
                d = x['ashare_ex_dividend_date']    # 除权除息日
                s = x['plan_explain']               # 分红方案
                equity_date = x['equity_date']      # 股权登记日
            except:
                print(ts_code)
                pprint(x)
                quit()

            pos = y.find('年')
            pos_dash = y.find('-')
            pos_mr = y.find('中报') # middle report
            pos_qr = y.find('季报') # quarter report
            if pos != -1:
                dividend_year_str = y[0:pos]
                year_arr.append(dividend_year_str)
                dividend_year = int(dividend_year_str)
            elif pos_mr != -1:
                dividend_year_str = y[0:pos_mr]
                year_arr.append(dividend_year_str)
                dividend_year = int(dividend_year_str)
            elif pos_qr != -1:
                dividend_year_str = y[0:pos_qr-1]
                year_arr.append(dividend_year_str)
                dividend_year = int(dividend_year_str)
            elif pos_dash != -1:
                dividend_year_dt= datetime.strptime(y,'%Y-%m-%d')
                dividend_year_str = datetime.strftime(dividend_year_dt, '%Y%m%d')
                dividend_year = dividend_year_dt.year
                year_arr.append(dividend_year_dt.year)
            else:
                year_arr.append(y)
                dividend_year_str = y
                dividend_year = 1900

            # debug use
            '''
            date_str = ''
            if d == d and d != None: # not nan
                date_str   = datetime.strftime(datetime.fromtimestamp(d/1000), '%Y%m%d')
            else:
                date_str = '--------'
            equity_str = ''
            if equity_date == equity_date and equity_date != None: # not nan
                equity_str = datetime.strftime(datetime.fromtimestamp(equity_date/1000), '%Y%m%d')
                equity_year = datetime.strptime(equity_str,'%Y%m%d').year
            else:
                equity_str = '--NaN---'
                equity_year = 1900

            #如果 ashare_ex_dividend_date 有值，则 data_ok
            #如果 ashare_ex_dividend_date 没有值，
            #    如果 dividend_year 是今年，则 date_ok
            #    如果 dividend_year 不是今年, 则 data_err

            status = 'date_ok'
            if date_str == '--------' and dividend_year != self.this_year and dividend_year != (self.this_year-1):
                status = 'date_err'
            print('          {} {} {}              {}                {} {}                {} {}'.format(
                y, dividend_year_str, dividend_year, 
                date_str, 
                equity_str, equity_year,
                s,
                status))
            '''

            ret, base, free, new, bonus = self.plan2digit(s)
            # if ret!=0 base,free,new,bonus = 0, still insert bonus db
            base_arr.append(base)
            free_arr.append(free)
            new_arr.append(new)
            bonus_arr.append(bonus)
            if ret != 0:
                ref_bad = self.col_bad_bonus.find_one({ "ts_code": ts_code })
                if ref_bad == None:
                    new_dic = { 'ts_code': ts_code , 'bad_plan':True}
                    self.col_bad_bonus.insert_one(new_dic)
                    print('{} insert bad bonus, bad_plan'.format(ts_code))
                else:
                    newvalues = { "$set": {'bad_plan':True}}
                    self.col_bad_bonus.update_one({ "ts_code": ts_code }, newvalues)
                    print('{} update bad bonus, bad_plan'.format(ts_code))

            # ashare_ex_dividend_date not NaN or null: insert ashare_ex_dividend_date to bonus_db
            #              dividend_year == this year: insert '' to bonus_db
            # otherwise insert '' to bonus_db and insert bad_bonus_db 
            if d == d and d != None: # not nan
                date_str = datetime.strftime(datetime.fromtimestamp(d/1000), '%Y%m%d')
                date_arr.append(date_str)
            elif dividend_year == self.this_year or dividend_year == (self.this_year-1): # has dividend plan no ex_date in this year or last year
                date_arr.append('')
            else: # ashare_ex_dividend_date == NaN
                if equity_date == equity_date and equity_date != None: # not nan
                    equity_str = datetime.strftime(datetime.fromtimestamp(equity_date/1000), '%Y%m%d')
                    equity_year = datetime.strptime(equity_str,'%Y%m%d').year
                else:
                    equity_str = 'NaN'
                    equity_year = 1900
                if dividend_year >= (self.this_year-5) or equity_year >= (self.this_year-5):
                    print('Warning: {} no date 5ys {} {}({}) {} {}'.format(ts_code, y, equity_date, equity_str, dividend_year_str, s))
                else:
                    print('Warning: {} no date     {} {}({}) {} {}'.format(ts_code, y, equity_date, equity_str, dividend_year_str, s))

                ref_bad = self.col_bad_bonus.find_one({ "ts_code": ts_code })
                if ref_bad == None:
                    new_dic = { 'ts_code': ts_code , 'no_date':True}
                    self.col_bad_bonus.insert_one(new_dic)
                    #print('{} insert bad bonus no_date {} {}'.format(ts_code, y, equity_date))
                else:
                    newvalues = { "$set": {'no_date':True}}
                    self.col_bad_bonus.update_one({ "ts_code": ts_code }, newvalues)
                    #print('{} update bad bonus no_date {} {}'.format(ts_code, y, equity_date))

                date_arr.append('')

        df = pd.DataFrame(data['items'])
        df_len = len(df.index)
        if df_len != 0:# some new stock has no dividend info
            df.insert(0, 'bonus', bonus_arr)
            df.insert(0, 'new', new_arr)
            df.insert(0, 'free', free_arr)
            df.insert(0, 'base', base_arr)
            df.insert(0, 'date', date_arr)
            df.insert(0, 'year', year_arr)
            #df = df.drop(['ashare_ex_dividend_date', 'equity_date', 'cancle_dividend_date'],axis=1)
            df = df.sort_values(by='date', ascending=False)
        return df

    # rewrite by GPT4 begin
    def extract_year(text):
        for pattern, offset in [("%Y年", 0), ("中报", 0), ("季报", -1), ("-%m-%d", 0)]:
            pos = text.find(pattern[:-2])
            if pos != -1:
                return text[0:pos + offset] if pattern[-1] == "Y" else datetime.strptime(text, pattern).year
        return "1900"

    def bonus2df_GPT4(self, ts_code, data):
        year_arr, base_arr, free_arr, new_arr, bonus_arr, date_arr = [], [], [], [], [], []

        for x in data['items']:
            try:
                y, d, s, equity_date = x['dividend_year'], x['ashare_ex_dividend_date'], x['plan_explain'], x['equity_date']
            except:
                print(ts_code)
                pprint(x)
                quit()

            dividend_year_str = extract_year(y)
            year_arr.append(dividend_year_str)
            dividend_year = int(dividend_year_str)

            ret, base, free, new, bonus = self.plan2digit(s)
            base_arr.append(base)
            free_arr.append(free)
            new_arr.append(new)
            bonus_arr.append(bonus)

        df = pd.DataFrame(data['items'])
        if len(df.index) != 0:
            df = df.assign(year=year_arr, date=date_arr, base=base_arr, free=free_arr, new=new_arr, bonus=bonus_arr)
            df = df.sort_values(by='date', ascending=False)
        return df

    def test_extract_year():
        def run_test(test_input, expected_output):
            result = extract_year(test_input)
            assert result == expected_output, f"Expected {expected_output}, but got {result} for input {test_input}"

        run_test("2021年", "2021")
        run_test("2021中报", "2021")
        run_test("2021季报", "2020")
        run_test("2021-06-30", 2021)
        run_test("No match found", "1900")

    #test_extract_year()
    # rewrite by GPT4 begin

    def req_basic(self):
        start_t = time.time()

        ts.set_token(basic_token)
        self.pro = ts.pro_api()
        df = self.pro.stock_basic(exchange='',fields='ts_code,symbol,name,industry,list_date,list_status,delist_date')

        ref = self.col_basic.find()
        if ref == None:
            all_stocks = df.to_dict('records')
            print('req_basic first create', len(all_stocks))
            ret = self.col_basic.insert_many(all_stocks)
            return

        for i in range(len(df.index)):
            # print(i, df.loc[i, 'ts_code'], df.loc[i, 'name'])

            ref = self.col_basic.find_one({'ts_code':df.loc[i, 'ts_code']})
            if ref == None:
                print('req_basic insert new', df.loc[i, 'ts_code'], df.loc[i, 'name'], df.loc[i, 'industry'])
                self.col_basic.insert_one(df.loc[i].to_dict())
                continue

            if df.loc[i, 'name'] != ref['name'] or df.loc[i, 'symbol'] != ref['symbol'] or df.loc[i, 'industry'] != ref['industry'] or df.loc[i, 'list_status'] != ref['list_status'] or df.loc[i, 'list_date'] != ref['list_date'] or df.loc[i, 'delist_date'] != ref['delist_date']:
                print('req_basic changed', df.loc[i, 'ts_code'], end=' ')
                df.loc[i, 'name'] != ref['name'] and print('name', df.loc[i, 'name'], '->', ref['name'], end=' ')
                df.loc[i, 'symbol'] != ref['symbol'] and print('symbol', df.loc[i, 'symbol'], '->', ref['symbol'], end=' ')
                df.loc[i, 'industry'] != ref['industry'] and print('industry', df.loc[i, 'industry'], '->', ref['industry'], end=' ')
                df.loc[i, 'list_status'] != ref['list_status'] and print('list_status', df.loc[i, 'list_status'], '->', ref['list_status'], end=' ')
                df.loc[i, 'list_date'] != ref['list_date'] and print('list_date', df.loc[i, 'list_date'], '->', ref['list_date'], end=' ')
                df.loc[i, 'delist_date'] != ref['delist_date'] and print('delist_date', df.loc[i, 'delist_date'], '->', ref['delist_date'], end=' ')
                print()
                self.col_basic.update_one({'ts_code':df.loc[i, 'ts_code']}, {'$set':df.loc[i].to_dict()})
                continue

        end_t = time.time()
        print('req_basic cost {:5.2f}s'.format(end_t - start_t))
        return

    def req_bonus(self, all_stocks):
        err_day = []

        for index,stock_info in enumerate(all_stocks):
            ret = 0
            ts_code = stock_info['ts_code']
            if ts_code == None:
                print('Error: ts_code == None')
                continue

            ts_code_arr = ts_code.split(".", 1)
            ts_code_symbol=ts_code_arr[1]+ts_code_arr[0]
            url = bonus_url +ts_code_symbol
            ret, resp = self.req_url_retry(url, 3)
            if ret != 0:
                err_day.append(stock_info)
                continue

            code = resp['error_code']
            if code != 0:
                print("Error: Get bonus error", ts_code, code)
                err_day.append(stock_info)
                continue

            data = resp['data']
            if not ('items' in data):
                print("Error: No item key in bonus resp", ts_code)
                continue
            df = pd.DataFrame(data['items'])
            df_len = len(df.index)

            ref = self.col_bonus_ori.find_one({ "ts_code": ts_code })
            if ref != None:
                df_ref = pd.DataFrame(ref['items'])
                df_ref_len = len(df_ref.index)

                # find ashare_ex_dividend_date == null in db
                # find same dividend_year in resp
                # if resp's ashare_ex_dividend_date != null, remove db item
                # if resp's ashare_ex_dividend_date == null, compare their plan_explain
                #   if their plan_explain different, remove db item
                #   if their plan_explain same, do nothing
                index_none = []
                for i in range(df_ref_len):
                    d = df_ref.loc[i, 'ashare_ex_dividend_date']
                    ref_plan_explain = df_ref.loc[i, 'plan_explain']
                    dividend_year    = df_ref.loc[i, 'dividend_year']
                    if d == d and d != None: # not nan
                        continue
                    for j in range(df_len):
                        new_d = df.loc[j, 'ashare_ex_dividend_date']
                        new_plan_explain = df.loc[j, 'plan_explain']
                        if df.loc[j, 'dividend_year'] == dividend_year:
                            if new_d == new_d and new_d != None: # not nan
                                new_d_str = datetime.strftime(datetime.fromtimestamp(new_d/1000), '%Y%m%d')
                                print('Info:', ts_code, dividend_year, 'ashare_ex_dividend_date NaN ->', new_d_str)
                                index_none.append(i)
                            else: # new ashare_ex_dividend_date == null, compare plan_explain
                                if ref_plan_explain != new_plan_explain:
                                    print('Info:', ts_code, dividend_year, 'plan_explain', ref_plan_explain, '->', new_plan_explain)
                                    index_none.append(i)

                df_ref = df_ref.drop(index_none)
                df_ref_len = len(df_ref.index)

                if df_ref_len !=0 or df_len != 0:
                    df_new = pd.concat([df, df_ref]).sort_values(by='ashare_ex_dividend_date', ascending=False).drop_duplicates().reset_index(drop=True)
                else:
                    df_new = df
                aaa = df_new.to_dict('records')
                try:
                    data = sorted(aaa,key = lambda e:e.__getitem__('ashare_ex_dividend_date'), reverse=True)
                except:
                    print('Error:', ts_code, 'ashare_ex_dividend_date == null')
                    pprint(aaa)
                    data = sorted(aaa,key = lambda e:e.__getitem__('dividend_year'), reverse=True)
                    print()
                    pprint(data)
                    continue

                new_dic = {}
                new_dic.update({'items':data})
                newvalues = { "$set": new_dic}    
                self.col_bonus_ori.update_one({ "ts_code": ts_code }, newvalues)

                # df: from url's resp, df_ref: from db, df_new: concat df and df_ref
                df_new_len = len(df_new.index)
                if df_new_len > df_len or df_new_len > df_ref_len:
                    print('{} update bonus_ori new  resp({}) db({}) new({})'.format(ts_code, df_len, df_ref_len, df_new_len))
                '''
                else:
                    print('{} update bonus_ori keep resp({}) db({}) new({})'.format(ts_code, df_len, df_ref_len, df_new_len))
                '''
            else:
                aaa = df.to_dict('records')
                data = sorted(aaa,key = lambda e:e.__getitem__('ashare_ex_dividend_date'), reverse=True)

                new_dic = { "ts_code": ts_code }
                new_dic.update({'items':data})
                self.col_bonus_ori.insert_one(new_dic)
                print('{} insert bonus_ori resp({})'.format(ts_code, df_len))

        return err_day

    def req_bonus_trans(self, all_stocks):
        err_day = []
        for index,stock_info in enumerate(all_stocks):
            ts_code = stock_info['ts_code']
            if ts_code == None:
                print('Error: ts_code == None')
                continue

            ref_ori = self.col_bonus_ori.find_one({ "ts_code": ts_code })
            if ref_ori == None:
                print('Warning: {} no bonus_ori'.format(ts_code))
                continue

            df = self.bonus2df(ts_code, ref_ori)
            df_len = len(df.index)
            aaa = df.to_dict('records')
            data = sorted(aaa,key = lambda e:e.__getitem__('date'), reverse=True)

            ref = self.col_bonus.find_one({ "ts_code": ts_code })
            if ref != None:
                new_dic = {}
                new_dic.update({'items':data})
                newvalues = { "$set": new_dic}
                self.col_bonus.update_one({ "ts_code": ts_code }, newvalues)
                #print('{} update bonus ({})'.format(ts_code, df_len))
            else:
                new_dic = { "ts_code": ts_code }
                new_dic.update({'items':data})
                self.col_bonus.insert_one(new_dic)
                #print('{} insert bonus ({})'.format(ts_code, df_len))

        return err_day

    def req_day(self, all_stocks):
        req_days = 365*5+10
        err_day = []

        for index,stock_info in enumerate(all_stocks):
            ret = 0
            ts_code = stock_info['ts_code']
            list_days = self.get_stock_trade_days(stock_info['list_date'])# #获取股票上市时长

            if ts_code == None:
                print('Error: ts_code == None')
                continue
            ts_code_arr = ts_code.split(".", 1)
            ts_code_symbol=ts_code_arr[1]+ts_code_arr[0]

            ref = self.col_day.find_one({ "ts_code": ts_code })
            if ref != None:
                stk_days = len(ref['day'])
                last_date = ref['day'][0]['date']
                early_date = ref['day'][stk_days-1]['date']

                last_dateTimp = str(int(datetime.timestamp(datetime.strptime(last_date, '%Y%m%d')+timedelta(days=1))*1000))
                new_req_days = self.get_stock_trade_days(last_date)

                if new_req_days == 0:
                    print('{} {}-{} in db, already up to date'.format(ts_code, early_date, last_date))
                    continue
                else:
                    pass
                    #print('{} {}-{} in db, try to get {:3d} days'.format(ts_code, early_date, last_date, new_req_days))

                url = day_url + str(new_req_days) + "&symbol=" + ts_code_symbol + "&begin=" + last_dateTimp
            else:
                url = day_url + str(req_days) + "&symbol=" + ts_code_symbol + "&begin=" + self.dateTimp

            ret, resp = self.req_url_retry(url, 3)
            if ret != 0:
                err_day.append(stock_info)
                continue

            code = resp['error_code']
            if code != 0:
                print("Error: Get day kline error", ts_code_symbol, code)
                err_day.append(stock_info)
                continue

            stock_daily = resp['data']
            if not ('item' in stock_daily):
                print("Error: No item key in day resp", ts_code_symbol)
                continue
            if len(stock_daily['item']) == 0:
                print("Error: No kline, maybe restday", ts_code_symbol)
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
        if len(all_stocks) == 1:
            pprint(all_stocks)
        err_stock = req_func(all_stocks)
        if len(err_stock)>0:
            print(threading.current_thread().name, 'Error', len(err_stock), err_stock)
        end_t = time.time()
        #print('{} cost {:.2f}s'.format(threading.current_thread().name, end_t - start_t))

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
            ref = self.col_basic.find().sort("ts_code", ASCENDING)
            if ref != None:
                self.stock_list = list(ref)

                '''
                # recover req from last_end
                tmp_list = list(ref)
                last_end = '600059.SH'
                last_index = next((index for (index, d) in enumerate(tmp_list) if d['ts_code'] == last_end), None)
                self.stock_list = tmp_list[last_index+1:] if last_index is not None else []
                '''
        else:
            ref = self.col_basic.find_one({ 'ts_code': code })
            if ref != None:
                self.stock_list = []
                self.stock_list.append(ref)
        print('find {} stocks'.format(len(self.stock_list)))
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

    if len(sys.argv)!=2 and len(sys.argv)!=3:
        print('update_stock [basic|bonus|day|bonus_trans]')
        print('update_stock [bonus|day|bonus_trans] 002457.SZ')
        quit()

    si = StockGet()
    if sys.argv[1] == 'basic':
        si.req_basic()
        quit()
    else:
        si.set_func(sys.argv[1])

    if sys.argv[1] == 'bonus':
        thread_num = 1250
    elif sys.argv[1] == 'bonus_trans':
        thread_num = 6000
    else:
        thread_num = 240

    find_str = None
    if len(sys.argv) == 3:
        find_str = sys.argv[2]
    ref = si.db_basicfind(find_str)
    if ref == None:
        print('Not found stock list')
        exit()

    start_t = time.time()
    threads = si.get_stocks(thread_num)
    for i in threads:
        i.join()
    end_t = time.time()

    print('total cost {:5.2f}s'.format(end_t - start_t))
