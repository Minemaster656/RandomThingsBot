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



                      ):
        with ctx.typing():
            await ctx.respond(f"Запись страны {country_name}...")
            userid = ctx.author.id
            cursor.execute("INSERT INTO countries (userid, countryname, government, ideology, currency, about, flagURL, extraSymbols, ownerdata, id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (userid, country_name, government, ideology, currency, about, flag_url, other_symbols, ownerdata, id))
            conn.commit()

            await ctx.send(f"Страна {country_name} пользователя <@{userid}> записана с ID {id}!")
    @commands.slash_command(name="статы-впи",description="Статистика ВПИ государства")
    async def fname(srlf, ctx, id : Option(str, description="ID государства. Не вводите для списка", required=False)="list"):
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

                await ctx.respond(embed=embed)
            else:
                imageSizeY=200
                image = Image.new('RGBA', (300, imageSizeY), (0, 0, 0, 0))

                cell0 = Image.open("graphics/cell.png")
                # # cell0.convert("L")
                # # cell1 = ImageOps.colorize(cell0, '#FF0000', '#000000')
                # cell1 = Image.open("10x10.png")
                # cells = [cell0, cell1]
                cells = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
                for i in range(16):
                    cells[i]=Image.open(f"graphics/cell{i}.png")
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


                def drawBar(barIndex, barPoints, barImage):
                    layersFull = (barPoints//10)
                    layersNotFull = barPoints%10
                    posX = (barIndex*16)+16+(8*barIndex-1)

                    for i in range(10):
                        image.paste(cells[layersFull], (posX, utils.invertY((i*8)+16, imageSizeY)))
                    for i in range(layersNotFull):
                        image.paste(cells[layersFull+1], (posX, utils.invertY((i*8)+16, imageSizeY)))

                    image.paste(barImage, (posX, utils.invertY((10*8)+16+16, imageSizeY)))


                drawBar(1, 11, money)
                drawBar(2, 9, money)


                image.save('image_buffer.png')

                modified_image_path = 'image_buffer.png'
                modified_image = discord.File(modified_image_path, filename='image_buffer.png')
                await ctx.respond(file=modified_image)
                barPoints = 9
                await ctx.send(f"layersFull: {(barPoints//10)}, layersNotFull: {barPoints%10} при barPoints: {barPoints}")
                barPoints = 11
                await ctx.send(
                    f"layersFull: {(barPoints // 10)}, layersNotFull: {barPoints % 10} при barPoints: {barPoints}")
