import asyncio
import codecs
import datetime
import math
import random
import re
import time
from random import randint

import discord
import pymongo
import requests

import Data
from Data import cursor, db


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

    # cursor.execute("SELECT karma, luck FROM users WHERE userid = ?", (id,))
    # result = cursor.fetchone()
    result = db.users.find_one({"userid":id}, {"karma":1, "luck":1})
    if result:
        karma = result["karma"]
        luck = result["luck"]
    else:
        Data.writeUserToDB(id, name)
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
                          color=Data.embedColors["Error"])
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
def formatStringLength(string : str, maxLength : int):
    strLen = int(len(string))
    lenOutLimit = int(maxLength) - int(strLen)
    r = ""
    if maxLength < 1:
        return ""
    if strLen <= maxLength:
        return string
    else:
        return string[:maxLength-1]+"…"
    # else:
    #     if maxLength < lenOutLimit + 20:
    #         if maxLength < lenOutLimit:
    #             if maxLength > 0:
    #                 return "."
    #             else:
    #                 return ""
    #         else:
    #
    #             return int(str(lenOutLimit))
    #     else:
    #         return string[:maxLength-int(len(str(lenOutLimit)))] + f"( и ещё {lenOutLimit+len(str(lenOutLimit))} символов...)"


def decode_unicode_escape(sequence):
    return codecs.decode(sequence, 'unicode_escape')

def convert_unicode_escape(input_string):
    pattern = re.compile(r'\\u([0-9a-fA-F]{4})')
    return re.sub(pattern, lambda x: decode_unicode_escape(x.group(0)), input_string)
def calc_levelByXP(xp):
    '''Returns tuple: [0] - current level, [1] - xp - minimal this level xp, [2] - next level xp - current level min xp
    Current level - int

    Thanks to PavelG for the formula!
    '''
    DIFFICULTY = 1.6
    level = int(math.log((xp * (DIFFICULTY-1) / 100) + 1, DIFFICULTY)) + 0
    xp_current = round(xp - ((100 * (DIFFICULTY ** (level - 1) - 1)) / (DIFFICULTY-1)))
    xp_next = round(100 * (DIFFICULTY ** (level - 1)))
    return (level,xp_current,xp_next)

async def initWebhook(channel, bot_id):
    try:
        hooks = await channel.webhooks()
        hook = None
        for h in hooks:
            if h.user.id == bot_id:
                hook = h
                break
        if not hook:
            hook = await channel.create_webhook(name="RTB hook", avatar=Data.webhook_avatar_url)
        return hook
    except:
        return None
def UTC2UNIX(UTC_string):
    utc_time = datetime.datetime.strptime(UTC_string, '%Y-%m-%d %H:%M:%S.%f%z')

    # Преобразование времени в UNIX-таймстамп в секундах
    unix_timestamp_sec = int(utc_time.timestamp())

    # Преобразование времени в UNIX-таймстамп в миллисекундах
    unix_timestamp_ms = unix_timestamp_sec * 1000
    return unix_timestamp_ms
def parseColorTo0xHEX(color_string: str) -> int:
    '''Input: 0xHEX, #HEX, RGB(0-1), RGB(0-255) with spaces between colors.
    Output: 0xHEX'''


    try:
        # Проверяем, является ли строка HEX-записью через 0x
        if color_string.startswith('0x'):
            color = int(color_string, 16)
        # Проверяем, является ли строка HEX-записью через #
        elif color_string.startswith('#'):
            color = int(color_string[1:], 16)
        # Проверяем, является ли строка RGB записью
        else:
            rgb_values = color_string.split()
            # Проверяем, являются ли значения в диапазоне 0-1
            if all(0 <= float(value) <= 1 for value in rgb_values):
                rgb_values = [str(int(float(value) * 255)) for value in rgb_values]
            # Проверяем, являются ли значения в диапазоне 0-255
            elif all(0 <= int(value) <= 255 for value in rgb_values):
                rgb_values = [str(int(value)) for value in rgb_values]
            else:
                return 0x3498db
            color = int(''.join(rgb_values), 10)
        return color
    except ValueError:
        return 0x3498db

    # Пример использования
    color_string = input("Введите строку цвета: ")
    parsed_color = parse_color(color_string)
    print(hex(parsed_color))
import asyncio
import subprocess

async def execute_python_code(code, timeout, allowed_libraries=None, allowed_modules=None):
    async def run_code():
        try:
            process = await asyncio.create_subprocess_exec(
                'python3', '-c', code,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
            if process.returncode == 0:
                return stdout.decode().strip() if stdout else "No output"
            else:
                return stderr.decode().strip() if stderr else "Unknown error"
        except asyncio.TimeoutError:
            return "Timed out"
        except Exception as e:
            return f"Error: {str(e)}"

    return await run_code()

# # Пример использования функции
# code = "print('Hello, World!')"
# allowed_libraries = ["math", "random"]
# allowed_modules = ["os", "sys"]
#
# result = asyncio.run(execute_python_code(code, 10, allowed_libraries, allowed_modules))
# print(result)
if __name__ == '__main__':
    ...
# print(hashgen(16))
# # Пример использования
# json_str = save_to_json("MyServer", "Some report text", 1632048765)
# print(json_str)
#
# load_from_json(json_str)
# while True:
#     print(format_number((convert_to_number(input(">")))))
# asyncio.run(Data.setPermissionForUser(609348530498437140, "root", True))
