import random
# import numpy as np
# import matplotlib.pyplot as plt
import discord
from discord.ext import commands
# import perlin_noise
from discord import Option
from random import *
# from youtube_dl import YoutubeDL

class voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#TODO: дописать


    @commands.slash_command(name="музыка",description="Запускает музыку с URL")
    async def play(self, ctx, url : Option(str, description="URL", required=False)="https://www.youtube.com/watch?v=YRvOePz2OqQ"):
        await ctx.author.voice.channel.connect()
        # with YoutubeDL(YDL_OPTIONS) as ydl:
        #     if "https://" in url:
        #         info = ydl.extract_info(url, download=False)
        #     else:
        #         info = ydl.extract_info(f"ytsearch:{url}", download=False)
        #
    @commands.command(aliases=["музыка"])
    async def play_yt(self, ctx, url):
        await ctx.message.author.voice.channel.connect()
        # with YoutubeDL(YDL_OPTIONS) as ydl:
        #     if "https://" in url:
        #         info = ydl.extract_info(url, download=False)
        #     else:
        #         info = ydl.extract_info(f"ytsearch:{url}", download=False)
        #