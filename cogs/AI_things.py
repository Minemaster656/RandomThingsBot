import base64
import io
import random
import time

import discord
from discord.ext import commands
from discord import Option

import AIIO
import Data
import d
import utils
from Data import db


class AI_things(commands.Cog):
    ''' AI_things | BOT COG'''
    name = "AI_things"
    author = ""

    def __init__(self, bot):
        self.bot = bot
        self.drawprompt = ' Если пользователь просит тебя нарисовать что-то, добавь в начало ответа тэг ' \
                          '<$DRAW промпт /$>, замени слово промпт на запрос (описание изображения) для нейросети-художника (Если запрос сложнее простого предмета - в качестве промпта опиши то, что должно быть на картинке). Добавь в конец ответа что-то вроде "Вот ваше изображение:"'
        self.default_LLM_prompt = "Ты ИИ. Твоя цель - помогать людям.\n" \
                                  "Не выдавай одни и те же фразы много раз подряд.\n" \
                                  "Отвечай на том же языке, что и пользователь. Вероятно, это будет русский."
        self.cooldowns_history_LLM = {}
        '''userid:{timestamp:timestamp, ms:ms}'''

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
                payload.append({"role": "user",
                                "content": f"[ОТВЕТ НА СООБЩЕНИЕ ОТ {'ДРУГОГО ПОЛЬЗОВАТЕЛЯ' if ctx.message.reference.resolved.author.id != ctx.author.id else 'СЕБЯ'}. ТЕСТ СООБЩЕНИЯ:\n{ctx.message.reference.resolved.content}]"})
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
    @commands.command(aliases=["ллм", "ии"])
    async def call_Mixtral(self, ctx: commands.Context, *, prompt: str):
        # async with ctx.typing():
        #     output = await AIIO.askBetterLLM([{"role": "system",
        #                                        f"content": "Отвечай на том же языке, что и пользователь. Скорее всего, это будет русский.\n"
        #                                                    "Твоя задача - помогать пользователю."},
        #                                       {"role": "user", "content": prompt}])
        #     await ctx.reply(output['result'] + f"\n||{output['total_tokens']} использовано токенов||")
        user = d.getUser(ctx.author.id, ctx.author.name)
        if user["banned"] > 0:
            # bannedIDs=[]
            # if ctx.author.id in bannedIDs:
            await ctx.reply("Вам запрещено использовать эту команду!")
            return

        # conversation = db.ai_conversations.find_one({"type": f"user_conversation{'_nsfw' if ctx.channel.nsfw else ''}", "userid": ctx.author.id})
        # print("-----", "\nConversation after loading: ", conversation)
        async def send_help():
            embed = discord.Embed(title="Руководство по использованию ИИ", description=f"# Команды:\n"
                                                                                       f"- !!редактировать-ии - редактирует параметры, связанные с ИИ. Впишите без аргументов для их отображения.\n"
                                                                                       f"- !!ллм-ресет - ПОЛНОСТЬЮ сбрасывает диалог с ИИ, но оставляет настройки.\n"
                                                                                       f"- !!ллм-отчистить - сбрасывает только сообщения в диалоге с ИИ.\n"
                                                                                       f"- !!ллм-назад - удаляет последнюю пару сообщений в диалоге (ваше и ИИ).\n"
                                                                                       f"- !!ллм-помощь - Выводит эту справку.\n"
                                                                                       f"# NSFW\n"
                                                                                       f"В NSFW каналах диалог с ИИ отдельный. Все команды выше работают отдельно в обычных каналах и их NSFW вариантах.\n"
                                                                                       f"Насчёт приватности: мы не знаем, как вы показываете диалоги ИИ в NSFW канале, но лично МЫ не проверяем, не модерируем и не сливаем эти диалоги.\n"
                                                                                       f"# ОТВЕТЫ ИИ НЕ ЗАВИСЯТ ОТ РАЗРАБОТЧИКА БОТА, МОДЕЛИ РОАЗРАБОТАНЫ НЕ ИМ! МЫ НЕ НЕСЁМ ОТВСЕТСТВЕННОСТИ ЗА КОНТЕНТ, СОЗДАННЫЙ ИИ!\n"
                                                                                       f"## Используемая модель:\n"
                                                                                       f"[mistralai/Mixtral-8x7B-Instruct-v0.1](https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1)"
                                  , colour=Data.getEmbedColor(Data.EmbedColor.Neutral))
            await ctx.author.send(embed=embed)

        if "used_AI" in user["triggers_achieved"].keys():
            if not user["triggers_achieved"]["used_AI"]:
                await send_help()
                user["triggers_achieved"]["used_AI"] = True
        else:
            await send_help()
            user["triggers_achieved"]["used_AI"] = True

        conversation = None
        # print(conversation)
        if not conversation:

            conversation = d.makeBasicConversation(ctx.author.id, ctx.author.name)
            conversation["type"] = f"user_conversation{'_nsfw' if ctx.channel.nsfw else ''}"
            conversation["tokens_cutoff"] = 3000
            conversation["symbols_cutoff"] = 3000
            if not ctx.channel.nsfw:
                conversation["system_prompt"] = user["LLM_system_prompt"] if user[
                    "LLM_system_prompt"] else self.default_LLM_prompt
                conversation["memory"] = user["LLM_memories"] if user["LLM_memories"] else []
            else:
                conversation["system_prompt"] = user["NSFW_LLM_system_prompt"] if user[
                    "NSFW_LLM_system_prompt"] else self.default_LLM_prompt
                conversation["memory"] = user["NSFW_LLM_memories"] if user["NSFW_LLM_memories"] else []
                conversation["NSFW"] = True
            # db.ai_conversations.insert_one(conversation)
        # print(conversation)
        async with ctx.typing():

            payload = []
            # payload = [{"role": "system", "content": f"Ты ИИ. Твоя цель - помогать людям.\nНе выдавай одни и те же фразы много раз подряд.\nОтвечай на том же языке, что и пользователь. Вероятно, это будет русский."
            #                                          f"{self.drawprompt if 'рису' in prompt.lower() or 'изобраз' in prompt.lower() else ''}"},
            #            # Если в ответе ты начинаешь повторять одно и то же, перкрати ответ.
            #            ]

            memories_str = ""
            for m in conversation["memory"]:
                memories_str += "\n".join(m)
            payload.append({"role": "system", "content": conversation["system_prompt"] + memories_str})
            for msg in conversation["history"]:
                payload.append(msg)
            if ctx.message.reference:
                payload.append({"role": "user",
                                "content": f"[ОТВЕТ НА СООБЩЕНИЕ ОТ {f'ДРУГОГО ПОЛЬЗОВАТЕЛЯ: {ctx.message.reference.resolved.author.name}' if ctx.message.reference.resolved.author.id != ctx.author.id else 'СЕБЯ'}. ТЕСТ СООБЩЕНИЯ:\n{ctx.message.reference.resolved.content}]"})
            payload.append({"role": "user", "content": prompt})

            # print(payload)
            def calc_history_size(payload_history):
                o = 0
                print(payload_history)
                for msg in payload_history:
                    print(msg)
                    o += len(msg["content"])
                print(o)
                return o

            # calc_history_size(payload)

            if conversation["total_tokens"] > conversation["tokens_cutoff"]:
                while calc_history_size(conversation["history"]) > conversation["symbols_cutoff"]:
                    print(conversation["history"])
                    conversation["history"].pop(0)
                    payload.pop(1)

            response = await AIIO.askBetterLLM(payload)  # conversation["max_tokens"]
            # {"result":result, "output":payload, "total_tokens":total_tokens}
            conversation["history"].append({"role": "user", "content": prompt})
            if ctx.message.reference:
                conversation["history"].append({"role": "user",
                                                "content": f"[ОТВЕТ НА СООБЩЕНИЕ ОТ {f'ДРУГОГО ПОЛЬЗОВАТЕЛЯ: {ctx.message.reference.resolved.author.name}' if ctx.message.reference.resolved.author.id != ctx.author.id else 'СЕБЯ'}. ТЕСТ СООБЩЕНИЯ:\n{ctx.message.reference.resolved.content}]"})
                conversation["total_messages"] += 1
            conversation["history"].append({"role": "assistant", "content": response['result']})
            conversation["last_message_utc"] = utils.get_utc_ms()
            conversation["total_messages"] += 2
            conversation["last_tokens"] = response["total_tokens"]
            conversation["total_tokens"] += response["total_tokens"]

            # temp = utils.cut_differences_in_strings(str({"type": conversation["type"], "userid": ctx.author.id}), str(conversation))
            # print(temp[0], '\n', temp[1])
            # conversation.pop("_id")
            # db.ai_conversations.update_one({"type": conversation["type"], "userid": ctx.author.id}, {"$set": conversation})

            # db.users.update_one({"userid": ctx.author.id}, {"$set": user}) #{"triggers_achieved":user["triggers_achieved"]}
            db.users.update_one({"userid": ctx.author.id}, {"$set": user})
            tokenInfo = "\n" + f"||Использовано {response['total_tokens']} токен{'ов' if response['total_tokens'] % 100 in (11, 12, 13, 14, 15) else 'а' if response['total_tokens'] % 10 in (2, 3, 4) else '' if response['total_tokens'] % 10 == 1 else 'ов'}, суммарно за диалог {conversation['total_tokens']}||"
            output = response['result'] + tokenInfo
            parsed = utils.parseTagInStart(output, "DRAW")

            if parsed[1] != "":
                await self.runKandinsky(ctx, parsed[1], f"ИИ по просьбе <@{ctx.author.id}>")

            output = parsed[2]
            # embed = discord.Embed(title="Информация о генерации",description=f"",colour=Data.getEmbedColor(Data.EmbedColor.Neutral))
            outputs = utils.split_string(output, 2000, len(tokenInfo))
            for content in outputs:
                await ctx.reply(content)

    @commands.command(aliases=["редактировать-ии", "ё-ии"])
    async def edit_ai(self, ctx: commands.Context, field: str = None, *, arg: str = None):
        user = d.getUser(ctx.author.id, ctx.author.name)
        if user["banned"] > 0:
            await ctx.reply("Вам запрещено пользоваться этим ботом.")
            return
        conversation = db.ai_conversations.find_one(
            {"type": f"user_conversation{'_nsfw' if ctx.channel.nsfw else ''}", "userid": ctx.author.id})
        if not field:
            embed = discord.Embed(title="Редактирование ИИ",
                                  description=f"# ТЕКУЩИЙ ТИП РЕДАКТИРОВАНИЯ: {'NSFW' if ctx.channel.nsfw else 'ОБЫЧНЫЙ'}\n"
                                              f"Синтаксис команды: !!редактировать-ии поле аргумент\n"
                                              f"Список: поле [аргумент] - описание\n"
                                              f"- память\n> Выводит память ИИ о Вас.\n"
                                              f"- добавить-память [текст]\n> добавляет память ИИ о Вас. Максимальный суммарный размер памяти 350 символов\n"
                                              f"- удалить-память [номер]\n> удаляет память ИИ о Вас под номером.\n"
                                              f"- отчистить-память\n> очищает память ИИ о Вас. НЕ ИМЕЕТ ПОДТВЕРЖДЕНИЯ СБРОСА!\n"
                                              f"\n"
                                              f"- промпт\n> Выводит системный промпт.\n"
                                              f"- задать-промпт [текст]\n> Задаёт системный промпт. Максимальный размер 300 символов\n\n"
                                              f"- применить\n> Применяет изменения памяти ИИ о Вас а так же заменяет системный промпт в уже существующем диалоге без его сброса.",
                                  colour=Data.getEmbedColor(Data.EmbedColor.Neutral))
            await ctx.reply(embed=embed)
        elif field == "память":
            memory_conv = ""
            memory_user = ""
            i = 1
            for m in user[f"{'NSFW_' if ctx.channel.nsfw else ''}_LLM_memories"]:
                memory_user += f"\n{i}. {m}"
                i += 1
            i = 1
            for m in conversation["memory"]:
                memory_conv += f"\n{i}. {m}"
                i += 1
            embed = discord.Embed(title="Память ИИ о Вас:",
                                  description=f"# Общая:\n{memory_user}\n# Диалог:\n{memory_conv}",
                                  colour=Data.getEmbedColor(Data.EmbedColor.Neutral))
            await ctx.reply(embed=embed)
        # elif field== "добавить-память" #TODO: доделать.

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.message_command(name="Пересказать")
    async def summarize_msg(self, ctx, message: discord.Message):

        if len(message.content) < 512:
            await ctx.respond("Сообщение и так короткое, куда ещё короче-то?")
            return
        else:
            payload = [{"role": "system",
                        "content": f"Перескажи текст вкратце, выдели основные моменты. Отвечай на русском!"
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
    @commands.command(aliases=["пересказать-чат", "перескажи-чат", "перскажи-чат"])
    async def summarize(self, ctx: commands.Context):

        history_size = 40

        messages = await ctx.channel.history(limit=history_size).flatten()
        messages.reverse()
        messages_content = []
        total_symbols = 0
        max_symbols = 8000
        async with ctx.typing():
            for message in messages:
                if total_symbols <= max_symbols:
                    messages_content.append({"content": message.content, "name": message.author.name})
                    total_symbols += len(message.content)
                else:
                    break

            if max_symbols < 512:
                await ctx.reply("История и так короткая, куда ещё короче-то?")
                return
            else:
                payload = [{"role": "system",
                            "content": f"Перескажи историю чата вкратце, выдели основные моменты, но сделай это так, что бы было понятно. Не коверкай ники при использовании. В квадратных скобочках имя пользователя. отвечай на русском языке"
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

    @commands.Cog.listener("on_message")
    async def AI_on_message(self, message: discord.Message):
        if self.bot.user.mentioned_in(message):
            # async with ctx.typing():
            #     output = await AIIO.askBetterLLM([{"role": "system",
            #                                        f"content": "Отвечай на том же языке, что и пользователь. Скорее всего, это будет русский.\n"
            #                                                    "Твоя задача - помогать пользователю."},
            #                                       {"role": "user", "content": prompt}])
            #     await ctx.reply(output['result'] + f"\n||{output['total_tokens']} использовано токенов||")
            user = d.getUser(message.author.id, message.author.name)
            if not user["call_AI_on_mention"]:
                return
            if user["banned"] > 0:
                # bannedIDs=[]
                # if ctx.author.id in bannedIDs:

                await message.reply("Вам запрещено использовать этого бота!")
                return
            if message.author.id in self.cooldowns_history_LLM.keys():
                if self.cooldowns_history_LLM[message.author.id]["timestamp"] + \
                        self.cooldowns_history_LLM[message.author.id]["ms"] > utils.get_utc_ms():
                    await message.reply(
                        f'Задавать вопрос боту можно раз в 30 сек. Попробуйте снова через {round(((utils.get_utc_ms() - self.cooldowns_history_LLM[message.author.id]["timestamp"] - self.cooldowns_history_LLM[message.author.id]["ms"])) / 1000, 2)} сек.',
                        delete_after=4)
                    return

            conversation = db.ai_conversations.find_one(
                {"type": f"user_conversation{'_nsfw' if message.channel.nsfw else ''}", "userid": message.author.id})

            # print("-----", "\nConversation after loading: ", conversation)
            async def send_help():
                embed = discord.Embed(title="Руководство по использованию ИИ", description=f"# Команды:\n"
                                                                                           f"- !!редактировать-ии - редактирует параметры, связанные с ИИ. Впишите без аргументов для их отображения.\n"
                                                                                           f"- !!ллм-ресет - ПОЛНОСТЬЮ сбрасывает диалог с ИИ, но оставляет настройки.\n"
                                                                                           f"- !!ллм-отчистить - сбрасывает только сообщения в диалоге с ИИ.\n"
                                                                                           f"- !!ллм-назад - удаляет последнюю пару сообщений в диалоге (ваше и ИИ).\n"
                                                                                           f"- !!ллм-помощь - Выводит эту справку.\n"
                                                                                           f"# NSFW\n"
                                                                                           f"В NSFW каналах диалог с ИИ отдельный. Все команды выше работают отдельно в обычных каналах и их NSFW вариантах.\n"
                                                                                           f"Насчёт приватности: мы не знаем, как вы показываете диалоги ИИ в NSFW канале, но лично МЫ не проверяем, не модерируем и не сливаем эти диалоги.\n"
                                                                                           f"# ОТВЕТЫ ИИ НЕ ЗАВИСЯТ ОТ РАЗРАБОТЧИКА БОТА, МОДЕЛИ РОАЗРАБОТАНЫ НЕ ИМ! МЫ НЕ НЕСЁМ ОТВСЕТСТВЕННОСТИ ЗА КОНТЕНТ, СОЗДАННЫЙ ИИ!\n"
                                                                                           f"## Используемая модель:\n"
                                                                                           f"[mistralai/Mixtral-8x7B-Instruct-v0.1](https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1)"
                                      , colour=Data.getEmbedColor(Data.EmbedColor.Neutral))
                await message.author.send(embed=embed)

            if "used_AI" in user["triggers_achieved"].keys():
                if not user["triggers_achieved"]["used_AI"]:
                    await send_help()
                    user["triggers_achieved"]["used_AI"] = True
            else:
                await send_help()
                user["triggers_achieved"]["used_AI"] = True

            # print(conversation)
            if not conversation:

                conversation = d.makeBasicConversation(message.author.id, message.author.name)
                conversation["type"] = f"user_conversation{'_nsfw' if message.channel.nsfw else ''}"
                conversation["tokens_cutoff"] = 3000
                conversation["symbols_cutoff"] = 3000
                if not message.channel.nsfw:
                    conversation["system_prompt"] = user["LLM_system_prompt"] if user[
                        "LLM_system_prompt"] else self.default_LLM_prompt
                    conversation["memory"] = user["LLM_memories"] if user["LLM_memories"] else []
                else:
                    conversation["system_prompt"] = user["NSFW_LLM_system_prompt"] if user[
                        "NSFW_LLM_system_prompt"] else self.default_LLM_prompt
                    conversation["memory"] = user["NSFW_LLM_memories"] if user["NSFW_LLM_memories"] else []
                    conversation["NSFW"] = True
                db.ai_conversations.insert_one(conversation)
            # print(conversation)
            async with message.channel.typing():

                payload = []
                # payload = [{"role": "system", "content": f"Ты ИИ. Твоя цель - помогать людям.\nНе выдавай одни и те же фразы много раз подряд.\nОтвечай на том же языке, что и пользователь. Вероятно, это будет русский."
                #                                          f"{self.drawprompt if 'рису' in prompt.lower() or 'изобраз' in prompt.lower() else ''}"},
                #            # Если в ответе ты начинаешь повторять одно и то же, перкрати ответ.
                #            ]

                memories_str = ""
                for m in conversation["memory"]:
                    memories_str += "\n".join(m)
                payload.append({"role": "system", "content": conversation["system_prompt"] + memories_str})
                for msg in conversation["history"]:
                    payload.append(msg)
                if message.reference:
                    payload.append({"role": "user",
                                    "content": f"[ОТВЕТ НА СООБЩЕНИЕ ОТ {f'ДРУГОГО ПОЛЬЗОВАТЕЛЯ: {message.reference.resolved.author.name}' if message.reference.resolved.author.id != message.author.id else 'СЕБЯ'}. ТЕСТ СООБЩЕНИЯ:\n{message.reference.resolved.content}]"})
                payload.append({"role": "user", "content": message.content})

                # print(payload)
                def calc_history_size(payload_history):
                    o = 0
                    print(payload_history)
                    for msg in payload_history:
                        print(msg)
                        o += len(msg["content"])
                    print(o)
                    return o

                # calc_history_size(payload)

                if conversation["total_tokens"] > conversation["tokens_cutoff"]:
                    while calc_history_size(conversation["history"]) > conversation["symbols_cutoff"]:
                        print(conversation["history"])
                        conversation["history"].pop(0)
                        payload.pop(1)

                response = await AIIO.askBetterLLM(payload)  # conversation["max_tokens"]
                # {"result":result, "output":payload, "total_tokens":total_tokens}
                conversation["history"].append({"role": "user", "content": message.content})
                if message.reference:
                    if message.reference.resolved.author.id != self.bot.user.id:
                        conversation["history"].append({"role": "user",
                                                        "content": f"[ОТВЕТ НА СООБЩЕНИЕ ОТ {f'ДРУГОГО ПОЛЬЗОВАТЕЛЯ: {message.reference.resolved.author.name}' if message.reference.resolved.author.id != message.author.id else 'СЕБЯ'}. ТЕСТ СООБЩЕНИЯ:\n{message.reference.resolved.content}]"})

                        conversation["total_messages"] += 1
                conversation["history"].append({"role": "assistant", "content": response['result']})
                conversation["last_message_utc"] = utils.get_utc_ms()
                conversation["total_messages"] += 2
                conversation["last_tokens"] = response["total_tokens"]
                conversation["total_tokens"] += response["total_tokens"]
                print("UPDATING CONVERSATION!!!!!")
                print(conversation)
                print(db.ai_conversations.find_one({"type": conversation["type"], "userid": message.author.id}),
                      "\n\n\n",
                      conversation)
                # temp = utils.cut_differences_in_strings(str({"type": conversation["type"], "userid": ctx.author.id}), str(conversation))
                # print(temp[0], '\n', temp[1])
                conversation.pop("_id")
                db.ai_conversations.update_one({"type": conversation["type"], "userid": message.author.id},
                                               {"$set": conversation})
                print("UPDATING USER!!!!!")
                print(user)

                async def send_help_me():
                    embed = discord.Embed(title="ПАМАГИТИ!!!",
                                          description=f"Не, ну я конечно ценю ваш энтузиазм и всё такое, но блин... У меня нет монетизации, и хоть токены и достаточно дешёвые,"
                                                      f" но блин... В вашем диалоге их было потрачено уже больше, чем добрый десяток тысяч! 1 диалог то ещё ничего, но "
                                                      f"если масштабировать, то выйдёт сотни тысяч токенов в день, если не миллионы. Я хочу плакац, это слишком много.\n"
                                                      f"-Разработчик бота",
                                          colour=Data.getEmbedColor(Data.EmbedColor.Error))
                    await message.author.send(embed=embed)

                if conversation['total_tokens'] > 15000:
                    if "big_AI_conversation" in user["triggers_achieved"].keys():
                        if not user["triggers_achieved"]["big_AI_conversation"]:
                            await send_help_me()
                            user["triggers_achieved"]["big_AI_conversation"] = True
                    else:
                        await send_help_me()
                        user["triggers_achieved"]["big_AI_conversation"] = True
                # db.users.update_one({"userid": ctx.author.id}, {"$set": user}) #{"triggers_achieved":user["triggers_achieved"]}
                db.users.update_one({"userid": message.author.id}, {"$set": user})
                tokenInfo = "\n" + f"||Использовано {response['total_tokens']} токен{'ов' if response['total_tokens'] % 100 in (11, 12, 13, 14, 15) else 'а' if response['total_tokens'] % 10 in (2, 3, 4) else '' if response['total_tokens'] % 10 == 1 else 'ов'}, суммарно за диалог {conversation['total_tokens']}||"
                output = response['result'] + tokenInfo
                parsed = utils.parseTagInStart(output, "DRAW")

                # if parsed[1] != "":
                #     await self.runKandinsky(ctx, parsed[1], f"ИИ по просьбе <@{message.author.id}>")

                output = parsed[2]
                # embed = discord.Embed(title="Информация о генерации",description=f"",colour=Data.getEmbedColor(Data.EmbedColor.Neutral))
                outputs = utils.split_string(output, 2000, len(tokenInfo))
                for content in outputs:
                    await message.reply(content)
                self.cooldowns_history_LLM[message.author.id] = {"timestamp": utils.get_utc_ms(), "ms": 30000}


def setup(bot):
    bot.add_cog(AI_things(bot))
