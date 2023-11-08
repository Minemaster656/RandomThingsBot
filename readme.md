Для запуска бота **необходимо** создать в папке `DBBot/private` файл `coreData.py`. БД на Mongo создастся сама, если [MongoDB установлен](https://www.mongodb.com/), а в .py-файле необходимо указать следующий код:
```python
token_ds = 'тут токен бота для Discord'
token_tg = "Токен бота Telegram"
tokens = {"OWM":'токен для OWM'}
mongo_url = "mongodb://localhost:27017/"
mongo_db_name = 'RTB_data'

```
На данный момент из них используется только токен для Discord, название и URL базы данных. Замените URL базы данных если используете не локальную базу, а удалённый доступ.
