import random
# import numpy as np
# import matplotlib.pyplot as plt
import discord
from discord.ext import commands
# import perlin_noise
from discord import Option
from random import *
import json
import os

import publicCoreData
import utils


class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.slash_command(name="залго",description="сделать залго")
    async def makeZalgo(self, ctx, text: Option(str, description="Текст", required=True)="a", intensity : Option(int, description="Интенсивность", required=False)=5, ephemeral : Option(bool, description="Видно только Вам", required=False)=True):

        output = utils.zalgo_text(text, intensity)
        embed = discord.Embed(title=f"Zalgo {intensity}",description=f"{output}",colour=0xffffff)
        await ctx.respond(embed=embed,ephemeral=ephemeral)


    @commands.slash_command(name="интерсервер",description="Помечает канал как интерсервер")
    async def interserver(self, ctx, channel : Option(discord.TextChannel, description="Канал", required=True)=0, type: Option(str, description="Тип канала. Можно иметь одновременно несколько на сервер.",choices=publicCoreData.interhubs, required=True)=0,reset : Option(bool, description="True для отчистки поля", required=False)=False):
        if publicCoreData.parsePermissionFromUser(ctx.author.id, "root") or (publicCoreData.parsePermissionFromUser(ctx.author.id, "verified") and(ctx.author.permissions.administrator or ctx.author.permissions.manage_channels) ):
            # with open('private/data.json', 'r') as file:
            #     try:
            #         data = json.load(file)
            #     except json.JSONDecodeError:
            #         data = {}
            #     except FileNotFoundError:
            #         data = {}
            #
            #
            #
            #
            #
            # with open('private/data.json', 'w') as file:
            #     json.dump(data, file)

            def update_json(data, array_name, delete=False):
                file_path = os.path.join('private', 'interchats.json')

                # Проверяем наличие файла
                if not os.path.exists(file_path):
                    # Если файла нет, создаем пустой JSON объект
                    json_data = {}
                else:
                    # Если файл существует, считываем его содержимое
                    with open(file_path, 'r') as file:
                        try:
                            json_data = json.load(file)
                        except json.JSONDecodeError:
                            # В случае ошибки при чтении файла (некорректный JSON), создаем пустой JSON объект
                            json_data = {}


                # Проверяем наличие массива с заданным именем
                if array_name not in json_data:
                    json_data[array_name] = []
                if len(json_data) > 0:
                    if type in json_data.keys():
                        if len(json_data[type]) > 0:
                            i = 0
                            for arr in json_data[type]:
                                if arr[0] == ctx.guild.id:
                                    json_data[type].pop(i)
                                    break
                                i += 1
                if delete:
                    # Удаление элемента из массива, если delete=True
                    # json_data[array_name] = [item for item in json_data[array_name] if item != data]
                    if len(json_data) > 0:
                        if type in json_data.keys():
                            if len(json_data[type]) > 0:
                                i = 0
                                for arr in json_data[type]:
                                    if arr[1] == channel.id:
                                        json_data[type].pop(i)
                                        break
                                    i += 1
                else:
                    # Добавление элемента в массив, если delete=False
                    json_data[array_name].append(data)
                publicCoreData.interchats = json_data
                # Записываем обновленные данные в файл
                with open(file_path, 'w') as file:
                    json.dump(json_data, file)
            update_json((ctx.guild.id, channel.id), type, reset)
            found = False
            for hook in await ctx.channel.webhooks():
                if hook.user.id == self.bot.user.id:
                    found = True
            if not found:
                await channel.create_webhook(name="RTB hook")
            await ctx.respond("Успешно!",ephemeral=True)
        else:
            await ctx.respond("У Вас недостаточно прав для этого действия!!!\nНеобходима верификация пользователя (в боте, не в Discord) и право управления каналами/администратор",ephemeral=True)




