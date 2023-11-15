import random
# import numpy as np
# import matplotlib.pyplot as plt
import discord
from discord.ext import commands
# import perlin_noise
from discord import Option
from random import *

import utils


class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.slash_command(name="залго",description="сделать залго")
    async def makeZalgo(self, ctx, text: Option(str, description="Текст", required=True)="a", intensity : Option(int, description="Интенсивность", required=False)=5, ephemeral : Option(bool, description="Видно только Вам", required=False)=True):

        output = utils.zalgo_text(text, intensity)
        embed = discord.Embed(title=f"Zalgo {intensity}",description=f"{output}",colour=0xffffff)
        await ctx.respond(embed=embed,ephemeral=ephemeral)

