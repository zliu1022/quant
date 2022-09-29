#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from random import randint
from pprint import pprint

client = MongoClient(port=27017)
db = client.tmp
col = db.bonus

items = {
    'ts_code' : 'SZ002475',
    'items' : [
        { 'date' : '20220609' },
        { 'date' : '20210207' },
        { 'date' : '00000000' }
    ]
}

items_new = {
    'ts_code' : 'SZ002475',
    'items' : [
        { 'date' : '00000000' },
        { 'date' : '20220609' },
        { 'date' : '20210917' }
    ]
}

'''
col.drop()
result = col.insert_one(items)
print('after insert_one')
print(result.inserted_id)
print()
'''

ref = col.find_one({ 'ts_code' : 'SZ002475' })
print('after find_one')
print(ref)
print()

result = col.update_one({'_id' : ref.get('_id') }, {'$set':items_new} )
print('after update_one with $set')
print(ref)
print()

a = col.find()
for x in a:
  pprint(x)

if __name__ == '__main__':
    quit()
