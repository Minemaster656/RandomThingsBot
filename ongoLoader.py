from pymongo import MongoClient
import json

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

# Пример использования
import_data('countries', 'private/RTB_data.countries.json')
import_data('servers', 'private/RTB_data.servers.json')
import_data('users', 'private/RTB_data.users.json')

print("Импорт данных завершен!")