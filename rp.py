import random
import numpy as np
import matplotlib.pyplot as plt
import discord
from discord.ext import commands
import perlin_noise
from discord import Option
from random import *
import sqlite3

import publicCoreData
import utils
from publicCoreData import cursor
from publicCoreData import conn
from PIL import Image, ImageFilter, ImageDraw, ImageOps


# from main import cursor
# from main import conn


class RP(commands.Cog):
    # choicesEditWPG = []
    cursor.execute('SELECT id FROM countries')

    # Получение всех значений из результата запроса
    result = cursor.fetchall()

    # Преобразование значений в формат, который можно передать в `choices` аргумент
    choicesEditWPG = [str(value[0]) for value in result]
    def __init__(self, bot):
        self.bot = bot



    @commands.slash_command(name="двадцатигранник",description="Бросить двадцатигранник удачи")
    async def dice(self, ctx, user:Option(discord.Member, description="Пользователь, от имени которого идёт бросок", required=False)= None):
        author = user if user else ctx.author
        cursor.execute("SELECT karma, luck FROM users WHERE userid = ?", (author.id,))
        result = cursor.fetchone()
        if result:
            karma = result[0]
            luck = result[1]
        else:
            publicCoreData.writeUserToDB(user)
            karma = 0
            luck = 0



        def makeThrow():
            def genRandom():
                o = randint(1, 20)+luck
                if o > 20:
                    o=20
                if o < 1:
                    o=1
                return o


            out = genRandom()

            if karma < -1 and out > 10:
                out = genRandom()
            if karma > 1 and out < 10:
                out = genRandom()
            return out


        await ctx.respond(f"На двадцатиграннике выпало {makeThrow()}")

    @commands.slash_command(name="регистрация-впи",description="Зарегистрировать анкету ВПИ")
    async def WPG_reg(self, ctx, country_name : Option(str, description="Имя страны", required=True)= "Unkown",
                      government : Option(str, description="Форма правления", required=True)="Unkown",
                      ideology : Option(str, description="Идеология", required=True)="Unkown",
                      currency : Option(str, description="Валюта страны. Желательно с символом", required=True)="None",
                      about : Option(str, description="Описание страны", required=True)="None",
                      flag_url : Option(str, description="URL флага", required=True)= "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                      other_symbols : Option(str, description="Прочая символика страны", required=True)= "None",
                      ownerdata : Option(str, description="Описание персонажа", required=True)="None",
                      id : Option(str, description="ID страны.", required=True)="None",
                      user : Option(discord.Member, description="Пользователь", required=True)=None



                      ):
        with ctx.typing():
            if ctx.author.id in publicCoreData.WPG_whitelist:
                if user is None:
                    user = ctx.author
                await ctx.respond(f"Запись страны {country_name}...")
                userid = user.id
                cursor.execute("INSERT INTO countries (userid, countryname, government, ideology, currency, about, flagURL, extraSymbols, ownerdata, id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (userid, country_name, government, ideology, currency, about, flag_url, other_symbols, ownerdata, id))
                conn.commit()

                await ctx.respond(f"Страна {country_name} пользователя <@{userid}> записана с ID {id}!")
            else:
                whitelisted_user_name = " "

                await ctx.respond(f"Вы не можете регистрировать страны. Попросите кого-нибудь из тех, кто может это сделать, например, <@{random.choice(publicCoreData.WPG_whitelist)}>")

    @commands.slash_command(name="удаление-анкеты-впи", description="Удалить анкету ВПИ")
    async def WPG_unreg(self, ctx,
                      id: Option(str, description="ID страны.", required=True) = "None",

                      ):
        with ctx.typing():
            if ctx.author.id in publicCoreData.WPG_whitelist:
                cursor.execute("DELETE FROM countries WHERE id = ?", (id, ))

                await ctx.respond(f"Страна {id} удалена!")
            else:
                whitelisted_user_name = " "

                await ctx.respond(
                    f"Вы не можете удалять страны. Попросите кого-нибудь из тех, кто может это сделать, например, <@{random.choice(publicCoreData.WPG_whitelist)}>")

    @commands.slash_command(name="редактировать-впи-статы",description="Редактирует статы ВПИ государства")
    async def editWPGStats(self, ctx,
                           id : Option(str, description="ID государства",choices=choicesEditWPG, required=True)="None",
                           field : Option(str, description="Поле редактирования", required=True,choices=[
                               "деньги","популяция","согласие населения","территория","инфраструктура","медицина","образование",
                               "защита","атака","топливо","космическое топливо","межзвёздное топливо","пустотное топливо","транспорт","индекс технологий", "еда","материалы"


                           ])="None", value : Option(int, description="Значение на которое изменить (отрицательное для вычитания)", required=True)=0, ephemeral : Option(bool, description="Видно лишь вам или нет", required=False)=False):

        if ctx.author.id in publicCoreData.WPG_whitelist:
            with ctx.typing():
                column = ""
                if field == "деньги":
                    column="money"
                elif field == "популяция":column="population"
                elif field == "согласие населения":column="agreement"
                elif field == "территория":column="area"
                elif field == "инфраструктура":column="infrastructure"
                elif field == "медицина":column="medicine"
                elif field == "образование":column="eudication"
                elif field == "защита":column="armor"
                elif field == "атака":column="attack"
                elif field == "топливо":column="fuel"
                elif field == "космическое топливо":
                    column = "fuel_space"
                elif field == "межзвёздное топливо": column = "fuel_star"
                elif field == "пустотное топливо": column = "fuel_void"
                elif field == "транспорт":column="transport"
                elif field == "индекс технологий":column="tech_index"
                elif field == "еда":column="food"
                elif field == "материалы":column="materials"
                cursor.execute(f"UPDATE countries SET {column} = {column} + ? WHERE id = ?", (value, id))
                conn.commit()
                await ctx.respond(f"Значение ``{field}`` у государства ``{id}`` изменено на {value} едениц(у/ы).", ephemeral=ephemeral)




        else:
            await ctx.respond(f"Вы не можете удалять страны. Попросите кого-нибудь из тех, кто может это сделать, например, <@{random.choice(publicCoreData.WPG_whitelist)}>", ephemeral=ephemeral)

    choisesWPGButWithList = choicesEditWPG
    choisesWPGButWithList.append("list")
    @commands.slash_command(name="статы-впи",description="Статистика ВПИ государства")
    async def WPG_stats(self, ctx, id : Option(str, description="ID государства. Не вводите для списка",choices=choisesWPGButWithList, required=False)="list", size : Option(int, description="Масштабирование", required=False, choices=[1, 2, 3, 4, 5])=1, ephemeral : Option(bool, description="Видно лишь вам или нет", required=False)=False):
        with ctx.typing():



            if id == "list":
                # Выполнение запроса
                cursor.execute('SELECT userid, id, countryname FROM countries')

                # Получение результатов
                results = cursor.fetchall()
                out=""
                # Вывод результатов
                for row in results:
                    userid, id, countryname = row
                    # print(f'userid: {userid}, id: {id}')
                    out += f"страна: **{countryname}** (ID: ``{id}``)  принадлежит <@{userid}> \n"
                embed = discord.Embed(title="Страны", description="Все страны, их владельцы и ID стран", color=discord.Color.orange())
                embed.add_field(name="Список стран", value=f"{out}", inline=False)
                embed.set_footer(text="Для статов страны введите эту же команду, но указав ID страны")

                await ctx.respond(embed=embed, ephemeral=ephemeral)
            else:
                columns = 17
                imageSizeY=200
                imageSizeX=columns*16+columns*8+16+64
                image = Image.new('RGBA', (imageSizeX, imageSizeY), (0, 0, 0, 0))
                bgTileSizeX=32
                bgTileSizeY=32
                cell0 = Image.open("graphics/cell.png")
                # # cell0.convert("L")
                # # cell1 = ImageOps.colorize(cell0, '#FF0000', '#000000')
                # cell1 = Image.open("10x10.png")
                # cells = [cell0, cell1]
                backgrounds=[None, None, None, None, None]

                cells = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
                for i in range(16):
                    cells[i]=Image.open(f"graphics/cell{i}.png")

                for i in range(5):
                    backgrounds[i]=Image.open(f"graphics/background{i+1}.png")
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
                tech= Image.open("graphics/tech.png")
                transport = Image.open("graphics/transport.png")
                materials = Image.open("graphics/materials.png")
                food = Image.open("graphics/food.png")



                cursor.execute("SELECT money, population, agreement, area, infrastructure, medicine, eudication, attack, armor, fuel, fuel_space, fuel_star, fuel_void, transport, tech_index, materials, food FROM countries WHERE id = ?", (id, ))
                result = cursor.fetchone()
                if result:
                    _money = result[0]
                    _population = result[1]
                    _agreement = result[2]
                    _area = result[3]
                    _infrastructure = result[4]
                    _medicine = result[5]
                    _eudication = result[6]
                    _attack = result[7]
                    _armor = result[8]
                    _fuel = result[9]
                    _fuel_space = result[10]
                    _fuel_star = result[11]
                    _fuel_void = result[12]
                    _transport = result[13]
                    _tech_index = result[14]
                    _materials = result[15]
                    _food=result[16]
                arrVal = 0
                if _tech_index / 10 < 5:
                    arrVal = int(_tech_index / 10)
                else:
                    arrVal=4
                for y in range(int(imageSizeY/bgTileSizeY)):
                    for x in range(int(imageSizeX/bgTileSizeX)):

                        image.paste(backgrounds[arrVal], (x*bgTileSizeX, y*bgTileSizeY))




                def drawBar(barIndex, barPoints, barImage):
                    layersFull = (barPoints//10)
                    layersNotFull = barPoints%10
                    posX = (barIndex*16)+16+(8*barIndex-1)

                    for i in range(10):
                        image.paste(cells[layersFull], (posX, utils.invertY((i*8)+16, imageSizeY)))
                    for i in range(layersNotFull):
                        image.paste(cells[layersFull+1], (posX, utils.invertY((i*8)+16, imageSizeY)))

                    image.paste(barImage, (posX, utils.invertY((10*8)+16+16, imageSizeY)))


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

                if size>1:
                    image = image.resize((imageSizeX*size, imageSizeY*size), resample=Image.NEAREST)
                image.save('image_buffer.png')

                modified_image_path = 'image_buffer.png'
                modified_image = discord.File(modified_image_path, filename='image_buffer.png')
                await ctx.respond(file=modified_image, ephemeral=ephemeral)
                # barPoints = 9
                # await ctx.send(f"layersFull: {(barPoints//10)}, layersNotFull: {barPoints%10} при barPoints: {barPoints}")
                # barPoints = 11
                # await ctx.send(
                #     f"layersFull: {(barPoints // 10)}, layersNotFull: {barPoints % 10} при barPoints: {barPoints}")
