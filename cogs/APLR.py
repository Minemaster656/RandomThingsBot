import re

import discord
from discord.ext import commands
from discord import Option

import logger



class APLR(commands.Cog):
    ''' APLR | BOT COG'''
    name = "APLR"
    author = ""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def aplr_on_message(self, message: discord.Message):
        # await logger.log(f"APLR on_message event handled: {message.content}", logger.LogLevel.DEBUG)
        if message.channel.id == 1337796154498486374:#1236366749658775676 and message.thread.id == 1337796154498486374:
            chars = {
                891289716501119016: "googer",
                609348530498437140: "ow.mn",
                1253778042665308331: "envnnpc",
            }
            await logger.log(f"APLR on_message event processing start: {message.content}", logger.LogLevel.DEBUG)
            if message.author.id in [891289716501119016, 609348530498437140, 1253778042665308331]:

                regex = r"^(<[@#]\d+>)*\s*[(\/)+(+)+].*[(\/)+({2,}){2,}]*(<[@#]\d+>)*"
                if re.match(regex, message.content):
                    # await message.reply("//это нон-рп",delete_after=10)
                    pass

                else:
                    # await message.reply("//это рп сообщение? оно же, да?",delete_after=10)
                    pass
            else:
                if message.author.id == self.bot.user.id:
                    return
                await message.reply(f"//Мы фигню тестим, не мешай пж. ну или если у тебя есть анкета в этом боте попроси тебя сюда прописать я хз",delete_after=30)
        else:
            # await logger.log(f"APLR on_message event handled: {message.content} | Wrong thread: {message.channel.name}:{message.thread}", logger.LogLevel.WARNING)
            pass
def setup(bot):
    bot.add_cog(APLR(bot))
