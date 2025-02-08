import discord
from discord.ext import commands
from discord import Option


class APLR(commands.Cog):
    ''' APLR | BOT COG'''
    name = "APLR"
    author = ""

    def __init__(self, bot: discord.Bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(APLR(bot))
