import asyncio
import datetime
import platform
# TODO: add transformers to requirements
import json
import time

import aiohttp
# -*- coding: utf-8 -*-
# try:
import discord
# from discord_components import DiscordComponents, Button
from discord import Option, Webhook, Forbidden
# except:
#     import pycord as discord
#     from pycord import Option, Webhook, Forbidden
# import Apocalypse
# import HetTol
import d
from tests_and_utils import dbClone
import Data
import utils


from private import coreData
from Data import db

import os

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
intents.members = True
intents.presences = True
# intents.guilds = True
# intents.channels = True
# intents.threads = True

# Задаём префикс и интенты
runtime = time.time()
loopCounter = 0
bot = commands.Bot(command_prefix=Data.preffix, intents=intents)
bot.max_messages = 20000


@bot.event
async def on_ready():
    total_members = sum(len(guild.members) for guild in bot.guilds)
    guildnames = ""
    totalguilds = len(bot.guilds)
    if totalguilds <= 100:
        guildnames = "╔" + "═" * 100 + "╦" + "═" * 20 + "╦" + "═" * 32 + "╗" + "\n"
        guildnames += "║" + "GUILD NAME".ljust(100) + "║" + "GUILD ID".ljust(20) + "║" + "GUILD OWNER NAME".ljust(
            32) + "║" + "\n"
        guildnames += "║" + "═" * 100 + "╬" + "═" * 20 + "╬" + "═" * 32 + "║" + "\n"
        for guild in bot.guilds:
            # print(guild.name)
            # try:
            guildnames += "║" + "═" * 100 + "╬" + "═" * 20 + "╬" + "═" * 32 + "║" + "\n"
            guildnames += "║" + f"{guild.name: <100}" + "║" + f"{guild.id: <20}" + "║" + f"{(guild.get_member(guild.owner_id).name): <32}" + "║" + "\n"
            # except:
            #     guildnames += "║" + "UNKNOWN".ljust(100) + "║" + "UNKNOWN".ljust(
            #         20) + "║" + "UNKNOWN".ljust(32) + "║" + "\n"
            #     guildnames += "║" + "═" * 100 + "╬" + "═" * 20 + "╬" + "═" * 32 + "║" + "\n"
        guildnames += "╚" + "═" * 100 + "╩" + "═" * 20 + "╩" + "═" * 32 + "╝" + "\n"

    print(
        f"Бот запущен как {bot.user} за {round(time.time() - startTimeCounter, 3)} секунд. Преффикс: {bot.command_prefix}\n"
        f"Коги:{str(bot.cogs.keys())}\n"
        f"{totalguilds} серверов | {total_members} пользователей\n"
        f"{guildnames}")

    await bot.change_presence(activity=discord.Game(f"{totalguilds} серверов"))
    if platform.system() == 'Windows':
        toaster.show_toast(f"Random Things Bot",
                           f"RTB:discord_bot запущен за {round(time.time() - startTimeCounter, 3)} секунд. Преффикс: {bot.command_prefix}\n",

                           threaded=True)


async def noPermission(ctx, permissions):
    """Вызов сообщения об отсутствии разрешений. Нужен контекст /-команды!"""
    result = db.users.find_one({"userid": ctx.author.id}, {"permissions": 1})
    perms = result["permissions"] if result else None
    permissions = permissions.replace("|", "или").replace("&", "и")
    permissions = f"`{permissions}`"
    embed = discord.Embed(title="У Вас нет прав!", description="Нет разрешения!",
                          color=Data.embedColors["Error"])
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
                              color=Data.embedColors["Error"])
        embed.add_field(name="Нет разрешения!", value=f"Вам необходимо(ы) разрешение(я): {none}")
        await ctx.send(embed=embed, ephemeral=False)
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Команда перезаряжается. Повторите через **{round(error.retry_after)}** секунд!")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"Недостаточно прав!")
    elif isinstance(error, IndexError):
        print(db)
        print(Data.client)
        await ctx.send(error)
    if not Data.ISHOST:
        if not sendAllExceptionsToChat:
            await ctx.send("Произошла ошибка! Обратитесь к разработчику.")
            print(error)
        else:
            await ctx.send(f'Произошла ошибка при выполнении команды: {error}')
            print(error)


@bot.slash_command(name="настройки-бота", description="Задать определённую настройку бота",
                   guilds=Data.BOT_INTERNAL_COMMANDS_GUILDS)
async def set_settings(ctx, field: Option(str, description="Поле", required=True,
                                          choices=["SQL+commit", "eval", "Таблицы", "Баланс"]) = 0,
                       value: Option(str, description="Значение", required=True) = 0,
                       ephemeral: Option(bool, description="Видно ли только вам? По умолчанию - всем.", required=False) = False,
                       member: Option(discord.Member, description="Пользователь, на которого влияет команда",
                                      required=False) = None):
    """Настройки и приколы бота для админов БОТА."""
    hasPermission = False
    hasPermission = await Data.parsePermissionFromUser(ctx.author.id, "root")
    if member is None:
        member = ctx.author
    if hasPermission == True:
        embed = discord.Embed(title="В разработке...", description="Вам необходимо разрешение root для использования.",
                              color=Data.embedColors["Warp"])

        if field == "eval":
            # eval(value)
            embed = discord.Embed(title="Код не выполнен!", description=f"Код: {value}",
                                  color=Data.embedColors["Success"])


        await ctx.respond(embed=embed, ephemeral=ephemeral)
    else:
        await noPermission(ctx, "root")


@bot.command(aliases=['me', 'я', '>'])
async def sendMsg(ctx, *, args):
    """Отправка сообщения от лица бота."""
    if await Data.parsePermissionFromUser(ctx.author.id, "say_as_bot"):
        if ctx.message.reference:
            await ctx.send(args, reference=ctx.message.reference)
        else:
            await ctx.send(args)
    await ctx.message.delete()


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


@bot.slash_command(name="разрешения", description="Редактирование разрешений пользователя", guilds=Data.BOT_INTERNAL_COMMANDS_GUILDS)
async def editMemberPermissions(ctx, permission: Option(str, description="Разрешение. ? для списка",
                                                        choises=Data.permissions_user,
                                                        required=True) = "none",
                                member: Option(discord.Member, description="Пользователь", required=True) = None,
                                value: Option(bool, description="Значение", required=True) = True,
                                ephemeral: Option(bool, description="Видно ли только вам?",
                                                  required=False) = False):
    if member is None:
        member = ctx.author
    perm_root = await Data.parsePermissionFromUser(ctx.author.id, "root")
    perm_edit = await Data.parsePermissionFromUser(ctx.author.id, "edit_permissions")
    if permission != "?":
        if perm_root or perm_edit:
            if permission != "root":
                await Data.setPermissionForUser(member.id, permission, value)
                embed = discord.Embed(title=f"Разрешение {permission} изменено успешно!",
                                      description=f"Разрешение изменено у участника <@{member.id}> на **{value}**",
                                      colour=Data.embedColors["Success"])
                await ctx.respond(embed=embed, ephemeral=ephemeral)
            else:
                if perm_root:
                    await Data.setPermissionForUser(member.id, permission, value)
                    embed = discord.Embed(title=f"Разрешение {permission} изменено успешно!",
                                          description=f"Разрешение изменено у участника <@{member.id}> на **{value}**",
                                          colour=Data.embedColors["Success"])
                    await ctx.respond(embed=embed, ephemeral=ephemeral)
                else:
                    await noPermission(ctx, "root")
        else:
            await noPermission(ctx, "root | edit_permissions")
    else:
        await ctx.respond(json.dumps(Data.permissions_user))


@bot.slash_command(name="добавить-опыт", description="Даёт опыт пользователю", guilds=Data.BOT_INTERNAL_COMMANDS_GUILDS)
async def addXP(ctx, user: Option(discord.Member, description="Пользователь", required=True) = 0,
                value: Option(float, description="Количество. Отрицательное для уменьшения", required=True) = 0):
    if await Data.parsePermissionFromUser(ctx.author.id, "root"):
        doc = db.users.find_one({"userid": user.id})
        if doc:
            # doc = db.users.find_one({"id":user.id})
            doc = d.schema(doc, d.Schemes.user)
            doc["xp"] += value
            db.users.update_one({"userid": user.id}, {"$set": doc})
            print("Found")
        else:
            Data.writeUserToDB(user.id, user.name)
            doc = db.users.find_one({"userid": user.id})
            doc = d.schema(doc, d.Schemes.user)
            doc["xp"] += value
            db.users.update_one({"userid": user.id}, {"$set": doc})
            print("None")
        embed = discord.Embed(title="Выдан опыт!", description=f"Выдано {value} опыта пользователю <@{user.id}>.",
                              colour=Data.embedColors["Success"])
        await ctx.respond(embed=embed)
    else:
        await ctx.respond("Недостаточно прав!", ephemeral=True)


@bot.slash_command(name="инфо", description="Информация о боте")
async def info(ctx):
    embed = discord.Embed(title="Информация о боте",
                          description=f"[Пригласить бота на сервер](https://discord.com/api/oauth2/authorize?client_id=1126887522690142359&permissions=8&scope=bot)"
                                      f"\n[Пригласить бота на сервер (BETA-тесты)](https://discord.com/api/oauth2/authorize?client_id=1169691387562835968&permissions=8&scope=bot)"
                                      f"\n[Исходники](https://github.com/Minemaster656/RandomThingsBot)\n"
                                      f"[Сайт](https://glitchdev.ru)"
                                      f"", colour=Data.embedColors["Neutral"])
    await ctx.respond(embed=embed)


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    try:
        await message.publish()
    except:
        ...






@bot.slash_command(name="отправить-жалобу-на-пользователя", description="Отправить жалобу на пользователя")
async def report(ctx):
    await ctx.respond("Жалобы не принимаются, эта фича ещё в разработке ;(")


# @bot.command(aliases=["код-от-ядерки"])
# async def getNukeCode(ctx):
#     await ctx.send(f"Одноразовый код от ядерки: ``nuke_{utils.hashgen(16)}::ot#FF#j#EX``")


# TODO: обработчик захода на сервер




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


# # voice:.idea/1696585352512.wav
# # voice:.idea/1696530559952.wav

def main():
    for f in os.listdir("./cogs"):
        if f.endswith("py"):
            bot.load_extension("cogs." + f[:-3])
    bot.run(token)


if __name__ == "__main__":
    main()
