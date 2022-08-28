//dbs = db.adminCommand('listDatabases')
//printjson(dbs);
//col = db.getCollectionNames()

db = db.getSiblingDB('stk1')

// { code: '600570.SH', plan: '10送3股派1元(实施方案)', date: '20220818' }

v =
  [
    { '$unwind': '$day' },
    {
      '$match': {
        '$and': [
          { 'ts_code': '600570.SH' },
          { 'day.date': { '$gte' : '20220817' }},
          { 'day.date': { '$lte' : '20220818' }}
        ]
      }
    }
  ]

ref = db.day.aggregate(v)

ref.forEach(function(t) {
  //print(t['_id']['code'], t['_id']['plan'], t['_id']['date']);
  printjson(t)
});

