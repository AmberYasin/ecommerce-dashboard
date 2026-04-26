from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce_db']
print("Collections:", db.list_collection_names())
for col in db.list_collection_names():
    print(f"{col}: {db[col].count_documents({}):,} documents")
