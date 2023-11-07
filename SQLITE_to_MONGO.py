import sqlite3
from pymongo import MongoClient

# Подключение к SQLite3
sqlite_conn = sqlite3.connect('your_sqlite_database.db')
sqlite_cursor = sqlite_conn.cursor()

# Получение списка таблиц в SQLite3
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = sqlite_cursor.fetchall()

# Подключение к MongoDB
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['your_mongodb_database']

# Перенос данных из SQLite3 в MongoDB
for table in tables:
    table_name = table[0]
    collection = mongo_db[table_name]

    # Получение столбцов таблицы
    sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in sqlite_cursor.fetchall()]

    # Получение данных из таблицы
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()

    # Вставка данных в MongoDB
    for row in rows:
        document = {}
        for i, value in enumerate(row):
            if isinstance(value, str):
                document[columns[i]] = value
            elif isinstance(value, int):
                document[columns[i]] = int(value)
            elif isinstance(value, float):
                document[columns[i]] = float(value)
        collection.insert_one(document)

# Закрытие подключений
sqlite_conn.close()
mongo_client.close()