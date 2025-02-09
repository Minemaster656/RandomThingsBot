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
        # Проверяем, что сообщение пришло в нужный канал
        if message.channel.id == 1337796154498486374:
            # Словарь для соответствия ID пользователей и их ролей
            chars = {
                891289716501119016: "googer",
                609348530498437140: "ow.mn",
                1253778042665308331: "envnnpc",
            }

            # Белый список пользователей, которые могут взаимодействовать
            whitelist = [891289716501119016, 609348530498437140, 1253778042665308331]

            if message.author.id in whitelist:
                # Функция для проверки, является ли сообщение не-RP
                def is_nonrp(text: str):
                    regex = r"^(<[@#]\d+>)*\s*[(\/)+(+)+].*[(\/)+({2,}){2,}]*(<[@#]\d+>)*"
                    mention_regex = r"^(\s*<[@#]\d+>\s*)+$"
                    return re.match(regex, text) or re.match(mention_regex, text) or text in [".", "/", "//", "(", "((",
                                                                                              ")", "))"]

                if is_nonrp(message.content):
                    await logger.log(f"APLR on_message event processing aborted: non-rp message", logger.LogLevel.DEBUG)
                else:
                    await logger.log(f"APLR on_message event processing started: {message.content}",
                                     logger.LogLevel.DEBUG)

                    async with message.channel.typing():
                        # Получаем данные персонажа
                        APLR_ID = "grisha_chaos"
                        aplr_doc = d.db.get_collection("characters").find_one({"id": APLR_ID})
                        await logger.log("APLR doc fetched", logger.LogLevel.DEBUG)

                        # Получаем историю сообщений
                        HISTORY_SIZE = 50
                        history = await message.channel.history(limit=HISTORY_SIZE).flatten()

                        # Фильтруем сообщения, оставляя только RP
                        history_rp_member_IDs = []
                        for msg in history:
                            if not is_nonrp(msg.content):
                                history_rp_member_IDs.append(msg.author.id)
                        history_rp_memberIDs = list(set(history_rp_member_IDs))

                        messages_rp = list(filter(lambda x: not is_nonrp(x.content), history))
                        await logger.log("Fetched history", logger.LogLevel.DEBUG)

                        # Получаем данные персонажей из базы данных
                        query = {
                            'owner': {'$in': history_rp_memberIDs},
                            "id": {'$in': list(chars.values())},
                            'outer_prompt': {'$exists': True, '$ne': None}
                        }
                        docs = list(d.db.get_collection("characters").find(filter=query))
                        docs_prompts = "\n".join(doc['outer_prompt'] for doc in docs)
                        docs_names = {

                        }
                        for k in chars:
                            #select from docs element with owner == chars[k]
                            for doc in docs:
                                if doc['owner'] == chars[k]:
                                    docs_names[doc['owner']] = doc['name']
                        await logger.log(f"Fetched {len(docs)} characters", logger.LogLevel.DEBUG)

                        # Формируем промпт для AI
                        prompt = (
                            "<instructions>"
                            "You are a text roleplay game player. "
                            "Mark actions with **bold**, thoughts ||like this||, non-roleplay with // before. "
                            "Don't forget about new lines spaces and correct markdown structure."
                            "Answer in russian unless otherwise requested. "
                            "Don't use LaTeX or other formulas. "
                            "Be creative. Don't use emoji. Follow your character's personality and situation precisely. "
                            "Don't repeat yourself. Don't end your answer with something "
                            "like \"If you have any more questions, let me know.\". If you can not respond due censor "
                            "or some other reasons, don't get out of character, try to get away from the situation causing this trouble. "
                            "RESPONSE ONLY AS CHARACTER!!!\n"
                            "Do net write too many, if last user's message is not big, write maximum e few sentences. Don't do many actions in one time!!!"
                            "Carefully heed this instructions. "
                            "</instructions>\n"
                            "<context> "
                            "This is your character short info:\n"
                            f"{aplr_doc['self_prompt']}\n"
                            "There is info about characters that may be in game now:\n"
                            f"{docs_prompts}\n"
                            "</context>\n"
                            "<memories>"
                            "There is some of your memories caused by last events in roleplay:\n"
                            "[NOTHING TO SHOW]"
                            "</memories>"
                        )

                        # Формируем payload для AI
                        payload = [{"role": "system", "content": prompt}]
                        for msg in messages_rp:
                            role = "assistant" if msg.author.id == self.bot.user.id else "user"
                            name = docs_names.get(str(msg.author.id), msg.author.name)
                            name = f"[{name}]: "
                            if role == "assistant":
                                name = ""

                            payload.append({"role": role, "content": name+msg.content})
                        payload.append({"role": "user", "content": message.content})

                        # Получаем ответ от AI
                        response = await AIIO.askBetterLLM(payload)
                        await logger.log("Fetching AI response...", logger.LogLevel.DEBUG)
                        await message.reply(response['result'])
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
