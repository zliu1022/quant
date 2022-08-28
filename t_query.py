#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pprint import pprint

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
        print('db.bonus.find_one', ref['ts_code'], len(ref['day']))
        print('date, open, close :')
        for x in ref['day']:
            if x['date'] <= end_date and x['date'] >= start_date:
                print(x['date'], x['open'], x['close'])

    print()
