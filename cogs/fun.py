import random
import typing

# import numpy as np
# import matplotlib.pyplot as plt

# import perlin_noise

try:
    import discord
    from discord import Option, Webhook, Forbidden
    from discord.ext import commands
except:
    import pycord as discord
    from pycord import Option, Webhook, Forbidden
    from discord.ext import commands

from random import *
import json
import os

import AI
import Data
from Data import db
import d
import utils

import assets.resources.tataroCards as tataro

from PIL import Image, ImageEnhance
import io


class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="залго", description="сделать залго")
    async def makeZalgo(self, ctx, text: Option(str, description="Текст", required=True) = "a",
                        intensity: Option(int, description="Интенсивность", required=False) = 5,
                        ephemeral: Option(bool, description="Видно только Вам", required=False) = True):

        output = utils.zalgo_text(text, intensity)
        embed = discord.Embed(title=f"Zalgo {intensity}", description=f"{output}", colour=0xffffff)
        await ctx.respond(embed=embed, ephemeral=ephemeral)

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name="интерсервер", description="Помечает канал как интерсервер")
    async def interserver(self, ctx,
                          type: Option(str, description="Тип канала. Можно иметь одновременно несколько на сервер.",
                                       choices=Data.interhubs, required=True) = 0,
                          reset: Option(bool, description="True для отчистки поля", required=False) = False):
        channel = ctx.channel
        if await Data.parsePermissionFromUser(ctx.author.id, "root") or (
                await Data.parsePermissionFromUser(ctx.author.id, "verified") and True):  # (
            # ctx.author.permissions.administrator or ctx.author.permissions.manage_channels)):
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
                                if arr['guild'] == ctx.guild.id:
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
                                    if arr['channel'] == channel.id:
                                        json_data[type].pop(i)
                                        break
                                    i += 1
                else:
                    # Добавление элемента в массив, если delete=False
                    json_data[array_name].append(data)
                Data.interchats = json_data
                # Записываем обновленные данные в файл
                with open(file_path, 'w') as file:
                    json.dump(json_data, file)

            isThread = isinstance(channel, discord.Thread)
            if isThread:
                data = {'guild': ctx.guild.id, 'channel': channel.parent_id, 'thread': channel.id}
            else:
                data = {'guild': ctx.guild.id, 'channel': channel.id}
            update_json(data, type, reset)
            found = False
            hooks = await ctx.channel.webhooks() if isinstance(channel,
                                                               discord.TextChannel) else await ctx.channel.parent.webhooks()
            hook_channel = ctx.channel if isinstance(channel, discord.TextChannel) else ctx.channel.parent
            for hook in hooks:
                if hook.user.id == self.bot.user.id:
                    found = True
            if not found:
                await hook_channel.create_webhook(name="RTB hook")
            await ctx.respond("Успешно!", ephemeral=True)
            embed = discord.Embed(title=f"Обновление интерчата",
                                  description=f"В канале {channel.name} {'установлен' if not reset else 'убран'} хаб межсерверного чата `{type}`!",
                                  colour=0xffffff)
            await ctx.respond(embed=embed)
        else:
            await ctx.respond(
                "У Вас недостаточно прав для этого действия!!!\nНеобходима верификация пользователя (в боте, не в Discord) и право управления каналами/администратор",
                ephemeral=True)

    @commands.slash_command(name="ии-художник", description="Отправляет запрос на генерацию изображения")
    async def ai_draw(self, ctx, prompt: Option(str, description="Промпт", required=True) = "Банан",
                      model: Option(str, description="Модель", required=True, choices=["Кандинский 3"]) = ""
                      ):
        if model == "Кандинский 3":
            # AI.Text2ImageAPI.generate(prompt=prompt)
            await ctx.respond("В разработке...")

    REQUEST_CODES = (100, 101, 102, 103,
                     200, 201, 202, 203, 204, 206, 207, 208, 218, 226,
                     300, 301, 302, 303, 304, 305, 306, 307, 308,
                     400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410,
                     411, 412, 413, 414, 415, 416, 417, 418, 420,
                     421, 422, 423, 424, 425, 426, 428, 429, 430,
                     431, 440, 444, 449, 450, 451, 460, 463, 464, 494, 495, 496, 497,
                     498, 499, 500, 501, 502, 503, 504, 506, 507, 508, 509, 510,
                     511, 520, 521, 522, 523, 524, 525, 526, 527, 529, 530, 561, 598, 599, 999)

    @commands.command(aliases=["error", "hstat" "httpstat", "сеть", "код", "статус"],
                      description="command_http_description", help="command_http_examples", brief="command_http_args")
    async def http(self, ctx: commands.Context, status_code: typing.Optional[int] = 200):
        if status_code in self.REQUEST_CODES:
            await ctx.reply(f"https://http.dog/{status_code}.jpg")
        else:
            await ctx.reply("Нет такого кода.")

    # @commands.command(aliases=["бассбуст"])
    # async def bassboost(self, ctx):

    @commands.command(aliases=["таро", "гадание", "карты", "татаро"])
    async def tataro(self, ctx: commands.Context):
        user = d.getUser(ctx.author.id, ctx.author.name)
        updateUserDoc = False
        card = choice(tataro.cards)
        file = None
        if not "image" in card.keys():
            ...
        elif card["image"] == "" or not card["image"]:
            ...
        elif "http" in card["image"]:
            # file = utils.urls2files(card["image"])
            ...
        elif "png" in card["image"] or "jpg" in card["image"]:
            file = discord.File(card["image"], filename='image.png')
        if "code" in card.keys():
            if card["code"] is None or card["code"] == "":
                ...
            else:

                exec(card["code"])  # TODO: убарть ивал

                updateUserDoc = True

                ...
        content = f"# {card['name']}\n" \
                  f"{card['message']}\n" \
                  f"||Предложено **{card['author']}**, качество: *{card['quality']}*, пул: ***{card['rarity_pool']}***||"
        await ctx.reply(content, file=file)
        if "http" in card["image"]:
            await ctx.send(card["image"])

        if updateUserDoc:
            user["money"] = round(user["money"], 5)
            db.users.update_one({"userid": ctx.author.id}, {"$set": user})


    # @commands.command(aliases=["шакал", "шакалайз", "зашакалить"])
    # async def shakalize(self, ctx, iterations=1):
    #     MAX_ITERATIONS = 5
    #     # Проверяем, что количество итераций находится в пределах допустимых значений
    #     iterations = min(int(iterations), MAX_ITERATIONS)
    #     if iterations <= 0:
    #         iterations = 1
    #
    #     # Проверяем, что пользователь прикрепил изображение к сообщению
    #     if len(ctx.message.attachments) == 0:
    #         await ctx.send("Ошибка: Пожалуйста, прикрепите изображение к вашему сообщению.")
    #         return
    #
    #     # Получаем прикрепленное изображение
    #     attachment = ctx.message.attachments[0]
    #     # if attachment.url.lower().endswith(("png", "jpg", "jpeg")):
    #     image_bytes = await attachment.read()
    #     print(image_bytes)
    #     # Обработка изображения
    #     with Image.open(io.BytesIO(image_bytes)) as img:
    #         enhancer = ImageEnhance.Contrast(img)
    #         # for _ in range(iterations):
    #         # Изменение контрастности
    #
    #         img = enhancer.enhance(2.0)
    #
    #         # "Повреждение" изображения
    #         img = img.convert('RGB').quantize(5).convert('RGB')
    #
    #         # Сохранение нового изображения
    #         output = io.BytesIO()
    #         img.save(output, format='JPEG', quality=10)
    #         output.seek(0)
    #
    #             # Отправка обработанного изображения обратно в чат
    #         await ctx.send(file=discord.File(output, filename='shakal.jpg'))
    #     # else:
    #     #     await ctx.send("Ошибка: Изображение должно быть в форматах PNG или JPEG.")

    @commands.command(aliases=["шакал", "шакалайз", "зашакалить"])
    async def shakalize(self, ctx, iterations=1):
        MAX_ITERATIONS=500
        # Проверяем, что количество итераций находится в пределах допустимых значений
        iterations = min(int(iterations), MAX_ITERATIONS)
        if iterations <= 0:
            iterations = 1

        # Проверяем, что пользователь прикрепил изображение к сообщению
        if len(ctx.message.attachments) == 0:
            await ctx.send("Ошибка: Пожалуйста, прикрепите изображение к вашему сообщению.")
            return

        # Получаем прикрепленное изображение
        attachment = ctx.message.attachments[0]
        if True:#attachment.url.lower().endswith(("png", "jpg", "jpeg")):
            image_bytes = await attachment.read()

            # Обработка изображения
            with Image.open(io.BytesIO(image_bytes)) as img:
                # Сохраняем изображение несколько раз с разным качеством JPEG
                for i in range(iterations):
                    output = io.BytesIO()
                    img.save(output, format='JPEG', quality=10 + iterations - i)
                    output.seek(0)
                    img = Image.open(output)

                # Усиление контрастности
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(iterations)

                # Сохранение обработанного изображения
                final_output = io.BytesIO()
                img.save(final_output, format='JPEG', quality=10)
                final_output.seek(0)

                # Отправка обработанного изображения обратно в чат
                await ctx.send(file=discord.File(final_output, filename='shakal.jpg'))
        # else:
        #     await ctx.send("Ошибка: Изображение должно быть в форматах PNG или JPEG.")
def setup(bot):
    bot.add_cog(fun(bot))
