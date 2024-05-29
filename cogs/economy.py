import random
import random as rd
import time

import numpy as np
import matplotlib.pyplot as plt

try:
    import discord
    from discord import Option, Webhook, Forbidden
    from discord.ext import commands
except:
    import pycord as discord
    from pycord import Option, Webhook, Forbidden
    from discord.ext import commands

import perlin_noise

from random import *

import Data
import d
from Data import db
import utils
from Data import cursor
from Data import conn


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    cmds = discord.SlashCommandGroup(
        "экономика",
        "",

    )

    @commands.slash_command(name="баланс", description="Показывает Ваш баланс или баланс пользователя")
    async def balance(self, ctx, member: Option(discord.Member, description="Пользователь", required=False) = None):
        with ctx.typing():
            if member is None:
                member = ctx.author

            data = db.users.find_one({"userid": member.id})
            if not data:
                Data.writeUserToDB(member.id, member.name)
                data = db.users.find_one({"userid": member.id})
                # data['money'] = 0
                # data['money_bank'] = 0
            # data = (0,0)

            embed = discord.Embed(title="Баланс", description=f"Баланс пользователя <@{member.id}>:"
                                  , colour=Data.embedColors["Economy"])
            embed.add_field(name="Баланс на руках", value=f"{data['money']}")
            embed.add_field(name="Баланс в банке", value=f"{data['money_bank']}")

            await ctx.respond(embed=embed)

    @cmds.command(name="заработок", description="Информация о заработке")
    async def howToMakeMoney(self, ctx):
        embed = discord.Embed(title="Способы поднять бабла",
                              description=f"Большинство команды заработка имеют откат, а что бы не переполнять API дискорда списком из десятков /-команд, часть из них с преффиксом бота."
                                          f""
                                          f""
                                          f"")
        embed.add_field(name=f"{Data.preffix}искатьДеньги",
                        value="Даёт вам случайное количество деняк. КД раз в минуту.")
        embed.add_field(name=f"{Data.preffix}казино",
                        value="КАЗИНО!!! Поставьте сумму и с шансом *50%* получите её в удвоенном размере, ну или потеряйте. КД раз в 10 сек.")
        await ctx.respond(embed=embed)

    @commands.command(aliases=["искатьДеньги"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def findMoney(self, ctx):

        # rand = rd.randint(0, utils.throwDice(ctx.author.id, ctx.author.name))
        rand = utils.throwDice(ctx.author.id, ctx.author.name)

        db.users.update_one({"userid": ctx.author.id}, {"$inc": {"money": rand}})
        await ctx.send(f"Получено **{rand}{Data.currency}**")

    @commands.command(aliases=["казино"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def casino(self, ctx,value:int):

        # rand = rd.randint(0, utils.throwDice(ctx.author.id, ctx.author.name))
        # rand = utils.throwDice(ctx.author.id, ctx.author.name)
        user = d.getUser(ctx.author.id, ctx.author.name)
        if user['money'] >= value:
            isWin = random.randint(0, 100) < 50
            db.users.update_one({"userid": ctx.author.id}, {"$inc": {"money": value * 1 if isWin else value * -1}})
            if isWin:
                await ctx.send(f"💸 Вы выиграли **{value}**{Data.currency}!")
            else:
                await ctx.send(f"🧨 Вы проиграли **{value}**{Data.currency}!")
        else:
            await ctx.send(f"Вам не хватает **{value - user['money']}**{Data.currency}!")


    @cmds.command(name="лидеры", description="Лидеры экономики")
    async def ec_leaders(self, ctx):
        leaderCount = 10
        result = db.users.find().sort([("money", -1), ("money_bank", -1)]).limit(leaderCount)
        out = ""
        it = 0
        # Вывод результатов
        embed = discord.Embed(title="Лидеры экономики", description="Топ-10 в экономике",
                              colour=Data.embedColors["Economy"])

        for row in result:
            # out +=f"`{it}`. @{row[0]} {row[1]}{Data.currency}:moneybag: + {row[2]}{Data.currency}:bank:. И того {row[1]+row[2]}{Data.currency}\n"
            embed.add_field(name=f"`{it + 1}`. @{row['username']}",
                            value=f"{row['money'] + row['money_bank']}{Data.currency}", inline=False)
            it += 1

        await ctx.respond(embed=embed)

    @cmds.command(name="перевод-денег", description="Пересылает деньги")
    async def pay(self, ctx, member: Option(discord.Member, description="Кому переслать?", required=True) = None,
                  value: Option(int, description="Сколько переслать?", required=True) = 0):
        user_sender = d.getUser(ctx.author.id, ctx.author.name)
        user_receiver = d.getUser(member.id, member.name)
        if user_sender["money"] < value:
            await ctx.respond(f"Вам нехватает {round(value - user_sender['money'],2)}{Data.currency}!")
        else:
            db.users.update_one({"userid": ctx.author.id}, {"$inc": {"money": -value}})
            db.users.update_one({"userid": member.id}, {"$inc": {"money": value}})
            await ctx.respond(f"Вы перевели {value}{Data.currency} пользователю {member.mention}!")

    # @cmds.command(name="регистрация-предмета", description="Регистрирует новый товар в экономике.")
    async def registerItem(self, ctx, name: Option(str, description="Название предмета", required=True) = " ",
                           description: Option(str, description="Описание предмета", required=True) = " ",
                           id: Option(str, description="Уникальный ID предмета", required=True) = " ",
                           type: Option(str, description="Тип предмета", required=True) = " ",
                           base_price: Option(float, description="Базовая цена", required=True) = 0,
                           dynamic_price: Option(bool, description="Изменяется ли цена товара от покупок",
                                                 required=False) = False,
                           owner: Option(str, description="ID владельца бизнеса", required=True) = ""

                           ):

        # buisness = db.buisnesses.find_one({"id":owner})
        if await Data.parsePermissionFromUser(ctx.author.id, "root") or Data.parsePermissionFromUser(ctx.author.id,
                                                                                                     "edit_economy"):

            buisness = True
            if buisness:
                doc = {
                    "id": id, "type": type, "base_price": base_price, "dynamic_price": dynamic_price,
                    "price": base_price, "owner": owner,
                    "timestamp": int(time.time() / 1000), "creator": ctx.author.id, "purchased": 0, "name": name,
                    "description": description, "quality": 0
                }
                db.items.insert_one(doc)
            else:
                embed = discord.Embed(title="Бизнес не найден!", description=f"Бизнесс {owner} не найден!",
                                      colour=Data.embedColors["Error"])
                await ctx.respond(embed=embed)
        else:
            await ctx.respond("Нет прав на редактирование экономики!", ephemeral=True)

    # @cmds.command(name="осмотреть-предмет",description="Выводит информацию о предмете")
    # async def inspect_item(self, ctx, id : Option(str, description="ID предмета", required=True)=" "):
    #     # doc = db.items.find({"id":id})
    #     if doc:
    #         await ctx.respond(doc)
    #     else:
    #         await ctx.respond(f"Предмет {id} не найден!")
    # @cmds.command(name="регистрация-бизнеса",description="Регистрирует бизнес.")
    async def registerBuisness(self, ctx, name: Option(str, description="Название", required=True) = " ",
                               id: Option(str, description="ID", required=True) = " "
                               , link: Option(str, description="Сайт бизнеса", required=False) = " ",
                               server: Option(str, description="Сервер бизнеса", required=False) = " ",
                               logo: Option(str, description="Логотип бизнесса (ссылка)", required=True) = " ",
                               owner: Option(discord.Member, description="Владелец бизнеса", required=True) = 0):
        if await Data.parsePermissionFromUser(ctx.author.id, "root") or await Data.parsePermissionFromUser(
                ctx.author.id, "edit_economy"):
            res = db.buisnesses.find_one({"id": id})
            if res:
                await ctx.respond("ID не уникален!")
            else:
                delivers = {}
                doc = {
                    "name": name, "id": id, "link": link, "server": server, "logo": logo, "owner": owner.id,
                    "timestamp": int(time.time() / 1000), "creator": ctx.author.id, "delivers": delivers,
                    "employee": {f"{owner.id}": 0}, "items": [], "money_last": 0, "money": 0,
                    "storage": {}, "tech": 0

                }
        else:
            ...
        # TODO: перки и прокачка, решить первичники


def setup(bot):
    bot.add_cog(Economy(bot))
