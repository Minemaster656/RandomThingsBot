# Подключение к MongoDB
from pymongo import MongoClient

# Установка соединения с сервером MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Выбор базы данных
db = client['mydatabase']

# Выбор коллекции
collection = db['mycollection']

# Добавление новой строки
document = {"id": 1000, "value": 10}
collection.insert_one(document)

# Поиск значения и вывод его в консоль
result = collection.find_one({"id": 1000})
print(result)

# Обновление строки
collection.update_one({"id": 1000}, {"$set": {"value": 11}})

# Добавление новой колонки в строках
collection.update_many({}, {"$set": {"new_column": "new_value"}})