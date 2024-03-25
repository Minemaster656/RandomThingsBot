import discord
from discord.ext import commands
from discord import Option

import swearfilter as sw
import utils


class Moderation(commands.Cog):
    ''' Moderation | BOT COG'''
    name = "Moderation"
    author = ""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["маты", "брань", "swears", "swear"])
    async def checkSwear(self, ctx, *, line):
        async with ctx.typing():
            line = line.replace("\n", "")

            line_checked = sw.findSwear(str(line))
            # print("LINE: ", line)
            # print(line_checked)
            await ctx.reply(utils.formatStringLength("Ругань: \n" + line_checked, 1950))


def setup(bot):
    bot.add_cog(Moderation(bot))
