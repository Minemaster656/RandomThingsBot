import json
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

import utils


class BotCog(commands.Cog):
    permissions = publicCoreData.permissions_user

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="массовое-редактирование-каналов",
                            description="Редактировать каналы категории. Выберите справку для информации.")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def massPermissionsEdit(self, ctx,
                                  mode: Option(str, description="Режим работы", required=False,
                                               choices=["Справка", "Имя", "Копировать права", "DEBUG"]) = None,  #
                                  category: Option(discord.CategoryChannel, description="Категория для работы команды",
                                                   required=True) = None,
                                  value: Option(str, description="Значение", required=False) = "None",
                                  filters: Option(str, description="Фильтр",
                                                  choices=["все", "первый", "последний", "не первый", "не последний",
                                                           "не крайний"], required=False) = "все",
                                  channel: Option(discord.TextChannel, description="Второй канал (см. справку.)",
                                                  required=False) = "None"
                                  ):  # "Выполнить"

        embed = discord.Embed(title="none", description="none")

        if mode == "Справка":
            embed = discord.Embed(title="Режимы массового редактирования каналов",
                                  colour=publicCoreData.embedColors["Neutral"],
                                  description=f"Справка по режимам команды"
                                  )
            embed.add_field(inline=False, name="Параметры", value=f"- Режим работы\n"
                                                                  f"Выбирает режим работы. Они указаны далее.\n"
                                                                  f"- Категория\n"
                                                                  f"Категория, каналы которой будут подвергнуты изменению\n"
                                                                  f"- Значение\n"
                                                                  f"Используется некоторыми из режимов. Например, массовое добавление текста в название использует параметры для шаблона переименования.\n"
                                                                  f"- Фильтр\n"
                                                                  f"Фильтр для каналов. Работает по позиции канала. Фильр `все` изменит ВСЕ каналы категории!\n"
                                                                  f"- Второй канал\n"
                                                                  f"Используется некоторыми режимами для копирования данных из него. Если он требуется, но пропущен, будет взят канал, в котором вызвана команда.\n")
            embed.add_field(inline=False, name="Имя", value=f"Меняет имя каналов по паттерну:\n"
                                                            f"``текст<name>текст``\n"
                                                            f"Меняет имя канала. Оригинальное имя находится на месте <name>. перед ним и после него можно добавлять текст. Меняет по шаблону имена ВСЕХ каналов категирии, попадающих под фильтр.\n")

            # embed.add_field(name="Выполнить", value=f"Выполняет специальный код для редактирования каналов. Вот как это работает:"
            #                                         f"`IF ENDIF` - условие. Между ними можно вписать код"
            #                                         f"`channelPosition == first|last|middle DO RENAME|aaa<name>bbb|` - условие и действие для логики: если канал **первый|последний|середина** в категории то переименовать его по паттерну:"
            #                                         f" aaa это первая часть текста, <name> это место где стоит название канала до редактирвования, а bbb это конец."
            #                                         f" Если ввести **<-<name>---** а канал будет назван до этого **тест**, то на выходе получится <-тест---"
            #                                         f"Если указано first то будет переименован только первый канал категории, last же последний. middle - средний"
            #                                         f"Пример команды - IF channelPosition == first DO RENAME|aaa<name>b| ENDIF"
            #                                         f"")
            await ctx.respond(embed=embed)

            embed.set_footer(
                text="Вам необходимы права Администратора для использования этой команды.\nВ целях безопасности, есть откат в 30 секунд на сервер.")
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

    @commands.slash_command(name="разрешения", description="Редактирование разрешений пользователя")
    async def editMemberPermissions(self, ctx, permission: Option(str, description="Разрешение. ? для списка",
                                                                  choises=permissions, required=True) = "none",
                                    member: Option(discord.Member, description="Пользователь", required=True) = None,
                                    value: Option(bool, description="Значение", required=True) = True,
                                    ephemeral: Option(bool, description="Видно ли только вам?",
                                                      required=False) = False):
        if member is None:
            member = ctx.author
        perm_root = publicCoreData.parsePermissionFromUser(ctx.author.id, "root")
        perm_edit = publicCoreData.parsePermissionFromUser(ctx.author.id, "edit_permissions")
        if permission != "?":
            if perm_root or perm_edit:
                if permission != "root":
                    await publicCoreData.setPermissionForUser(member.id, permission, value)
                    embed = discord.Embed(title=f"Разрешение {permission} изменено успешно!",
                                          description=f"Разрешение изменено у участника <@{member.id}> на **{value}**",
                                          colour=publicCoreData.embedColors["Success"])
                    await ctx.respond(embed=embed, ephemeral=ephemeral)
                else:
                    if perm_root:
                        await publicCoreData.setPermissionForUser(member.id, permission, value)
                        embed = discord.Embed(title=f"Разрешение {permission} изменено успешно!",
                                              description=f"Разрешение изменено у участника <@{member.id}> на **{value}**",
                                              colour=publicCoreData.embedColors["Success"])
                        await ctx.respond(embed=embed, ephemeral=ephemeral)
                    else:
                        await utils.noPermission(ctx, "root")
            else:
                await utils.noPermission(ctx, "edit_permissions | root")
        else:
            await ctx.respond(json.dumps(publicCoreData.permissions_user))
