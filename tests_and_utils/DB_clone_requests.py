import sqlite3

def generate_insert_queries(database, table):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # Получение столбцов таблицы
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [column[1] for column in cursor.fetchall()]

    # Получение строк таблицы
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()

    # Генерация запросов для добавления строк
    for row in rows:
        values = ', '.join([f"'{value}'" if isinstance(value, str) else str(value) for value in row])
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({values})"
        print(query)

    conn.close()

# Пример использования
database = input("Введите адрес БД: ")
table = input("Введите название таблицы: ")

generate_insert_queries(database, table)