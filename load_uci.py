import pandas as pd
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce_db']

df = pd.read_csv('uci_clean.csv')
db['uci_raw'].drop()
db['uci_raw'].insert_many(df.to_dict(orient='records'))
print(f"uci_raw loaded: {db['uci_raw'].count_documents({}):,} documents")
print("Columns:", list(df.columns))
