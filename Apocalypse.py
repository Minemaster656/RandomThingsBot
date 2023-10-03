import random
# import numpy as np
# import matplotlib.pyplot as plt
import discord
from discord.ext import commands
# import perlin_noise
from discord import Option
from random import *


class Apocalypse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.slash_command(name="name",description="description")
    async def fname(self, ctx):
        ...
