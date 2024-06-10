import glob
import importlib.util
import os

import discord
from discord.ext import commands
from discord import Option

import Data


class RTB_SH(commands.Cog):
    ''' RTB_SH | BOT COG'''
    name = "RTB_SH"
    author = ""


    def __init__(self, bot: discord.Bot):
        self.bot = bot

        self.commands = self.load_SH_commands()

    def load_SH_commands(self):
        commands_dict = {}
        # directory_name = "sh-commands"
        # for filename in os.listdir(directory_name):
        #     if filename.endswith(".py"):
        #         class_name = filename.replace(".py", "")
        #         filepath = os.path.join(directory_name, filename)
        #
        return commands_dict

    @commands.Cog.listener("on_message")
    async def message_listener(self, message: discord.Message):
        if message.channel.id in Data.SH_CHANNELS:
            # print("SH: ", message.content, " in channel ", message.channel.name)
            tokens = message.content.split(" ")
            command = tokens[0]
            # print(tokens)
            # print(commands)
            if command in self.commands.keys():
                await self.commands[command].execute(message.channel)
            else:
                print("Команда не найдена")


def setup(bot):
    bot.add_cog(RTB_SH(bot))
