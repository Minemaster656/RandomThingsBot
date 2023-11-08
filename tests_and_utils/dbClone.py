import sqlite3

def getSQLs(isPrinted : bool):
    output = ""
    # Подключение к базе данных
    conn = sqlite3.connect('../private/data.db')
    cursor = conn.cursor()

    # Получение списка всех таблиц в базе данных
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Перебор таблиц и вывод SQL-запросов для их создания
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ("
        for column in columns:
            column_name = column[1]
            column_type = column[2]
            default_value = column[4]
            is_unique = column[5]

            create_query += f"{column_name} {column_type}"

            if default_value:
                create_query += f" DEFAULT {default_value}"

            if is_unique == 1:
                create_query += " UNIQUE"

            create_query += ", "

        create_query = create_query.rstrip(", ") + ");"
        if isPrinted:
            print(create_query)
        else:
            output+=create_query
            output+="\n\n=======\n\n"
    # Закрытие соединения с базой данных
    conn.close()
    return output