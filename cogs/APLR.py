import datetime
import re
import random
from typing import Union

import discord
from discord.ext import commands, tasks
from discord import Option

import AIIO
import d
import logger
import qdrant
import utils
from libs import chunker, embedder


class APLR(commands.Cog):
    ''' APLR | BOT COG'''
    name = "APLR"
    author = ""

    aplrs_to_tick = ["alex_n_volkov"]
    aplrs_cooldowns = {}

    APLR_SEC_PER_TICK = 10
    def __init__(self, bot: discord.Bot):
        global aplrs_cooldowns
        self.bot = bot
        for aplr_id in self.aplrs_to_tick:
            self.aplrs_cooldowns[aplr_id] = random.randint(1, 10)
        self.background.start()

    async def aplr_worker(self, APLR_ID:str, message: Union[discord.Message, None]=None):
        ...
    @tasks.loop(seconds=APLR_SEC_PER_TICK)  # Указываете интервал в секундах
    async def aplr_tick(self):
        for aplr in self.aplrs_to_tick:
            if self.aplrs_cooldowns[aplr] > 0:
                self.aplrs_cooldowns[aplr] -= self.APLR_SEC_PER_TICK
            else:
                self.aplrs_cooldowns[aplr] = random.randint(10, 120)
        pass

    @commands.Cog.listener("on_message")
    async def aplr_on_message(self, message: discord.Message):
        # APLR_ID = "grisha_chaos"
        APLR_ID = "alex_n_volkov"
        LOCATION_ID = "test_meadow"
        # Проверяем, что сообщение пришло в нужный канал
        if message.channel.id == 1337796154498486374:
            # Словарь для соответствия ID пользователей и их ролей
            chars = {
                891289716501119016: "googer",
                609348530498437140: "ow.mn",
                1253778042665308331: "envnnpc",
                # self.bot.user.id: APLR_ID,
                629999906429337600: "michaclown",
            }

            # Белый список пользователей, которые могут взаимодействовать
            whitelist = [891289716501119016, 609348530498437140, 1253778042665308331, 629999906429337600]

            if message.author.id in whitelist:
                # Функция для проверки, является ли сообщение не-RP
                def is_nonrp(text: str):
                    regex = r"^(<[@#]\d+>)*\s*[(\/)+(+)+].*[(\/)+({2,}){2,}]*(<[@#]\d+>)*"
                    mention_regex = r"^(\s*<[@#]\d+>\s*)+$"
                    return re.match(regex, text) or re.match(mention_regex, text) or text in [".", "/", "//", "(", "((",
                                                                                              ")", "))", "", "** **"]

                if is_nonrp(message.content):
                    ...
                else:

                    async with message.channel.typing():
                        # Получаем данные персонажа

                        aplr_doc = d.db.get_collection("characters").find_one({"id": APLR_ID})
                        history = await message.channel.history(limit=50).flatten()
                        history_rp = list(filter(lambda x: not is_nonrp(x.content), history))
                        history_rp_memberids = list(set(map(lambda x: x.author.id, history_rp)))
                        charIDs_to_find = [chars.get(id, None) for id in history_rp_memberids]
                        # remove none\
                        charIDs_to_find = [id for id in charIDs_to_find if id is not None]
                        query = {
                            'id': {'$in': charIDs_to_find},
                            'outer_prompt': {'$exists': True, '$ne': None}
                        }
                        docs = list(d.db.get_collection("characters").find(filter=query))
                        docs_prompts = "\n".join(doc['name'] + ": " + doc['outer_prompt'] for doc in docs)
                        docs_names = {doc['id']: doc['name'] for doc in docs}
                        authors_charid = chars.get(message.author.id, None)
                        char_name = message.author.name
                        if authors_charid:
                            for chardoc in docs:
                                if chardoc['id'] == authors_charid:
                                    char_name = chardoc['name']
                                    break
                        await logger.log(f"Fetched {len(docs)} characters", logger.LogLevel.DEBUG)
                        new_doc = d.schema({"message_id": message.id,
                                            "content": message.content,
                                            "author_id": message.author.id,
                                            "author_charname": char_name,
                                            "author_charid": chars[message.author.id],
                                            "timestamp": message.created_at.timestamp(),
                                            "actor": APLR_ID,
                                            }, d.Schemes.rp_message_v0)
                        messages_collection = d.db.get_collection("rp_messages_v0")
                        messages_collection.insert_one(new_doc)
                        # Количество объектов, которые нужно получить
                        n = 50

                        # Запрос для получения последних n объектов с полем actor, отсортированных по timestamp
                        query = {"actor": APLR_ID}
                        sort_field = [("timestamp", -1)]  # Сортировка по убыванию (последние записи будут первыми)

                        # Выполнение запроса
                        results = messages_collection.find(query).sort(sort_field).limit(n)

                        # Преобразование результатов в список (если нужно)
                        results_list = list(results)
                        # reversing
                        results_list.reverse()

                        # Формируем промпт для AI
                        # location_doc = d.db.get_collection("location").find_one({"id": LOCATION_ID})
                        think_prompt = f"Ты играешь в текстовую ролевую игру. Твой персонаж {aplr_doc['name']}\n" \
                                       f"{aplr_doc['self_prompt']}\n" \
                                       f"И посте можно использовать действия, речь и мысли от лица персонажа, а так же в случае необходимости спросить что-то у других игроков (не персонажей) от своего лица напрямую.\n" \
                                       f"Сейчас твоя задача - продумать что ты будешь отвечать (не написать пост, а именно подумать). ВЕДИ ТОЛЬКО РАЗМЫШЛЕНИЕ ЧТО СТОИТ НАПИСАТЬ. АНАЛИЗИРУЙ И ДУМАЙ А НЕ ПИШИ СООБЩЕНИЕ ДЛЯ ИГРЫ. " \
                                       f"Ниже представлен список персонажей в сессии, а в истории диалога будет представлена сама сессия с подписями.\n" \
                                       f"НИ ПРИ КАКИХ ОБСТОЯТЕЛЬСТВАХ не играй за других персонажей, кроме {aplr_doc['name']}\n" \
                                       f"Учти что в конечном посте (который будет написан но основе твоих размышлений) нельзя будет делать одновременно много всего или написать огромный пост.\n" \
                                       f"Так же для контекста вот воспоминания, вызванные постами:\n" \
                                       f"[nothing to show]\n" \
                                       f"Вот персонажи в игре:\n" \
                                       f"{docs_prompts}"
                        # print(location_doc)
                        prompt = f"Ты - игрок текстовой ролевой игре.\n" \
                                 f"Разметка (соблюдай её предельно осторожно, не выдумывай свою ни в коем случае): действия: **жирный**; мысли персонажа: ||спойлер||; если очень нужно сказать что-то другим пользователям (не персонажам) не от лица персонажа (не рекомендуется без причины): //комментарий в конце поста; для речи разметка не нужна.\n" \
                                 f"Не забудь пробелы и переносы строк. Не повторяйся.\n" \
                                 f"Вот описание твоего персонажа: {aplr_doc['self_prompt']}\n" \
                                 f"Персонажа зовут {aplr_doc['name']} (не пиши свое имя в ответе, твое сообщение и так подписано)\n" \
                                 f"Отвечай на русском, не отвечай за других персонажей ни при каких обстоятельствах. Под твоим управлением ТОЛЬКО {aplr_doc['name']}. Не пиши слишком большие посты за раз.\n" \
                                 f"Вместе с тобой в игре участвуют под управлением других игроков следующие персонажи:\n" \
                                 f"{docs_prompts}\n\n" \
                                 f"Для контекста под некоторыми твоими старыми сообщениями система дописала тебе связанные воспоминания. Они не являются частью оригинального поста. Не пиши их в ответе."
                        # f"\n\n" \
                        # f"Текущая локация: {location_doc['title']}\n" \
                        # f"{location_doc['prompt']}\n"

                        # f"Последнее сообщение в истории - от тебя, это твои размышления (не от лица персонажа) для текущего ответа. их видишь только ты." \

                        # await logger.log("System prompt: "+prompt, logger.LogLevel.DEBUG)
                        # Формируем payload для AI
                        payload = [{"role": "system", "content": prompt}]


                        # Получаем ответ от AI
                        for _message in results_list:
                            role = "assistant" if _message["author_id"] == self.bot.user.id else "user"
                            name = _message["author_charname"]
                            name = f"[{name}]: "
                            if role == "assistant":
                                name = ""
                            memories = _message.get("memories")
                            mems = "\n\n---\n# Связанные воспоминания:\n"
                            if memories and type(memories) == dict:

                                for m in memories.values():
                                    # print(m)
                                    mems += f"{m['chunk']}\n"
                            else:
                                mems=""

                            payload.append({"role": role, "content": name + _message["content"] + "" + mems})
                        payload_thinking = payload.copy()
                        payload_thinking[0] = {"role": "system", "content": think_prompt}
                        # thinking = await AIIO.askBetterLLM(payload_thinking)
                        # await logger.log("AI throughtput for "+str(thinking['total_tokens'])+" tokens on "+thinking['model']+": "+thinking['result'], logger.LogLevel.DEBUG)
                        # payload.append({"role": "assistant", "content": "Это мои размышления, на которые нужно ориентироваться при моем ответе: \n"+thinking['result']})
                        # await logger.log("Payload: " + str(payload), logger.LogLevel.DEBUG)
                        await logger.log("Fetching AI response...", logger.LogLevel.DEBUG)
                        response = await AIIO.askBetterLLM(payload)
                        if response['result'] == "Something went terribly wrong.":
                            await message.reply(
                                "// >>> ОЙ, кажется модуль запросов к ИИ навернулся и ни одна модель даже не ответила. какая жалось :( <<<")
                            return
                        result = response['result']
                        # print(result)
                        if "--- \n# Связанные воспоминания:" in result.lower():
                            # removing this shit from result
                            print("Mem block found")
                            result = result.split("---\n# Связанные воспоминания:")[0]
                        if "//Не стал писать большие куски" in result:
                            # remove from line with this shit this and everything to end of the line
                            print("comment shit block found")
                            lines = result.split("\n")
                            for i in range(len(lines)):
                                if "//Не стал писать большие куски" in lines[i]:
                                    lines[i] = lines[i].split("//Не стал писать большие куски")[0]
                            result = "\n".join(lines)

                        response['result'] = result
                        # msg = await message.reply("### Размышление:\n-# "+thinking['result'].replace("\n", "\n-# ")+"\n\n------\n\n"+response['result'])
                        webhook = None
                        if type(message.channel) == discord.Thread:
                            channel = message.channel.parent
                        else:
                            channel = message.channel
                        for hook in await channel.webhooks():
                            if hook.user.id == self.bot.user.id:
                                webhook = hook
                                break
                        else:

                            try:
                                webhook = await channel.create_webhook(name="RTB hook")
                            except:
                                pass
                        # msg = await message.reply(response['result'])
                        # await webhook.send(response['result'])
                        if len(response['result']) < 2:
                            await message.reply(
                                "// >>> Модель ничерта не ответила. Не, серьезно, пустое сообщение! <<<")
                            await logger.log("EMPTY AI response: " + response['result'], logger.LogLevel.ERROR)
                            return
                        # embed = discord.Embed(title="Что думает этот чертов бот",description="Системный промпт: \n" + prompt,colour=discord.Colour.random())

                        embed = None
                        # embed = discord.Embed(title="Чанки [ДЕБАГ]", description="\n".join(chunks),
                        #                       colour=discord.Colour.random())
                        # TODO: gather chunks



                        if webhook:
                            if type(message.channel) == discord.Thread:
                                msg = await webhook.send(content=response['result'], username=aplr_doc['name'],
                                                         # avatar_url=avatar,
                                                         allowed_mentions=discord.AllowedMentions.none()
                                                         ,
                                                         # files=[await i.to_file() for i in message.attachments],
                                                         thread=discord.Object(message.channel.id),
                                                         wait=True)
                            else:
                                msg = await webhook.send(content=response['result'], username=aplr_doc['name'],
                                                         # avatar_url=avatar,
                                                         allowed_mentions=discord.AllowedMentions.none()

                                                         # files=[await i.to_file() for i in message.attachments],
                                                         , wait=True)
                        else:
                            msg = await message.reply(content=response['result'])

                        # print(payload)

                        chunks = await chunker.split_to_chunks(payload)
                        mem_payload = {}
                        for chunk in chunks:
                            mem_payload[chunk] = await embedder.get_embedding(chunk)  # TODO: асинк
                        mem_uuids = qdrant.add_memories(APLR_ID, mem_payload, datetime.datetime.now().timestamp(),
                                                              LOCATION_ID)
                        if mem_uuids:
                            mem = qdrant.get_memories_by_chunks_uuids(APLR_ID, list(mem_uuids.values()))
                        else:
                            mem = None

                        await logger.log(f"Chunks generated: {chunks}\nMemories found: {mem}", logger.LogLevel.DEBUG)

                        new_doc = d.schema({"message_id": msg.id,
                                            "content": response['result'],
                                            "author_id": msg.author.id,
                                            "author_charname": aplr_doc['name'],
                                            "author_charid": APLR_ID,
                                            "timestamp": message.created_at.timestamp(),
                                            "actor": APLR_ID,
                                            "chunks":mem_uuids,
                                            "memories":mem
                                            }, d.Schemes.rp_message_v0)

                        # messages_collection = d.db.get_collection("rp_messages_v0")
                        messages_collection.insert_one(new_doc)

                        await logger.log(
                            f"APLR on_message event handled using {response['total_tokens']} tokens on {response['model']}",
                            #: {response['result']}
                            logger.LogLevel.DEBUG)


            else:
                if message.author.id == self.bot.user.id:
                    return
                # await message.reply(
                #     "//Мы фигню тестим, не мешай пж. Ну или если у тебя есть анкета в этом боте, попроси тебя сюда прописать.",
                #     delete_after=30)
        else:
            pass


def setup(bot):
    bot.add_cog(APLR(bot))
