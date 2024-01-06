import asyncio
import datetime
import platform
# TODO: add transformers to requirements
import json
import time

import aiohttp
# -*- coding: utf-8 -*-
import discord
# from discord_components import DiscordComponents, Button
from discord import Option, Webhook, Forbidden
import pymongo
from pymongo import MongoClient

# from discord_components import DiscordComponents, Button, ButtonStyle

# from discord import Option

# from commands import *

# from pyowm import OWM
# import torch
# import torchvision
# from stable_diffusion import DiffusionModel

import Apocalypse
import HetTol
import ServerCore
import _AI_Stuff
import d
import fun
import voice
from tests_and_utils import dbClone
import economy
import publicCoreData
import utilities
import utils

# cogs
import game
import rp
import tests

from private import coreData
from publicCoreData import cursor
from publicCoreData import conn
from publicCoreData import db
from publicCoreData import collections

# db = MongoClient(coreData.mongo_url)
# mongo_db = db[coreData.mongo_db_name]


whitelist = [609348530498437140, 617243612857761803]
token = coreData.token_ds
from discord.ext import commands

sendAllExceptionsToChat = True

if platform.system() == 'Windows':
    try:
        import win10toast
    except:
        import os

        os.system("pip install win10toast")
        import win10toast
    toaster = win10toast.ToastNotifier()
startTimeCounter = time.time()
intents = discord.Intents.default()  # Подключаем "Разрешения"
intents.message_content = True
intents.reactions = True
# intents.guilds = True
# intents.channels = True
# intents.threads = True

# Задаём префикс и интенты
runtime = time.time()
loopCounter = 0
bot = commands.Bot(command_prefix=publicCoreData.preffix, intents=intents)


@bot.event
async def on_ready():
    print(
        f"Бот запущен как {bot.user} за {round(time.time() - startTimeCounter, 3)} секунд. Преффикс: {bot.command_prefix}")
    total_members = sum(len(guild.members) for guild in bot.guilds)
    await bot.change_presence(activity=discord.Game(f"{total_members} серверов"))
    if platform.system() == 'Windows':
        toaster.show_toast(f"Random Things Bot",
                           f"RTB:discord_bot запущен за {round(time.time() - startTimeCounter, 3)} секунд. Преффикс: {bot.command_prefix}",
                           threaded=True)


async def noPermission(ctx, permissions):
    """Вызов сообщения об отсутствии разрешений. Нужен контекст /-команды!"""
    result = db.users.find_one({"userid": ctx.author.id}, {"permissions": 1})
    perms = result["permissions"] if result else None
    permissions = permissions.replace("|", "или").replace("&", "и")
    permissions = f"`{permissions}`"
    embed = discord.Embed(title="У Вас нет прав!", description="Нет разрешения!",
                          color=publicCoreData.embedColors["Error"])
    embed.add_field(name="Нет разрешения!",
                    value=f"Вам необходимо(ы) разрешение(я): \n> {permissions}\n<@{ctx.author.id}>\n"
                          f"Ваши текущие разрешения: \n"
                          f"> {perms}")
    await ctx.respond(embed=embed, ephemeral=False)


@bot.event
async def on_command_error(ctx, error):
    """Обработка ошибок"""
    none = "None"
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="У Вас нет прав!", description="Нет разрешения!",
                              color=publicCoreData.embedColors["Error"])
        embed.add_field(name="Нет разрешения!", value=f"Вам необходимо(ы) разрешение(я): {none}")
        await ctx.send(embed=embed, ephemeral=False)
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Команда перезаряжается. Повторите через **{round(error.retry_after)}** секунд!")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"Недостаточно прав!")
    elif isinstance(error, IndexError):
        print(db)
        print(publicCoreData.client)
        await ctx.send(error)
    if (sendAllExceptionsToChat):
        await ctx.send(error)
    # else:
    #     await ctx.send(f'Произошла ошибка при выполнении команды: {error}')


@bot.slash_command(name="настройки-бота", description="Задать определённую настройку бота",
                   guilds=[1019180616731873290, 855045703235928094])
async def set_settings(ctx, field: Option(str, description="Поле", required=True,
                                          choices=["SQL+commit", "eval", "Таблицы", "Баланс"]) = 0,
                       value: Option(str, description="Значение", required=True) = 0,
                       ephemeral: Option(bool, description="Видно ли только вам?", required=False) = False,
                       member: Option(discord.Member, description="Пользователь, на которого влияет команда",
                                      required=False) = None):
    """Настройки и приколы бота для админов БОТА."""
    hasPermission = False
    hasPermission = await publicCoreData.parsePermissionFromUser(ctx.author.id, "root")
    if member is None:
        member = ctx.author
    if hasPermission == True:
        embed = discord.Embed(title="В разработке...", description="Вам необходимо разрешение root для использования.",
                              color=publicCoreData.embedColors["Warp"])
        if field == "SQL+commit":
            # cursor.execute(value)
            # conn.commit()
            embed = discord.Embed(title="Не поддерживается!",
                                  description=f"БАЗА ДАННЫХ ПЕРЕЕЗЖАЕТ НА MONGODB! Запрос: {value}",
                                  color=publicCoreData.embedColors["Exception"])
        elif field == "eval":
            eval(value)
            embed = discord.Embed(title="Код выполнен!", description=f"Код: {value}",
                                  color=publicCoreData.embedColors["Success"])
        elif field == "Таблицы":
            embed = discord.Embed(title="Таблицы получены!",
                                  description=f"БАЗА ДАННЫХ ПЕРЕЕЗЖАЕТ НА MONGODB! Запросы: \n=====\n\n{dbClone.getSQLs(False)}",
                                  color=publicCoreData.embedColors["Exception"])

        await ctx.respond(embed=embed, ephemeral=ephemeral)
    else:
        await noPermission(ctx, "root")


@bot.command(aliases=['me', 'я', '>'])
async def sendMsg(ctx, *, args):
    """Отправка сообщения от лица бота."""
    if publicCoreData.parsePermissionFromUser(ctx.author.id, "say_as_bot"):
        if ctx.message.reference:
            await ctx.send(args, reference=ctx.message.reference)
        else:
            await ctx.send(args)
    await ctx.message.delete()


@bot.slash_command(description="Список команд.", name="хелп")  # guilds=[1076117733428711434]
async def help(ctx):
    await ctx.respond(
        f"Тут должен быть нормальный help"
    )


# @bot.slash_command(description="Сообщение от лица бота.", name="бот")
# async def me(ctx, text):
#     if publicCoreData.parsePermissionFromUser(ctx.author.id, "say_as_bot"):
#         if ctx.message.reference:
#             await ctx.send(text, reference=ctx.message.reference)
#         else:
#             await ctx.send(text)
#     await ctx.message.delete()


@bot.command(aliases=["осебе", "профиль", "profile"])
async def about(ctx, user: discord.Member = None):
    async with ctx.typing():
        if user is None:
            user = ctx.author
        userid = user.id
        print("finding result")
        result = None
        try:
            result = db.users.find({"userid": userid})[0]
            result = d.schema(result, d.Schemes.user)
        except:
            print(result)
            # if not result:
            #     publicCoreData.writeUserToDB(ctx.author.id, ctx.author.name)

        async def send_user_info_embed(color, about, age, timezone, karma, luck, permissions, xp):
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
            embed.add_field(name="Разрешения", value=f"{str(permissions)}", inline=False)
            xps = utils.calc_levelByXP(xp)
            embed.add_field(name="Опыт",value=f"Всего опыта: {xp}\nУровень: {xps[0]}\nОпыта до следующего уровня: {xps[2]}",inline=False)
            embed.set_footer(
                text='Редактировтаь параметры - .редактировать <имяпараметра строчными буквами без пробелов и этих <> > \"значение\"')
            await ctx.send(embed=embed)

        if result:
            await ctx.send("Запись найдена")

            clr = "#5865F2" if result["color"] is None else result["color"]
            abt = "Задать поле 'О себе' можно командой `!!редактировать осебе`" if result["about"] is None else result[
                "about"]
            tmz = "UTC+?. Задать часовой пояс можно командой `.редактировать часовойпояс`. Укажите свой часовой пояс относительно Гринвича." if \
                result["timezone"] is None else str(result["timezone"])
            age = "Задать поле 'Возраст' можно командой `!!редактировать возраст`\nПожалуйста, ставьте только свой реальный возраст, не смотря на то, сколько вам лет." if \
                result["age"] is None else str(result["age"])
            karma = 0 if result["karma"] is None else str(result["karma"])
            luck = 0 if result["luck"] is None else str(result["luck"])
            await send_user_info_embed(clr, abt, age, tmz, int(karma), int(luck),
                                       result["permissions"], result["xp"])  # if result["permissions"] is None else '{}'
        else:
            await ctx.send("Запись о пользователе не найдена. Добавление...")
            publicCoreData.writeUserToDB(user.id, user.name)

            await send_user_info_embed("#5865F2", "Задать поле 'О себе' можно командой .редактировать осебе",
                                       "Задать поле 'Возраст' можно командой `.редактировать возраст`\nПожалуйста, ставьте только свой реальный возраст, не смотря на то, сколько вам лет.",
                                       "UTC+?. Задать часовой пояс можно командой `.редактировать часовойпояс`. Укажите свой часовой пояс относительно Гринвича.", 0,0,None,0)


@bot.command(aliases=["редактировать"])
async def edit(ctx, field, value):
    if field == "осебе":
        db.users.update_one({"userid": ctx.author.id}, {"$set": {"about": value}})
        await ctx.reply("**Строка** `осебе` (.осебе) изменена!")
    elif field == "возраст":
        db.users.update_one({"userid": ctx.author.id}, {"$set": {"age": int(value)}})
        await ctx.reply("**Число** `возраст` (.осебе) изменено!")
    elif field == "часовойпояс":
        db.users.update_one({"userid": ctx.author.id}, {"$set": {"timezone": int(value)}})
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


@bot.slash_command(name="разрешения", description="Редактирование разрешений пользователя")
async def editMemberPermissions(ctx, permission: Option(str, description="Разрешение. ? для списка",
                                                        choises=publicCoreData.permissions_user,
                                                        required=True) = "none",
                                member: Option(discord.Member, description="Пользователь", required=True) = None,
                                value: Option(bool, description="Значение", required=True) = True,
                                ephemeral: Option(bool, description="Видно ли только вам?",
                                                  required=False) = False):
    if member is None:
        member = ctx.author
    perm_root = await publicCoreData.parsePermissionFromUser(ctx.author.id, "root")
    perm_edit = await publicCoreData.parsePermissionFromUser(ctx.author.id, "edit_permissions")
    if permission != "?":
        if perm_root or perm_edit:
            if permission != "root":
                await publicCoreData.setPermissionForUser(member.id, permission, value)
                embed = discord.Embed(title=f"Разрешение {permission} изменено успешно!",
                                      description=f"Разрешение изменено у участника <@{member.id}> на **{value}**",
                                      colour=publicCoreData.embedColors["Success"])
                await ctx.respond(embed=embed, ephemeral=ephemeral)
            else:
                if perm_root:
                    await publicCoreData.setPermissionForUser(member.id, permission, value)
                    embed = discord.Embed(title=f"Разрешение {permission} изменено успешно!",
                                          description=f"Разрешение изменено у участника <@{member.id}> на **{value}**",
                                          colour=publicCoreData.embedColors["Success"])
                    await ctx.respond(embed=embed, ephemeral=ephemeral)
                else:
                    await noPermission(ctx, "root")
        else:
            await noPermission(ctx, "root | edit_permissions")
    else:
        await ctx.respond(json.dumps(publicCoreData.permissions_user))


@bot.slash_command(name="инфо", description="Информация о боте")
async def info(ctx):
    embed = discord.Embed(title="Информация о боте",
                          description=f"[Пригласить бота на сервер](https://discord.com/api/oauth2/authorize?client_id=1126887522690142359&permissions=8&scope=bot)"
                                      f"\n[Пригласить бота на сервер (BETA-тесты)](https://discord.com/api/oauth2/authorize?client_id=1169691387562835968&permissions=8&scope=bot)"
                                      f"\n[Исходники](https://github.com/Minemaster656/RandomThingsBot)\n"
                                      f"[Сайт](https://glitchdev.ru)"
                                      f"", colour=publicCoreData.embedColors["Neutral"])
    await ctx.respond(embed=embed)


@bot.command(aliases=["код"])
async def code(ctx, length):
    if length:
        await ctx.send(utils.hashgen(int(length)))
    else:
        await ctx.send(utils.hashgen(16))

def inter_formatContent(content : str):
    content = content.replace("@everyone", "@еvеryonе")
    content = content.replace("@here", "@hеrе")
    return content
def inter_formatName(message):
    type = ""
    if message.webhook_id:
        type = "⚓"
    elif message.author.bot:
        type="🤖"
    else:
        type = "😎"
    return ">» " + utils.formatStringLength(message.author.name, 32) + " | " + utils.formatStringLength(
        message.guild.name, 20) + " | " + type
@bot.event
async def on_message(message):
    await bot.process_commands(message)

    # ИНТЕРСЕРВЕР!!!

    async def interchat(mode, message, hname, havatar, data_pair):  # h - webHook

        if mode in publicCoreData.interchats:
            leng = len(publicCoreData.interchats[mode])
            i = 0
            for array in publicCoreData.interchats[mode]:
                i += 1
                server_id = array[0]
                channel_id = array[1]

                send = False
                found = True
                # Поиск сервера по ID
                server = bot.get_guild(server_id)
                if server is None:
                    found = False

                # Поиск канала по ID
                channel = server.get_channel(channel_id)
                if channel is None:
                    found = False

                isBotHook = False
                try:
                    hooks = await channel.webhooks()
                    for hook in hooks:
                        isBotHook = hook.user.id in publicCoreData.botIDs
                        break
                except Forbidden:
                    isBotHook = True

                isInterchatter = str(message.author.name).startswith(">» ")#message.author.id == bot.user.id or isBotHook

                if channel_id != message.channel.id and server_id != message.guild.id and not isInterchatter:
                    # print("Iteration guild: ", server_id, " Iteration channel: ", channel_id, " Channel: ",
                    #       message.channel.id, " Guild: ", message.guild.id)

                    if found and not send:

                        # Отправка сообщения в найденный канал
                        try:
                            hooks = await channel.webhooks()
                            async def send(hook):
                                if message.reference:

                                    embed = discord.Embed(title="⤴️ Reply",description=f"{message.reference.resolved.content}",colour=publicCoreData.embedColors["Neutral"]
                                                          )
                                    embed.set_author(name=message.reference.resolved.author.name, icon_url=message.reference.resolved.author.avatar.url if message.reference.resolved.author.avatar else message.reference.resolved.author.default_avatar.url)
                                    try:
                                        if len(data_pair)>=3:
                                            await hook.send(content=message.content, username=hname, avatar_url=havatar,
                                                            embed=embed,thread=discord.Object(data_pair[2]), files=[await i.to_file() for i in message.attachments]
                                                            )
                                        else:
                                            await hook.send(content=message.content, username=hname, avatar_url=havatar,embed=embed, files=[await i.to_file() for i in message.attachments]
                                                    )
                                    except:
                                        print("No hook?")
                                else:

                                    try:
                                        if len(data_pair) >= 3:
                                            print("3!!!")
                                            #TODO: ветки
                                            await hook.send(content=message.content, username=hname, avatar_url=havatar,
                                                    allowed_mentions=discord.AllowedMentions.none()
                                                    , files=[await i.to_file() for i in message.attachments],thread=discord.Object(data_pair[2]))
                                        else:
                                            await hook.send(content=message.content, username=hname, avatar_url=havatar,
                                                            allowed_mentions=discord.AllowedMentions.none()
                                                            , files=[await i.to_file() for i in message.attachments])
                                    except:
                                        print("No hook?")

                                send = True
                            for hook in hooks:
                                if hook.user.id == bot.user.id:
                                    await send(hook)
                                    break
                            if not send:
                                print("No hook.")
                                _hook = await channel.create_webhook(name="RTB hook")
                                await send(_hook)

                        except Forbidden:
                            ...

                        # await channel.send(message.content)
                        send = True
                if i >= leng:
                    # print("ITERATION COMPLETE. BREAKING")
                    try:
                        # await message.add_reaction("🚀")
                        ...
                    except:
                        ...
                    break

    try:
        target = [message.guild.id, message.channel.id]
    except:
        target = [0, 0]
    name = inter_formatName(message)
    avatar = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url
    if not str(message.author.name).startswith(">» "):
        for hub in publicCoreData.interhubs:
            if hub in publicCoreData.interchats:
                for pair in publicCoreData.interchats[hub]:
                    if target[0] in pair and target[1] in pair:
                        # найдено
                        await interchat(hub, message, name, avatar, target)
                        # print("FOUND pair normal")
                        break
                        # print("BROKEN")
        

    # ИНФЕКЦИОННАЯ РОЛЬ И КАКАЯ-ТО ДИЧЬ!!!

    # if message.mention_roles:  # Проверяем, были ли упомянуты роли в сообщении
    #         mentioned_roles = message.role_mentions  # Получаем список упомянутых ролей
    #         for role in mentioned_roles:
    #             if role.id in publicCoreData.infectionRolesID:  # Замени 'YOUR_ROLE_ID' на фактический ID роли
    #                 await message.author.add_roles(role)  # Даем автору сообщения эту роль
    for i in publicCoreData.infectionRolesID:
        # if str(i) in message.content:
        try:
            role = message.guild.get_role(i)
            for j in message.role_mentions:
                # print(str(j.id) + "   " + str(i))
                if j.id == i:
                    await message.author.add_roles(role)
        except:
            ...

    try:
        await message.publish()
    except:
        ...
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


async def interdeletion(message):
    async def interchat_delete(name, message, mode,data_pair):
        # print("CALLED DELETE FUNC")
        leng = len(publicCoreData.interchats[mode])
        i = 0
        for array in publicCoreData.interchats[mode]:
            i += 1
            server_id = array[0]
            channel_id = array[1]

            send = False
            found = True
            # Поиск сервера по ID
            server = bot.get_guild(server_id)
            if server is None:
                found = False

            # Поиск канала по ID
            channel = server.get_channel(channel_id)
            if len(data_pair)==3:

                channel=channel.get_thread(data_pair[2])
            if channel is None:
                found = False
            if found:
                # print("FOUND")
                msgs = list()
                async for x in channel.history(limit=32):
                    # print("FETCHING... ", (x.content == message.content and x.author.name == name), " ", datetime.datetime.now(x.created_at.tzinfo) - x.created_at <= datetime.timedelta(
                    #             days=14))
                    # print(x.content, "           ", message.content, "                             ", x.author.name, "      ", name)
                    if ((x.content == message.content and x.author.name == name)
                            # and "⭐" not in [i.emoji for i in x.reactions]
                            and datetime.datetime.now(x.created_at.tzinfo) - x.created_at <= datetime.timedelta(
                                days=14) and not x.pinned):
                        msgs.append(x)
                        # print("APPENDED")
                        break

                for i in range(0, len(msgs), 100):
                    await channel.delete_messages(msgs[i:i + 100], reason="Удаление межсерверного сообщения")
                    # print("DELETED")

        ...

    target = [message.guild.id, message.channel.id]
    name = inter_formatName(message)
    # print("DELETION")
    if not str(message.author.name).startswith(">» "):
        # print("SOURCE FOUND")
        for hub in publicCoreData.interhubs:
            if hub in publicCoreData.interchats:
                for pair in publicCoreData.interchats["normal"]:
                    if target[0] in pair and target[1] in pair:
                        # найдено
                        await interchat_delete(name, message, "normal",target)
                        # print("FOUND pair normal")
                        break
                        # print("BROKEN")
        
@bot.event
async def on_message_delete(message):
    await interdeletion(message)
@bot.event
async def on_bulk_message_delete(messages):
    for m in messages:
        await interdeletion(m)


# if message.content.lower() in commands:
#        await commands[message.content.lower()](message)
@bot.slash_command(name="отправить-жалобу-на-пользователя", description="Отправить жалобу на пользователя")
async def report(ctx):
    await ctx.respond("Жалобы не принимаются, эта фича ещё в разработке ;(")


@bot.command(aliases=["код-от-ядерки"])
async def getNukeCode(ctx):
    await ctx.send(f"Одноразовый код от ядерки: ``nuke_{utils.hashgen(16)}::ot#FF#j#EX``")


# TODO: обработчик захода на сервер

# @bot.event
# async def on_member_join(member):
#     guild = member.guild
#     community_updates_channel_id = guild.system_channel.id
#     community_updates_channel = guild.get_channel(community_updates_channel_id)
#     cursor.execute("SELECT reports FROM users WHERE id = ?", (member.id, ))
#     dt = cursor.fetchone()
#     if dt is not None and dt != "":
#         data = utils.load_report_from_json(dt[0])
#         if len(data)>0:
#             await community_updates_channel.send(f"На пользователя {member.name} аж {len(data)} жалоб!")


async def statusLoop():
    global loopCounter
    await asyncio.sleep(120)
    if loopCounter == 0:
        total_members = sum(len(guild.members) for guild in bot.guilds)
        await bot.change_presence(activity=discord.Game(name=f"{total_members} серверов"))
        loopCounter += 1
    elif loopCounter == 1:

        await bot.change_presence(activity=discord.Game(f"Discord-издание бота"))
        loopCounter += 1
    elif loopCounter == 2:

        await bot.change_presence(activity=discord.Game(name=f"PyCharm уже {int(time.time() - runtime)} секунд"))
        loopCounter += 1
    elif loopCounter == 3:

        await bot.change_presence(activity=discord.Game(f"DoorkaEternal"))
        loopCounter = 0


# voice:.idea/1696585352512.wav
# voice:.idea/1696530559952.wav
# bot.add_cog(Weather(bot))
bot.add_cog(game.Game(bot))
# for f in os.listdir("./cogs"):
#     if f.endswith(".py"):
#         bot.load_extension("cogs." + f[:-3])
bot.add_cog(tests.Tests(bot))
bot.add_cog(rp.RP(bot))
bot.add_cog(economy.Economy(bot))
bot.add_cog(utilities.BotCog(bot))
bot.add_cog(Apocalypse.Apocalypse(bot))
bot.add_cog(ServerCore.ServerCore(bot))
bot.add_cog(_AI_Stuff._AI_Stuff(bot))
bot.add_cog(fun.fun(bot))
# bot.add_cog(voice.voice(bot))
# bot.add_cog(paginator.PageTest(bot))
# asyncio.run(loop())
bot.add_cog(HetTol.PingCog(bot))

# loop_thread = Thread(target=loopRunner())
# loop_thread.start()

# client = discord.Client()

# client.loop.create_task(loop())
bot.run(token)
# asyncio.run(statusLoop())
