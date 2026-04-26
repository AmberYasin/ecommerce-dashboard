from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce_db']
doc = db['uci_raw'].find_one()
print('uci_raw columns:')
print(list(doc.keys()))
