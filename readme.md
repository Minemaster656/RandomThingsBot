Для запуска бота **необходимо** создать в папке `DBBot/private` файл `coreData.py`. БД на Mongo создастся сама, если [MongoDB установлен](https://www.mongodb.com/), а в coreData.py необходимо указать следующий код:
```python
token_ds = 'тут токен бота для Discord'
token_tg = "Токен бота Telegram"
tokens = {"OWM":'токен для OWM'}
mongo_url = "mongodb://localhost:27017/"
mongo_db_name = 'RTB_data'
API_KEYS={
"kandinskiy3":[{"X-Key":"публичный ключ", "X-Secret":"секрет"}], #сейчас в боте используется 4 таких пары, если вдруг вы решили стырить этого бота, то вам в лицо кинет ошибку, если вы не оставите тут 4 ключа
"GigaChat":{"secret":"client secret", "auth":"auth string, окно client secret, строка 2",
            "clientID":"client id", "scope":"scope"},
    "deepinfra":"token",
    "openrouter":"token"
}
qdrant_url = "Qdrant url"
qdrant_api_key = "API ключ Qdrant"
qdrant_port = 6333
```
На данный момент из них используется только токен для Discord, название и URL базы данных, а так же API ключи. Замените URL базы данных если используете не локальную базу, а удалённый доступ.
Спасибо Pavelg за мотивацию создать бота и самую различную помощь.
Спасибо MichaAI за хост бота
Спасибо Googer (Def-try) за помощь с MongoDB
Спасибо Clyde (ChatGPT) за помощь с изучением библиотек

FactCheckExplorer ставится командой:
pip install git+https://github.com/GONZOsint/factcheckexplorer.git