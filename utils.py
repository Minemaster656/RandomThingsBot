import asyncio
import random
import time
from random import randint

import discord
import pymongo
import requests

import publicCoreData
from publicCoreData import cursor


def invertY(y, maxY):
    invertedY = maxY - y - 1
    return invertedY
def format_number(num):
    if num < 10000:
        return str(num)
    elif num < 1e15:
        if num < 1e3:
            return f"{num:.2f}"
        elif num < 1e6:
            return f"{num/1e3:.2f}K"
        elif num < 1e9:
            return f"{num/1e6:.2f}M"
        elif num < 1e12:
            return f"{num/1e9:.2f}B"
        else:
            return f"{num/1e12:.2f}T"
    else:
        return f"{num:.2e}".replace("+", "")

def convert_to_number(string):
    if string.endswith("K"):
        return int(float(string[:-1]) * 1e3)
    elif string.endswith("M"):
        return int(float(string[:-1]) * 1e6)
    elif string.endswith("B"):
        return int(float(string[:-1]) * 1e9)
    elif string.endswith("T"):
        return int(float(string[:-1]) * 1e12)
    elif "e" in string:
        return float(string)
    else:
        return int(string)
def throwDice(id, name):

    cursor.execute("SELECT karma, luck FROM users WHERE userid = ?", (id,))
    result = cursor.fetchone()
    if result:
        karma = result[0]
        luck = result[1]
    else:
        publicCoreData.writeUserToDB(id, name)
        karma = 0
        luck = 0

    def makeThrow():
        def genRandom():
            o = randint(1, 20) + luck
            if o > 20:
                o = 20
            if o < 1:
                o = 1
            return o

        out = genRandom()

        if karma < -1 and out > 10:
            out = genRandom()
        if karma > 1 and out < 10:
            out = genRandom()
        return out
    return makeThrow()
async def noPermission(ctx, permissions):
    cursor.execute('SELECT permissions FROM users WHERE userid = ?', (ctx.author.id,))
    perms = cursor.fetchone()
    permissions = permissions.replace("|", "или")
    permissions = permissions.replace("&", "и")
    permissions = "`"+permissions+"`"
    embed = discord.Embed(title="У Вас нет прав!", description="Нет разрешения!",
                          color=publicCoreData.embedColors["Error"])
    embed.add_field(name="Нет разрешения!", value=f"Вам необходимо(ы) разрешение(я): \n> {permissions}\n<@{ctx.author.id}>\n"
                                                  f"Ваши текущие разрешения: \n"
                                                  f"> {perms}")
    await ctx.respond(embed=embed, ephemeral=False)
import json

def save_report_to_json(server_name: str, report_text: str, timestamp: int) -> str:
    data = {
        "server_name": server_name,
        "report_text": report_text,
        "timestamp": timestamp
    }
    json_str = json.dumps(data)
    return json_str

def load_report_from_json(json_str: str):
    data = json.loads(json_str)
    server_name = data["server_name"]
    report_text = data["report_text"]
    timestamp = data["timestamp"]
    # print(f"Server Name: {server_name}")
    # print(f"Report Text: {report_text}")
    # print(f"Timestamp: {timestamp}")
    return data
def hashgen(length):
    hash_symbols = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ12345/-#$%:."
    output = ""
    for i in range(length):
        output += random.choice(hash_symbols)
    return output
async def sendMessageWithhook(ctx, text, name, embed):
    avatar_url = str(
        "https://images-ext-2.discordapp.net/external/-1-6AJKBQh38RYGz6D3j-IgURlKEfFifX5LeJ8h-TBw/%3Fsize%3D4096/https/cdn.discordapp.com/avatars/1126887522690142359/0767783560eee507f86c95a4b09f120a.png?width=437&height=437")  # str(self.bot.user.avatar_url)  # ссылка на аватар бота
    webhook_name = str("RTBot's webhook")
    channel = ctx.channel
    webhooks = await channel.webhooks()
    webhook = discord.utils.get(webhooks, name=webhook_name)
    if webhook is None:
        avatar_bytes = requests.get(avatar_url).content
        webhook = await channel.create_webhook(name=str(webhook_name), avatar=avatar_bytes)
    user = ctx.author
    if name is None or name == "" or name == " ":
        name=webhook_name

    await webhook.send(f'{text}', username=name, embed=embed)
def get_current_day():
    current_time = time.time()
    days_since_unix_epoch = current_time // (24 * 60 * 60)
    return int(days_since_unix_epoch)
def checkStringForNoContent(strg : str):
    if strg == "" or strg is None or strg == " " or strg == "  " or strg == "\n":
        return True
    return False
def handle_key_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return None
    return wrapper
def handle_missing_field(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except pymongo.errors.PyMongoError as e:
            if isinstance(e, pymongo.errors.OperationFailure) and e.code == 16840:
                # Поле отсутствует в документе
                collection = args[0]  # Первый аргумент - коллекция MongoDB
                document_id = args[1]  # Второй аргумент - идентификатор документа
                field = kwargs['field']  # Поле, которое отсутствует
                default_value = e.details.get('errmsg').split()[-1].strip("'")
                collection.update_one({"_id": document_id}, {"$set": {field: default_value}})
                return func(*args, **kwargs)
            else:
                print(f"Произошла ошибка MongoDB: {str(e)}")
                # Дополнительные действия по обработке ошибки
    return wrapper


def zalgo_text(text, intensity):
    zalgo_chars = [
        '\u030d', '\u030e', '\u0304', '\u0305', '\u033f', '\u0311', '\u0306', '\u0310', '\u0352', '\u0357',
        '\u0351', '\u0307', '\u0308', '\u030a', '\u0342', '\u0343', '\u0344', '\u034a', '\u034b', '\u034c',
        '\u0303', '\u0302', '\u030c', '\u0350', '\u0300', '\u0301', '\u030b', '\u030f', '\u0312', '\u0313',
        '\u0314', '\u033d', '\u0309', '\u0363', '\u0364', '\u0365', '\u0366', '\u0367', '\u0368', '\u0369',
        '\u036a', '\u036b', '\u036c', '\u036d', '\u036e', '\u036f', '\u033e', '\u035b', '\u0346', '\u031a'
    ]

    intensity = max(75, min(125, intensity))  # Limit intensity to 75-125%
    intensity = intensity / 100  # Convert intensity to decimal

    zalgo_text = ''
    for char in text:
        zalgo_text += char
        for _ in range(int(intensity * len(char) * len(zalgo_chars))):
            zalgo_text += random.choice(zalgo_chars)

    return zalgo_text



# print(hashgen(16))
# # Пример использования
# json_str = save_to_json("MyServer", "Some report text", 1632048765)
# print(json_str)
#
# load_from_json(json_str)
# while True:
#     print(format_number((convert_to_number(input(">")))))
# asyncio.run(publicCoreData.setPermissionForUser(609348530498437140, "root", True))
