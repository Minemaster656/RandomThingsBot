import random as rd
import numpy as np
import matplotlib.pyplot as plt
import discord
from discord.ext import commands
import perlin_noise
from discord import Option
from random import *

import publicCoreData
import utils
from publicCoreData import cursor
from publicCoreData import conn


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(name="баланс",description="Показывает Ваш баланс или баланс пользователя")
    async def balance(self, ctx, member : Option(discord.Member, description="Пользователь", required=False)=None):
        with ctx.typing():
            if member is None:
                member = ctx.author
            cursor.execute('SELECT money, money_bank FROM users WHERE userid = ?',(member.id, ))
            data = cursor.fetchone()
            if not data:
                publicCoreData.writeUserToDB(member.id, member.name)
            data = (0,0)

            embed = discord.Embed(title="Баланс",description=f"Баланс пользователя <@{member.id}>:"
                                                             , colour=publicCoreData.embedColors["Economy"])
            embed.add_field(name="Баланс на руках", value=f"{data[0]}")
            embed.add_field(name="Баланс в банке",value=f"{data[1]}")

            await ctx.respond(embed=embed)
    @commands.slash_command(name="заработок",description="Информация о заработке")
    async def howToMakeMoney(self, ctx):
        embed = discord.Embed(title="Способы поднять бабла",description=f"Большинство команды заработка имеют откат, а что бы не переполнять API дискорда списком из десятков /-команд, часть из них с преффиксом бота."
                                                                        f""
                                                                        f""
                                                                        f"")
        embed.add_field(name=f"{publicCoreData.preffix}искатьДеньги", value="Даёт вам случайное количество деняк. КД раз в минуту.")
        await ctx.respond(embed=embed)

    @commands.command(aliases=["искатьДеньги"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def findMoney(self, ctx):

        rand = rd.randint(1, utils.throwDice(ctx.author.id, ctx.author.name))
        cursor.execute(f"UPDATE users SET money = money + ? WHERE userid = ?", (rand, ctx.author.id))
        conn.commit()
        await ctx.send(f"Получено **{rand}{publicCoreData.currency}**")
    @commands.slash_command(name="лидеры",description="Лидеры экономики")
    async def ec_leaders(self, ctx):
        leaderCount = 10
        cursor.execute("SELECT username, money, money_bank, money + money_bank AS sum FROM users ORDER BY sum DESC LIMIT 10")
        result = cursor.fetchall()
        out = ""
        it = 0
        # Вывод результатов
        embed = discord.Embed(title="Лидеры экономики", description="Топ-", colour=publicCoreData.embedColors["Economy"])
        for row in result:
            # out +=f"`{it}`. @{row[0]} {row[1]}{publicCoreData.currency}💰 + {row[2]}{publicCoreData.currency}🏦. И того {row[1]+row[2]}{publicCoreData.currency}\n"
            embed.add_field(name=f"`{it}`. @{row[0]}",value=f""
                                                            f"{row[1]+row[2]}{publicCoreData.currency}",inline=False)
            it+=1

        await ctx.respond(embed=embed)


