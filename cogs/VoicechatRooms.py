import discord
from discord.ext import commands
from discord import Option


class VoicechatRooms(commands.Cog):
    ''' VoicechatRooms | BOT COG'''
    name = "VoicechatRooms"
    author = ""

    def __init__(self, bot: discord.Bot):
        self.bot = bot




def setup(bot):
    bot.add_cog(VoicechatRooms(bot))
