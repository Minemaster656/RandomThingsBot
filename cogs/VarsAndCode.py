import asyncio

# try:
import discord
from discord import Option, Webhook, Forbidden
from discord.ext import commands
# except:
#     import pycord as discord
#     from pycord import Option, Webhook, Forbidden
#     from discord.ext import commands

import Data
import utils


class VarsAndCode(commands.Cog):
    ''' VarsAndCode | BOT COG'''
    name = "VarsAndCode"
    author = ""

    def __init__(self, bot):
        self.bot = bot
    # @commands.slash_command(name="выполнить",description="Выполняет Python-код. Документация: undefined")
    # async def execute(self, ctx, code : Option(str, description="код.", required=True)="print('Hello, World!)'"):
    #
    #
    #     allowed_libraries = ["math", "random"]
    #     allowed_modules = ["Nerdcord", "SafeUtils"]
    #
    #     result = await utils.execute_python_code(code, 16, allowed_libraries, allowed_modules)
    #     await ctx.respond(f"```{utils.formatStringLength(result, 2000)}```")


def setup(bot):
    bot.add_cog(VarsAndCode(bot))
