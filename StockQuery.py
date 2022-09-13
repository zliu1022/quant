#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pprint import pprint
from datetime import datetime, timedelta
import chinese_calendar as calendar
from time import time

class StockQuery:
    def __init__(self):
        self.today_str = datetime.now().strftime('%Y%m%d')

        client = MongoClient(port=27017)
        db = client.stk1
        self.col_basic = db.basic
        self.col_bonus = db.bonus
        self.col_day = db.day

        self.stock_list = []
        self.day = []
        return

    # return:
    # dict_keys(['_id', 'ts_code', 'symbol', 'name', 'industry', 'list_status', 'list_date', 'delist_date'])
    def query_basic(self, ts_code):
        if ts_code == None:
            ref = self.col_basic.find()
            self.stock_list = list(ref)
        else:
            ref = self.col_basic.find_one({ 'ts_code': ts_code })
            self.stock_list = []
            self.stock_list.append(ref)

        if ref != None:
            print('query_basic')
            print('format', self.stock_list[0].keys())
            return self.stock_list
        return None

    # dict_keys(['year', 'date', 'base', 'free', 'new', 'bonus', 'dividend_year', 'plan_explain'])
    def query_bonus_code(self, ts_code):
        v = {'ts_code': ts_code}
        ref = self.col_bonus.find_one(v)

        if ref != None:
            self.stock_list = list(ref['items'])
            print('query_bonus_code', ts_code)
            print('format', self.stock_list[0].keys())
            return self.stock_list
        return None

    # dict_keys(['_id'])
    #[{'_id': {'code': '603060.SH',
    #          'date': '20220609',
    #          'plan': '10送1股转1股派1.26元(实施方案)'}},
    def query_bonus_plan(self, plan_str):
        unwind_stage = { '$unwind': '$items' }
        match_stage = {   
                    '$match': { 
                        '$and': [
                            { 'items.year': '2021' },
                            { 'items.plan_explain': { '$regex':'.*送.*'} },
                            { 'items.plan_explain': { '$regex':'.*转.*'} }
                        ]
                    }
                }
        group_stage = {
                    '$group': { 
                        '_id': {
                            'code': '$ts_code',
                            'plan': '$items.plan_explain',
                            'date': '$items.date'
                        }
                    }
                }
        sort_stage = { '$sort': { '_id.date': -1 } }
        v = [ unwind_stage, match_stage, group_stage, sort_stage ]
        ref = self.col_bonus.aggregate(v)
        '''
        if ref == None:
            print('None')
        else:
            print('db.bonus.aggregate')
            pprint(v)
            print(':')
            for item in ref:
                x = item['_id']
                pprint(x)
        return
        '''
        if ref != None:
            self.stock_list = list(ref)
            print('query_bonus_plan', plan_str)
            print('format', self.stock_list[0].keys())
            return self.stock_list
        return None

    # dict_keys(['date', 'volume', 'open', 'high', 'low', 'close', 'chg', 'percent', 'turnoverrate', 'amount'])
    def query_day_code(self, ts_code):
        v = {'ts_code': ts_code}
        ref = self.col_day.find_one(v)

        if ref != None:
            self.stock_list = list(ref['day'])
            print('query_day_code', ts_code)
            print('format', self.stock_list[0].keys())
            return self.stock_list
        return None

    def query_day_code_date(self, ts_code, start_date, end_date):
        s_time = time()
        ret = []
        v = {'ts_code': ts_code}
        ref = self.col_day.find_one(v)
        '''
        if ref != None:
            for x in ref['day']:
                if x['date'] <= end_date and x['date'] >= start_date:
                    ret.append(x)
            e_time = time()
            print('query_day_code_date cost %.2f s' % (e_time - s_time))
            return ret
        return None
        '''
        if ref != None:
            self.stock_list = list(ref)
            print('query_day_code_date', ts_code, start_date, end_date)
            print('format', self.stock_list[0].keys())
            return self.stock_list
        return None

    # dict_keys(['_id', 'amount', 'num'])
    def stat_day_amount(self, start_date=None, end_date=None, amount=None):
        start_date = start_date or '20180101'
        end_date = end_date or self.today_str
        amount = amount or 2000000000

        s_time = time()
        unwind_stage = { '$unwind': '$day' }
        match_stage = {
                    '$match': { 
                        '$and': [
                            { 'day.date': { '$gte':start_date} },
                            { 'day.date': { '$lte':end_date} },
                            { 'day.amount': { '$gte':amount } }
                        ]
                    }
                }
        group_stage = {
                    '$group': { 
                        '_id': {
                            'ts_code': '$ts_code'
                        },
                        'amount': { '$avg': '$day.amount' },
                        'num': { '$count': {} }
                    }
                }
        sort_stage = { '$sort': { 'amount': -1 } }
        v = [ unwind_stage, match_stage, group_stage, sort_stage ]
        ref = self.col_day.aggregate(v)
        if ref != None:
            self.stock_list = list(ref)
            e_time = time()
            print('stat_day_amount cost %.2f s' % (e_time - s_time))
            print('format', self.stock_list[0].keys())
            return self.stock_list
        return None

    # dict_keys(['_id', 'num'])
    def stat_day_num(self):
        s_time = time()
        unwind_stage = { '$unwind': '$day' }
        group_stage = { '$group': { "_id": { "ts_code": "$ts_code" }, "num": {'$count':{}} }}
        sort_stage = { '$sort': { "num" : 1 } }
        v = [ unwind_stage, group_stage, sort_stage ]
        ref = self.col_day.aggregate(v)
        if ref != None:
            self.stock_list = list(ref)
            e_time = time()
            print('stat_day_num cost %.2fs' % (e_time - s_time))
            print('format', self.stock_list[0].keys())
            return self.stock_list
        return None

    def check_day(self, ts_code, start_date, end_date):
        v = {'ts_code': ts_code}
        ref = self.col_day.find_one(v)

        if ref == None:
            print('check_day find None')
            return
      
        print('check_day', ref['ts_code'], len(ref['day']), 'days', end=' ')

        yesterday_date = datetime.strptime(start_date, '%Y%m%d')
        for x in ref['day'][::-1]:
            if x['date'] <= end_date and x['date'] >= start_date:
                #print(x['date'])
                today_date = datetime.strptime(x['date'], '%Y%m%d')
                delta_days = (today_date - yesterday_date).days

                if delta_days == 0: # special case for first day
                    #print(x['date'], ' = ', start_date)
                    yesterday_date = today_date
                    continue
                if delta_days == 1: # normal
                    yesterday_date = today_date
                    continue

                if delta_days != 1: # check weekend or holiday
                    for i in range(1, delta_days):
                        tmp_date = yesterday_date + timedelta(days=i)

                        on_holiday, holiday_name = calendar.get_holiday_detail(tmp_date)
                        tmp_weekday_str = tmp_date.strftime('%A')
                        if tmp_weekday_str != 'Saturday' and tmp_weekday_str != 'Sunday' and on_holiday == False:
                            print('Error', ts_code, datetime.strftime(tmp_date, '%Y%m%d'), tmp_date.strftime('%A'))
                            return
                        #print(delta_days-1, datetime.strftime(tmp_date, '%Y%m%d'), tmp_weekday_str, 'holiday', on_holiday, holiday_name)
                    yesterday_date = today_date
        print('finished')
        return

def check_day(db, ts_code, start_date, end_date):
    return

if __name__ == '__main__':
    sq = StockQuery()

    ts_code = '603060.SH'
    start_date = '20220608'
    end_date = '20220609'

    ts_code = '002475.SZ'
    sq.query_bonus_code(ts_code)
    print()

    ref = sq.query_bonus_plan('.*送.*')
    pprint(ref)
    print()

    sq.query_day_code(ts_code)
    print()

    ts_code = '002475.SZ'
    start_date = '20180101'
    end_date = '20220901'
    sq.check_day(ts_code, start_date, end_date)
    print()

    ts_code = '002475.SZ'
    start_date = '20180101'
    end_date = '20220901'

    ref = sq.query_basic(None)
    print(len(ref))
    print(ref[0].keys())
    print(ref[0].items())
    print()

    ref = sq.query_basic(ts_code)
    print(len(ref))
    print(ref[0].keys())
    print(ref[0].items())
    for item in ref:
        ts_code = item['ts_code']
        list_date = item['list_date']
        if list_date < start_date:
            sq.check_day(ts_code, start_date, end_date)
        else:
            sq.check_day(ts_code, list_date, end_date)
    print()

    # 统计日期范围内，日交易额 >= 20亿; 返回：代码，达到交易额的平均交易量，达到交易额的天数
    start_date = '20220101'
    end_date = '20220901'
    amount = 2000000000
    ref = sq.stat_day_amount(start_date, end_date, amount)
    for item in ref:
        ts_code = item['_id']['ts_code']
        amount = item['amount']
        num = item['num']
        if num > 150:
            print('%s %3d %.1f' % (ts_code, num, amount))
            sq.check_day(ts_code, start_date, end_date)
            print()

    # 统计数据库中，每个股票有交易价格的数据个数（目前的数据是从2016年至今）
    ref = sq.stat_day_num()
    for item in ref:
        num = item['num']
        if num <= 2:
            pprint(item)

