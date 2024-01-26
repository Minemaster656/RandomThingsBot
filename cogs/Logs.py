import discord
from discord.ext import commands
from discord import Option

import Data
from Data import db


class Logs(commands.Cog):
    ''' Logs | BOT COG'''
    name = "Logs"
    author = "Minemaster"

    def __init__(self, bot):
        self.bot = bot

    events = ["Вход/выход пользователя", "Обновление пользователя", "Баны",
              "Каналы",
              "Обновление сервера", "Изменение ролей", "Изменение вебхуков",
              "Боты", "Приглашения", "Голосовые каналы", "Изменение и удаление сообщений"]

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name="логи-настроить", description="description")
    async def configlogs(self, ctx, category: Option(str, description="Категория событий", required=True,
                                                     choices=events) = " ",
                         channel: Option(discord.TextChannel, description="Канал для лога", required=True) = 0,
                         mode: Option(str, description="Подробность", required=True,
                                      choices=["Подробно", "Основное", "Отключить"]) = " "
                         ):
        doc = db.logscfg.find_one({"id": ctx.guild.id})
        parsedmodes = {"Подробно": 2, "Основное": 1, "Отключить": 0}
        parsedmode = parsedmodes[mode]
        if doc:
            doc["states"][category] = parsedmode
            doc["channels"][category] = channel.id
            db.logscfg.update_one({"id": ctx.guild.id}, {"$set": doc})
        else:
            default_channels={}
            default_states = {}
            for k in self.events:
                default_states[k]=0
                default_channels[k]=0
            doc = {"id": ctx.guild.id, "states": default_states, "channels": default_channels}
            doc["states"][category]=parsedmode
            doc["channels"][category]=channel.id

            db.logscfg.insert_one(doc)
        embed = discord.Embed(title="Лог настроен!",
                              description=f"Категория: `{category}`\nКанал: <#{channel.id}>\nПодробность: **{mode}**",
                              colour=Data.embedColors["Success"])
        await ctx.respond(embed=embed)


    @commands.Cog.listener("on_member_ban")
    async def on_membar_ban(self, guild, user):
        doc = db.logscfg.find_one({"id":guild.id})
        if doc:
            channel = guild.get_channel(doc["channels"]["Баны"])
            state = doc["states"]["Баны"]
            if channel and state>0:
                try:
                    hooks = await channel.webhooks()
                    hook = None
                    for h in hooks:
                        if h.user.id == self.bot.user.id:
                            hook = h
                            break
                    if not hook:
                        hook = await channel.create_webhook(name="RTB hook")
                    embed = discord.Embed(title="Бан пользователя",description=f"Пользователь `{user.name}` был забанен!",colour=discord.Colour.blue())
                    embed.set_footer(text=f"ID: {user.id}") #TODO: роли, когда присоеденился
                    if state>1:
                        embed.add_field(name="Дополнительная информация",value=f"Аккаунт создан <t:{user.created_at}:R>"
                                                                               f"",inline=False)

                    await hook.send(avatar_url=Data.webhook_avatar_url, username=f"{self.bot.user.name} | 📚Логи", embed=embed)

                except:
                    ...



def setup(bot):
    bot.add_cog(Logs(bot))
