import random
import numpy as np
import matplotlib.pyplot as plt
import discord
from discord.ext import commands
import perlin_noise
from discord import Option, ButtonStyle
from random import *
from PIL import Image
import requests
from io import BytesIO

from discord.ui import Button


class Tests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="webhook-test")
    async def webhook(self, ctx):
        await ctx.respond("Trying to create webhook...")
        avatar_url = str("https://images-ext-2.discordapp.net/external/-1-6AJKBQh38RYGz6D3j-IgURlKEfFifX5LeJ8h-TBw/%3Fsize%3D4096/https/cdn.discordapp.com/avatars/1126887522690142359/0767783560eee507f86c95a4b09f120a.png?width=437&height=437") #str(self.bot.user.avatar_url)  # ссылка на аватар бота
        webhook_name = str("RTBot's webhook")
        channel = ctx.channel
        webhooks = await channel.webhooks()
        webhook = discord.utils.get(webhooks, name=webhook_name)
        if webhook is None:
            avatar_bytes = requests.get(avatar_url).content
            webhook = await channel.create_webhook(name=str(webhook_name), avatar=avatar_bytes)
        user = ctx.author
        await webhook.send(f'Username: **{user.name}**, server: **{ctx.guild.name}**', username=user.name)#,
                           #avatar_url=user.avatar_url)

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






