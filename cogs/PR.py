import datetime
from datetime import datetime, timedelta
import random
# import numpy as np
# import matplotlib.pyplot as plt
import discord
import pytz
from discord.ext import commands
# import perlin_noise
from discord import Option
from random import *

import Data
import d
import utils
from Data import cursor, db
from Data import conn

class Pr(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # cursor.execute("CREATE TABLE IF NOT EXISTS partners (serverid INTEGER, servername TEXT, ownerid INTEGER, link TEXT,text       TEXT,color      TEXT)")
        # conn.commit()

    def check_account_age(self, user: discord.User, days: int) -> bool:
        account_creation_date = user.created_at.replace(tzinfo=pytz.UTC)
        now = datetime.now(pytz.UTC)
        age = now - account_creation_date
        return age >= timedelta(days=days)

    def check_server_age(self, guild: discord.Guild, days: int) -> bool:
        server_creation_date = guild.created_at.replace(tzinfo=pytz.UTC)
        now = datetime.now(pytz.UTC)
        age = now - server_creation_date
        return age >= timedelta(days=days)

    # Функция для проверки количества реальных участников (не включая ботов)
    def check_real_members(self, guild: discord.Guild, threshold: int) -> bool:
        real_members = sum(not member.bot for member in guild.members)

        return real_members >= threshold

    def checkChannel(self, channel : discord.TextChannel, ctx):
        perms = channel.overwrites_for(ctx.guild.default_role)
        can_view_channel = perms.view_channel
        can_read_history = perms.read_message_history
        return (can_view_channel, can_read_history)

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name="партнёрка-настроить",description="Настройка рекламы вашего сервера")
    async def setpartnerinfo(self, ctx, text : Option(str, description="Текст партнёрки", required=True)=" ",
                             color: Option(str, description="Цвет полоски эмбеда (HEX или RGB (0-1, 0-255) с цветами через пробел)", required=False)=None):


        bumpcolor = utils.parseColorTo0xHEX(color)
        # Получаем первый канал на сервере
        channel = ctx.guild.text_channels[0]

        # Проверяем, есть ли уже ссылка-приглашение в канале
        existing_invites = await channel.invites()
        for invite in existing_invites:
            if invite.inviter.id in Data.botIDs and invite.max_age == 0:
                invite_url = invite.url
                break
        else:
            # Если ссылка-приглашение не найдена, создаем новую бессрочную
            new_invite = await channel.create_invite(max_age=0)
            invite_url = new_invite.url

        doc = db.servers.find_one({"serverid":ctx.guild.id})

        new = False
        if doc:
            ...
        else:
            doc = {}
            new = True
            doc["serverid"] = ctx.guild.id


        doc["bumpcolor"] = bumpcolor
        doc["name"] = ctx.guild.name
        doc["icon"] = ctx.guild.icon.url if ctx.guild.icon else Data.discord_logo
        doc["bumptext"] = text + f"\n\n🔗[Ссылка на сервер]({invite_url})🔗\nГлава - **{ctx.guild.owner.name}**"
        doc["invitelink"] = invite_url
        doc["ownerid"] = ctx.guild.owner.id
        doc["ownername"] = ctx.guild.owner.name
        doc["partnershipState"] = 1

        doc = d.schema(doc, d.Schemes.server)
        embed = discord.Embed(title=ctx.guild.name,description=doc["bumptext"],colour=bumpcolor)
        embed.set_thumbnail(url=doc["icon"])
        guildAgeCheck = self.check_server_age(ctx.guild, 7)
        guildMembersCheck = True#self.check_real_members(ctx.guild, 20)
        userAgeCheck = self.check_account_age(ctx.author, 14)
        ownerAgeCheck = self.check_account_age(ctx.guild.owner, 14)
        if guildMembersCheck and guildAgeCheck and userAgeCheck and ownerAgeCheck:
            #TODO: сохранение в БД, проверка канала.
            await ctx.respond("Сообщение для партнёрки обновлено! (В РАЗРАБОТКЕ)\n"
                              "Напоминаем, что мы против использования матов, оскорблений, скама и прочего нежелательного контента в партнёрках. [Подробнее](https://glitchdev.ru/EULA)\n"
                              "# Как использовать партнёрки:\n"
                              "1. Используйте команду /рекламный-канал для настройки канала для рекламы (туда будут приходить другие партнёрки). Суть партнёрки в том, что сервера обмениваются объявлениями, так что это действие обязательно.\n"
                              "2. Используйте команду /бамп для отправки своего объявления. Лимит - 1 раз в 4 часа.",embed=embed)
            if new:
                db.servers.insert_one(doc)
            else:
                db.servers.update_one({"serverid":ctx.guild.id}, {"$set" : doc})
        else:
            req=""
            req+=("✅" if guildAgeCheck else "❌") + " Серверу должно быть минимум 7 дней.\n"
            req+=("✅" if guildMembersCheck else "❌")+" На сервере должно быть минимум 20 реальных людей.\n"
            req+=("✅" if userAgeCheck else "❌")+" Вашему аккаунту должно быть минимум 2 недели.\n"
            req+=("✅" if ownerAgeCheck else "❌")+" Аккаунту владельца сервера должно быть минимум 2 недели."
            embed = discord.Embed(title="Сервер не подходит требованиям!",description=req,colour=Data.embedColors["Error"])
            await ctx.respond(embed=embed)


    @commands.slash_command(name="бамп",description="Отправляет рекламу вашего сервера")
    async def bump(self, ctx):

        doc = db.servers.find_one({"serverid": ctx.guild.id})
        noDocMessage = not doc
        if not noDocMessage:
            btext = doc["bumptext"]
            if btext == None or btext == "" or btext == " ":
                noDocMessage = True

        if not doc or "pr_channel" not in doc.keys():
            embed = discord.Embed(title="Сервер не найден или не настроен",description="Ваш сервер не найден в базе данных или партнёрка не настроена!\nИспользуйте /партнёрка-настроить",colour=Data.embedColors["Error"])
            await ctx.respond(embed = embed)
            return

        if doc["pr_channel"]:
            channel = ctx.guild.get_channel(doc["pr_channel"])
        else:
            embed = discord.Embed(title="Канал для рекламы не найден!",
                                  description="Используйте /рекламный-канал для настройки!",
                                  colour=Data.embedColors["Error"])
            await ctx.respond(embed=embed)
            return
        if not channel:
            embed = discord.Embed(title="Канал для рекламы не найден!",
                                  description="Используйте /рекламный-канал для настройки!",
                                  colour=Data.embedColors["Error"])
            await ctx.respond(embed=embed)
            return
        channelCheck = self.checkChannel(channel, ctx)
        if channelCheck[0] != False and channelCheck[1] != False:
            query = {"partnershipState": 1, "pr_channel": {"$ne": None}}
            await ctx.respond("Отправка...")
            # Выполнение запроса
            # result = db.servers.find(query)
            embed = discord.Embed(title=ctx.guild.name, description=doc["bumptext"], colour=doc["bumpcolor"])
            embed.set_thumbnail(url=doc["icon"])
            # records = result.count()
            for server in db.servers.find(query):
                # server = records.next()
                found = True
                guild = self.bot.get_guild(server["serverid"])
                if guild is None:
                    found = False
                # Поиск канала по ID
                channel = guild.get_channel(server["pr_channel"])
                if channel is None:
                    found = False
                if found:
                    await channel.send(embed=embed)
                print(server, " ", found)
            await ctx.respond("Объявление отправлено!")
        else:

            embed = discord.Embed(title="Неправильные разрешения!",
                                  description="Канал должен иметь разрешения для everyone:\n✅ Просмотр канала\n✅ Просмотр истории сообщений",
                                  colour=Data.embedColors["Error"])
            await ctx.respond(embed=embed)
            return


    @commands.has_permissions(administrator=True)
    @commands.slash_command(name="рекламный-канал",description="Канал для рекламы партнёрки")
    async def set_adds_channel(self, ctx, channel: Option(discord.TextChannel, description="Канал", required=True)=0):
        channelCheck = self.checkChannel(channel, ctx)
        doc = db.servers.find_one({"serverid":ctx.guild.id})
        new = not doc
        save = False
        if channelCheck[0]!=False and channelCheck[1]!=False:
            embed = discord.Embed(title="Успешно!",description=f"Успешно задан канал {channel.mention}",colour=Data.embedColors["Success"])
            save = True


        else:
            embed = discord.Embed(title="Неправильные разрешения!",description="Канал должен иметь разрешения для everyone:\n✅ Просмотр канала\n✅ Просмотр истории сообщений",colour=Data.embedColors["Error"])

        if not doc:
            doc = {"partnershipState":0, "bumptext":None}
        if doc["partnershipState"] == 0 or not doc["bumptext"]:
            doc = d.schema(doc, d.Schemes.server)
            doc["ownerid"] = ctx.guild.owner.id
            doc["ownername"] = ctx.guild.owner.name
            doc["partnershipState"] = 1
            doc["name"] = ctx.guild.name
            doc["icon"] = ctx.guild.icon.url if ctx.guild.icon else Data.discord_logo
            embed = discord.Embed(title="Не настроено!",description="На Вашем сервере не настроена партнёрка!\nРеклама приходить будет, но Вам нужно использовать /партнёрка-настроить для создания своего поста, а так же /бамп для его публикации!",colour=Data.embedColors["Error"])
        await ctx.respond(embed=embed)
        if save:
            doc["pr_channel"] = channel.id
            if new:
                db.servers.insert_one(doc)
            else:
                db.servers.update_one({"serverid": ctx.guild.id}, {"$set": doc})


    @commands.slash_command(name="партнёрка-предпросмотр",description="Предпросмотр вашего сообщения для партнёрки")
    async def preview(self, ctx):
        await ctx.respond("В разработке!", ephemeral=True)





def setup(bot):
    bot.add_cog(Pr(bot))