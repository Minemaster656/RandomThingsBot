import io
import json
import random
import re

import aiohttp
# import numpy as np
# import matplotlib.pyplot as plt
import discord
from discord.ext import commands
# import perlin_noise
from discord import Option
from random import *

import AIIO
# import sqlite3

import Data
import d
import utils

from Data import db
from PIL import Image, ImageFilter, ImageDraw, ImageOps
import pymongo


# from main import cursor
# from main import conn

class ConfirmGenArt(discord.ui.View):
    def __init__(self, character_registerer, prompt):
        super().__init__()

        self.character_registerer = character_registerer
        self.prompt = prompt

    @discord.ui.button(label="Сгенерировать!", style=discord.ButtonStyle.green)
    async def confirm_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Генерация...", view=None)

        gen = await AIIO.askT2I(self.prompt, AIIO.Text2Imgs.KANDINSKY)
        if gen:
            file = AIIO.kandinskyOutputToFile(gen)
            await interaction.guild.get_channel(interaction.channel_id).send(
                f"Генерация `{self.prompt}` по запросу {self.character_registerer.name} завершена!\nСохраните в личке с этим ботом это изображение и используйте его ссылку в качестве арта. Если изображение вас не устраивает, создайте новое с помощью `{Data.preffix}кандинский {self.prompt}`!",
                file=file)
            await interaction.response.edit_message(content="Генерация завершена!", view=None)
        else:
            await interaction.guild.get_channel(interaction.channel_id).send("Ошибка генерации!")

        self.stop()

    @discord.ui.button(label="Отмена", style=discord.ButtonStyle.red)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Отменено.", view=None)

        self.stop()


class RemoveCharView(discord.ui.View):
    def __init__(self, author, id, timeout=180):
        super().__init__(timeout=timeout)
        self.author = author
        self.id = id

    @discord.ui.button(label="Удалить", row=0, style=discord.ButtonStyle.danger, emoji="🚮")
    async def first_button_callback(self, button, interaction):
        db.characters.delete_one({"id": self.id})
        await interaction.response.send_message(f"Удалён персонаж ``{self.id}``!")
        # self.disable_all_items()
        # await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Отмена", row=0, style=discord.ButtonStyle.green, emoji="⏹")
    async def second_button_callback(self, button, interaction):
        await interaction.response.send_message(f"Удаление персонажа ``{self.id}`` отменено!")
        # self.disable_all_items()
        #
        # await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.author.id


class SelectBlankScheme(discord.ui.View):

    @discord.ui.select(  # the decorator that lets you specify the properties of the select menu
        placeholder="Choose a Flavor!",  # the placeholder text that will be displayed if nothing is selected
        min_values=1,  # the minimum number of values that must be selected by the users
        max_values=1,  # the maximum number of values that can be selected by the users
        options=[  # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="ATK 3",
                description=""
            ),
            discord.SelectOption(
                label="Список макетов",
                description="Даёт список макетов."
            ),
            discord.SelectOption(
                label="Руины",
                description=""
            )
        ]
    )
    async def select_callback(self, select,
                              interaction):  # the function called when the user is done selecting options
        # await interaction.response.send_message(f"Awesome! I like {select.values[0]} too!")
        if select.values[0] == "Список макетов":
            embed = discord.Embed(title="Список макетов анкет", description="Список макетов", colour=0xffffff)
            embed.add_field(name="АТК", value='''1. Имя, фамилия и отчество персонажа (второе и тем более третье по желанию)
Возраст, телосложение, рост, вес, родной мир
Способности
Слабости
Характер
Инвентарь
Биография
Внешность. Можно с артом.
Сокращённая версия. Не обязательно, для маленьких анкет не нужно, для больших настоятельно рекомендуется.''',
                            inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)


class RP(commands.Cog):
    result = db.countries.find({}, {"id": 1})  # Получение всех значений из коллекции "countries"
    choicesEditWPG = [str(value["id"]) for value in
                      result]  # Преобразование значений в формат, который можно передать в choices аргумент

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="двадцатигранник", description="Бросить двадцатигранник удачи")
    async def dice(self, ctx, user: Option(discord.Member, description="Пользователь, от имени которого идёт бросок",
                                           required=False) = None):
        author = user if user else ctx.author
        user_data = db.users.find_one({"userid": author.id})
        if user_data:
            karma = user_data.get("karma", 0)
            luck = user_data.get("luck", 0)
        else:
            # db.users.insert_one({"userid": author.id, "karma": 0, "luck": 0})
            Data.writeUserToDB(ctx.author.id, ctx.author.name)
            karma = 0
            luck = 0

        def makeThrow():
            def genRandom():
                o = randint(1, 20) + luck
                if o > 20:
                    o = 20
                if o < 1:
                    o = 1
                return o

            out = genRandom()

            if karma < -1 and out > 10:
                out = genRandom()
            if karma > 1 and out < 10:
                out = genRandom()
            return out

        await ctx.respond(f"На двадцатиграннике выпало {makeThrow()}")

    @commands.slash_command(name="регистрация-впи", description="Зарегистрировать анкету ВПИ")
    async def WPG_reg(self, ctx, country_name: Option(str, description="Имя страны", required=True) = "Unkown",
                      government: Option(str, description="Форма правления", required=True) = "Unkown",
                      ideology: Option(str, description="Идеология", required=True) = "Unkown",
                      currency: Option(str, description="Валюта страны. Желательно с символом", required=True) = "None",
                      about: Option(str, description="Описание страны", required=True) = "None",
                      flag_url: Option(str, description="URL флага",
                                       required=True) = "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                      other_symbols: Option(str, description="Прочая символика страны", required=True) = "None",
                      ownerdata: Option(str, description="Описание персонажа", required=True) = "None",
                      id: Option(str, description="ID страны.", required=True) = "None",
                      user: Option(discord.Member, description="Пользователь", required=True) = None

                      ):
        with ctx.typing():
            if ctx.author.id in Data.WPG_whitelist:
                if user is None:
                    user = ctx.author
                await ctx.respond(f"Запись страны {country_name}...")
                userid = user.id
                db.countries.insert_one({
                    "userid": userid,
                    "countryname": country_name,
                    "government": government,
                    "ideology": ideology,
                    "currency": currency,
                    "about": about,
                    "flagURL": flag_url,
                    "extraSymbols": other_symbols,
                    "ownerdata": ownerdata,
                    "id": id
                })

                await ctx.respond(f"Страна ``{country_name}`` пользователя <@{userid}> записана с ID ``{id}``!")
            else:
                whitelisted_user_name = " "

                await ctx.respond(
                    f"Вы не можете регистрировать страны. Попросите кого-нибудь из тех, кто может это сделать, например, <@0000000000000000000>")

    @commands.slash_command(name="удаление-анкеты-впи", description="Удалить анкету ВПИ")
    async def WPG_unreg(self, ctx,
                        id: Option(str, description="ID страны.", required=True) = "None",

                        ):
        with ctx.typing():
            if ctx.author.id in Data.WPG_whitelist:
                db.countries.delete_one({"id": id})
                await ctx.respond(f"Страна {id} удалена!")
            else:
                whitelisted_user_name = " "

                await ctx.respond(
                    f"Вы не можете удалять страны. Попросите кого-нибудь из тех, кто может это сделать, например, <@{random.choice(Data.WPG_whitelist)}>")

    @commands.slash_command(name="редактировать-впи-статы", description="Редактирует статы ВПИ государства")
    async def editWPGStats(self, ctx,
                           id: Option(str, description="ID государства", choices=choicesEditWPG,
                                      required=True) = "None",
                           field: Option(str, description="Поле редактирования", required=True, choices=[
                               "деньги", "популяция", "согласие населения", "территория", "инфраструктура", "медицина",
                               "образование",
                               "защита", "атака", "топливо", "космическое топливо", "межзвёздное топливо",
                               "пустотное топливо", "транспорт", "индекс технологий", "еда", "материалы"

                           ]) = "None",
                           value: Option(int, description="Значение на которое изменить (отрицательное для вычитания)",
                                         required=True) = 0,
                           ephemeral: Option(bool, description="Видно лишь вам или нет", required=False) = False):

        if ctx.author.id in Data.WPG_whitelist:
            with ctx.typing():
                column = ""
                if field == "деньги":
                    column = "money"
                elif field == "популяция":
                    column = "population"
                elif field == "согласие населения":
                    column = "agreement"
                elif field == "территория":
                    column = "area"
                elif field == "инфраструктура":
                    column = "infrastructure"
                elif field == "медицина":
                    column = "medicine"
                elif field == "образование":
                    column = "eudication"
                elif field == "защита":
                    column = "armor"
                elif field == "атака":
                    column = "attack"
                elif field == "топливо":
                    column = "fuel"
                elif field == "космическое топливо":
                    column = "fuel_space"
                elif field == "межзвёздное топливо":
                    column = "fuel_star"
                elif field == "пустотное топливо":
                    column = "fuel_void"
                elif field == "транспорт":
                    column = "transport"
                elif field == "индекс технологий":
                    column = "tech_index"
                elif field == "еда":
                    column = "food"
                elif field == "материалы":
                    column = "materials"
                db.countries.update_one({"id": id}, {"$inc": {column: value}})
                await ctx.respond(f"Значение ``{field}`` у государства ``{id}`` изменено на {value} едениц(у/ы).",
                                  ephemeral=ephemeral)




        else:
            await ctx.respond(
                f"Вы не можете удалять страны. Попросите кого-нибудь из тех, кто может это сделать, например, <@{random.choice(Data.WPG_whitelist)}>",
                ephemeral=ephemeral)

    choisesWPGButWithList = choicesEditWPG
    choisesWPGButWithList.append("list")

    @commands.slash_command(name="статы-впи", description="Статистика ВПИ государства")
    async def WPG_stats(self, ctx, id: Option(str, description="ID государства. Не вводите для списка",
                                              choices=choisesWPGButWithList, required=True) = "list",
                        size: Option(int, description="Масштабирование", required=False, choices=[1, 2, 3, 4, 5]) = 1,
                        ephemeral: Option(bool, description="Видно лишь вам или нет", required=False) = False):
        with ctx.typing():

            if id == "list":
                # Получение результатов
                results = db.countries.find({}, {"userid": 1, "id": 1, "countryname": 1})
                out = ""
                # Вывод результатов
                for row in results:
                    userid = row["userid"]
                    id = row["id"]
                    countryname = row["countryname"]
                    out += f"страна: **{countryname}** (ID: ``{id}``)  принадлежит <@{userid}> \n"
                embed = discord.Embed(title="Страны", description="Все страны, их владельцы и ID стран",
                                      color=discord.Color.orange())
                embed.add_field(name="Список стран", value=f"{out}", inline=False)
                embed.set_footer(text="Для статов страны введите эту же команду, но указав ID страны")

                await ctx.respond(embed=embed, ephemeral=ephemeral)
            else:
                columns = 17
                imageSizeY = 200
                imageSizeX = columns * 16 + columns * 8 + 16 + 64
                image = Image.new('RGBA', (imageSizeX, imageSizeY), (0, 0, 0, 0))
                bgTileSizeX = 32
                bgTileSizeY = 32
                cell0 = Image.open("graphics/cell.png")

                backgrounds = [None, None, None, None, None]

                cells = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
                for i in range(16):
                    cells[i] = Image.open(f"graphics/cell{i}.png")

                for i in range(5):
                    backgrounds[i] = Image.open(f"graphics/background{i + 1}.png")
                agreement = Image.open("graphics/agreement.png")
                area = Image.open("graphics/area.png")
                armor = Image.open("graphics/armor.png")
                attack = Image.open("graphics/attack.png")

                eudication = Image.open("graphics/eudication.png")
                fuel = Image.open("graphics/fuel.png")
                fuel_space = Image.open("graphics/fuel_space.png")
                fuel_star = Image.open("graphics/fuel_star.png")
                fuel_void = Image.open("graphics/fuel_void.png")
                infrastructure = Image.open("graphics/infrastructure.png")
                medicine = Image.open("graphics/medicine.png")
                money = Image.open("graphics/money.png")
                population = Image.open("graphics/population.png")
                tech = Image.open("graphics/tech.png")
                transport = Image.open("graphics/transport.png")
                materials = Image.open("graphics/materials.png")
                food = Image.open("graphics/food.png")

                result = db.countries.find_one({"id": id}, {"money": 1, "population": 1, "agreement": 1, "area": 1,
                                                            "infrastructure": 1, "medicine": 1, "eudication": 1,
                                                            "attack": 1, "armor": 1, "fuel": 1, "fuel_space": 1,
                                                            "fuel_star": 1, "fuel_void": 1, "transport": 1,
                                                            "tech_index": 1, "materials": 1, "food": 1})

                if result:
                    _money = result.get("money")
                    _population = result.get("population")
                    _agreement = result.get("agreement")
                    _area = result.get("area")
                    _infrastructure = result.get("infrastructure")
                    _medicine = result.get("medicine")
                    _eudication = result.get("eudication")
                    _attack = result.get("attack")
                    _armor = result.get("armor")
                    _fuel = result.get("fuel")
                    _fuel_space = result.get("fuel_space")
                    _fuel_star = result.get("fuel_star")
                    _fuel_void = result.get("fuel_void")
                    _transport = result.get("transport")
                    _tech_index = result.get("tech_index")
                    _materials = result.get("materials")
                    _food = result.get("food")
                arrVal = 0
                if _tech_index / 10 < 5:
                    arrVal = int(_tech_index / 10)
                else:
                    arrVal = 4
                for y in range(int(imageSizeY / bgTileSizeY)):
                    for x in range(int(imageSizeX / bgTileSizeX)):
                        image.paste(backgrounds[arrVal], (x * bgTileSizeX, y * bgTileSizeY))

                def drawBar(barIndex, barPoints, barImage):
                    layersFull = (barPoints // 10)
                    layersNotFull = barPoints % 10
                    posX = (barIndex * 16) + 16 + (8 * barIndex - 1)

                    for i in range(10):
                        image.paste(cells[layersFull], (posX, utils.invertY((i * 8) + 16, imageSizeY)))
                    for i in range(layersNotFull):
                        image.paste(cells[layersFull + 1], (posX, utils.invertY((i * 8) + 16, imageSizeY)))

                    image.paste(barImage, (posX, utils.invertY((10 * 8) + 16 + 16, imageSizeY)))

                # drawBar(1, 11, money)
                # drawBar(2, 9, money)
                drawBar(1, _money, money)
                drawBar(2, _materials, materials)
                drawBar(3, _food, food)
                drawBar(4, _population, population)
                drawBar(5, _agreement, agreement)
                drawBar(6, _area, area)
                drawBar(7, _infrastructure, infrastructure)
                drawBar(8, _medicine, medicine)
                drawBar(9, _eudication, eudication)
                drawBar(10, _attack, attack)
                drawBar(11, _armor, armor)
                drawBar(12, _fuel, fuel)
                drawBar(13, _fuel_space, fuel_space)
                drawBar(14, _fuel_star, fuel_star)
                drawBar(15, _fuel_void, fuel_void)
                drawBar(16, _transport, transport)
                drawBar(17, _tech_index, tech)

                if size > 1:
                    image = image.resize((imageSizeX * size, imageSizeY * size), resample=Image.NEAREST)
                image.save('image_buffer.png')

                modified_image_path = 'image_buffer.png'
                modified_image = discord.File(modified_image_path, filename='image_buffer.png')
                await ctx.respond(file=modified_image, ephemeral=ephemeral)
                # barPoints = 9
                # await ctx.send(f"layersFull: {(barPoints//10)}, layersNotFull: {barPoints%10} при barPoints: {barPoints}")
                # barPoints = 11
                # await ctx.send(
                #     f"layersFull: {(barPoints // 10)}, layersNotFull: {barPoints % 10} при barPoints: {barPoints}")

    def makeCharacterPage(self, doc):
        embed = discord.Embed(title=f"Персонаж {utils.formatStringLength(doc['name'], 120)}",
                              description=f"{utils.formatStringLength(doc['bio'], 4000)}",
                              colour=Data.embedColors["Warp"])
        embed.add_field(name="Данные", value=f"Автор: <@{doc['owner']}>\nID: ``{doc['id']}``", inline=False)
        embed.add_field(name="Рост, вес, возраст, мир", value=f"{doc['bodystats']}\n{doc['age']} лет",
                        inline=False)
        embed.add_field(name="Способности", value=f"{utils.formatStringLength(doc['abilities'], 1024)}",
                        inline=False)
        embed.add_field(name="Слабости", value=f"{utils.formatStringLength(doc['weaknesses'], 1024)}", inline=False)
        embed.add_field(name="Характер", value=f"{utils.formatStringLength(doc['character'], 1024)}", inline=False)
        embed.add_field(name="Инвентарь", value=f"{utils.formatStringLength(doc['inventory'], 1024)}", inline=False)
        embed.add_field(name="Внешность", value=f"{utils.formatStringLength(doc['appearances'], 1024)}",
                        inline=False)
        embed.add_field(name="Краткий пересказ", value=f"{utils.formatStringLength(doc['shortened'], 1024)}",
                        inline=False)
        arts = str(doc['art']).split(" ")
        thumb = arts[0]

        arts_extra = arts[1:]

        embed.set_thumbnail(url=thumb)
        return (embed, arts_extra)

    async def urls2files(self, urls):
        attachment_urls = urls[:10]
        files = []

        for url in attachment_urls:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        ...
                    data = io.BytesIO(await resp.read())
                    files.append(discord.File(data, f'image.png'))
        return files

    @commands.slash_command(name="регистрация-рп", description="Регистрация РП персонажа. Макс. 2к символов/поле")
    async def registerChar(self, ctx, name: Option(str, description="Имя", required=True) = " ",
                           bodystats: Option(str, description="Вес", required=True) = " ",
                           age: Option(float, description="Возраст (в годах)", required=True) = 0,
                           abilities: Option(str, description="Способности", required=True) = " ",
                           weaknesses: Option(str, description="Слабости", required=True) = " ",
                           character: Option(str, description="Характер", required=True) = " ",
                           inventory: Option(str, description="Инвентарь", required=True) = " ",
                           bio: Option(str, description="Биография. Макс. 4к символов", required=True) = " ",
                           appearances: Option(str, description="Внешность", required=True) = " ",
                           art: Option(str, description="Арт (URL)",
                                       required=False) = "https://media.discordapp.net/attachments/1018886769619505212/1176561157939662978/ad643992b38e34e2.png",
                           shortened: Option(str, description="Сокращённый пересказ", required=True) = " ",
                           id: Option(str, description="ID", required=True) = " ",
                           owner: Option(discord.Member, description="Владелец персонажа", required=True) = 0):
        doc = {
            "name": name, "bodystats": bodystats, "age": age,
            "abilities": abilities, "weaknesses": weaknesses,
            "character": character, "inventory": inventory, "bio": bio,
            "appearances": appearances, "art": art, "shortened": shortened, "id": id,
            "owner": owner.id}
        sizeLimit = False
        oversizeKey = ""
        for k, v in doc.items():
            # if (len(str(v)) > 2000 and k!="bio") or (len(str(v)) > 4000 and k=="bio"):
            #     oversizeKey=k
            #     sizeLimit = True
            #     break
            if not "http" in art:
                oversizeKey = "Неверная ссылка! Она должна начинаться на http(s)://"
                sizeLimit = True
                break
        if db.characters.find_one({"id": id}):
            embed = discord.Embed(title="Конфликт имён!", description=f"ID {id} занят другой анкетой!",
                                  colour=Data.embedColors["Error"])
            await ctx.respond(embed=embed)
        else:
            if (await Data.parsePermissionFromUser(ctx.author.id,
                                                   "edit_characters") or await Data.parsePermissionFromUser(
                ctx.author.id, "root")):  # TODO: оптимизировать поиск прав
                if not sizeLimit:
                    db.characters.insert_one(doc)
                    embed = discord.Embed(title="Персонаж зарегистрирован!",
                                          description=f"{name} зарегистрирован как ``{id}`` и принадлежит <@{owner.id}>\nТак же начислено 25 едениц опыта.",
                                          colour=Data.embedColors["Success"])
                    await ctx.respond(embed=embed)
                    await Data.addXP(ctx.author.id, 25, ctx.author.name)
                    await Data.addXP(owner.id, 25, owner.name)
                    if art == "https://media.discordapp.net/attachments/1018886769619505212/1176561157939662978/ad643992b38e34e2.png":
                        view = ConfirmGenArt(ctx.author, appearances)
                        await ctx.respond(f"Ой, вы не указали арт! Как же жаль! Ну ничего, это можно исправить!\n"
                                          f"Запустить генерацию запроса с помощью нейросети Кандинский (запустить генерацию заново можно будет через {Data.preffix}кандинский)?\n"
                                          f"Запрос: **`{appearances}`**", view=view)

                else:
                    embed = discord.Embed(title="Превышение размера или неверная ссылка!",
                                          description=f"Ключ: {oversizeKey}",
                                          colour=Data.embedColors["Error"])
                    await ctx.respond(embed=embed)
            else:
                embed = discord.Embed(title="Нет прав!",
                                      description="Необходимо право ``edit_characters`` или ``root`` для регистрации персонажа!",
                                      colour=Data.embedColors["Error"])
                await ctx.respond(embed=embed)

    @commands.slash_command(name="персонаж", description="Открывает анкету персонажа по ID")
    async def inspectChar(self, ctx, id: Option(str, description="ID", required=True) = " ",
                          ephemeral: Option(bool, description="Видно только вам?", required=False) = False):
        result = db.characters.find_one({"id": id})
        if not result:

            await ctx.respond(f"Персонаж ``{id}`` не найден!")
        else:
            page = self.makeCharacterPage(result)
            await ctx.respond(embed=page[0], ephemeral=ephemeral, files=await self.urls2files(page[1]))
            # TODO: поиск анкет

    @commands.slash_command(name="поиск-персонажей-пользователя",
                            description="Ищет зарегистрированных на пользователя персонажей.")
    async def searchChar(self, ctx,
                         member: Option(discord.Member, description="У кого искать персонажей", required=True) = 0,
                         ephemeral: Option(bool, description="Видно ли только вам", required=False) = True):

        documents = db.characters.find({"owner": member.id}, {"name": 1, "id": 1})

        # result = []
        #
        # for doc in documents:
        #     result.append((doc["name"], doc["id"]))

        output = ""

        for doc in documents:
            output += f"- **[{doc['name']}](https://glitchdev.ru/character/{doc['id']})** {'| (***__НА ПРОВЕРКЕ__***) ' if str(doc['id']).endswith('$temp') else ''}| **ID**: ``{doc['id']}``\n"
        if len(output) < 1:
            output = "Нет персонажей"
        embed = discord.Embed(title="Результаты поиска",
                              description=f"Персонажи пользователя <@{member.id}>:\n{output}",
                              colour=Data.embedColors["Neutral"])
        await ctx.respond(embed=embed, ephemeral=ephemeral)

    @commands.slash_command(name="редактировать-анкету-рп", description="РЕДАКТИРУЕТ анкету персонажа")
    async def editCharacter(self, ctx, field: Option(str, description="Поле",
                                                     choices=["name", "bio", "bodystats", "abilities", "weaknesses",
                                                              'character', 'inventory', 'appearances', 'shortened',
                                                              'art'], required=True) = "",
                            value: Option(str, description="Значение", required=True) = " ",
                            mode: Option(str, description="Режим редактирования", required=True,
                                         choices=["Добавить в конец", "Заменить", "Добавить к началу"]) = " ",
                            id: Option(str, description="ID", required=True) = " "
                            ):
        doc = db.characters.find_one({"id": id})
        if not doc:
            embed = discord.Embed(title="Ошибка!", description="Анкета не найдена!", colour=Data.embedColors["Error"])
            await ctx.respond(embed=embed)
            return
        if not (await Data.parsePermissionFromUser(ctx.author.id,
                                                   "edit_characters") or await Data.parsePermissionFromUser(
            ctx.author.id, "root")):  # TODO: оптимизировать поиск прав
            embed = discord.Embed(title="Нет прав!",
                                  description="Необходимо право ``edit_characters`` или ``root`` для изменения персонажа!",
                                  colour=Data.embedColors["Error"])
            await ctx.respond(embed=embed)
            return
        doc_field = doc[field]
        if mode == "Заменить":
            doc[field] = value
        elif mode == "Добавить в конец":
            doc[field] = doc_field + value
        else:
            doc[field] = value + doc_field
        db.characters.update_one({"id": id}, {"$set": doc})
        embed = discord.Embed(title="Успешно!",
                              description=f"Редактирование поля `{field}` с режимом **`{mode}`** произведено успешно!",
                              colour=Data.embedColors["Success"])
        await ctx.respond(embed=embed)

    @commands.slash_command(name="удалить-персонажа", description="Удаляет персонажа")
    async def removeChar(self, ctx, id: Option(str, description="ID", required=True) = " "):
        if await Data.parsePermissionFromUser(ctx.author.id, "root") or await Data.parsePermissionFromUser(
                ctx.author.id, "edit_characters"):
            # view = RemoveCharView(ctx.author, id)  # or ctx.author/message.author where applicable
            # await ctx.response.send_message(view=view)
            db.characters.delete_one({"id": id})
            await ctx.respond(f"Удалён персонаж ``{id}``!")
        else:
            await ctx.respond("У Вас нет права ``root`` или ``edit_characters`` для удаления персонажей!",
                              ephemeral=True)

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.message_command(name="Обработать анкету персонажа")
    async def parse_blank(self, ctx, message):

        if len(message.attachments) > 0:
            # Проверяем каждое вложение в сообщении
            found = False
            for attachment in message.attachments:

                if re.match(r'blank.*\.json', attachment.filename):
                    found = True
                    # Читаем содержимое файла в виде строки
                    file_contents = await attachment.read()

                    # Преобразуем содержимое в объект JSON

                    try:
                        blank_data = json.loads((await attachment.read()).decode("utf-8"))
                        # Здесь blank_data будет объектом JSON с полями {"field1":1, "field2":"a", "aaa":["", ""]}
                        # Дальнейшая работа с данными
                        # ...
                        if db.characters.find_one({"id": str(blank_data["id"])}):

                            embed = discord.Embed(title="Персонаж уже зарегестрирован!",
                                                  description=f"ID {str(blank_data['id'])} уже занят одобренной анкетой!",
                                                  colour=Data.embedColors["Error"])
                            await ctx.respond(embed=embed)
                        elif db.characters.find_one({"id": str(blank_data["id"]) + "$temp"}):
                            embed = discord.Embed(title="Персонаж уже на рассмотрении!",
                                                  description=f"ID {str(blank_data['id']) + '$temp'} уже занят анкетой на рассмотрении!",
                                                  colour=Data.embedColors["Error"])
                            await ctx.respond(embed=embed)
                        else:
                            id = str(blank_data["id"]) + "$temp"
                            try:
                                age = float(blank_data["age"])
                            except:
                                await ctx.respond("Неверное значение возраста!")
                                return
                            doc = {
                                "name": blank_data["name"], "bodystats": blank_data["bodystats"], "age": age,
                                "abilities": blank_data["abilities"], "weaknesses": blank_data["weaknesses"],
                                "character": blank_data["character"], "inventory": blank_data["inventory"],
                                "bio": blank_data["bio"],
                                "appearances": blank_data["appearances"],
                                "art": blank_data["art"] if blank_data["art"] and blank_data["art"] != "" and str(
                                    blank_data["art"]).startswith("http") and blank_data[
                                                                "art"] != " " else "https://media.discordapp.net/attachments/1018886769619505212/1176561157939662978/ad643992b38e34e2.png",
                                "shortened": blank_data["shortened"], "id": str(blank_data["id"]) + "$temp",
                                "owner": ctx.author.id}
                            for k in doc.keys():
                                if not doc[k] or doc[k] == "":
                                    doc[k] = " "
                            # print(doc)
                            embed = discord.Embed(title=f"Персонаж {utils.formatStringLength(doc['name'], 120)}",
                                                  description=f"{utils.formatStringLength(doc['bio'], 4000)}",
                                                  colour=Data.embedColors["Warp"])
                            embed.add_field(name="Данные", value=f"Автор: <@{doc['owner']}>\nID: ``{id}``",
                                            inline=False)
                            embed.add_field(name="Рост, вес, возраст, мир",
                                            value=f"{doc['bodystats']}\n{doc['age']} лет", inline=False)
                            embed.add_field(name="Способности",
                                            value=f"{utils.formatStringLength(doc['abilities'], 1024)}",
                                            inline=False)
                            embed.add_field(name="Слабости",
                                            value=f"{utils.formatStringLength(doc['weaknesses'], 1024)}",
                                            inline=False)
                            embed.add_field(name="Характер",
                                            value=f"{utils.formatStringLength(doc['character'], 1024)}",
                                            inline=False)
                            embed.add_field(name="Инвентарь",
                                            value=f"{utils.formatStringLength(doc['inventory'], 1024)}",
                                            inline=False)
                            embed.add_field(name="Внешность",
                                            value=f"{utils.formatStringLength(doc['appearances'], 1024)}",
                                            inline=False)
                            embed.add_field(name="Краткий пересказ",
                                            value=f"{utils.formatStringLength(doc['shortened'], 1024)}",
                                            inline=False)
                            embed.set_thumbnail(url=doc['art'])
                            await ctx.respond(embed=embed)
                            server = self.bot.get_guild(Data.team_server_id)
                            if server is None:
                                found = False
                            else:
                                channel = server.get_channel(Data.blanks_moderation_channel_id)
                                message = f"# Новая заявка на регистрацию!!!\nСервер: {ctx.guild.name} (`{ctx.guild.id}`)\nПользователь: {ctx.author.name} (`{ctx.author.id}`)\nКанал: {ctx.channel.name} (`{ctx.channel.id}`)"

                                await channel.send(message, embed=embed)
                            db.characters.insert_one(doc)


                    except json.JSONDecodeError:
                        await ctx.respond(f"Невозможно считать содержимое файла {attachment.filename}!")
                    break
                if not found:
                    await ctx.respond(
                        "Вложение не найдено!\nУчтите, что вложение должно быть названо blank.json! (допустимы символы между blank и .json)!")
        else:
            await ctx.respond("Вложения не найдены!")

    @commands.slash_command(name="одобрить-регистрацию-рп", description="Одобряет регистрацию рп персонажа")
    async def approve_registration(self, ctx, id: Option(str, description="ID персонажа (можно без $temp, можно с ним)",
                                                         required=True) = " "):
        hasTemp = str(id).endswith("$temp")
        if hasTemp:
            id_temp = id
            id_notemp = str(id)[:-5]
        else:
            id_temp = id + "$temp"
            id_notemp = id
        if db.characters.find_one({"id": id_temp}):
            if (await Data.parsePermissionFromUser(ctx.author.id,
                                                   "edit_characters") or await Data.parsePermissionFromUser(
                ctx.author.id, "root")):  # TODO: оптимизировать поиск прав

                db.characters.update_one({"id": id_temp}, {"$set": {"id": id_notemp}})
                embed = discord.Embed(title="Успешно!", description=f"Успешно одобрена анкета ``{id_temp}``!",
                                      colour=Data.embedColors["Success"])
                await ctx.respond(embed=embed)

            else:
                embed = discord.Embed(title="Нет прав!",
                                      description="Необходимо право ``edit_characters`` или ``root`` для подтверждения регистрации персонажа!",
                                      colour=Data.embedColors["Error"])
                await ctx.respond(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title="Не найдено!",
                                  description=f"Неподтверждённая анкета с ID ``{id_temp}`` не найдена!",
                                  colour=Data.embedColors["Error"])
            await ctx.respond(embed=embed,
                              ephemeral=True)  # TODO: добавить "искромётную" шутку в сообщение об ненайденной анкете: "... да и к тому же у вас нет прав для этого действия!"

    @commands.slash_command(name="отклонить-регистрацию-рп", description="Отклоняет регистрацию рп персонажа")
    async def reject_registration(self, ctx, id: Option(str, description="ID персонажа (можно без $temp, можно с ним)",
                                                        required=True) = " "):
        hasTemp = str(id).endswith("$temp")
        if hasTemp:
            id_temp = id
            id_notemp = str(id)[:-5]
        else:
            id_temp = id + "$temp"
            id_notemp = id
        if db.characters.find_one({"id": id_temp}):

            if (await Data.parsePermissionFromUser(ctx.author.id,
                                                   "edit_characters") or await Data.parsePermissionFromUser(
                ctx.author.id, "root")):  # TODO: оптимизировать поиск прав

                db.characters.delete_one({"id": id_temp})
                embed = discord.Embed(title="Успешно!", description=f"Успешно отклонена анкета ``{id_temp}``!",
                                      colour=Data.embedColors["Success"])
                await ctx.respond(embed=embed)

            else:
                embed = discord.Embed(title="Нет прав!",
                                      description="Необходимо право ``edit_characters`` или ``root`` для отклонения регистрации персонажа!",
                                      colour=Data.embedColors["Error"])
                await ctx.respond(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title="Не найдено!",
                                  description=f"Неподтверждённая анкета с ID ``{id_temp}`` не найдена!",
                                  colour=Data.embedColors["Error"])
            await ctx.respond(embed=embed,
                              ephemeral=True)  # TODO: добавить "искромётную" шутку в сообщение об ненайденной анкете: "... да и к тому же у вас нет прав для этого действия!"

    existing_fields = ["name", "bio", "bodystats", "abilities", "weaknesses",
                       'character', 'inventory', 'appearances', 'shortened',
                       'any']

    @commands.slash_command(name="поиск-персонажей", description="Ищет персонажей по запросу")
    async def advancedSearch(self, ctx, field: Option(str, description="Поле. По умолчанию любое",
                                                      choices=["name", "bio", "bodystats", "abilities", "weaknesses",
                                                               'character', 'inventory', 'appearances', 'shortened',
                                                               'any'], required=False) = "any",
                             query: Option(str, description="Поисковый запрос.", required=True) = "банан",
                             use_regex: Option(bool, description="Использовать запрос Regex", required=False) = False,
                             ephemeral: Option(bool, description="Видно ли только Вам? По умолчанию нет.",
                                               required=False) = False):
        embed = discord.Embed(title="Результаты поиска:",
                              description=f"Поле: `{field}`, использование Regex: **{use_regex}**\nЗапрос: `{query}`",
                              colour=Data.embedColors["Success"])
        field = field.lower()
        query = re.escape(query) if use_regex else re.escape(query.lower())

        if field not in self.existing_fields:
            await ctx.send("Неверное поле")
            return

        query_dict = {field: {'$regex': query, '$options': 'i'}} if field != 'any' else {
            '$or': [{key: {'$regex': query, '$options': 'i'}} for key in self.existing_fields[:-1]]}

        results = db.characters.find(query_dict).sort('id', pymongo.ASCENDING).limit(10)

        output = []
        for idx, result in enumerate(results):
            matched_fields = ""
            for key, value in result.items():
                match = re.search(query, str(value), re.IGNORECASE)
                if match:
                    start_idx = max(match.start() - 40, 0)
                    end_idx = min(match.end() + 40, len(value))
                    highlighted_value = f"...{value[start_idx:match.start()]}**{match.group()}**{value[match.end():end_idx]}..."
                    matched_fields += (f"`{key}`: {highlighted_value}\n")

            num_matches = len(matched_fields)
            output.append(f"{idx + 1}. ID: {result.get('id')} - Matches: {num_matches}\n" + "\n".join(matched_fields))
            embed.add_field(name=f"{result.get('name')}",
                            value=f"ID: `{result.get('id')}`\nСовпадений: {num_matches}\nАвтор: <@{result['owner']}> ({Data.getUserNameByID(result['owner'], ctx)})\n"
                                  f"[Страница на сайте](https://glitchdev.ru/character/{result.get('id')})\n"
                                  f"--> Совпадения <--\n"
                                  f"{matched_fields}", inline=False)
        if len(output) < 1:
            embed.colour = Data.embedColors["Error"]
            embed.add_field(name="Нет совпадений!", value="Ничего не найдено!", inline=False)
        await ctx.respond(embed=embed, ephemeral=ephemeral)

    @commands.slash_command(name="задать-преффикс-персонажа", description="Задаёт преффикс персоны персонажа")
    async def setCharPreffix(self, ctx, prefix: Option(str, description="Преффикс", required=True) = " ",
                             id: Option(str, description="ID персонажа", required=True) = ""):
        doc = db.characters.find_one({"id": id})
        if not doc:
            await ctx.respond("Не найдено!", ephemeral=True)
            return
        if await Data.parsePermissionFromUser(ctx.author.id, "edit_characters") or await Data.parsePermissionFromUser(
                ctx.author.id, "root") or doc["owner"] == ctx.author.id:
            await ctx.respond(f"Преффикс изменён: ``{doc['prefix']}`` -> ``{prefix}``")
            db.characters.update_one({"id": id}, {"$set": {"prefix": prefix}})
        else:
            await ctx.respond("У вас нет права на редактирование персонажей или это не ваш персонаж!", ephemeral=True)

    @commands.Cog.listener("on_message")
    async def interchat_on_message(self, message: discord.Message):
        for doc in db.characters.find({"owner": message.author.id}):
            if not "prefix" in doc.keys():
                return
            if doc["prefix"]:
                if str(message.content).startswith(doc['prefix']):
                    hook = await utils.initWebhook(message.channel, self.bot.user.id)
                    if hook:
                        arts = str(doc['art']).split(" ")
                        havatar = arts[0]
                        hname = doc["name"]
                        content = message.content
                        if content.startswith(doc['prefix']):
                            content = content[len(doc['prefix']):]
                        # if message.reference:
                        #     contentPrefix = f"{message.reference.resolved.content[:30]}...\n" \
                        #                     f""
                        #     if message.reference.resolved.webhook_id:
                        #         ownerdoc = db.characters.find_one({"name":message.reference.resolved.author.name})
                        #         if ownerdoc:
                        #             mention = f" (<@{ownerdoc['owner']}>)"
                        #         else:
                        #             mention = ""
                        #         contentPrefix+=f"{message.reference.resolved.author.name}{mention}"
                        #     else:
                        #         f" (<@{message.reference.resolved.author.id}>)"
                        #     content = f"{contentPrefix}\n{content}"
                        # TODO: референс
                        if len(content) < 1:
                            content = "** **"
                        if isinstance(message.channel, discord.Thread):
                            await hook.send(content=content, username=hname,
                                            avatar_url=havatar,
                                            thread=discord.Object(message.channel.parent_id),
                                            files=[await i.to_file() for i in message.attachments]
                                            )

                        else:
                            await hook.send(content=content, username=hname,
                                            avatar_url=havatar,

                                            files=[await i.to_file() for i in message.attachments]
                                            )
                        await message.delete()
                    break

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.message_command(name="Краткий пересказ анкеты")
    async def summarize(self, ctx, message: discord.Message):

        if len(message.content) < 512:
            await ctx.respond("Сообщение и так короткое, куда ещё короче-то?")
            return
        else:
            # userdoc = d.getUser(ctx.author.id, ctx.author.name)
            # if await Data.parsePermissionFromUser(ctx.author.id, "root") or await Data.parsePermissionFromUser(ctx.author.id, "edit_characters"):
            payload = [{"role": "system",
                        "content": f"Вероятно, это анкета персонажа или её часть. Перескажи текст вкратце, выдели основные моменты."
                        },
                       # Если в ответе ты начинаешь повторять одно и то же, перкрати ответ.
                       {"role": "user", "content": message.content}]
            # print(payload)
            response = await AIIO.askLLM(payload, AIIO.LLMs.GIGACHAT, 3, AIIO.gigachat_temptoken)

            if response == "No token":
                response = await AIIO.askLLM(payload, AIIO.LLMs.GIGACHAT, 3, AIIO.gigachat_temptoken)


            resp = response[0]
            tokens = response[1]['total_tokens']
            tokenInfo = "\n" + f"||Использовано {tokens} токен{'ов' if tokens % 100 in (11, 12, 13, 14, 15) else 'а' if tokens % 10 in (2, 3, 4) else '' if tokens % 10 == 1 else 'ов'}||"
            output = resp + tokenInfo





            outputs = utils.split_string(output, 2000, len(tokenInfo))
            for content in outputs:
                print( "|||", content)

                await ctx.respond(content)
                # print("...")
                #
                # await ctx.send(content)


            # await ctx.respond()
            # else:
            # await ctx.respond("Вы не анкетолог.")


def setup(bot):
    bot.add_cog(RP(bot))
