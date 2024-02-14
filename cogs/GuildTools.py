import discord
from discord.ext import commands
from discord import Option

import d
from Data import db


class GuildTools(commands.Cog):
    ''' GuildTools | BOT COG'''
    name = "GuildTools"
    author = ""

    def __init__(self, bot):
        self.bot = bot

    cmds = discord.SlashCommandGroup(
        "template",
        "",

    )

    @cmds.command(name="сохранить-пресет", description="Сохранение названий ролей, каналов и прочего в слот.")
    async def savePreset(self, ctx, category: Option(str, description="Категория",
                                                     choices=["Названия каналов", "Названия ролей"], required=True) = 0,
                         slot: Option(str, description="Слот сохранения", choices=[
                             "Основной", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                             "✨11", "✨12", "✨13", "✨14", "✨15", "✨16", "✨17", "✨18", "✨19", "✨20"
                         ], required=True) = "Основной"):
        doc = d.getGuild(ctx)
        categories = {"Названия каналов": "channels", "Названия ролей": "roles"}
        slots = {"Основной":0, "1":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10,
                             "✨11":11, "✨12":12, "✨13":13, "✨14":14, "✨15":15, "✨16":16, "✨17":17, "✨18":18, "✨19":19, "✨20":20}
        slot_num = slots[slot]
        category_key = categories[category]

        if


def setup(bot):
    bot.add_cog(GuildTools(bot))
