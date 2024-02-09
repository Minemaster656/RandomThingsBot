import discord
from discord.ext import commands
from discord import Option


class Moderation(commands.Cog):
    ''' Moderation | BOT COG'''
    name = "Moderation"
    author = ""

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Moderation(bot))
