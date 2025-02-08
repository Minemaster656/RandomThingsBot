from pymongo import MongoClient
import json

import collectionClearer
from private import coreData

# Подключение к базе данных MongoDB
client = MongoClient(coreData.mongo_url)
db = client[coreData.mongo_db_name]

# Загрузка данных из JSON-файла и импорт в базу данных
def import_data(collection_name, file_path):
    collection = db[collection_name]
    with open(file_path, 'r') as file:
        data = json.load(file)
        collection.insert_many(data)

collections = ["users"]
# Пример использования
# import_data('countries', 'private/RTB_data.countries.json')
# import_data('servers', 'private/RTB_data.servers.json')
# import_data('users', 'private/RTB_data.users.json')
clearOld = False
for i in collections:
    import_data(i, f"private/RTB_data.{i}.json")

if clearOld:
    collectionClearer.clearCollections(collections)

print(f"Импорт данных завершен!")