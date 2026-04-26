from dagster import resource
from pymongo import MongoClient
from sqlalchemy import create_engine

@resource
def mongo_resource(init_context):
    client = MongoClient('mongodb://localhost:27017/')
    return client['ecommerce_db']

@resource
def postgres_resource(init_context):
    engine = create_engine(
        'postgresql://ecommerce_user:ecommerce_pass@localhost:5432/ecommerce_db'
    )
    return engine
