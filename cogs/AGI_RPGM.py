import discord
from discord.ext import commands
from discord import Option
import AIIO
import utils


class AGI_RPGM(commands.Cog):
    ''' AGI_RPGM | BOT COG'''
    name = "AGI_RPGM"
    author = ""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.command(aliases=["иигм"])
    async def airpgm(self, ctx: commands.Context):

        history_size = 5

        messages = await ctx.channel.history(limit=history_size).flatten()
        messages.reverse()
        for message in messages:
            await ctx.reply(message.content)

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.message_command(name="Сгенерировать РП пост")
    async def gen_RP_post(self, ctx, message: discord.Message):

        history_size = 25

        messages = await ctx.channel.history(limit=history_size).flatten()
        messages.reverse()
        messages_content = []
        total_symbols = 0
        max_symbols = 8000
        for message in messages:
            if total_symbols <= max_symbols:

                if not message.content.startswith("//") and not message.content.startswith("(("):
                    messages_content.append({"content": message.content, "name": message.author.name})
                    total_symbols += len(message.content)
            else:
                break
        if False:
            ...
        else:
            # userdoc = d.getUser(ctx.author.id, ctx.author.name)
            # if await Data.parsePermissionFromUser(ctx.author.id, "root") or await Data.parsePermissionFromUser(ctx.author.id, "edit_characters"):
            payload = [{"role": "system",
                        "content": f"Ты ИИ-ГМ в текстовом РП. твоя задача - написать пост в ответ на пост пользователя. Вероятно, это будет описанием окружения, реже - описанием NPC и их действий. Как твои ответы помечены так же ответы от других ГМов, но если это не так, то их ники все равно зачастую либо Окружение, либо Окружение и NPC либо судьба и всякое в этом роде.\nДействия и описания (не речью) заключены в *описания или одинарные звездочки**, мысли в ||двойные палочки|| или иногда в (скобочки). Частью РП поста не является сообщение о расходе токенов. Структура > текст [jump](link) это ответ на сообщение. Отвечай на  русском!! В ответе пиши ТОЛЬКО текст поста от лица ГМа, не добавляй никаких прочих пояснений!! Название локации - {message.channel.name}. Не пиши от лица персонажей! Не отвечай на старые сообщения, они нужны только для предоставления контекста!"
                        },
                       # Если в ответе ты начинаешь повторять одно и то же, перкрати ответ.
                       {"role": "user", "content": message.content}]
            for msg in messages_content:
                if "окружение" in msg["name"].lower() or "NPC" in msg["name"].lower() or "судьба" in msg[
                    "name"].lower() or msg["name"] == str(self.bot.user)[:-5]:
                    payload.append({"role": "assistant", "content": msg['content']})
                else:
                    payload.append({"role": "user", "content": "[" + msg["name"] + "]: " + msg['content']})
            # print(payload)
            response = await AIIO.askBetterLLM(payload, 8000)

            tokens = response['total_tokens']
            resp = response['result']

            tokenInfo = "\n" + f"||Использовано {tokens} токен{'ов' if tokens % 100 in (11, 12, 13, 14, 15) else 'а' if tokens % 10 in (2, 3, 4) else '' if tokens % 10 == 1 else 'ов'}||"
            output = resp + tokenInfo

            outputs = utils.split_string(output, 2000, len(tokenInfo))
            for content in outputs:
                print("|||", content)

                await ctx.send(content)
                # print("...")
                #
                # await ctx.send(content)

            # await ctx.respond()
            # else:
            # await ctx.respond("Вы не анкетолог.")


def setup(bot):
    bot.add_cog(AGI_RPGM(bot))
