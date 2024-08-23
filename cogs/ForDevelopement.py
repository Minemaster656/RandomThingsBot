import datetime
import hashlib
import time

# try:
import discord
from discord import Option, Webhook, Forbidden
from discord.ext import commands
# except:
#     import pycord as discord
#     from pycord import Option, Webhook, Forbidden
#     from discord.ext import commands

import AIIO
import Data
import d
import utils
from Data import db, EmbedColor


class ForDevelopement(commands.Cog):
    ''' ForDevelopement | BOT COG'''
    name = "ForDevelopement"
    author = ""

    def __init__(self, bot):
        self.bot = bot

    def makeIdeaEmbed(self, doc):
        '''Принимает документ с идеей, предназначенный для MongoDB, возвращает эмбед'''
        colors = {
            "Этот бот": Data.getEmbedColor(EmbedColor.Neutral),
            "Наш сайт": Data.getEmbedColor(EmbedColor.Warp),
            "Забанить/разбанить кого-либо в боте": Data.getEmbedColor(EmbedColor.Error)
        }
        embed = discord.Embed(title=f"Предложение от {doc['author']}", description=f"{doc['content']}",
                              colour=colors[doc['category']])

        embed.set_footer(
            text=f"ID: {doc['authorid']} | {doc['category']} | Сервер: {doc['guildid']} | Хэш: {doc['hash']}")
        # embed.timestamp=doc["timestamp"]
        return embed

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.slash_command(name="предложить-идею",
                            description="Отправляет вашу чудесную идею касательно бота или сайта на рассмотрение")
    async def addIdea(self, ctx,
                      idea: Option(str, description="Ваша идея. \n для новой строки. Поддерживается разметка.",
                                   required=True) = " ",
                      category: Option(str,
                                       description="Категория предложения. Для банов ОБЯЗАТЕЛЬНО укажите ID пользователя и доказательста.",
                                       choices=[
                                           'Этот бот', 'Наш сайт', 'Забанить/разбанить кого-либо в боте'
                                       ], required=True) = " "):
        user = Data.writeUserToDB(ctx.author.id, ctx.author.name)
        user = d.schema(user, d.Schemes.user)
        db.users.update_one({"userid": ctx.author.id}, {"$set": user})
        if user['banned'] > 0:
            embed = discord.Embed(title="Нет доступа!",
                                  description=f"Вы забанены в этом боте!\n{'Более того, вы помечены как опасный человек!' if user['banned'] > 1 else ''}",
                                  colour=Data.embedColors["Error"])
            await ctx.respond(embed=embed)
            return
        doc = db.ideas.find_one({"hash": utils.md5(idea)})
        if doc:
            await ctx.respond("Такая идея уже предложена и находится на рассмотрении!!!", ephemeral=True)
            return
        doc = {
            'author': ctx.author.name,
            'authorid': ctx.author.id,
            'category': category,
            'content': idea,
            # 'timestamp':int(time.time()/1000),
            'guildid': ctx.guild.id,
            'hash': utils.md5(idea)
        }
        db.ideas.insert_one(doc)
        embed = self.makeIdeaEmbed(doc)
        await ctx.respond(
            "Если Вашу идею одобрят, Вы получите опыт, если же отклонят, Вы всё равно можете получить опыт.Просьба не спамить этой командой и не отправлять бессмыслицу.",
            embed=embed)
        guild = self.bot.get_guild(Data.team_server_id)
        if guild is None:
            found = False
        else:
            channel = guild.get_channel(Data.ideasChannel)
            message = f"# Новая идея!!!\nСервер: {ctx.guild.name} (`{ctx.guild.id}`)\nПользователь: {ctx.author.name} (`{ctx.author.id}`)\nКанал: {ctx.channel.name} (`{ctx.channel.id}`)"

            await channel.send(message, embed=embed)

    @commands.slash_command(name="случайная-идея", description="Выводит случайную идею")
    async def getRandomIdea(self, ctx):
        # pipeline = [{"$sample": {"size": 1}}]
        # random_document = list(db.ideas.aggregate(pipeline))
        rdocs = db.ideas.aggregate([{"$sample": {"size": 1}}])

        random_document = next(rdocs, None)
        if not random_document:
            await ctx.respond("Идей нет. Можете предложить свою с помощью /предложить-идею")
            return
        await ctx.respond(embed=self.makeIdeaEmbed(random_document))

    @commands.slash_command(name="рассмотреть-идею", description="Принимает идею. 🚧 Только для админов бота.", guilds=Data.BOT_INTERNAL_COMMANDS_GUILDS)
    async def checkIdea(self, ctx, hash: Option(str, description="Хэш идеи", required=True) = "",
                        xp: Option(float, description="Сколько опыта выдать?", required=True) = 25,
                        dest: Option(str, description="Одобрить или отклонить",
                                     choices=["Одобрить", "Отклонить и удалить"], required=True) = " "):
        idea = db.ideas.find_one({'hash': hash})
        if not ctx.author.id in Data.devs:
            await ctx.respond("Доступно только разработчикам бота!", ephemeral=True)
            return
        if idea:

            new_data = {
                '$set': {
                    'checkedat': int(time.time() / 1000),
                    'checker': ctx.author.id
                }
            }
            db.ideas.update_one({'_id': idea['_id']}, new_data)

            # Перенос документа в другую коллекцию
            if dest == "Одобрить":
                db.ideasApproved.insert_one(idea)

            # Удаление документа из коллекции 'ideas'
            db.ideas.delete_one({'_id': idea['_id']})
            db.users.update_one({"userid": idea["authorid"]}, {"$inc": {"xp": xp}})
            user = self.bot.get_user(idea["authorid"])
            await ctx.respond("Успешно!", ephemeral=True)

            if user is None:
                user = await self.bot.fetch_user(self.user_id)

            if user:
                await user.send(f"# Привет!\n"
                                f"Твою идею **{'одобрили' if dest == 'Одобрить' else 'отклонили'}**\n"
                                f"Тебе начислено **{xp}** опыта."
                                f"Твоя идея:", embed=self.makeIdeaEmbed(idea))

        else:
            await ctx.respond(f"Идея {hash} не найдена!")

    @commands.slash_command(name="забанить-разбанить-пользователя",
                            description="Банит или разбанивает пользователя в БОТЕ. 🚧 Только для админов бота.", guilds=Data.BOT_INTERNAL_COMMANDS_GUILDS)
    async def banOrUnbanUser(self, ctx, id: Option(str, description="ID пользователя", required=True) = "",
                             state: Option(str, description="",
                                           choices=["Разбанить", "Забанить команды и доступы", "Забанить в боте"],
                                           required=True) = ""):
        try:
            id = int(id)
        except:
            await ctx.respond("Неверный ID!", ephemeral=True)
            return
        states = {"Разбанить": 0, "Забанить команды и доступы": 1, "Забанить в боте": 2}
        user = self.bot.get_user(id)

        if user is None:
            user = await self.bot.fetch_user(self.user_id)
        doc = Data.writeUserToDB(id, user.name)
        if not await Data.parsePermissionFromUser(ctx.author.id, "root"):
            await ctx.respond("У Вас нет разрешения на это!!!", ephemeral=True)
            return
        if doc:
            doc['banned'] = states[state]
            if doc['banned'] > 0:
                doc['permissions'] = None
            await ctx.respond("Успешно!", ephemeral=True)
            db.users.update_one({"userid": id}, {"$set": doc})

            if user:
                message = ""
                if states[state] == 0:
                    message += "# Тебя разбанили в этом боте!"
                elif states[state] == 1:
                    message += "# Тебе забанили использование команд в этом боте!"
                    message += "\nТак же при заходе на сервер с включёнными уведомлениями об опасных пользователях, система сообщит о тебе!"
                else:
                    message += "# Тебя забанили в этом боте!"
                    message += "\nТак же при заходе на сервер с включёнными уведомлениями об опасных пользователях, система сообщит о тебе!"

                await user.send(message)
        else:
            await ctx.respond("Не найдено!", ephemeral=True)


def setup(bot):
    bot.add_cog(ForDevelopement(bot))
