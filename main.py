import asyncio
import os
import time
from datetime import datetime
# -*- coding: utf-8 -*-
import discord
# from discord_components import DiscordComponents, Button
import sqlite3
from discord import Option, ButtonStyle

# from discord_components import DiscordComponents, Button, ButtonStyle

# from discord import Option
import requests

# from commands import *
import sqlite3

from discord.ui import Button
# from pyowm import OWM
# import torch
# import torchvision
# from stable_diffusion import DiffusionModel
from PIL import Image, ImageFilter, ImageDraw, ImageOps
import requests
from io import BytesIO

import dbClone
import economy
import paginator
import publicCoreData
import utilities
from coreData import *

# cogs
import game
import rp
import tests

import coreData
from publicCoreData import cursor
from publicCoreData import conn

whitelist = [609348530498437140, 617243612857761803]
token = coreData.token_ds
from discord.ext import commands
import random

startTimeCounter = time.time()
intents = discord.Intents.default()  # Подключаем "Разрешения"
intents.message_content = True
intents.reactions = True
# Задаём префикс и интенты
runtime = time.time()
loopCounter = 0
bot = commands.Bot(command_prefix=publicCoreData.preffix, intents=intents)





@bot.command()
async def ping(ctx):
    await ctx.send('pong')



@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user} за {time.time() - startTimeCounter} секунд.")
    total_members = sum(len(guild.members) for guild in bot.guilds)
    await bot.change_presence(activity=discord.Game(f"{total_members} серверов"))



async def noPermission(ctx, permissions):
    cursor.execute('SELECT permissions FROM users WHERE userid = ?', (ctx.author.id,))
    perms = cursor.fetchone()
    embed = discord.Embed(title="У Вас нет прав!", description="Нет разрешения!",
                          color=publicCoreData.embedColors["Error"])
    embed.add_field(name="Нет разрешения!", value=f"Вам необходимо(ы) разрешение(я): \n> {permissions}\n<@{ctx.author.id}>\n"
                                                  f"Ваши текущие разрешения: \n"
                                                  f"> {perms}")
    await ctx.respond(embed=embed, ephemeral=False)
@bot.event
async def on_command_error(ctx, error):
    none = "None"
    # if isinstance(error, commands.CommandError):
    # Отправляем сообщение об ошибке в канал, где была использована команда
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="У Вас нет прав!", description="Нет разрешения!",
                              color=publicCoreData.embedColors["Error"])
        embed.add_field(name= "Нет разрешения!", value=f"Вам необходимо(ы) разрешение(я): {none}")
        await ctx.send(embed=embed, ephemeral=False)
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Команда перезаряжается. Повторите через **{round(error.retry_after)}** секунд!")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"Недостаточно прав!")
    else:
        await ctx.send(f'Произошла ошибка при выполнении команды: {error}')
@bot.slash_command(name="настройки", description="Задать определённую настройку бота")
async def set_settings(ctx, field : Option(str, description="Поле", required=True, choices=["SQL+commit", "eval", "Таблицы","Баланс"])=0, value : Option(str, description="Значение", required=True)=0, ephemeral : Option(bool, description="Видно ли только вам?", required=False)=False):
    hasPermission=False
    hasPermission = await publicCoreData.parsePermissionFromUser(ctx.author.id, "root")
    if hasPermission==True:
        embed = discord.Embed(title="В разработке...", description="Вам необходимо разрешение root для использования.",
                              color=publicCoreData.embedColors["Warp"])
        if field == "SQL+commit":
            cursor.execute(value)
            conn.commit()
            embed = discord.Embed(title="Запрос выполнен!", description=f"Запрос: {value}",
                                  color=publicCoreData.embedColors["Success"])
        elif field == "eval":
            eval(value)
            embed = discord.Embed(title="Код выполнен!", description=f"Код: {value}",
                                  color=publicCoreData.embedColors["Success"])
        elif field == "Таблицы":
            embed = discord.Embed(title="Таблицы получены!", description=f"Запросы: \n=====\n\n{dbClone.getSQLs(False)}",
                                  color=publicCoreData.embedColors["Success"])


        await ctx.respond(embed=embed, ephemeral=ephemeral)
    else:
        await noPermission(ctx, "root")


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


@bot.slash_command(description="Список команд.", name="хелп")  # guilds=[1076117733428711434]
async def help(ctx):
    await ctx.respond(
        f"Чел, используй /-команды\nА если невтерпёж то вот список:\nhelp, sendHelp, hlp, хелп, помощь, commands, команды\n"
        f"sendMsg, me, я, >"
        f"\nrand, ранд, r, р, rnd, рнд, random, рандом, random_int"
        f"\nping"
        f"\nВсё с преффиксом ."
        f"\nВ дальнейшем этот список может быть расширен, но всё же приоритетнее разработка /-комманд. Из их минусов - их долгая индексация и ввод в замен на простоту использования."
        )


@bot.slash_command(description="Сообщение от лица бота.", name="бот")
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


@bot.command(aliases=["осебе", "профиль", "profile"])
async def about(ctx, user: discord.Member = None):
    async with ctx.typing():
        if user is None:
            user = ctx.author
        userid = user.id
        cursor.execute("SELECT * FROM users WHERE userid = ?", (userid,))
        result = cursor.fetchone()

        async def send_user_info_embed(color, about, age, timezone, karma, luck):
            def convertKarmaToEmoji(karma):
                if karma < -1:
                    return "⬛"
                elif karma > 1:
                    return "⬜"
                else:
                    return "🔲"

            def convertLuckToEmoji(luck):
                if luck < -10:
                    return "⬛"
                elif luck < -5:
                    return "🟫"
                elif luck < -3:
                    return "🟥"
                elif luck < -1:
                    return "🟧"

                elif luck > 1:
                    return "🟨"
                elif luck > 3:
                    return "🟩"
                elif luck > 5:
                    return "🟦"
                elif luck > 10:
                    return "🟪"
                else:
                    return "⬜"

            embed = discord.Embed(title=user.display_name, description=user.name, color=discord.Colour.blue())
            embed.add_field(name="О себе", value="> *" + about + "*", inline=False)
            embed.add_field(name="Личные данные", value="- Возраст: " + age + "\n- Часовой пояс: UTC+" + timezone,
                            inline=True)

            embed.add_field(name="прочее", value=f"{convertKarmaToEmoji(karma)}{convertLuckToEmoji(luck)}",
                            inline=False)
            embed.set_footer(
                text='Редактировтаь параметры - .редактировать <имяпараметра строчными буквами без пробелов и этих <> > \"значение\"')
            await ctx.send(embed=embed)

        if result:
            await ctx.send("Запись найдена")




            clr = "#5865F2" if result[5] is None else result[5]
            abt = "Задать поле 'О себе' можно командой `.редактировать осебе`" if result[2] is None else result[2]
            tmz = "UTC+?. Задать часовой пояс можно командой `.редактировать часовойпояс`. Укажите свой часовой пояс относительно Гринвича." if \
            result[4] is None else str(result[4])
            age = "Задать поле 'Возраст' можно командой `.редактировать возраст`\nПожалуйста, ставьте только свой реальный возраст, не смотря на то, сколько вам лет." if \
            result[3] is None else str(result[3])
            karma = result[6]
            luck = result[7]
            await send_user_info_embed(clr, abt, age, tmz, karma, luck)
        else:
            await ctx.send("Запись о пользователе не найдена. Добавление...")
            # cursor.execute("INSERT INTO users (userid, username) VALUES (?, ?)", (userid, user.name))
            # conn.commit()
            publicCoreData.writeUserToDB(user)

            await send_user_info_embed("#5865F2", "Задать поле 'О себе' можно командой .редактировать осебе",
                                       "Задать поле 'Возраст' можно командой `.редактировать возраст`\nПожалуйста, ставьте только свой реальный возраст, не смотря на то, сколько вам лет.",
                                       "UTC+?. Задать часовой пояс можно командой `.редактировать часовойпояс`. Укажите свой часовой пояс относительно Гринвича.")


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


@bot.slash_command(description="Перевод раскладки", name="раскладка")  # guilds=[1076117733428711434]
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


@bot.slash_command(name="тест-работы-с-изображениями", description="обеме")
async def send_image(ctx):
    # image = Image.open('10x10.png')

    # Выполняем необходимые операции с изображением
    # Например, изменение размера, обрезка, фильтры и т.д.
    # image = image.resize((256, 256), resample=Image.NEAREST)

    # Создаем пустое прозрачное изображение размером 300x200 пикселей
    image = Image.new('RGBA', (300, 200), (0, 0, 0, 0))

    # Открываем изображение квадратика
    square_image = Image.open('10X10.png')
    gray = Image.open("gray.png")
    gray = gray.convert("L")
    # Создаем объект ImageDraw для рисования
    draw = ImageDraw.Draw(image)

    # Определяем координаты верхнего левого и нижнего правого углов квадратика
    x1 = 10
    y1 = 10
    x2 = x1 + 3
    y2 = y1 + 3
    for i in range(10):

        # Рисуем квадратик поверх пустого изображения
        if i % 2 == 0:
            cim = ImageOps.colorize(gray, '#FF0000', '#000000')
            image.paste(cim, (i * 10, y1 + 10))
        image.paste(square_image, (i * 10, y1))

    # jittered_image = image.filter(ImageFilter.GaussianBlur(radius=2))
    # jittered_image = jittered_image.resize(image.size)
    # jittered_image = Image.blend(image, jittered_image, alpha=0.5)

    # image = glitch(image)

    # Сохраняем измененное изображение

    image.save('image_buffer.png')
    # jittered_image.save('image_buffer.png')

    # Отправляем изображение в качестве сообщения

    modified_image_path = 'image_buffer.png'
    modified_image = discord.File(modified_image_path, filename='image_buffer.png')
    await ctx.respond(file=modified_image)


# @bot.command()
# async def send_buttons(ctx):
#     await ctx.send(
#         "Нажмите кнопку:",
#         components=[
#             Button(style=ButtonStyle.primary, label="Кнопка 1"),
#             Button(style=ButtonStyle.secondary, label="Кнопка 2"),
#             Button(style=ButtonStyle.success, label="Кнопка 3"),
#         ],
#     )
#
#
# @bot.event
# async def on_button_click(interaction):
#     if interaction.component.label == "Кнопка 1":
#         await interaction.respond(content="Вы нажали Кнопку 1")
#     elif interaction.component.label == "Кнопка 2":
#         await interaction.respond(content="Вы нажали Кнопку 2")
#     elif interaction.component.label == "Кнопка 3":
#         await interaction.respond(content="Вы нажали Кнопку 3")


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


@bot.event
async def on_message(message):
    # if message.mention_roles:  # Проверяем, были ли упомянуты роли в сообщении
    #         mentioned_roles = message.role_mentions  # Получаем список упомянутых ролей
    #         for role in mentioned_roles:
    #             if role.id in publicCoreData.infectionRolesID:  # Замени 'YOUR_ROLE_ID' на фактический ID роли
    #                 await message.author.add_roles(role)  # Даем автору сообщения эту роль
    for i in publicCoreData.infectionRolesID:
        # if str(i) in message.content:
        role = message.guild.get_role(i)
        for j in message.role_mentions:
            # print(str(j.id) + "   " + str(i))
            if j.id == i:

                await message.author.add_roles(role)
    # if message.mentions:  # Проверяем, были ли упомянуты пользователи в сообщении
    #     mentioned_users = message.mentions  # Получаем список упомянутых пользователей
    #     for role_id in publicCoreData.infectionRolesID:
    #     # role_id = 1234567890  # Замени на фактический ID роли
    #         role = message.guild.get_role(role_id)  # Получаем объект роли по ID
    #
    #         for user in mentioned_users:
    #             if role in user.roles and not message.reference:  # Проверяем наличие роли и отсутствие ответа на другое сообщение
    #                 # Выполняем нужные действия
    #                 # await message.channel.send(f"{user.mention}, у тебя есть роль с нужным ID!")
    #                 role = message.guild.get_role(role_id)
    # await message.add_reaction("❤")

    # await bot.process_commands(message)  # Обязательно добавь эту строку, чтобы обработать другие команды и события


# if message.content.lower() in commands:
#        await commands[message.content.lower()](message)

async def loop():

    ...
async def statusLoop():
    global loopCounter
    await asyncio.sleep(120)
    if loopCounter == 0:
        total_members = sum(len(guild.members) for guild in bot.guilds)
        await bot.change_presence(activity=discord.Game(name=f"{total_members} серверов"))
        loopCounter+=1
    elif loopCounter == 1:

        await bot.change_presence(activity=discord.Game(f"Discord-издание бота"))
        loopCounter += 1
    elif loopCounter == 2:

        await bot.change_presence(activity=discord.Game(name=f"PyCharm уже {int(time.time()-runtime)} секунд"))
        loopCounter += 1
    elif loopCounter == 3:

        await bot.change_presence(activity=discord.Game(f"DoorkaEternal"))
        loopCounter =0

# bot.add_cog(Weather(bot))
bot.add_cog(game.Game(bot))
# for f in os.listdir("./cogs"):
#     if f.endswith(".py"):
#         bot.load_extension("cogs." + f[:-3])
bot.add_cog(tests.Tests(bot))
bot.add_cog(rp.RP(bot))
bot.add_cog(economy.Economy(bot))
bot.add_cog(utilities.BotCog(bot))
# bot.add_cog(paginator.PageTest(bot))
asyncio.run(loop())
# asyncio.run(statusLoop())


bot.run(token)
