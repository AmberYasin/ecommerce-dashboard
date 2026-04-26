import pandas as pd
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce_db']

print("Loading amazon_raw...")
df_amazon = pd.read_csv('amazon_clean.csv')
db['amazon_raw'].drop()
db['amazon_raw'].insert_many(df_amazon.to_dict(orient='records'))
print(f"amazon_raw: {db['amazon_raw'].count_documents({}):,} documents")

print("Loading criteo_raw...")
df_criteo = pd.read_csv('criteo_clean.csv')
db['criteo_raw'].drop()
db['criteo_raw'].insert_many(df_criteo.to_dict(orient='records'))
print(f"criteo_raw: {db['criteo_raw'].count_documents({}):,} documents")

print("Done — all collections ready")
