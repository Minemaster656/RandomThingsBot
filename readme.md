Для запуска бота **необходимо** создать в папке `DBBot/private` файлы `coreData.py` и `data.db`. Таблицы в базе данных создадутся автоматически при первом запуске (*наверно*), а в .py-файле необходимо указать следующий код:
```python
token_ds = 'тут токен бота для Discord'
token_tg = "Токен бота Telegram"
tokens = {"OWM":'токен для OWM'}

```
На данный момент из них используется только токен для Discord.