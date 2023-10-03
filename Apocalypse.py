import random
import sqlite3

# import numpy as np
# import matplotlib.pyplot as plt
import discord
from discord.ext import commands
# import perlin_noise
from discord import Option
from random import *


class Apocalypse(commands.Cog):
    items = sqlite3.connect("ApocalypseData/ApocalypseItems.db")
    itemsCursor = items.cursor()
    def __init__(self, bot):
        self.bot = bot
    @commands.slash_command(name="создать-список",description="Создаёт список предметов и заданий.")
    async def getList(self, ctx):
        ...
