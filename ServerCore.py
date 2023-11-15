import random
import typing

# import numpy as np
# import matplotlib.pyplot as plt
import discord
import requests
from discord.ext import commands
# import perlin_noise
from discord import Option
from random import *

import publicCoreData
from publicCoreData import conn, cursor, db


class ServerCore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="настройки-каналов", description="description")
    @commands.has_permissions(administrator=True)
    async def settings_channels(self, ctx, field: Option(str, description="Поле",
                                                         choices=["игра Апокалипсис", "Объявления", "реклама"],
                                                         required=True) = "",
                                channel: Option(typing.Union[discord.TextChannel, discord.Thread], description="Канал.",
                                                required=True) = None, clear_field : Option(bool, description="Очистить настройку? Удалит значение вместо установки.", required=False)=False):

        publicCoreData.findServerInDB(ctx)

        if field == "игра Апокалипсис":
            if clear_field:
                none = "none"
                db.servers.update_one({"serverid": ctx.guild.id}, {
                    "$set": {"apocalypseChannel": 0, "apocalypseChannelHook": none, "isAPchannelThread": False}})
                await ctx.respond("Канал отчищен!")
            else:
                isThread = True if isinstance(channel, discord.Thread) else False
                parent = channel
                if isinstance(channel, discord.Thread):
                    parent = channel.parent
                avatar_url = publicCoreData.webhook_avatar_url
                webhook_name = str("RTBot's webhook")
                channel = ctx.channel
                webhooks = await parent.webhooks()
                webhook = discord.utils.get(webhooks, name=webhook_name)

                if webhook is None:
                    avatar_bytes = requests.get(avatar_url).content
                    webhook = await parent.create_webhook(name=str(webhook_name), avatar=avatar_bytes)
                db.servers.update_one({"serverid": ctx.guild.id}, {
                    "$set": {"apocalypseChannel": channel.id, "apocalypseChannelHook": webhook.url,
                             "isAPchannelThread": isThread, "parentID": parent.id}})
                await ctx.respond("Канал установлен!")

    @commands.slash_command(name="настройки-сервера", description="description")
    @commands.has_permissions(administrator=True)

    async def server_settings(self, ctx,
                              field: Option(str, description="Поле", choices=["ссылка на сервер","автопубликация"], required=True) = "0",
                              value: Option(bool, description="Значение", required=True) = False):
        if field == "ссылка на сервер":
            if value:
                result = db.servers.find_one({"serverid": ctx.guild.id}, {"invitelink": 1})
                if not result["invitelink"]:
                    invite = await ctx.channel.create_invite(max_age=0)
                    db.servers.update_one({"serverid": ctx.guild.id}, {"$set": {"invitelink": str(invite)}})
                    await ctx.respond(f"Поле **{field}** установлено на {str(invite)}")
                else:
                    await ctx.respond(
                        f"На сервер уже есть ссылка-приглашение **{result['invitelink']}**. Если она недействительна, пожалуйста, повторите команду, но с False, а затем снова с True")
            else:
                db.servers.update_one({"serverid": ctx.guild.id}, {"$set": {"invitelink": ""}})
                await ctx.respond(f"Поле **{field}** отчищено.")

        # if field == "автопубликация":
        #     if value:
        #
        #
        #         await ctx.respond(f"Поле **{field}** установлено на {value}")
    @commands.slash_command(name="настройки-серверных-строк",description="description")
    @commands.has_permissions(administrator=True)
    async def server_settings_str(self, ctx, field : Option(str, description="Поле",choices=["текст партнёрки"], required=True)="", value : Option(str, description="Значение", required=True)=" "):
        if field == "текст партнёрки":
            db.servers.update_one({"serverid": ctx.guild.id}, {"$set": {"text": value}})
            srv = db.servers.find_one({"serverid":ctx.guild.id}, {"bumpcolor":1,"invitelink":1})
            clr =srv["bumpcolor"]
            lnk = srv["invitelink"]
            embed = discord.Embed(title=f"{ctx.guild.name}",description=f"{value}",colour= publicCoreData.embedColors["Neutral"] if clr is None else int(clr))
            embed.add_field(name="Ссылка на сервер",value=f"🔗{lnk}",inline=False)
            await ctx.respond("Текст партнёрского соглашения сервера заменён на:", embed=embed)

