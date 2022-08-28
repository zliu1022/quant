//dbs = db.adminCommand('listDatabases')
//printjson(dbs);
//col = db.getCollectionNames()

db = db.getSiblingDB('stk1')

v =
  [
    { '$unwind': '$items' },
    {
      '$match': {
        '$and': [
          { 'items.year': '2021' },
          { 'items.plan_explain': { '$regex': /送/ } },
          { 'items.plan_explain': { '$regex': /转/ } }
        ]
      }
    },
    {
      '$group': { _id: { 
        code: '$ts_code', 
        plan: '$items.plan_explain',
        date: '$items.date'
        } }
    },
    { '$sort': { '_id.date': -1 } }
  ]

ref = db.bonus.aggregate(v)

ref.forEach(function(t) {
  //print(t['_id']['code'], t['_id']['plan'], t['_id']['date']);
  printjson(t['_id'])
});

