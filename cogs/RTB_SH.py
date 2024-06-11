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
        # directory_name = "shcommands"
        # for filename in os.listdir(directory_name):
        #     if filename.endswith(".py"):
        #         class_name = filename.replace(".py", "")
        #         filepath = os.path.join(directory_name, filename)
        #



        path = os.path.join(os.getcwd(), "cogs", 'shcommands',"")
        # print(path)
        files = os.listdir(path)

        # Создаем пустой массив, куда будем добавлять объекты классов
        objects = []

        # Импортируем каждый модуль и добавляем объекты классов в массив
        for file in files:
            if file.endswith('.py'):  # Проверка, что файл - это модуль Python
                module_name = file[:-3]  # Удаляем расширение .py
                module = importlib.import_module(f'cogs.shcommands.{module_name}')
                class_name = module_name.capitalize()  # Предполагаем, что класс назван как модуль с заглавной буквы
                if hasattr(module, class_name):
                    obj = getattr(module, class_name)()
                    # objects.append(obj)
                    commands_dict[obj.command_name] = obj

        return commands_dict

    @commands.Cog.listener("on_message")
    async def message_listener(self, message: discord.Message):
        if message.channel.id in Data.SH_CHANNELS:
            if message.author.id == self.bot.user.id:
                return
            # print("SH: ", message.content, " in channel ", message.channel.name)
            tokens = message.content.split(" ")
            command = tokens[0]
            # print(tokens)
            # print(commands)
            if command in self.commands.keys():
                await self.commands[command].execute(message.channel)
            else:
                # print("Команда не найдена")
                await message.channel.send("Команда не найдена!")


def setup(bot):
    bot.add_cog(RTB_SH(bot))
