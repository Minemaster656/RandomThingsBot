import random
import numpy as np
import matplotlib.pyplot as plt
import discord
from discord.ext import commands
import perlin_noise
from discord import Option
from random import *
from PIL import Image
import requests
from io import BytesIO


class Tests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command(aliasses=["шахматы"])
    # async def chessboard(ctx):
    #     def get_image_from_url(url):
    #         response = requests.get(url)
    #         image = Image.open(BytesIO(response.content))
    #         return image
    #
    #     def create_chessboard(user_image):
    #         width, height = user_image.size
    #         chessboard = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    #
    #         for x in range(0, width, width // 5):
    #             for y in range(0, height, height // 5):
    #                 if (x // (width // 5) + y // (height // 5)) % 2 == 0:
    #                     chessboard.paste(user_image, (x, y))
    #
    #         return chessboard
    #     # Получаем прикрепленное изображение от пользователя
    #     attachment = ctx.message.attachments[0]
    #     image_url = attachment.url
    #
    #     # Загружаем изображение пользователя
    #     user_image = await get_image_from_url(image_url)
    #
    #     # Создаем шахматную доску 5 на 5 с чередующимися пикселями
    #     chessboard = create_chessboard(user_image)
    #
    #     # Отправляем шахматную доску в качестве сообщения
    #     await ctx.send(file=discord.File(chessboard, 'chessboard.png'))





