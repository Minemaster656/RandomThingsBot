import pymongo
from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')

db = client['RTB_data']

print(db.users.find())
print(list(db.users.find()))
print(db.list_collections())
print(db.list_collection_names())