#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from random import randint
from pprint import pprint

client = MongoClient(port=27017)
db = client.stk1
col = db.day
col.drop()

item1 = {
    'ts_code' : 'SZ002475',
    'day' : [
        { 'high' : 36.576, 'low':5 },
        { 'high' : 35.5726 , 'low':3}
    ],
    'info' : 'gr',
    'dividend' : [
        { 'year' : 2021, 'base':5 },
        { 'year' : 2019, 'base':3 }
    ],
}

item2 = {
    'ts_code' : 'SZ002475',
    'day' : [
        { 'high' : 16 , 'low':1 },
        { 'high' : 25 , 'low':9 }
    ],
    'info' : 'lt',
    'dividend' : [
        { 'year' : 2011, 'base':5 },
        { 'year' : 2012, 'base':3 }
    ],
}

result = col.insert_one(item1)
print('after insert_one')
print(result.inserted_id)
print()

ref = col.find_one({ 'ts_code' : 'SZ002475' })
print('after find_one')
print(ref)
print(ref['day'][0])
print(ref['day'][len(ref['day'])-1])
print()

result = col.update_one({'_id' : ref.get('_id') }, {'$set':item2} )
print('after update_one with $set')
print(ref)
print()

result = col.update_one({'_id' : ref.get('_id') }, 
    { '$push' : { 
        'day': { 
            '$each': [ 
                {'high':19, 'low':3 }, 
                {'high':37, 'low':7 }, 
                {'high':16, 'low':1 }, 
                {'high':25, 'low':9 }, 
                {'high':28, 'low':5 }, 
                {'high':18, 'low':2 } 
            ],
            '$sort': {'high':1}
        } 
    }})
print('after update_one with $push and $sort field high')
info = col.find_one({ 'ts_code' : 'SZ002475' })
print(info['day'])
print(len(info['day']))
print(info['day'][0])
print(info['day'][len(info['day'])-1])

#col.ensureIndex( { 'high':1 }, { 'unique':'true', 'dropDups':'true' } )
#col.ensureIndex( { 'ts_code':1 }, { 'unique':'true', 'dropDups':'true' } )

a = col.find()
for x in a:
  pprint(x)



if __name__ == '__main__':
    quit()
