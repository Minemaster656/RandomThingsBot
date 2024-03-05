import discord
from discord.ext import commands
from discord import Option


class AGI_RPGM(commands.Cog):
    ''' AGI_RPGM | BOT COG'''
    name = "AGI_RPGM"
    author = ""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.command(aliases=["иигм"])
    async def airpgm(self, ctx: commands.Context):

        history_size = 5

        messages = await ctx.channel.history(limit=history_size).flatten()
        messages.reverse()
        for message in messages:
            await ctx.reply(message.content)







def setup(bot):
    bot.add_cog(AGI_RPGM(bot))
