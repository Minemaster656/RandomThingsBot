import base64
import io
import random
import time

import discord
from discord.ext import commands
from discord import Option

import AIIO
import Data
import utils


class AI_things(commands.Cog):
    ''' AI_things | BOT COG'''
    name = "AI_things"
    author = ""

    def __init__(self, bot):
        self.bot = bot
        self.drawprompt = ' Если пользователь просит тебя нарисовать что-то, добавь в начало ответа тэг ' \
                          '"<$DRAW промпт /$>" (КАВЫЧКИ И ЭТО УБЕРИ!!!), замени слово промпт на запрос (описание изображения) для нейросети-художника (Если запрос сложнее простого предмета - в качестве промпта опиши то, что должно быть на картинке). Добавь в конец ответа что-то вроде "Вот ваше изображение:"'

    async def runKandinsky(self, ctx, prompt, author):
        time_start = time.time()
        async with ctx.typing():

            embed = discord.Embed(title="Запуск генерации...",
                                  description=f"**Запрос:** {prompt}\n\n***Генерация может занять немного времени...***",
                                  colour=Data.getEmbedColor(Data.EmbedColor.Neutral))
            embed.add_field(name="Запросил генерацию", value=f"{author}", inline=False)
            # embed.add_field(name="Подсказка",value="Используйте !: что бы начать вводить негативный промпт (делайте это после обычного)",inline=False)
            await ctx.reply(embed=embed)

            gen = await AIIO.askT2I(prompt, AIIO.Text2Imgs.KANDINSKY)
            if gen['censored']:
                embed = discord.Embed(title="Ошибка генерации!",
                                      description="NSFW изображения не разрешены этой моделью!",
                                      colour=Data.getEmbedColor(Data.EmbedColor.Error))
                await ctx.reply(embed=embed)
            else:
                if gen["image"] == "Error":
                    embed = discord.Embed(title="Ошибка генерации!",
                                          description="Время ожидания истекло!",
                                          colour=Data.getEmbedColor(Data.EmbedColor.Error))
                    await ctx.reply(embed=embed)
                    return
                file_content = io.BytesIO(base64.b64decode(gen["image"]))

                file = discord.File(filename=f"gen_kandinsky_{random.randint(0, 35565)}.png", fp=file_content)
                embed = discord.Embed(title="Генерация завершена!", description=f"**Запрос:** {prompt}",
                                      colour=Data.getEmbedColor(Data.EmbedColor.Success))
                embed.add_field(name="Запросил генерацию", value=f"{author}", inline=False)
                embed.add_field(name="Время генерации", value=f"{round(time.time() - time_start, 2)} сек.",
                                inline=False)

                await ctx.reply(embed=embed)
                await ctx.reply(prompt, file=file)

    # AI_cooldown = commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.user)
    @commands.cooldown(1, 30, commands.BucketType.member)
    @commands.command(aliases=["ИИ", "гигачат", "gigachat"])
    async def askGigachat(self, ctx, *, prompt: str = "Привет!"):
        bannedIDs = []
        if ctx.author.id in bannedIDs:
            await ctx.reply("Вам запрещено использовать эту команду!")
            return
        async with ctx.typing():
            payload = [{"role": "system", "content": f"Не выдавай одни и те же фразы много раз подряд.\n"
                                                     f"{self.drawprompt if 'рису' in prompt else ''}"},
                       # Если в ответе ты начинаешь повторять одно и то же, перкрати ответ.
                       ]
            if ctx.message.reference:
                payload.append({"role": "user", "content": f"[ОТВЕТ НА СООБЩЕНИЕ ОТ {'ДРУГОГО ПОЛЬЗОВАТЕЛЯ' if ctx.message.reference.resolved.author.id != ctx.author.id else 'СЕБЯ'}. ТЕСТ СООБЩЕНИЯ:\n{ctx.message.reference.resolved.content}]"})
            payload.append({"role": "user", "content": prompt})
            # print(payload)
            response = await AIIO.askLLM(payload, AIIO.LLMs.GIGACHAT, 3, AIIO.gigachat_temptoken)
            print(response)
            if response == "No token":
                response = await AIIO.askLLM(payload, AIIO.LLMs.GIGACHAT, 3, AIIO.gigachat_temptoken)
                print(response)

            resp = response[0]
            tokens = response[1]['total_tokens']
            tokenInfo = "\n" + f"||Использовано {tokens} токен{'ов' if tokens % 100 in (11, 12, 13, 14, 15) else 'а' if tokens % 10 in (2, 3, 4) else '' if tokens % 10 == 1 else 'ов'}||"
            output = resp + tokenInfo
            parsed = utils.parseTagInStart(output, "DRAW")
            print(parsed)
            print(parsed[0])
            if parsed[1] != "":
                await self.runKandinsky(ctx, parsed[1], f"ГигаЧат по просьбе <@{ctx.author.id}>")

            output = parsed[2]
            # embed = discord.Embed(title="Информация о генерации",description=f"",colour=Data.getEmbedColor(Data.EmbedColor.Neutral))
            outputs = utils.split_string(output, 2000, len(tokenInfo))
            for content in outputs:
                await ctx.reply(content)

    # @commands.cooldown(1, 35, commands.BucketType.member)
    # @commands.command(aliases=["атк", "аткгпт", "atk", "ATK", "АТК", "atkgpt"])
    async def askATKGPT(self, ctx, *, prompt: str = "Привет!"):
        bannedIDs = []
        if ctx.author.id in bannedIDs:
            await ctx.reply("Вам запрещено использовать эту команду!")
            return
        async with ctx.typing():
            payload = [
                {"role": "system",
                 "content": f"Ты ATK GPT. Искуственный интеллект, задача которого - помогать людям.\nЕсли в ответе ты начинаешь повторять одно и то же, перкрати ответ.\n"
                            f"{' Если пользователь просит тебя нарисовать что-то, добавь в начало ответа текст <$DRAW запрос /$> где запрос - описание (промпт) изображения для нейросети-художника' if 'рису' in prompt else ''}"},
                {"role": "user", "content": prompt}]
            # print(payload)
            response = await AIIO.askLLM(payload, AIIO.LLMs.GIGACHAT, 3, AIIO.gigachat_temptoken)
            print(response)
            if response == "No token":
                response = await AIIO.askLLM(payload, AIIO.LLMs.GIGACHAT, 3, AIIO.gigachat_temptoken)
                print(response)

            resp = response[0]
            tokens = response[1]['total_tokens']
            tokenInfo = "\n" + f"||Использовано {tokens} токен{'ов' if tokens % 100 in (11, 12, 13, 14, 15) else 'а' if tokens % 10 in (2, 3, 4) else '' if tokens % 10 == 1 else 'ов'}||"
            output = resp + tokenInfo
            parsed = utils.parseTagInStart(output, "DRAW")
            if parsed[1] != "":
                await self.runKandinsky(ctx, parsed[1], f"ГигаЧат по просьбе <@{ctx.author.id}>")
            output = parsed[2]
            # embed = discord.Embed(title="Информация о генерации",description=f"",colour=Data.getEmbedColor(Data.EmbedColor.Neutral))
            outputs = utils.split_string(output, 2000, len(tokenInfo))
            for content in outputs:
                await ctx.reply(content)

    @commands.cooldown(1, 15, commands.BucketType.member)
    @commands.command(aliases=["кандинский"])
    async def kandinsky(self, ctx, *, prompt: str):
        await self.runKandinsky(ctx, prompt, f"<@{ctx.author.id}>")

    @commands.cooldown(1, 30, commands.BucketType.member)
    @commands.command(aliases=["ллм"])
    async def call_Mixtral(self, ctx: commands.Context, *, prompt: str):
        # async with ctx.typing():
        #     output = await AIIO.askBetterLLM([{"role": "system",
        #                                        f"content": "Отвечай на том же языке, что и пользователь. Скорее всего, это будет русский.\n"
        #                                                    "Твоя задача - помогать пользователю."},
        #                                       {"role": "user", "content": prompt}])
        #     await ctx.reply(output['result'] + f"\n||{output['total_tokens']} использовано токенов||")
        bannedIDs=[]
        if ctx.author.id in bannedIDs:
            await ctx.reply("Вам запрещено использовать эту команду!")
            return
        async with ctx.typing():
            payload = [{"role": "system", "content": f"Ты ИИ. Твоя цель - помогать людям.\nНе выдавай одни и те же фразы много раз подряд.\nОтвечай на том же языке, что и пользователь. Вероятно, это будет русский."
                                                     f"{self.drawprompt if 'рису' in prompt.lower() or 'изобраз' in prompt.lower() else ''}"},
                       # Если в ответе ты начинаешь повторять одно и то же, перкрати ответ.
                       ]
            if ctx.message.reference:
                payload.append({"role": "user", "content": f"[ОТВЕТ НА СООБЩЕНИЕ ОТ {'ДРУГОГО ПОЛЬЗОВАТЕЛЯ' if ctx.message.reference.resolved.author.id != ctx.author.id else 'СЕБЯ'}. ТЕСТ СООБЩЕНИЯ:\n{ctx.message.reference.resolved.content}]"})
            payload.append({"role": "user", "content": prompt})
            # print(payload)
            response = await AIIO.askBetterLLM(payload, 1024)




            tokenInfo = "\n" + f"||Использовано {response['total_tokens']} токен{'ов' if response['total_tokens'] % 100 in (11, 12, 13, 14, 15) else 'а' if response['total_tokens'] % 10 in (2, 3, 4) else '' if response['total_tokens'] % 10 == 1 else 'ов'}||"
            output = response['result'] + tokenInfo
            parsed = utils.parseTagInStart(output, "DRAW")

            if parsed[1] != "":
                await self.runKandinsky(ctx, parsed[1], f"ИИ по просьбе <@{ctx.author.id}>")

            output = parsed[2]
            # embed = discord.Embed(title="Информация о генерации",description=f"",colour=Data.getEmbedColor(Data.EmbedColor.Neutral))
            outputs = utils.split_string(output, 2000, len(tokenInfo))
            for content in outputs:
                await ctx.reply(content)

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.message_command(name="Пересказать")
    async def summarize(self, ctx, message: discord.Message):

        if len(message.content) < 512:
            await ctx.respond("Сообщение и так короткое, куда ещё короче-то?")
            return
        else:
            payload = [{"role": "system",
                        "content": f"Перескажи текст вкратце, выдели основные моменты."
                        },
                       # Если в ответе ты начинаешь повторять одно и то же, перкрати ответ.
                       {"role": "user", "content": message.content}]
            # print(payload)
            response = await AIIO.askBetterLLM(payload)




            tokenInfo = "\n" + f"||Использовано {response['total_tokens']} токен{'ов' if response['total_tokens'] % 100 in (11, 12, 13, 14, 15) else 'а' if response['total_tokens'] % 10 in (2, 3, 4) else '' if response['total_tokens'] % 10 == 1 else 'ов'}||"
            output = response['result'] + tokenInfo

            outputs = utils.split_string(output, 2000, len(tokenInfo))
            for content in outputs:


                await ctx.respond(content)
                # print("...")
                #
                # await ctx.send(content)

    @commands.cooldown(1, 300, commands.BucketType.channel)
    @commands.command(aliases=["пересказать-чат", "перескажи-чат"])
    async def summarize(self, ctx: commands.Context):
        history_size = 40

        messages = await ctx.channel.history(limit=history_size).flatten()
        # messages.reverse()
        messages_content=[]
        total_symbols = 0
        max_symbols = 8000
        for message in messages:
            if total_symbols<=max_symbols:
                messages_content.append({"content": message.content, "name":message.author.name})
                total_symbols+=len(message.content)
            else:
                break

        if max_symbols < 512:
            await ctx.reply("История и так короткая, куда ещё короче-то?")
            return
        else:
            payload = [{"role": "system",
                        "content": f"Перескажи историю чата вкратце, выдели основные моменты, но сделай это так, что бы было понятно. Не коверкай ники при использовании. В квадратных скобочках имя пользователя"
                        },
                       # Если в ответе ты начинаешь повторять одно и то же, перкрати ответ.
                       ]
            for msg in messages_content:
                payload.append({"role": "user", "content": f'[{msg["name"]}]: {msg["content"]}'})
            # print(payload)
            response = await AIIO.askBetterLLM(payload)

            tokenInfo = "\n" + f"||Использовано {response['total_tokens']} токен{'ов' if response['total_tokens'] % 100 in (11, 12, 13, 14, 15) else 'а' if response['total_tokens'] % 10 in (2, 3, 4) else '' if response['total_tokens'] % 10 == 1 else 'ов'}. {len(messages_content)}/{history_size} сообщ. {total_symbols}/{max_symbols} симв.||"
            output = response['result'] + tokenInfo

            outputs = utils.split_string(output, 2000, len(tokenInfo))
            for content in outputs:
                await ctx.reply(content)
                # print("...")
                #
                # await ctx.send(content)


def setup(bot):
    bot.add_cog(AI_things(bot))
