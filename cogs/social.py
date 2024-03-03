import datetime
import time

import discord
from discord.ext import commands, tasks
from discord import Option

import utils
from Data import db, getEmbedColor, EmbedColor, preffix
import d


class social(commands.Cog):
    ''' social | BOT COG'''
    name = "social"
    author = "Minemaster"

    def __init__(self, bot:discord.Bot):
        self.bot = bot
        self.background.start()


    social = discord.SlashCommandGroup(
        "социал",
        "",

    )
    coRPlayerFindRequest_ExpirationTime=600000 #in ms
    def getUTC(self)->int:
        #TODO: часовой пояс
        current_time_utc = datetime.datetime.utcnow()

        timestamp_utc_ms = int(current_time_utc.timestamp() * 1000)
        # print(timestamp_utc_ms)
        return timestamp_utc_ms

    def UTCtoTimestamp(self, utcValueInMS):
        return int(utcValueInMS/1000)
    @tasks.loop(seconds=10)  # Указываете интервал в секундах
    async def background(self):
        # print("BG")
        for doc in db.coRPsFindRequests.find({"timestamp": {"$lt": self.getUTC()-self.coRPlayerFindRequest_ExpirationTime}}):
            user = self.bot.get_user(doc['uid'])
            # print(doc)
            if user:
                await user.send(f"Ваш запрос на поиск сорола на сервере **{doc['gname']}** истёк!")
            db.coRPsFindRequests.delete_one(doc)
        # print("BG")

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(aliases=["начать-поиск-сорола"])
    async def startFindCoRPlayer(self, ctx: commands.Context):
        doc = db.coRPsFindRequests.find_one({"gid": ctx.author.guild.id, "uid": ctx.author.id})

        if not doc:
            utc = self.getUTC()
            db.coRPsFindRequests.insert_one(
                {"gid": ctx.author.guild.id, "uid": ctx.author.id, "gname": ctx.guild.name, "uname": ctx.author.name,
                 "timestamp": utc})
            await ctx.reply(f"Запрос на поиск сорола отправлен для этого сервера! Он истечёт <t:{self.UTCtoTimestamp(utc+self.coRPlayerFindRequest_ExpirationTime)}:R>."
                            f"\nОтменить - `{preffix}начать-поиск-сорола` | Поиск других соролов - `{preffix}поиск-сорола`",delete_after=10)
        else:
            await ctx.reply(f"У вас уже есть запрос на поиск сорола, который истечет <t:{self.UTCtoTimestamp(doc['timestamp']+self.coRPlayerFindRequest_ExpirationTime)}:R>.",delete_after=10)

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(aliases=["отменить-поиск-сорола"])
    async def cancelFindCoRPlayer(self, ctx: commands.Context):
        doc = db.coRPsFindRequests.find_one({"gid": ctx.author.guild.id, "uid": ctx.author.id})
        if doc:
            await ctx.reply("Поиск сорола отменён на этом сервере.",delete_after=10)
            db.coRPsFindRequests.delete_one({"gid": ctx.author.guild.id, "uid": ctx.author.id})
        else:
            await ctx.reply(f"Вы не начали поиск сорола. Сделать это можно командой `{preffix}начать-поиск-сорола`", delete_after=10)
    @commands.command(aliases=["поиск-сорола"])
    async def findCoRPlayer(self, ctx: commands.Context):
        embedContent=""
        for doc in db.coRPsFindRequests.find({"gid": ctx.guild.id}):
            embedContent+=f"<@{doc['uid']}> ищет сорола! Найти его персонажей - </поиск-персонажей-пользователя:1203654817692778538>. Поиск заканчивается <t:{self.UTCtoTimestamp(doc['timestamp']+self.coRPlayerFindRequest_ExpirationTime)}:R>\n"
        embedContent=utils.formatStringLength(embedContent, 3990)
        if embedContent=="":
            embedContent="Никто не ищет сорола"
        embed = discord.Embed(title="Кто сейчас ищет сорола",description=f"{embedContent}",colour=getEmbedColor(EmbedColor.Neutral))

        await ctx.reply(embed=embed)

    # @commands.Cog.listener("on_presence_update")
    # async def on_presence_update(self, before:discord.Member, after:discord.Member):
    #     ...
        # if before.activity != after.activity:
        #     print(after.name)
        #     before_activity_name=""
        #     after_activity_name=""
        #     if before.activity:
        #         before_activity_name=before.activity.name
        #     if after.activity:
        #         after_activity_name=after.activity.name
        #     print(before_activity_name, "   ==>   ", after_activity_name)

def setup(bot):
    bot.add_cog(social(bot))
