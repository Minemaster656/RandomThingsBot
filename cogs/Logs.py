import discord
from discord.ext import commands
from discord import Option

import Data
import utils
from Data import db
import datetime


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
            default_channels = {}
            default_states = {}
            for k in self.events:
                default_states[k] = 0
                default_channels[k] = 0
            doc = {"id": ctx.guild.id, "states": default_states, "channels": default_channels}
            doc["states"][category] = parsedmode
            doc["channels"][category] = channel.id

            db.logscfg.insert_one(doc)
        embed = discord.Embed(title="Лог настроен!",
                              description=f"Категория: `{category}`\nКанал: <#{channel.id}>\nПодробность: **{mode}**",
                              colour=Data.embedColors["Success"])
        await ctx.respond(embed=embed)

    async def sendLog(self, category, embed):
        ...

    @commands.Cog.listener("on_member_ban")
    async def on_member_ban(self, guild, user):
        doc = db.logscfg.find_one({"id": guild.id})
        if doc:
            channel = guild.get_channel(doc["channels"]["Баны"])
            state = doc["states"]["Баны"]
            if channel and state > 0:
                try:
                    hook = await utils.initWebhook(channel, self.bot.user.id)
                    if not hook:
                        return
                    embed = discord.Embed(title="Бан пользователя",
                                          description=f"Пользователь `{user.name}` был забанен!",
                                          colour=discord.Colour.red())
                    if isinstance(user, discord.Member):
                        result = ', '.join([f'<@&{role.id}>' for role in user.roles[1:]])
                        output = f'{result}, ' if len(user.roles) > 1 else ''
                        userdata = f"Пользователь присоеденился к серверу <t:{int(user.joined_at.timestamp())}:R>.\n" \
                                   f"**Роли:**{output}"
                    else:
                        userdata = "Больше информации не найдено."
                    embed.add_field(name="Дополнительная информация", value=f"Аккаунт создан <t:{'AAA'}:R>\n" + userdata
                                    , inline=False)
                    embed.set_footer(text=f"ID: {user.id}")
                    if state > 1:
                        ...
                    await hook.send(avatar_url=Data.webhook_avatar_url, username=f"{self.bot.user.name} | 📚Логи",
                                    embed=embed)


                except:
                    ...

    @commands.Cog.listener("on_member_unban")
    async def on_member_unban(self, guild, user):
        doc = db.logscfg.find_one({"id": guild.id})
        if doc:
            channel = guild.get_channel(doc["channels"]["Баны"])
            state = doc["states"]["Баны"]
            if channel and state > 0:
                # try:
                hook = None
                # try:
                hooks = await channel.webhooks()
                hook = None
                for h in hooks:
                    if h.user.id == self.bot.user.id:
                        hook = h
                        break
                if not hook:
                    hook = await channel.create_webhook(name="RTB hook")
                    # return hook
                    # hook=await utils.initWebhook(channel, self.bot.user.id)
                # except:
                #
                #
                #     ...
                # hook = await utils.initWebhook(channel, self.bot.user.id)
                print(hook)
                if not hook:
                    print("NO HOOK")
                    return

                embed = discord.Embed(title="Разбан пользователя",
                                      description=f"Пользователь `{user.name}` был разбанен!",
                                      colour=discord.Colour.green())
                if isinstance(user, discord.Member):
                    result = ', '.join([f'<@&{role.id}>' for role in user.roles[1:]])
                    output = f'{result}, ' if len(user.roles) > 1 else ''
                    userdata = f"Пользователь присоеденился к серверу <t:{int(user.joined_at.timestamp())}:R>.\n" \
                               f"**Роли:**{output}"
                else:
                    userdata = "Больше информации не найдено."
                embed.add_field(name="Дополнительная информация",
                                value=f"Аккаунт создан <t:{int(user.created_at.timestamp())}:R>\n" + userdata
                                , inline=False)
                embed.set_footer(text=f"ID: {user.id}")
                if state > 1:
                    ...
                await hook.send(avatar_url=Data.webhook_avatar_url, username=f"{self.bot.user.name} | 📚Логи",
                                embed=embed, content="** **")
                print("SENT")

                # except:
                #     ...


def setup(bot):
    bot.add_cog(Logs(bot))
# TODO: ЭТО КУСОК НЕРАБОЧЕГО ГОВНОКОДА. ЕГО НУЖНО СЖЕЧЬ!!!
