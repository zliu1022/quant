#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pprint import pprint
from datetime import datetime, timedelta
import chinese_calendar as calendar

class StockQuery:
    def __init__(self):
        client = MongoClient(port=27017)
        db = client.stk1
        self.col_basic = db.basic
        self.col_bonus = db.bonus
        self.col_day = db.day

        self.stock_list = []
        return

    def query_basic(self, ts_code):
        if ts_code == None:
            ref = self.col_basic.find()
            if ref != None:
                self.stock_list = list(ref)
                '''
                for x in ref:
                    self.stock_list.append(x)
                '''
                return ref
        else:
            ref = self.col_basic.find_one({ 'ts_code': ts_code })
            if ref != None:
                self.stock_list = []
                self.stock_list.append(ref)
                return ref
        return None

    def query_bonus_code(self, ts_code):
        v = {'ts_code': ts_code}
        ref = self.col_bonus.find_one(v)
        print('db.bonus.find_one', ref['ts_code'])
        pprint(v)
        print('date, base, free, new, bonus, plan_explain:')
        for x in ref['items']:
            if x['date'] <= end_date and x['date'] >= start_date:
                print(x['date'], x['base'], x['free'], x['new'], x['bonus'], x['plan_explain'])
        return

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

    def query_day_code(self, ts_code):
        v = {'ts_code': ts_code}
        ref = self.col_day.find_one(v)
        if ref == None:
            print('None')
        else:
            print('db.day.find_one', ref['ts_code'], len(ref['day']))
            print('date, open, close :')
            for x in ref['day']:
                if x['date'] <= end_date and x['date'] >= start_date:
                    print(x['date'], x['open'], x['close'])
        return

    def query_day_amount(self, amount):
        return

    def check_day(self, ts_code, start_date, end_date):
        v = {'ts_code': ts_code}
        ref = self.col_day.find_one(v)

        if ref == None:
            print('check_day find None')
            return
      
        print('db.day.find_one', ref['ts_code'], len(ref['day']), end=' ')

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

    #sq.query_bonus_code(ts_code)
    #print()

    #sq.query_bonus_plan(ts_code, plan_str)
    #print()

    #sq.query_day_code(ts_code)
    #print()

    ts_code = '002475.SZ'
    start_date = '20180101'
    end_date = '20220901'
    #check_day(db, ts_code, start_date, end_date)
    #print()

    start_date = '20180101'
    end_date = '20220901'
    sq.query_basic(None)
    for item in sq.stock_list:
        ts_code = item['ts_code']
        list_date = item['list_date']
        print(ts_code, list_date)
        quit()
        if list_date < start_date:
            sq.check_day(ts_code, start_date, end_date)
        else:
            sq.check_day(ts_code, list_date, end_date)

    quit()

    unwind_stage = { '$unwind': '$day' }
    match_stage = {   
                '$match': { 
                    '$and': [
                        { 'day.date': { '$gte':'20220801'} },
                        { 'day.amount': { '$gte':2000000000 } }
                    ]
                }
            }
    group_stage = {
                '$group': { 
                    '_id': {
                        'code': '$ts_code'
                    },
                    'amount': { '$avg': '$day.amount' },
                    'num': { '$count': {} }
                }
            }
    sort_stage = { '$sort': { 'amount': -1 } }
    v = [ unwind_stage, match_stage, group_stage, sort_stage ]
    ref = db.day.aggregate(v)
    if ref == None:
        print('None')
    else:
        print('db.day.aggregate')
        pprint(v)
        print(':')
        for item in ref:
            code = item['_id']['code']
            amount = item['amount']
            num = item['num']
            if num>10:
                print('%s %3d %.1f' % (code, num, amount))
                ts_code = code
                start_date = '20180101'
                end_date = '20220901'
                check_day(db, ts_code, start_date, end_date)
                print()

    
