import dis
import json
import random
import time
import uuid

import aiohttp
# import numpy as np
# import matplotlib.pyplot as plt
# import perlin_noise
from random import *

try:
    import discord
    from discord import Option, Webhook, Forbidden
    from discord.ext import commands, tasks
except:
    import pycord as discord
    from pycord import Option, Webhook, Forbidden
    from discord.ext import commands, tasks

import Apocalypse
import Data
import d
from Data import db
import re

import utils


class Utilities(commands.Cog):
    permissions = Data.permissions_user

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.index = 1
        self.loop.start()

    def cog_unload(self):
        self.loop.cancel()

    @tasks.loop(seconds=5.0)
    async def loop(self):
        # # TODO: сохранение даты и списка в джсон
        # list = Apocalypse.genApocalypseItems()
        #
        # # def saveList(string):
        # #     with open('list.txt', 'w') as file:
        # #         file.write(string)
        # #
        # # saveList(list[0])
        # # apocalypse = Apocalypse.Apocalypse(commands.Bot)
        # # list = Apocalypse.genApocalypseItems()
        #
        # urls = db.servers.find({},
        #                        {"apocalypseChannelHook": 1, "apocalypseLastSendDay": 1, "serverid": 1,
        #                         "isAPchannelThread": 1,
        #                         "apocalypseChannel": 1})
        #
        # for hook_url in urls:
        #     url = hook_url["apocalypseChannelHook"]
        #     date = hook_url["apocalypseLastSendDay"]
        #     if url is not None and date is not None and hook_url["serverid"] is not None and hook_url[
        #         "isAPchannelThread"] is not None and hook_url["apocalypseChannel"] is not None:
        #         if date < utils.get_current_day():
        #             try:
        #                 if url is not None:
        #                     db.servers.update_one({"serverid": hook_url["serverid"]},
        #                                           {"$set": {"apocalypseLastSendDay": utils.get_current_day()}})
        #                     async with aiohttp.ClientSession() as session:
        #                         webhook = Webhook.from_url(str(url), session=session)
        #
        #                         if hook_url["isThread"]:
        #                             await webhook.send(list[0], username=Data.hook_names["apocalypse"],
        #                                                embed=list[1],
        #                                                thread=discord.Object(hook_url["apocalypseChannel"]))
        #                         else:
        #                             await webhook.send(list[0], username=Data.hook_names["apocalypse"],
        #                                                embed=list[1])
        #                         await webhook.send(list[0], username=Data.hook_names["apocalypse"],
        #                                            embed=list[1])
        #
        #             except:
        #                 ...
        # === НАПОМИНАНИЯ ===
        def find_user_mentions_with_regex(input_str):
            pattern = r'\<\@(\d+)\>'
            matches = re.findall(pattern, input_str)
            for match in matches:
                match = match[2:-1]
            return matches

        for doc in db.reminders.find({"expires": {"$lt": time.time()}}):
            # print(doc)
            channel = self.bot.get_channel(doc['channel'])
            embed_content = doc['content']
            if embed_content is None or embed_content == "":
                embed_content = "Текст напоминания отсутствует..."
            embed_content = utils.formatStringLength(embed_content, 3990)
            embed = discord.Embed(title="Напоминание!!!", description=f"{embed_content}",
                                  colour=Data.getEmbedColor(Data.EmbedColor.Notification))
            mentions = find_user_mentions_with_regex(doc['content'])
            content = f"Время истекло, <@{doc['author']}>"
            author = self.bot.get_user(doc['author'])
            # print(author)
            if author:
                content += f" ({author.name})"
            for mention in mentions:

                content += f", <@{mention}>"
                user = self.bot.get_user(mention)
                if user:
                    content += f" ({user.name})"
            content += "!"
            if channel:
                await channel.send(content, embed=embed)
            else:

                if author:
                    await author.send(content, embed=embed)
                for mention in mentions:
                    user = self.bot.get_user(mention)
                    if user:
                        await user.send(content, embed=embed)
            db.reminders.delete_one(doc)

    # TODO: фиксики массового эдита каналов
    # @commands.slash_command(name="массовое-редактирование-каналов",
    #                         description="Редактировать каналы категории. Выберите справку для информации.")
    # @commands.has_permissions(administrator=True)
    # @commands.cooldown(1, 30, commands.BucketType.guild)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(aliases=["напоминание", "напомни", "напомнить"])
    async def addReminder(self, ctx: commands.Context, end_time: str = "1мин", *,
                          content: str = "Текст напоминания не задан"):
        expire = time.time() + utils.parse_duration_string(end_time)
        user = d.getUser(ctx.author.id, ctx.author.name)
        doc = {
            "author": ctx.author.id,
            "content": content,
            "created": time.time(),
            "expires": expire,
            "id": user["total_reminders"] + 1,
            "channel": ctx.channel.id
        }

        user["total_reminders"] += 1
        db.users.update_one({"userid": user['userid']}, {"$set": user})
        db.reminders.insert_one(doc)
        await ctx.reply(
            f"Напоминание создано с ID {user['total_reminders']}! Оповещение {utils.seconds_to_ds_timestamp(expire, 'R')}!\n"
            f"Удалить напоминание можно командой `{Data.preffix}удалить-напоминание`, а посмотреть все - `{Data.preffix}напоминания`")

    @commands.command(aliases=["напоминания"])
    async def reminders(self, ctx: commands.Context):
        reminders = ""
        for doc in db.reminders.find({"author": ctx.author.id}):
            reminders += f"[{doc['id']}]: {utils.formatStringLength(doc['content'], 20)} | Сработает {utils.seconds_to_ds_timestamp(doc['expires'], 'R')}.\n"
        if reminders == "":
            reminders = "Нет напоминаний!"
        reminders = utils.formatStringLength(reminders, 3990)
        embed = discord.Embed(title="Ваши напоминания:", description=f"{reminders}",
                              colour=Data.getEmbedColor(Data.EmbedColor.Neutral))
        await ctx.reply(embed=embed)

    @commands.command(aliases=["удалить-напоминание"])
    async def deleteReminder(self, ctx: commands.Context, id: int = -1):
        if id < 0:
            await ctx.reply("Некорректный ID напоминания!", delete_after=5)
            return
        else:
            try:
                db.reminders.delete_one({"author": ctx.author.id, "id": id})
                await ctx.reply("Напоминание удалено!")
            except:
                await ctx.reply("Напоминание не найдено!")

    async def massChannelsEdit(self, ctx,
                               mode: Option(str, description="Режим работы", required=False,
                                            choices=["Справка", "Имя", "Копировать права", "DEBUG"]) = None,  #
                               category: Option(discord.CategoryChannel, description="Категория для работы команды",
                                                required=True) = None,
                               value: Option(str, description="Значение", required=False) = "None",
                               filters: Option(str, description="Фильтр",
                                               choices=["все", "первый", "последний", "не первый", "не последний",
                                                        "не крайний"], required=False) = "все",
                               channel: Option(discord.TextChannel, description="Второй канал (см. справку.)",
                                               required=False) = "None"
                               ):  # "Выполнить"

        embed = discord.Embed(title="none", description="none")

        if mode == "Справка":
            embed = discord.Embed(title="Режимы массового редактирования каналов",
                                  colour=Data.embedColors["Neutral"],
                                  description=f"Справка по режимам команды"
                                  )
            embed.add_field(inline=False, name="Параметры", value=f"- Режим работы\n"
                                                                  f"Выбирает режим работы. Они указаны далее.\n"
                                                                  f"- Категория\n"
                                                                  f"Категория, каналы которой будут подвергнуты изменению\n"
                                                                  f"- Значение\n"
                                                                  f"Используется некоторыми из режимов. Например, массовое добавление текста в название использует параметры для шаблона переименования.\n"
                                                                  f"- Фильтр\n"
                                                                  f"Фильтр для каналов. Работает по позиции канала. Фильр `все` изменит ВСЕ каналы категории!\n"
                                                                  f"- Второй канал\n"
                                                                  f"Используется некоторыми режимами для копирования данных из него. Если он требуется, но пропущен, будет взят канал, в котором вызвана команда.\n")
            embed.add_field(inline=False, name="Имя", value=f"Меняет имя каналов по паттерну:\n"
                                                            f"``текст<name>текст``\n"
                                                            f"Меняет имя канала. Оригинальное имя находится на месте <name>. перед ним и после него можно добавлять текст. Меняет по шаблону имена ВСЕХ каналов категирии, попадающих под фильтр.\n")

            # embed.add_field(name="Выполнить", value=f"Выполняет специальный код для редактирования каналов. Вот как это работает:"
            #                                         f"`IF ENDIF` - условие. Между ними можно вписать код"
            #                                         f"`channelPosition == first|last|middle DO RENAME|aaa<name>bbb|` - условие и действие для логики: если канал **первый|последний|середина** в категории то переименовать его по паттерну:"
            #                                         f" aaa это первая часть текста, <name> это место где стоит название канала до редактирвования, а bbb это конец."
            #                                         f" Если ввести **<-<name>---** а канал будет назван до этого **тест**, то на выходе получится <-тест---"
            #                                         f"Если указано first то будет переименован только первый канал категории, last же последний. middle - средний"
            #                                         f"Пример команды - IF channelPosition == first DO RENAME|aaa<name>b| ENDIF"
            #                                         f"")
            await ctx.respond(embed=embed)

            embed.set_footer(
                text="Вам необходимы права Администратора для использования этой команды.\nВ целях безопасности, есть откат в 30 секунд на сервер.")
        elif mode == "Выполнить":
            # await tokenize_text(value)
            ...

        elif mode == "DEBUG":
            if category:
                for channel in category.channels:
                    # await channel.edit(name="Новое название канала")
                    # await channel.set_permissions(ctx.guild.default_role, read_messages=False)
                    await ctx.send(channel.name)
                # await ctx.send("Названия и права каналов в категории были обновлены.")
            else:
                await ctx.send("Категория не найдена.")
        # async def tokenize_text(text):
        #     tokens = re.findall(r'IF channelPosition == (first|last|middle) DO RENAME|(.*?)| ENDIF', text) #(RENAME \w+)
        #
        #     for token in tokens:
        #         condition = token[0]
        #         action = token[1]
        #
        #         if condition == 'first':
        #             # Выполнить код для первого условия
        #
        #             await channel_rename(action, 0)
        #         elif condition == 'middle':
        #             # Выполнить код для второго условия
        #
        #             await channel_rename(action,1)
        #         elif condition == 'last':
        #             # Выполнить код для второго условия
        #
        #             await channel_rename(action, 2)
        #
        # async def channel_rename(action, pos):
        #     text = str.split(action, "<name>")
        #     channels = category.channels
        #     if pos == 0 or pos == 2:
        #         if pos == 0:
        #             chPos = 0
        #         else:
        #             chPos = len(channels)-1
        #         await ctx.send("---" + channels[chPos].name)
        #         channelName = channels[chPos].name
        #         chName = text[0] + channelName
        #         if len(text) > 1:
        #             chName += text[chPos]
        #         await channels[chPos].edit(name=chName)
        #         # await channel.set_permissions(ctx.guild.default_role, read_messages=False)
        #         await ctx.send(channels[chPos].name + "\n===")
        #
        #
        #     for channel in category.channels:
        #
        #         if pos == 1:
        #             await ctx.send("---"+channel.name)
        #             channelName = channel.name
        #             chName= text[0]+channelName
        #             if len(text)>1:
        #                 chName+=text[1]
        #             await channel.edit(name=chName)
        #             # await channel.set_permissions(ctx.guild.default_role, read_messages=False)
        #             await ctx.send(channel.name+"\n===")

        # Выполнить соответствующее действие в зависимости от типа токена RENAME
        # Например, переименовать канал

        # Пример использования
        # user_input = "IF channelPosition == first DO RENAME aaa<TEXT> IF channelPosition == last DO RENAME bbb<TEXT>"
        # tokenize_text(user_input)
        # await ctx.respond(embed=embed)
        # await ctx.respond("Учтите, что у Вас должно быть разрешение Администратора для использования этой команды!")

    @commands.slash_command(name="винжер", description="кодировщик-декодировщик в винжере")
    async def vinger(self, ctx, input: Option(str, description="Текст на русском/английском", required=True) = "none",
                     key: Option(str, description="Ключ", required=True) = "а",
                     destination: Option(bool, description="True - шифровка, False - дешифровка",
                                         required=False) = True):

        def setupAlphabet():

            return r'абвгдеёжзийклмнопрстуфхцчшщъыьэюя1234567890-=_+/\!.,:;"[]{}<>abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ`~ ™°*±@#№$%&?()¤←→↖↗↑↔↙↘↓↕⁰³⁶⁹¹⁴⁷²⁵⁸ⁿ√∑ΔΩΨω∅∞≈†‡µ♪'

        def vigenere_cipher(alphabet, key, text, encode=True):
            result = ""
            key_index = 0

            for char in text:
                if char in alphabet:
                    char_index = alphabet.index(char)
                    key_char = key[key_index % len(key)]
                    key_char_index = alphabet.index(key_char)

                    if encode:
                        encrypted_char_index = (char_index + key_char_index) % len(alphabet)
                    else:
                        encrypted_char_index = (char_index - key_char_index) % len(alphabet)

                    encrypted_char = alphabet[encrypted_char_index]
                    result += encrypted_char
                    key_index += 1
                else:
                    result += char

            return result

        embed = discord.Embed(title="Винжер", description="Результат:", colour=0xffffff)
        embed.add_field(name="Исходный текст", value=f"{input}", inline=False)
        embed.add_field(name="Результат", value=f"{vigenere_cipher(setupAlphabet(), key, input, destination)}")
        await ctx.respond(embed=embed, ephemeral=True)

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):

        if message.author.bot or isinstance(message.author, discord.Webhook):
            return

        mentioned_users = message.mentions
        replied_user: discord.Member = message.reference.resolved.author if message.reference and message.reference.resolved else None

        if mentioned_users or replied_user:
            if replied_user and replied_user.bot:
                return
            pinged = message.author
            # Получаем статус упомянутого пользователя
            status = None
            if mentioned_users:
                user = mentioned_users[0]
                status = user.status
                pinged = user
            elif replied_user:
                status = replied_user.status
                pinged = replied_user
            # print(status)
            statuses = {
                discord.Status.offline: "autoresponder-offline",
                discord.Status.dnd: "autoresponder-disturb",
                discord.Status.idle: "autoresponder-inactive"
            }
            # if status == :
            #     # Код для пользователя в сети
            #     await message.channel.send(f"{pinged.mention} Я вижу, что вы в сети! 👀")
            # elif status == discord.Status.offline:
            #     # Код для оффлайн пользователя
            #     await message.channel.send(f"{pinged.mention} Вы не в сети. 😴")
            # elif status == discord.Status.idle:
            #     # Код для неактивного пользователя
            #     await message.channel.send(f"{pinged.mention} Вы сейчас неактивны. 🌀")
            # elif status == discord.Status.dnd:
            #     # Код для пользователя со статусом "не беспокоить"
            #     await message.channel.send(f"{pinged.mention} Вы на не беспокоить. 🤫")
            # elif status == discord.Status.streaming:
            #     ...
            doc = db.users.find_one({"userid": pinged.id})

            # print(doc)
            if doc:
                # hook : discord.Webhook = await utils.initWebhook(message.channel, self.bot.user.id)
                # hooks = await message.channel.webhooks()
                # hook = None
                # for h in hooks:
                #     if h.user.id in Data.botIDs:
                #         hook = h
                #         break
                # if not hook:
                #     hook = await message.channel.create_webhook(name="RTB hook", avatar=Data.webhook_avatar_url)
                # if hook:
                try:
                    # print(statuses[status])
                    # print(status)
                    a_message = doc[statuses[status]]
                    # print(a_message)
                    # print(doc["autoresponder"])

                    if a_message and doc["autoresponder"]:
                        # print('---')
                        # avatar = pinged.avatar.url if pinged.avatar else pinged.default_avatar.url
                        await message.channel.send(f"Автоответчик @{pinged.name}: {a_message}", delete_after=10,
                                                   allowed_mentions=discord.AllowedMentions.none()

                                                   )

                except:
                    ...

    @commands.command(aliases=["токен", "token", "токендоступа", "токен-доступа", "access-token"])
    async def update_user_token(self, ctx: commands.Context):
        doc = d.getUser(ctx.author.id, ctx.author.name)
        token = str(uuid.uuid4())
        print(token)
        token = token[:8]
        print(token)
        expire_at = int(time.time()) + 14400
        db.users.update_one({"userid": ctx.author.id},
                            {"$set": {"access_token": token, "access_token_expires": expire_at}})
        await ctx.author.send(f"# Токен доступа обновлён!\n"
                              f"Никому не показывайте его!\n"
                              f"Токен: {token}\n"
                              f"Ваш ID: {ctx.author.id}\n"
                              f"Токен устареет <t:{expire_at}:R>\n"
                              f"Не отправляйте токен никому! Он предназначен ТОЛЬКО для использования [на нашем сайте](https://glitchdev.ru).\n"
                              f"Токен одноразовый.")
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Utilities(bot))
