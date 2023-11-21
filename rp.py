import random
# import numpy as np
# import matplotlib.pyplot as plt
import discord
from discord.ext import commands
# import perlin_noise
from discord import Option
from random import *
# import sqlite3

import publicCoreData
import utils

from publicCoreData import db
from PIL import Image, ImageFilter, ImageDraw, ImageOps
import pymongo


# from main import cursor
# from main import conn


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
            db.users.insert_one({"userid": author.id, "karma": 0, "luck": 0})
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
            if ctx.author.id in publicCoreData.WPG_whitelist:
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
            if ctx.author.id in publicCoreData.WPG_whitelist:
                db.countries.delete_one({"id": id})
                await ctx.respond(f"Страна {id} удалена!")
            else:
                whitelisted_user_name = " "

                await ctx.respond(
                    f"Вы не можете удалять страны. Попросите кого-нибудь из тех, кто может это сделать, например, <@{random.choice(publicCoreData.WPG_whitelist)}>")

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

        if ctx.author.id in publicCoreData.WPG_whitelist:
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
                f"Вы не можете удалять страны. Попросите кого-нибудь из тех, кто может это сделать, например, <@{random.choice(publicCoreData.WPG_whitelist)}>",
                ephemeral=ephemeral)

    choisesWPGButWithList = choicesEditWPG
    choisesWPGButWithList.append("list")

    @commands.slash_command(name="статы-впи", description="Статистика ВПИ государства")
    async def WPG_stats(self, ctx, id: Option(str, description="ID государства. Не вводите для списка",
                                              choices=choisesWPGButWithList, required=False) = "list",
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
                           art: Option(str, description="Арт (URL)", required=False) = "https://media.discordapp.net/attachments/1018886769619505212/1176561157939662978/ad643992b38e34e2.png",
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
        for k,v in doc.items():
            if (len(str(v)) > 2000 and k!="bio") or (len(str(v)) > 4000 and k=="bio"):
                oversizeKey=k
                sizeLimit = True
                break
            if not "http" in art:
                oversizeKey = "Неверная ссылка! Она должна начинаться на http(s)://"
                sizeLimit=True
                break
        if (await publicCoreData.parsePermissionFromUser(owner.id, "edit_characters")):
            if not sizeLimit:
                db.characters.insert_one(doc)
                embed = discord.Embed(title="Персонаж зарегистрирован!",description=f"{name} зарегистрирован как ``{id}`` и принадлежит <@{owner.id}>",colour=publicCoreData.embedColors["Success"])
                await ctx.respond(embed=embed)
            else:
                embed = discord.Embed(title="Превышение размера!",description=f"Ключ: {oversizeKey}",colour=publicCoreData.embedColors["Error"])
                await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="Нет прав!",
                                  description="Необходимо право ``edit_characters`` для регистрации персонажа!",
                                  colour=publicCoreData.embedColors["Error"])
            await ctx.respond(embed=embed)
    @commands.slash_command(name="песронаж",description="Открывает анкету персонажа по ID")
    async def inspectChar(self, ctx, id : Option(str, description="ID", required=True)=" ",ephemeral : Option(bool, description="Видно только вам?", required=False)=False):
        result = db.characters.find_one({"id": id})
        if not result:

            await ctx.respond(f"Персонаж ``{id}`` не найден!")
        else:
            embed = discord.Embed(title=f"Персонаж {result['name']}",description=f"{result['bio']}",colour=publicCoreData.embedColors["Warp"])
            embed.add_field(name="Данные",value=f"Автор: <@{result['owner']}>\nID: ``{id}``",inline=False)
            embed.add_field(name="Рост, вес, возраст, мир",value=f"{result['bodystats']}\n{result['age']} лет",inline=False)
            embed.add_field(name="Способности",value=f"{result['abilities']}",inline=False)
            embed.add_field(name="Слабости",value=f"{result['weaknesses']}",inline=False)
            embed.add_field(name="Характер",value=f"{result['character']}",inline=False)
            embed.add_field(name="Инвентарь",value=f"{result['inventory']}",inline=False)
            embed.add_field(name="Внешность",value=f"{result['appearances']}",inline=False)
            embed.add_field(name="Краткий пересказ",value=f"{result['shortened']}",inline=False)
            embed.set_thumbnail(url=result['art'])
            await ctx.respond(embed=embed, ephemeral=ephemeral)
            #TODO: поиск анкет
