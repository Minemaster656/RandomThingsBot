import sqlite3
from pymongo import MongoClient
from private import coreData

SQL_DB_PATH = r"C:\Users\Admin\Downloads\data_to_export.db"
MONGO_DB_NAME = "RTB_data"

# Подключение к базе данных SQLite3
sqlite_conn = sqlite3.connect(SQL_DB_PATH)
sqlite_cursor = sqlite_conn.cursor()

# Подключение к MongoDB
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client[MONGO_DB_NAME]

# Получение списка таблиц в базе данных SQLite3
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = sqlite_cursor.fetchall()

# Проход по таблицам
for table in tables:
    table_name = table[0]
    collection = mongo_db[table_name]

    # Получение данных из таблицы SQLite3
    sqlite_cursor.execute(f"SELECT * FROM {table_name};")
    rows = sqlite_cursor.fetchall()

    # Проход по строкам
    for row in rows:
        document = {}
        for i, column_name in enumerate(sqlite_cursor.description):
            column_value = row[i]
            document[column_name[0]] = column_value

        # Добавление документа в коллекцию MongoDB
        collection.insert_one(document)

# Закрытие соединений
sqlite_cursor.close()
sqlite_conn.close()
mongo_client.close()