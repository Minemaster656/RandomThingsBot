import random
import numpy as np
import matplotlib.pyplot as plt
import perlin_noise


# try:
import discord
from discord import Option, Webhook, Forbidden, ButtonStyle
from discord.ext import commands
# except:
#     import pycord as discord
#     from pycord import Option, Webhook, Forbidden, ButtonStyle
#     from discord.ext import commands
from random import *
from PIL import Image
import requests
from io import BytesIO

from discord.ui import Button

import Data
import utils


class MyView(discord.ui.View):  # Create a class called MyView that subclasses discord.ui.View
    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary,
                       emoji="😎")  # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, button, interaction):
        await interaction.response.send_message(
            "You clicked the button!")  # Send a message when the button is clicked


class Tests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.slash_command(name="webhook-test")
    # async def webhook(self, ctx):
    #     await ctx.respond("Trying to create webhook...")
    #     avatar_url = str("https://images-ext-2.discordapp.net/external/-1-6AJKBQh38RYGz6D3j-IgURlKEfFifX5LeJ8h-TBw/%3Fsize%3D4096/https/cdn.discordapp.com/avatars/1126887522690142359/0767783560eee507f86c95a4b09f120a.png?width=437&height=437") #str(self.bot.user.avatar_url)  # ссылка на аватар бота
    #     webhook_name = str("RTBot's webhook")
    #     channel = ctx.channel
    #     webhooks = await channel.webhooks()
    #     webhook = discord.utils.get(webhooks, name=webhook_name)
    #     if webhook is None:
    #         avatar_bytes = requests.get(avatar_url).content
    #         webhook = await channel.create_webhook(name=str(webhook_name), avatar=avatar_bytes)
    #     user = ctx.author
    #     await webhook.send(f'Username: **{user.name}**, server: **{ctx.guild.name}**', username=user.name)#,
    #

    # avatar_url=user.avatar_url)

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

    @commands.slash_command()  # Create a slash command
    async def button(self, ctx):
        await ctx.respond("This is a button!",
                          view=MyView())  # Send a message with our View class that contains the button

    @commands.slash_command(name="тест-форматтера", description="Тестирование форматирования строк",
                            guilds=Data.test_guilds)
    async def test_formatter(self, ctx, text: Option(str, description="Строка", required=True) = " ",
                             length: Option(int, description="Максимальная длина", required=True) = 10):
        embed = discord.Embed(title="Информация о строке", description=f"Длина исходной строки - {len(text)}"
                                                                       f"\nДлина выходной строки - {len(str(utils.formatStringLength(text, length)))}",
                              colour=0xffffff)
        await ctx.respond(utils.formatStringLength(text, length), embed=embed)


def setup(bot):
    bot.add_cog(Tests(bot))
