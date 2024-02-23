from pymongo import MongoClient

from private import coreData


def clearCollections(collections):
    # Подключение к MongoDB
    client = MongoClient(coreData.mongo_url)
    db = client[coreData.mongo_db_name]

    # Список коллекций, из которых нужно удалить данные
    collections = ['users']

    # Удаление данных из коллекций
    for collection_name in collections:
        collection = db[collection_name]
        collection.delete_many({})

    print("Данные успешно удалены из выбранных коллекций: ", end="")
    print(collections)
