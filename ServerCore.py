import random
import typing

# import numpy as np
# import matplotlib.pyplot as plt
import discord
from discord.ext import commands
# import perlin_noise
from discord import Option
from random import *

import publicCoreData
from publicCoreData import conn, cursor


class ServerCore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="настройки-каналов", description="description")
    @commands.has_permissions(administrator=True)
    async def settings_channels(self, ctx, field: Option(str, description="Поле",
                                                         choices=["игра Апокалипсис", "Объявления", "реклама"],
                                                         required=True) = "",
                                channel: Option(typing.Union[discord.TextChannel, discord.Thread], description="Канал.",
                                                required=True) = None):
        publicCoreData.findServerInDB(ctx)

    @commands.slash_command(name="настройки-сервера", description="description")
    @commands.has_permissions(administrator=True)

    async def server_settings(self, ctx,
                              field: Option(str, description="Поле", choices=["ссылка на сервер"], required=True) = "0",
                              value: Option(bool, description="Значение", required=True) = False):
        if field == "ссылка на сервер":
            if value:
                cursor.execute("SELECT invitelink FROM servers WHERE serverid=?", (ctx.guild.id,))
                result = cursor.fetchone()
                if result == "" or result is None or result == " ":
                    invite = await ctx.channel.create_invite(max_age=0)
                    cursor.execute("UPDATE servers SET invitelink = ? WHERE serverid = ?",
                                   (str(invite), int(ctx.guild.id)))
                    conn.commit()
                    await ctx.respond(f"Поле **{field}** установлено на {str(invite)}")
                else:
                    await ctx.respond(
                        f"На сервер уже есть ссылка-приглашение **{result}**. Если она недействительна, пожалуйста, повторите команду но с False, и потом снова True")
            else:
                cursor.execute("UPDATE servers SET invitelink = ? WHERE serverid = ?",
                               (" ", ctx.guild.id))
                conn.commit()
                await ctx.respond(f"Поле **{field}** отчищено.")
    @commands.slash_command(name="настройки-серверных-строк",description="description")
    @commands.has_permissions(administrator=True)
    async def server_settings_str(self, ctx, field : Option(str, description="Поле",choices=["текст партнёрки"], required=True)="", value : Option(str, description="Значение", required=True)=" "):
        if field == "текст партнёрки":
            cursor.execute("UPDATE servers SET text = ? WHERE serverid = ?", (value, ctx.guild.id))
            conn.commit()

