import random
# import numpy as np
# import matplotlib.pyplot as plt
import discord
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

        doc = db.servers.find_one({"id":ctx.guild.id})
        if not doc:
            doc = {"serverid": ctx.guild.id,



            "bumpcolor": bumpcolor,
            "name":ctx.guild.name,
            "icon":ctx.guild.icon.url if ctx.guild.icon else Data.discord_logo,

            "bumptext": text+f"\n🔗[Ссылка на сервер]({invite_url})🔗",

            "invitelink": invite_url,

            "ownerid": ctx.guild.owner.id, "ownername":ctx.guild.owner.name

            }
            doc = d.schema(doc, d.Schemes.server)
        embed = discord.Embed(title=ctx.guild.name,description=doc["bumptext"],colour=bumpcolor)
        embed.set_thumbnail(url=doc["icon"])
        #TODO: сохранение в БД, проверка канала.
        await ctx.respond("Сообщение для партнёрки обновлено! (В РАЗРАБОТКЕ)",embed=embed)
    @commands.slash_command(name="бамп",description="Отправляет рекламу вашего сервера")
    async def bump(self, ctx):
        await ctx.respond("В разработке!", ephemeral=True)
    @commands.slash_command(name="рекламный-канал",description="Канал для рекламы партнёрки")
    async def set_adds_channel(self, ctx, channel: Option(discord.TextChannel, description="Канал", required=True)=0):
        await ctx.respond("В разработке!", ephemeral=True)
    @commands.slash_command(name="партнёрка-предпросмотр",description="Предпросмотр вашего сообщения для партнёрки")
    async def preview(self, ctx):
        await ctx.respond("В разработке!", ephemeral=True)





def setup(bot):
    bot.add_cog(Pr(bot))