#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from random import randint
from pprint import pprint

#Step 1: Connect to MongoDB - Note: Change connection string as needed
client = MongoClient(port=27017)
db=client.stk1

'''
ASingleReview = db.reviews.find_one({})
print('A sample document:')
pprint(ASingleReview)

result = db.reviews.update_one({'_id' : ASingleReview.get('_id') }, {'$inc': {'likes': 1}})
print('Number of documents modified : ' + str(result.modified_count))

UpdatedDocument = db.reviews.find_one({'_id':ASingleReview.get('_id')})
print('The updated document:')
pprint(UpdatedDocument)
'''

#Step 2: Create sample data

# timestamp volume open high low close chg percent turnoverrate amount volume_post amount_post pe pb ps pcf market_capital balance hold_volume_cn hold_ratio_cn net_vol      ume_cn hold_volume_hk hold_ratio_hk net_volume_hk
# [1647532800000, 56519780, 34.3566, 35.5726, 34.0975, 34.7852, 0.2006, 0.58, 0.77, 1977068691.0, None, None, 34.9322, 7.1053, 1.6044, 33.9048, 246988515532.1, 2417823      384.0, 559002413, 7.89, -545339, None, None, None]

item = {
    'code' : 'SZ002475',
    'dividend' : [
        {   'year' : 2021,
            'ex_dividend_date' : 1657641600000,
            'base' : 10,
            'new' : 3,
            'bonus' : 1 },
        {   'year' : 2020,
            'ex_dividend_date' : 1657641600000,
            'base' : 10,
            'new' : 3,
            'bonus' : 1 }
    ],
    'day' : [
        {   'timestamp' : 1647532800000, 
            'volume' : 56519780, 
            'open' : 34.3566, 
            'high' : 35.5726, 
            'low'  : 34.0975, 
            'close' : 34.7852, 
            'chg' : 0.2006, 
            'percent' : 0.58, 
            'turnoverrate' : 0.77, 
            'amount' : 1977068691.0 },
        {   'timestamp' : 1647532700000, 
            'volume' : 56519780, 
            'open' : 34.3566, 
            'high' : 35.5726, 
            'low'  : 34.0975, 
            'close' : 34.7852, 
            'chg' : 0.2006, 
            'percent' : 0.58, 
            'turnoverrate' : 0.77, 
            'amount' : 1977068691.0 }
    ]
}


for x in range(1):

    #Step 3: Insert business object directly into MongoDB via insert_one
    #result=db.reviews.insert_one(item)
    result = db.reviews.insert_one(item)

    #Step 4: Print to the console the ObjectID of the new document
    print('Created {0} as {1}'.format(x,result.inserted_id))

#Step 5: Tell us that you are done
print('finished creating reviews')

if __name__ == '__main__':
    quit()
