import asyncio
from datetime import datetime
# -*- coding: utf-8 -*-
import discord
# from discord_components import DiscordComponents, Button
import sqlite3
from discord import Option

# from discord import Option
import requests

# from commands import *
import sqlite3
from pyowm import OWM
# import torch
# import torchvision
# from stable_diffusion import DiffusionModel

#cogs
import game

import coreData

whitelist = [609348530498437140, 617243612857761803]
token = coreData.token_ds
from discord.ext import commands
import random

intents = discord.Intents.default()  # Подключаем "Разрешения"
intents.message_content = True
intents.reactions = True
# Задаём префикс и интенты
bot = commands.Bot(command_prefix='.', intents=intents)

# Подключение к базе данных
conn = sqlite3.connect('data.db')
cursor = conn.cursor()


def makeDSTimestamp(year, month, day, hour, minute, second, timezone, mode):
    dt = datetime.datetime(year, month, day, hour, minute, second,
                           tzinfo=datetime.timezone(datetime.timedelta(hours=timezone)))
    return f"<t:{int(dt.timestamp())}:{mode[0]}>"

# class Weather(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.owm = OWM(coreData.tokens["OWM"])
#
#     @commands.command(name="погода")
#     async def weather(self, ctx, city: str):
#         # Получите данные о текущей погоде в указанном городе
#         observation = requests.get(url)#self.owm.weather_at_place(city)
#         weather = observation.get_weather()
#
#         # Выведите информацию о текущей погоде
#         await ctx.send(f"Текущая погода в {city}:")
#         await ctx.send(f"* Температура: {weather.get_temperature('celsius').get('temp'):.1f} °C")
#         await ctx.send(f"* Ощущается как: {weather.get_temperature('celsius').get('feels_like'):.1f} °C")
#         await ctx.send(f"* Погода: {weather.get_weather_description()}")
#
#         # Получите данные о прогнозе погоды на ближайшее время
#         forecast = self.owm.daily_forecast(city)
#         for day in forecast.get_forecast().get_days():
#             # Выведите информацию о погоде на один день
#             await ctx.send(f"Прогноз погоды на {day.get_date()}:")
#             await ctx.send(f"* Температура: {day.get_temperature('celsius').get('min'):.1f}-{day.get_temperature('celsius').get('max'):.1f} °C")
#             await ctx.send(f"* Погода: {day.get_weather().get('main')}")


@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

@bot.command(aliases=['rand', 'ранд', 'r', 'р', 'rnd', 'рнд', 'random', 'рандом'])
async def random_int(ctx, arg1: int, arg2: int):
    await ctx.send(random.randint(arg1, arg2))


@bot.command(aliases=['me', 'я', '>'])
async def sendMsg(ctx, *, args):
    if ctx.author.id in whitelist:
        if ctx.message.reference:
            await ctx.send(args, reference=ctx.message.reference)
        else:
            await ctx.send(args)
    await ctx.message.delete()


@bot.command(aliases=["hlp", "хелп", "помощь", "commands", "команды"])
async def sendHelp(ctx):
    await ctx.send('''Preffix: .
ping - sends pong
rand, ранд, r, р, rnd, рнд, random, рандом - sends a random integer. Arguments: a b

<@1126887522690142359> by @minemaster_''')

@bot.slash_command(description="Список команд.",name="хелп") #guilds=[1076117733428711434]
async def help(ctx):
    await ctx.respond(f"Чел, используй /-команды\nА если невтерпёж то вот список:\nhelp, sendHelp, hlp, хелп, помощь, commands, команды\n"
                      f"sendMsg, me, я, >"
                      f"\nrand, ранд, r, р, rnd, рнд, random, рандом, random_int"
                      f"\nping"
                      f"\nВсё с преффиксом ."
                      f"\nВ дальнейшем этот список может быть расширен, но всё же приоритетнее разработка /-комманд. Из их минусов - их долгая индексация и ввод в замен на простоту использования."
                      )
@bot.slash_command(description="Сообщение от лица бота.",name="бот")
async def me(ctx, text):
    if ctx.author.id in whitelist:
        if ctx.message.reference:
            await ctx.send(text)

# @bot.command()
# async def send_embed(ctx):
#     embed = discord.Embed(title="Заголовок", description="Описание", color=discord.Color.blue())
#     embed.add_field(name="Поле 1", value="Значение 1", inline=False)
#     embed.add_field(name="Поле 2", value="Значение 2", inline=True)
#     embed.set_footer(text="Футер")
#
#     await ctx.send(embed=embed)

@bot.command(aliases=[".."])
async def cmd_trigger_bruh(ctx):
    await ctx.send("bruh")

@bot.command(aliases=["осебе","профиль","profile"])
async def about(ctx, user: discord.Member = None):
    async with ctx.typing():
        if user is None:
            user = ctx.author
        userid = user.id
        cursor.execute("SELECT * FROM users WHERE userid = ?", (userid,))
        result = cursor.fetchone()

        async def send_user_info_embed(color, about, age, timezone):

            embed = discord.Embed(title=user.display_name, description=user.name, color=discord.Colour.blue())
            embed.add_field(name="О себе", value="> *"+about+"*", inline=False)
            embed.add_field(name="Личные данные", value="- Возраст: "+age+"\n- Часовой пояс: UTC+"+timezone, inline=True)
            embed.set_footer(text='Редактировтаь параметры - .редактировать <имяпараметра строчными буквами без пробелов и этих <> > \"значение\"')
            await ctx.send(embed=embed)

        if result:
            await ctx.send("Запись найдена")
            #await send_user_info_embed("#5865F2" if result[5] is None else result[5], "Задать поле 'О себе' можно командой `.редактировать осебе`" if result[2] is None else result[2], "Задать поле 'Возраст' можно командой `.редактировать возраст`\nПожалуйста, ставьте только свой реальный возраст, не смотря на то, сколько вам лет." if result[3] is None else str(result[3]), "UTC+?. Задать часовой пояс можно командой `.редактировать часовойпояс`. Укажите свой часовой пояс относительно Гринвича." if result[4] is None else str(result[4]))
            clr = "#5865F2" if result[5] is None else result[5]
            abt = "Задать поле 'О себе' можно командой `.редактировать осебе`" if result[2] is None else result[2]
            tmz = "UTC+?. Задать часовой пояс можно командой `.редактировать часовойпояс`. Укажите свой часовой пояс относительно Гринвича." if result[4] is None else str(result[4])
            age = "Задать поле 'Возраст' можно командой `.редактировать возраст`\nПожалуйста, ставьте только свой реальный возраст, не смотря на то, сколько вам лет." if result[3] is None else str(result[3])
            await send_user_info_embed(clr, abt, age, tmz)
        else:
            await ctx.send("Запись о пользователе не найдена. Добавление...")
            cursor.execute("INSERT INTO users (userid, username) VALUES (?, ?)", (userid, user.name))
            conn.commit()
            await send_user_info_embed("#5865F2", "Задать поле 'О себе' можно командой .редактировать осебе", "Задать поле 'Возраст' можно командой `.редактировать возраст`\nПожалуйста, ставьте только свой реальный возраст, не смотря на то, сколько вам лет.", "UTC+?. Задать часовой пояс можно командой `.редактировать часовойпояс`. Укажите свой часовой пояс относительно Гринвича.")

@bot.command(aliases=["редактировать"])
async def edit(ctx, field, value):
    if field == "осебе":
        cursor.execute("UPDATE users SET about = ? WHERE userid = ?", (value, ctx.author.id))
        conn.commit()
        await ctx.reply("**Строка** `осебе` (.осебе) изменена!")
    elif field == "возраст":
        cursor.execute("UPDATE users SET age = ? WHERE userid = ?", (int(value), ctx.author.id))
        conn.commit()
        await ctx.reply("**Число** `возраст` (.осебе) изменено!")
    elif field == "часовойпояс":
        cursor.execute("UPDATE users SET timezone = ? WHERE userid = ?", (int(value), ctx.author.id))
        conn.commit()
        await ctx.reply("**Число** `часовойпояс` (.осебе) изменено!")
    else:
        ctx.reply("Допустимые параметры:\n"
                  "- осебе (строка)\n"
                  "- часовойпояс (целое число)\n"
                  "- возраст (целое число)")




@bot.command()
async def send_message(ctx):
    message = await ctx.send("Нажми на реакцию ❓, чтобы отправить это сообщение.")
    await message.add_reaction("❓")

@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return
    if reaction.message.author == bot.user:
        if str(reaction.emoji) == "❓":
            # await reaction.message.remove_reaction("❓", user)

            # reactors = await reaction.users().flatten()
            # authors = [str(author) for author in reactors]

            # for i in authors:
            #     if i ==
            # await reaction.message.channel.send(reaction.message.content)ё
            reactors = await reaction.users().flatten()
            # Проверка, что бот находится в списке авторов реакции
            if bot.user in reactors:
                await reaction.message.channel.send(reaction.message.content)
@bot.slash_command(description="Перевод раскладки",name="раскладка") #guilds=[1076117733428711434]
async def keyboard_layout_switcher(ctx, text):
    ru_layout = 'йцукенгшщзхъфывапролджэячсмитьбюё'
    en_layout = 'qwertyuiop[]asdfghjkl;\'zxcvbnm,.`'
    result = ''
    for char in text:
        if char.lower() in ru_layout:
            index = ru_layout.index(char.lower())
            result += en_layout[index] if char.islower() else en_layout[index].upper()
        elif char.lower() in en_layout:
            index = en_layout.index(char.lower())
            result += ru_layout[index] if char.islower() else ru_layout[index].upper()
        else:
            result += char
    await ctx.respond(result, ephemeral=True)


# @commands.slash_command(name="мьют",description="Переключить мьют пользоваателя (роль)")
# async def my_command(self, ctx, user : discord.Member):
#     role = discord.utils.get(ctx.guild.roles, id=role_id)
#     if role in user.roles:
#         await
#     else:
#         await


# @bot.slash_command(name="метка-времени", description="Конвертирует дату, время и часовой пояс в метку времени")
# async def time(ctx, year: Option(int, description="Год для даты", required=False) = 1970,
#                month: Option(int, description="Номер месяца года", required=False) = 1,
#                day: Option(int, description="Номер дня месяца", required=False) = 1,
#                hour: Option(int, description="Час дня", required=False) = 0,
#                minute: Option(int, description="Минута часа", required=False) = 0,
#                second: Option(int, description="Секунда минуты", required=False) = 0,
#                timezone: Option(int, description="Временная зона GMT+n", required=False) = 0,
#                mode: Option(str, description="Тип отображения", choices=("R — Оставшееся время",
#                                                                          "d — Короткая запись даты только цифрами",
#                                                                          "D — Дата с подписью месяца словом",
#                                                                          "f — Дата и время",
#                                                                          "F — Полные день недели, дата и время",
#                                                                          "t — Часы и минуты",
#                                                                          "T — Часы, минуты и секунды"),
#                             required=False) = "R"):
#     await ctx.respond(makeDSTimestamp(year, month, day, hour, minute, second, timezone, mode))



# @help.slash_option(name="name", description="Enter your name.", required=True)
# async def hello_name(ctx, name: str):
#     await ctx.send(f"Hello, {name}!")



# commands = {
#    '!rand': rand,
#    '!ранд': rand,
#    '!р': rand,
#    '!r': rand
# }


# @bot.event
# async def on_message(message):
#    if message.content.lower() in commands:
#        await commands[message.content.lower()](message)

async def loop():
    ...
# bot.add_cog(Weather(bot))
bot.add_cog(game.Game(bot))
asyncio.run(loop())
bot.run(token)
