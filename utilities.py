import random
# import numpy as np
# import matplotlib.pyplot as plt
import discord
from discord.ext import commands
# import perlin_noise
from discord import Option
from random import *

import publicCoreData
import re


class BotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="массивное-редактирование-каналов",
                            description="Редактировать каналы категории. Выберите ? для информации.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def massPermissionsEdit(self, ctx,
                                  mode: Option(str, description="Режим работы", required=False,
                                               choices=["?", "Имя", "Копировать права", "DEBUG"]) = None, #
                                  category: Option(discord.CategoryChannel, description="Категория для работы команды",
                                                   required=True) = None, value : Option(str, description="Значение", required=False)="None",
                                  filters : Option(str, description="Фильтры", choices=["-", "первый", "последний"], required=False)="-",
                                  channel : Option(discord.TextChannel, description="Второй канал (см. справку.)", required=False)="None"
                                  ): #"Выполнить"


        embed = discord.Embed(title="none", description="none")





        if mode == "?":
            embed = discord.Embed(title="Режимы массивного редактирования каналов",
                                  colour=publicCoreData.embedColors["Neutral"],
                                  description=f"Справка по режимам команды"
                                  )
            # embed.add_field(name="Выполнить", value=f"Выполняет специальный код для редактирования каналов. Вот как это работает:"
            #                                         f"`IF ENDIF` - условие. Между ними можно вписать код"
            #                                         f"`channelPosition == first|last|middle DO RENAME|aaa<name>bbb|` - условие и действие для логики: если канал **первый|последний|середина** в категории то переименовать его по паттерну:"
            #                                         f" aaa это первая часть текста, <name> это место где стоит название канала до редактирвования, а bbb это конец."
            #                                         f" Если ввести **<-<name>---** а канал будет назван до этого **тест**, то на выходе получится <-тест---"
            #                                         f"Если указано first то будет переименован только первый канал категории, last же последний. middle - средний"
            #                                         f"Пример команды - IF channelPosition == first DO RENAME|aaa<name>b| ENDIF"
            #                                         f"")


            embed.set_footer(text="Вам необходимы права Администратора для использования этой команды.\nВ целях безопасности, есть откат в 30 секунд на сервер.")
        elif mode == "Выполнить":
            # await tokenize_text(value)
            ...

        elif mode == "DEBUG":
            if category:
                for channel in category.channels:
                    # await channel.edit(name="Новое название канала")
                    # await channel.set_permissions(ctx.guild.default_role, read_messages=False)
                    await ctx.send(channel.name)
                # await ctx.send("Названия и права каналов в категории были обновлены.")
            else:
                await ctx.send("Категория не найдена.")
        # async def tokenize_text(text):
        #     tokens = re.findall(r'IF channelPosition == (first|last|middle) DO RENAME|(.*?)| ENDIF', text) #(RENAME \w+)
        #
        #     for token in tokens:
        #         condition = token[0]
        #         action = token[1]
        #
        #         if condition == 'first':
        #             # Выполнить код для первого условия
        #
        #             await channel_rename(action, 0)
        #         elif condition == 'middle':
        #             # Выполнить код для второго условия
        #
        #             await channel_rename(action,1)
        #         elif condition == 'last':
        #             # Выполнить код для второго условия
        #
        #             await channel_rename(action, 2)
        #
        # async def channel_rename(action, pos):
        #     text = str.split(action, "<name>")
        #     channels = category.channels
        #     if pos == 0 or pos == 2:
        #         if pos == 0:
        #             chPos = 0
        #         else:
        #             chPos = len(channels)-1
        #         await ctx.send("---" + channels[chPos].name)
        #         channelName = channels[chPos].name
        #         chName = text[0] + channelName
        #         if len(text) > 1:
        #             chName += text[chPos]
        #         await channels[chPos].edit(name=chName)
        #         # await channel.set_permissions(ctx.guild.default_role, read_messages=False)
        #         await ctx.send(channels[chPos].name + "\n===")
        #
        #
        #     for channel in category.channels:
        #
        #         if pos == 1:
        #             await ctx.send("---"+channel.name)
        #             channelName = channel.name
        #             chName= text[0]+channelName
        #             if len(text)>1:
        #                 chName+=text[1]
        #             await channel.edit(name=chName)
        #             # await channel.set_permissions(ctx.guild.default_role, read_messages=False)
        #             await ctx.send(channel.name+"\n===")

        # Выполнить соответствующее действие в зависимости от типа токена RENAME
        # Например, переименовать канал

        # Пример использования
        # user_input = "IF channelPosition == first DO RENAME aaa<TEXT> IF channelPosition == last DO RENAME bbb<TEXT>"
        # tokenize_text(user_input)
            # await ctx.respond(embed=embed)
        # await ctx.respond("Учтите, что у Вас должно быть разрешение Администратора для использования этой команды!")
