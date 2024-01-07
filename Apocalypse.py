import json
import random
# import random
import sqlite3

# import numpy as np
# import matplotlib.pyplot as plt
import discord
from discord.ext import commands
# import perlin_noise
from discord import Option
from random import *

import Data
import utils

def genApocalypseItems():
    items = sqlite3.connect("ApocalypseData/ApocalypseItems.db")
    itemsCursor = items.cursor()
    itemsCursor.execute("SELECT ItemNameRu FROM items ORDER BY RANDOM() LIMIT 10")

    results = itemsCursor.fetchall()

    result_ds = ""
    for result in results:
        # print(result[0])
        result_ds += "1. " + result[0] + "\n"
    # print("Выбор таска")
    with open('ApocalypseData/MainApocalypseData.json', encoding="utf-8") as f:
        ap_values = json.load(f)
    # print(ap_values)
    taskTypes = ap_values["taskTypes"]
    task = choice(taskTypes)
    extras = ap_values["extraTasks"]
    ex_tasks_out = ""
    ex_tasks = choices(extras, k=randint(0, 3))
    for i in ex_tasks:
        ex_tasks_out += "\n- " + i
    # await ctx.respond("Отправка...", ephemeral=True)
    guide = f"\n\nЭто список предметов для игры {Data.apocalypseDLC}. \n" \
            f"Правила игры - У Вас есть список предметов. Можно гипертрофировать их смысл, использовать мемный или прямой смысл. " \
            f"\nПо умолчанию Вы не можете использовать предметы не из списка. Обычно цель - уничтожить планету/мир/человечество, однако могут быть другие типы заданий.\n" \
            f"Так же есть дополнительные эффекты, изменяющие правила игры.\n" \
            f"Так же не делайте предметы из списка из других предметов из списка. ОНИ У ВАС УЖЕ ЕСТЬ!\n" \
            f"При мемных применениях объясняйте, почему это так работает!\n" \
            f"**ИГРА ЕЩЁ В РАЗРАБОТКЕ!** \n*В планах сделать автоотправку и ИИ ответы автоматические.*"
    embed = discord.Embed(title="Дополнительно...",description="Дополнительная часть: ответ от ИИ (если есть) и руководство.",colour=0xffffff)
    embed.add_field(name="Что это за игра?",value=guide,inline=False)
    output = (f"# Список:\n{result_ds}\n"
              f"# Условие: \n{task}\n"
              f"# Дополнительные условия:\n{ex_tasks_out}", embed)
              #f"\n{guide}", )

    return output
class apocalypse(commands.Cog):
    currentDLC = Data.apocalypseDLC  # "Самый странный апокалипсис⁶™"

    def __init__(self, bot):
        self.bot = bot
        self.items = sqlite3.connect("ApocalypseData/ApocalypseItems.db")
        self.itemsCursor = self.items.cursor()

        @commands.slash_command(name="создать-список-апокалипсиса",description="создаёт новый случайный список для апокалипсиса")
        async def genApocalypseList(self, ctx):
            list = genApocalypseItems()
            await ctx.respond(list[0], embed=list[1])

# def setup(bot):
#     bot.add_cog(apocalypse(bot))