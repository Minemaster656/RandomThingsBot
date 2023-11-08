import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('../private/data.db')
cursor = conn.cursor()

# Выполнение запроса на выборку всех данных из таблицы
cursor.execute("SELECT * FROM servers")
rows = cursor.fetchall()

# Вывод данных
for row in rows:
    print(row)

# Закрытие соединения с базой данных
conn.close()