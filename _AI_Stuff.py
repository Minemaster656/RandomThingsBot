import random
# import numpy as np
# import matplotlib.pyplot as plt
import discord
from discord.ext import commands
# import perlin_noise
from discord import Option
from random import *

import AI
import Data


class _AI_Stuff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="спросить-gpt3",description="Отправляет одиночный вопрос GPT3.5")
    async def askGPT3(self, ctx, prompt : Option(str, description="Запрос для ИИ", required=True)="Hello!"):
        # async with ctx.typing():
        response : str = await AI.askGPT("", prompt, False)
        print(response)
        resp = str(response)
        try:
            embed = discord.Embed(title="Ответ от ChatGPT 3.5",description=f"{resp}",colour=discord.Colour.blue())
            await ctx.respond(embed=embed)
        except:
            print(f"THERE IS ANOTHER SHITTING ERROR! THIS AWFUL STRING IS {resp}")

    @commands.slash_command(name="спросить-gpt4", description="Отправляет одиночный вопрос GPT4")
    async def askGPT4(self, ctx, prompt: Option(str, description="Запрос для ИИ", required=True) = "Hello!"):
        # async with ctx.typing():
        response: str = await AI.askGPT("", prompt, True)
        print(response)
        resp = str(response)
        try:
            embed = discord.Embed(title="Ответ от ChatGPT 4", description=f"{resp}",
                                  colour=discord.Colour.blue())
            await ctx.respond(embed=embed)
        except:
            print(f"THERE IS ANOTHER SHITTING ERROR! THIS AWFUL STRING IS {resp}")

    @commands.slash_command(name="спросить-никого", description="Отправляет одиночный вопрос никому")
    async def askNobody(self, ctx, prompt: Option(str, description="Запрос для никого", required=True) = "Hello!"):
        # async with ctx.typing():
        response: str = f"{prompt}"
        print(response)
        resp = str(response)
        embed = discord.Embed(title="Ответ от никого", description=f"{resp}",
                              colour=discord.Colour.blue())
        await ctx.respond(embed=embed)