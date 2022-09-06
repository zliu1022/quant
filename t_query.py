#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pprint import pprint
from datetime import datetime, timedelta
import chinese_calendar as calendar


if __name__ == '__main__':
    ts_code = '603060.SH'
    start_date = '20220608'
    end_date = '20220609'

    client = MongoClient(port=27017)
    db = client.stk1

    v = {'ts_code': ts_code}
    ref = db.bonus.find_one(v)
    print('db.bonus.find_one', ref['ts_code'])
    pprint(v)
    print('date, base, free, new, bonus, plan_explain:')
    for x in ref['items']:
        if x['date'] <= end_date and x['date'] >= start_date:
            print(x['date'], x['base'], x['free'], x['new'], x['bonus'], x['plan_explain'])
    print()

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
    ref = db.bonus.aggregate(v)
    if ref == None:
        print('None')
    else:
        print('db.bonus.aggregate')
        pprint(v)
        print(':')
        for item in ref:
            x = item['_id']
            pprint(x)
    print()

    v = {'ts_code': ts_code}
    ref = db.day.find_one(v)
    if ref == None:
        print('None')
    else:
        print('db.day.find_one', ref['ts_code'], len(ref['day']))
        print('date, open, close :')
        for x in ref['day']:
            if x['date'] <= end_date and x['date'] >= start_date:
                print(x['date'], x['open'], x['close'])
    print()

    ts_code = '002475.SZ'
    start_date = '20180101'
    end_date = '20220901'
    v = {'ts_code': ts_code}
    ref = db.day.find_one(v)
    yesterday_date = datetime.strptime(start_date, '%Y%m%d')
    if ref == None:
        print('None')
    else:
        print('db.day.find_one', ref['ts_code'], len(ref['day']))
        for x in ref['day'][::-1]:
            if x['date'] <= end_date and x['date'] >= start_date:
                print(x['date'])
                today_date = datetime.strptime(x['date'], '%Y%m%d')
                delta_days = (today_date - yesterday_date).days
                if delta_days == 0:
                    print(x['date'], ' = ', start_date)
                    yesterday_date = today_date
                    continue
                if delta_days == 1:
                    yesterday_date = today_date
                    continue
                if delta_days != 1:
                    for i in range(1, delta_days):
                        tmp_date = yesterday_date + timedelta(days=i)
                        on_holiday, holiday_name = calendar.get_holiday_detail(tmp_date)
                        tmp_weekday_str = tmp_date.strftime('%A')
                        if tmp_weekday_str != 'Saturday' and tmp_weekday_str != 'Sunday' and on_holiday == False:
                            print('Error', ts_code, datetime.strftime(tmp_date, '%Y%m%d'), tmp_date.strftime('%A'))
                        print(delta_days-1, datetime.strftime(tmp_date, '%Y%m%d'), tmp_date.strftime('%A'), 'holiday', on_holiday, holiday_name)
                    yesterday_date = today_date
    print()
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
    print()

