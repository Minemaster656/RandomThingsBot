import re

import discord
from discord.ext import commands
from discord import Option

import AIIO
import d
import logger



class APLR(commands.Cog):
    ''' APLR | BOT COG'''
    name = "APLR"
    author = ""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def aplr_on_message(self, message: discord.Message):
        # APLR_ID = "grisha_chaos"
        APLR_ID = "alex_n_volkov"
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
                                                                                              ")", "))","","** **"]

                if is_nonrp(message.content):
                    # await logger.log(f"APLR on_message event processing aborted: non-rp message", logger.LogLevel.DEBUG)
                    ...
                else:
                    # await logger.log(f"APLR on_message event processing started: {message.content}",
                    #                  logger.LogLevel.DEBUG)

                    async with message.channel.typing():
                        # Получаем данные персонажа

                        aplr_doc = d.db.get_collection("characters").find_one({"id": APLR_ID})
                        # await logger.log("APLR doc fetched", logger.LogLevel.DEBUG)
                        # await logger.log(aplr_doc, logger.LogLevel.DEBUG)
                        # # Получаем историю сообщений
                        # HISTORY_SIZE = 50
                        # history = await message.channel.history(limit=HISTORY_SIZE).flatten()
                        #
                        # # Фильтруем сообщения, оставляя только RP
                        # history_rp_member_IDs = []
                        # for msg in history:
                        #     if not is_nonrp(msg.content):
                        #         history_rp_member_IDs.append(msg.author.id)
                        # history_rp_memberIDs = list(set(history_rp_member_IDs))
                        #
                        # messages_rp = list(filter(lambda x: not is_nonrp(x.content), history))
                        # await logger.log("Fetched history", logger.LogLevel.DEBUG)
                        #
                        # # Получаем данные персонажей из базы данных
                        # query = {
                        #     'owner': {'$in': history_rp_memberIDs},
                        #     "id": {'$in': list(chars.values())},
                        #     'outer_prompt': {'$exists': True, '$ne': None}
                        # }
                        # docs = list(d.db.get_collection("characters").find(filter=query))
                        # docs_prompts = "\n".join(doc['outer_prompt'] for doc in docs)
                        # docs_names = {
                        #
                        # }
                        # for k in chars:
                        #     #select from docs element with owner == chars[k]
                        #     for doc in docs:
                        #         if doc['owner'] == chars[k]:
                        #             docs_names[doc['owner']] = doc['name']
                        # await logger.log(f"Fetched {len(docs)} characters", logger.LogLevel.DEBUG)
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
                        docs_prompts = "\n".join(doc['name']+": "+doc['outer_prompt'] for doc in docs)
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
                                            "actor":APLR_ID,
                                            }, d.Schemes.rp_message_v0)
                        messages_collection = d.db.get_collection("rp_messages_v0")
                        messages_collection.insert_one(new_doc)
                        # Количество объектов, которые нужно получить
                        n = 10

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
                        # prompt = (
                        #     "<instructions>"
                        #     "You are a text roleplay game player. "
                        #     "Mark actions with **bold**, thoughts ||like this||, non-roleplay with // before. "
                        #     "Don't forget about new lines spaces and correct markdown structure."
                        #     "Answer in russian unless otherwise requested. "
                        #     "Don't use LaTeX or other formulas. "
                        #     "Be creative. Don't use emoji. Follow your character's personality and situation precisely. "
                        #     "Don't repeat yourself. Don't end your answer with something "
                        #     "like \"If you have any more questions, let me know.\". If you can not respond due censor "
                        #     "or some other reasons, don't get out of character, try to get away from the situation causing this trouble. "
                        #     "RESPONSE ONLY AS CHARACTER!!!\n"
                        #     "Do not write too many, if last user's message is not big, write maximum e few sentences. Don't do many actions in one time!!! If you say or do something, await for user's reaction."
                        #     "Carefully heed this instructions. "
                        #     "</instructions>\n"
                        #     "<context> "
                        #     "This is your character short info:\n"
                        #     f"{aplr_doc['self_prompt']}\n"
                        #     "There is info about characters that may be in game now:\n"
                        #     f"{docs_prompts}\n"
                        #     "</context>\n"
                        #     "<memories>"
                        #     "There is some of your memories caused by last events in roleplay:\n"
                        #     "[NOTHING TO SHOW]"
                        #     "</memories>"
                        # )
                        prompt = f"Ты - {aplr_doc['self_prompt']}\n" \
                                 f"Ты игрок в текстовом roleplay. Отвечай от лица персонажа, используя **жирный** для " \
                                 f"разметки действий, ||спойлер|| для мыслей или //два слеша в начале для сообщений не " \
                                 f"от лица персонажа и не являющиеся частью игры. " \
                                 f"Не забудь пробелы, пренеосы строк для читаемости и корректность разметки markdown. " \
                                 f"НИ ПРИ КАКИХ ОБСТОЯТЕЛЬСТВАХ НЕ ВЫХОДИ ИЗ РОЛИ ЗА ИСКЛЮЧЕНИЕМ //нон-рп комментариев, там наоборот ты - управляющий персонажем. " \
                                 f"Если не можешь дать ответ, постарайся уйти от темы, а не пиши что-то вроде 'Я не могу ответить на это'." \
                                 f"Не веди себя как ассистент, забудь про 'Чем вам еще помочь?' или подобных вещах." \
                                 f"Не пиши слишком большие сообщения, только если последнее сообщение игрока не большое." \
                                 f"Сделав дело и/или сказав что-то, жди реакцию от игрока, а не пиши дальше. " \
                                 f"Не делай много всего за 1 пост. " \
                                 f"Будь живым, не стой на месте как палка, не неси бред и не путай персонажей, включая себя. Они все подписаны. Не игнорируй слова и действия игрока. Особенно самые новые. " \
                                 f"Будь самостоятельным, ты не зависишь от других персонажей и можешь действовать сам. НЕ ПОВТОРЯЙ СЕБЯ" \
                                 f"Пиши хоть что-то связанное с игрой. Не пиши пустую строку или только комментарий. ПИШИ ТОЛЬКО ЗА СЕБЯ, {aplr_doc['name']}" \
                                 f"Вероятно, с тобой могут быть эти игроки: \n" \
                                 f"{docs_prompts}\n" \
                                 f"Вот для контекста некоторые твои воспоминания, вызванные событиями в игре:\n" \
                                 f"[nothing to show]"
                        await logger.log("System prompt: "+prompt, logger.LogLevel.DEBUG)
                        # Формируем payload для AI
                        payload = [{"role": "system", "content": prompt}]
                        # for msg in messages_rp:
                        #     role = "assistant" if msg.author.id == self.bot.user.id else "user"
                        #     name = docs_names.get(str(msg.author.id), msg.author.name)
                        #     name = f"[{name}]: "
                        #     if role == "assistant":
                        #         name = ""
                        #
                        #     payload.append({"role": role, "content": name+msg.content})
                        # payload.append({"role": "user", "content": message.content})

                        # Получаем ответ от AI
                        for _message in results_list:
                            role = "assistant" if _message["author_id"] == self.bot.user.id else "user"
                            name = _message["author_charname"]
                            name = f"[{name}]: "
                            if role == "assistant":
                                name = ""
                            payload.append({"role": role, "content": name+_message["content"]})
                        response = await AIIO.askBetterLLM(payload)
                        if response['result'] == "Something went terribly wrong.":
                            await message.reply("// >>> ОЙ, кажется модуль запросов к ИИ навернулся и ни одна модель даже не ответила. какая жалось :( <<<")
                            return
                        await logger.log("Fetching AI response...", logger.LogLevel.DEBUG)
                        msg = await message.reply(response['result'])

                        new_doc = d.schema({"message_id": msg.id,
                                            "content": response['result'],
                                            "author_id": msg.author.id,
                                            "author_charname": "Гриша",
                                            "author_charid": APLR_ID,
                                            "timestamp": message.created_at.timestamp(),
                                            "actor": APLR_ID,
                                            }, d.Schemes.rp_message_v0)
                        # messages_collection = d.db.get_collection("rp_messages_v0")
                        messages_collection.insert_one(new_doc)
                        await logger.log(
                            f"APLR on_message event handled: {response['result']} using {response['total_tokens']} tokens on {response['model']}",
                            logger.LogLevel.DEBUG)


            else:
                if message.author.id == self.bot.user.id:
                    return
                await message.reply(
                    "//Мы фигню тестим, не мешай пж. Ну или если у тебя есть анкета в этом боте, попроси тебя сюда прописать.",
                    delete_after=30)
        else:
            pass
def setup(bot):
    bot.add_cog(APLR(bot))
