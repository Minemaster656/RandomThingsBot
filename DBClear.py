import sqlite3

# Соединение с базой данных
conn = sqlite3.connect('ApocalypseData/ApocalypseItems.db')  # Замените 'database.db' на имя вашей базы данных
cursor = conn.cursor()

# Выполнение SQL-запроса для удаления всех значений
cursor.execute("DELETE FROM items")  # Замените 'table_name' на имя вашей таблицы

# Подтверждение изменений в базе данных
conn.commit()

# Закрытие соединения с базой данных
cursor.close()
conn.close()