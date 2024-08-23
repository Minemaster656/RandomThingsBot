import datetime
import json
import time

# try:
import discord
from discord import Option, Webhook, Forbidden
from discord.ext import commands, tasks
# except:
#     import pycord as discord
#     from pycord import Option, Webhook, Forbidden
#     from discord.ext import commands, tasks

import Data
import utils
from Data import db, getEmbedColor, EmbedColor, preffix
import d


class social(commands.Cog):
    ''' social | BOT COG'''
    name = "social"
    author = "Minemaster"

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.background.start()

    social = discord.SlashCommandGroup(
        "социал",
        "",

    )
    coRPlayerFindRequest_ExpirationTime = 600000  # in ms

    def getUTC(self) -> int:
        # TODO: часовой пояс
        current_time_utc = datetime.datetime.utcnow()

        timestamp_utc_ms = int(current_time_utc.timestamp() * 1000)
        # print(timestamp_utc_ms)
        return timestamp_utc_ms

    def UTCtoTimestamp(self, utcValueInMS):
        return int(utcValueInMS / 1000)

    @tasks.loop(seconds=10)  # Указываете интервал в секундах
    async def background(self):
        # print("BG")
        for doc in db.coRPsFindRequests.find(
                {"timestamp": {"$lt": self.getUTC() - self.coRPlayerFindRequest_ExpirationTime}}):
            user = self.bot.get_user(doc['uid'])
            # print(doc)
            if user:
                await user.send(f"Ваш запрос на поиск сорола на сервере **{doc['gname']}** истёк!")
            db.coRPsFindRequests.delete_one(doc)
        # print("BG")

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(aliases=["начать-поиск-сорола"])
    async def startFindCoRPlayer(self, ctx: commands.Context):
        doc = db.coRPsFindRequests.find_one({"gid": ctx.author.guild.id, "uid": ctx.author.id})

        if not doc:
            utc = self.getUTC()
            db.coRPsFindRequests.insert_one(
                {"gid": ctx.author.guild.id, "uid": ctx.author.id, "gname": ctx.guild.name, "uname": ctx.author.name,
                 "timestamp": utc})
            await ctx.reply(
                f"Запрос на поиск сорола отправлен для этого сервера! Он истечёт <t:{self.UTCtoTimestamp(utc + self.coRPlayerFindRequest_ExpirationTime)}:R>."
                f"\nОтменить - `{preffix}начать-поиск-сорола` | Поиск других соролов - `{preffix}поиск-сорола`",
                delete_after=10)
        else:
            await ctx.reply(
                f"У вас уже есть запрос на поиск сорола, который истечет <t:{self.UTCtoTimestamp(doc['timestamp'] + self.coRPlayerFindRequest_ExpirationTime)}:R>.",
                delete_after=10)

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(aliases=["отменить-поиск-сорола"])
    async def cancelFindCoRPlayer(self, ctx: commands.Context):
        doc = db.coRPsFindRequests.find_one({"gid": ctx.author.guild.id, "uid": ctx.author.id})
        if doc:
            await ctx.reply("Поиск сорола отменён на этом сервере.", delete_after=10)
            db.coRPsFindRequests.delete_one({"gid": ctx.author.guild.id, "uid": ctx.author.id})
        else:
            await ctx.reply(f"Вы не начали поиск сорола. Сделать это можно командой `{preffix}начать-поиск-сорола`",
                            delete_after=10)

    @commands.command(aliases=["поиск-сорола"])
    async def findCoRPlayer(self, ctx: commands.Context):
        embedContent = ""
        for doc in db.coRPsFindRequests.find({"gid": ctx.guild.id}):
            embedContent += f"<@{doc['uid']}> ищет сорола! Найти его персонажей - </поиск-персонажей-пользователя:1203654817692778538>. Поиск заканчивается <t:{self.UTCtoTimestamp(doc['timestamp'] + self.coRPlayerFindRequest_ExpirationTime)}:R>\n"
        embedContent = utils.formatStringLength(embedContent, 3990)
        if embedContent == "":
            embedContent = "Никто не ищет сорола"
        embed = discord.Embed(title="Кто сейчас ищет сорола", description=f"{embedContent}",
                              colour=getEmbedColor(EmbedColor.Neutral))

        await ctx.reply(embed=embed)

    # @commands.Cog.listener("on_presence_update")
    # async def on_presence_update(self, before:discord.Member, after:discord.Member):
    #     ...
    # if before.activity != after.activity:
    #     print(after.name)
    #     before_activity_name=""
    #     after_activity_name=""
    #     if before.activity:
    #         before_activity_name=before.activity.name
    #     if after.activity:
    #         after_activity_name=after.activity.name
    #     print(before_activity_name, "   ==>   ", after_activity_name)

    @commands.command(aliases=["осебе", "профиль", "profile"])
    async def about(self, ctx, user: discord.Member = None):
        async with ctx.typing():
            if user is None:
                user = ctx.author
            userid = user.id
            print("finding result")
            result = None
            try:
                result = db.users.find({"userid": userid})[0]
                result = d.schema(result, d.Schemes.user)
            except:
                print(result)
                # if not result:
                #     Data.writeUserToDB(ctx.author.id, ctx.author.name)

            async def send_user_info_embed(color, about, age, timezone, karma, luck, permissions, xp, doc):
                def convertKarmaToEmoji(karma):
                    if karma < -1:
                        return "⬛"
                    elif karma > 1:
                        return "⬜"
                    else:
                        return "🔲"

                def convertLuckToEmoji(luck):
                    if luck < -10:
                        return "⬛"
                    elif luck < -5:
                        return "🟫"
                    elif luck < -3:
                        return "🟥"
                    elif luck < -1:
                        return "🟧"

                    elif luck > 10:
                        return "🟪"
                    elif luck > 5:
                        return "🟦"
                    elif luck > 3:
                        return "🟩"
                    elif luck > 1:
                        return "🟨"



                    else:
                        return "⬜"

                icons = " "
                try:
                    perms = json.loads(permissions)
                except:
                    perms = {}
                if "verified" in perms.keys():
                    icons += Data.icons[Data.Icons.verified] if perms["verified"] else ""
                if "root" in perms.keys():
                    icons += Data.icons[Data.Icons.root] if perms["root"] else ""
                if "edit_characters" in perms.keys():
                    icons += Data.icons[Data.Icons.edit_characters] if perms["edit_characters"] else ""
                if doc['banned'] == 1:
                    icons += Data.icons[Data.Icons.banned1]
                if doc['banned'] > 1:
                    icons += Data.icons[Data.Icons.banned2]
                embed = discord.Embed(title=user.display_name + icons, description=user.name, color=color)
                embed.add_field(name="О себе", value="> *" + about + "*", inline=False)
                embed.add_field(name="Личные данные", value="- Возраст: " + age + "\n- Часовой пояс: UTC+" + timezone,
                                inline=True)

                embed.add_field(name="прочее", value=f"{convertKarmaToEmoji(karma)}{convertLuckToEmoji(luck)}",
                                inline=False)
                embed.add_field(name="Разрешения", value=f"{str(permissions)}", inline=False)
                xps = utils.calc_levelByXP(xp)
                embed.add_field(name="Опыт",
                                value=f"Всего опыта: {xp}\nУровень: {xps[0]}\nОпыта до следующего уровня: {xps[2]}",
                                inline=False)
                embed.add_field(name="Экономика",
                                value=f"На руках: {utils.format_number(doc['money'])}{Data.currency}\n"
                                      f"В банке: {utils.format_number(doc['money_bank'])}{Data.currency}\n")
                embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
                embed.set_footer(
                    text=f'Для редактирования параметров - \"{Data.preffix}редактировать\" - там вся нужная информация.'
                         f' Для справки используйте **помощь** или просто !!редактировать.\n'
                         f'Для редактирования данных для ИИ используйте {Data.preffix}редактировать-ии')

                embed.add_field(name="Автоответчики",
                                value=f"Автоответчик {'✅ВКЛЮЧЕН✅' if doc['autoresponder'] else '❌ВЫКЛЮЧЕН❌'}\n\n"
                                      f"# НЕ БЕСПОКОИТЬ: **{doc['autoresponder-disturb']}**\n\n"
                                      f"# НЕАКТИВЕН: **{doc['autoresponder-inactive']}**\n\n"
                                      f"# ОФФЛАЙН: **{doc['autoresponder-offline']}**", inline=False)
                await ctx.send(f"[Страница пользователя](https://glitchdev.ru/user/{doc['username']})", embed=embed)

            if result:
                await ctx.send("Запись найдена")

                clr = 0x5865F2 if result["color"] is None else result["color"]
                abt = "Задать поле 'О себе' можно командой `!!редактировать осебе`" if result["about"] is None else \
                    result[
                        "about"]
                tmz = "UTC+?. Задать часовой пояс можно командой `.редактировать часовойпояс`. Укажите свой часовой пояс относительно Гринвича." if \
                    result["timezone"] is None else str(result["timezone"])
                age = "Задать поле 'Возраст' можно командой `!!редактировать возраст`\nПожалуйста, ставьте только свой реальный возраст, не смотря на то, сколько вам лет." if \
                    result["age"] is None else str(result["age"])
                karma = 0 if result["karma"] is None else str(result["karma"])
                luck = 0 if result["luck"] is None else str(result["luck"])
                result = d.schema(result, d.Schemes.user)
                await send_user_info_embed(clr, abt, age, tmz, int(karma), int(luck),
                                           result["permissions"], result["xp"],
                                           result)  # if result["permissions"] is None else '{}'
            else:
                await ctx.send("Запись о пользователе не найдена. Добавление...")
                doc = Data.writeUserToDB(user.id, user.name)
                doc = d.schema(doc, d.Schemes.user)

                await send_user_info_embed(0x5865F2, "Задать поле 'О себе' можно командой !!редактировать осебе",
                                           "Задать поле 'Возраст' можно командой `!!редактировать возраст`\nПожалуйста, ставьте только свой реальный возраст, не смотря на то, сколько вам лет.",
                                           "UTC+?. Задать часовой пояс можно командой `!!редактировать часовойпояс`. Укажите свой часовой пояс относительно Гринвича.",
                                           0, 0, None, 0, doc)
                # TODO: прогрессбар уровня

    @commands.command(aliases=["редактировать", "ё"])
    async def edit(self, ctx: commands.Context, field="помощь", *, value=None):
        bans = [629999906429337600]  # 1064870586985234434
        if ctx.author.id in bans:
            await ctx.reply("Вы забанены в этой команде!", delete_after=5)
            return
        doc = db.users.find_one({"userid": ctx.author.id})
        if not doc:
            doc = await Data.writeUserToDB(ctx.author.id, ctx.author.name)
        if field == "осебе":
            db.users.update_one({"userid": ctx.author.id}, {"$set": {"about": value}})
            await ctx.reply("**Строка** `осебе` (!!осебе) изменена!")
        elif field == "возраст":
            db.users.update_one({"userid": ctx.author.id}, {"$set": {"age": int(value)}})
            await ctx.reply("**Число** `возраст` (!!осебе) изменено!")
        elif field == "часовойпояс":
            db.users.update_one({"userid": ctx.author.id}, {"$set": {"timezone": int(value)}})
            await ctx.reply("**Число** `часовойпояс` (!!осебе) изменено!")
        elif field == "цвет":
            db.users.update_one({"userid": ctx.author.id}, {"$set": {"color": utils.parseColorTo0xHEX(value)}})
            await ctx.reply("**Цвет профиля** `цвет` (!!осебе) изменен!")


        elif field == "автоответчик":
            no = ["0", "нет", "false", "False", "no", "ложь"]
            pvalue = not value in no
            if value is None:
                doc = db.users.find_one({"userid": ctx.author.id})
                pvalue = not doc["autoresponder"]

            db.users.update_one({"userid": ctx.author.id}, {"$set": {"autoresponder": pvalue}})

            await ctx.reply(f"Автоответчик **{'включен' if pvalue else 'выключен'}**\n"
                            f"Если вы хотите задать текст для автоответчика, то используйте в качестве поля не **автоответчик** а **автоответчик-статус**, где статус - неактивен, оффлайн или небеспокоить. Для отчистки строки просто оставьте строку пустой.")

        elif field == "автоответчик-неактивен":
            db.users.update_one({"userid": ctx.author.id},
                                {"$set": {"autoresponder-inactive": value if value != '-' else None}})
            await ctx.reply(f"Автоответчик **неактивен** изменён на `{value if value != '-' else 'ОТСУТСТВИЕ ОТВЕТА'}`")

        elif field == "автоответчик-оффлайн":
            db.users.update_one({"userid": ctx.author.id},
                                {"$set": {"autoresponder-offline": value if value != '-' else None}})
            await ctx.reply(f"Автоответчик **оффлайн** изменён на `{value if value != '-' else 'ОТСУТСТВИЕ ОТВЕТА'}`")

        elif field == "автоответчик-небеспокоить":
            db.users.update_one({"userid": ctx.author.id},
                                {"$set": {"autoresponder-disturb": value if value != '-' else None}})
            await ctx.reply(
                f"Автоответчик **небеспокоить** изменён на `{value if value != '-' else 'ОТСУТСТВИЕ ОТВЕТА'}`")
        elif field == "пол":
            gender = None if value == '-' else True if value == 'м' else False if value == 'ж' else None
            db.users.update_one({"userid": ctx.author.id},
                                {"$set": {"bio_gender": gender}})
            await ctx.reply(
                f"Запись о вашем поле изменена на `{'Мужской' if gender else 'Женский' if gender is False else 'Не установлено'}`")
        elif field == "др" or field == "деньрождения":
            day = None
            month = None
            year = None

            parts = value.split('.')
            try:
                if len(parts) == 3:
                    day = int(parts[0])
                    month = int(parts[1])
                    year = int(parts[2])

                elif value == '-':
                    day = 0
                    month = 0
                    year = 0
                else:
                    await ctx.reply("Введённая вами некорректная.")
                    return
                db.users.update_one({"userid": ctx.author.id},
                                    {"$set": {"birthday_day": day, "birthday_month": month, "birthday_year": year}})
                await ctx.reply(f"Ваш день рождения записан как `{value}`.")
            except:
                await ctx.reply("Введённая вами некорректная.")

        elif field == "помощь":
            embed = discord.Embed(title="Помощь по редактированию",
                                  description=f'Редактировать - {Data.preffix}редактировать <поле> "значение" (<> не писать)\n'
                                              f'Вставка значений: в разработке',
                                  colour=Data.getEmbedColor(Data.EmbedColor.Neutral))
            embed.add_field(name="осебе", value="Строка О себе. Принимает любую строку", inline=False)
            embed.add_field(name="возраст", value="Ваш возраст: число", inline=False)
            embed.add_field(name="часовойпояс", value="Часовой пояс относительно гринвича. Число", inline=False)
            embed.add_field(name="цвет", value="Цвет вашего профиля в HEX-записи.", inline=False)
            embed.add_field(name="Автоответчики",
                            value=f"`автоответчик` - любое значение кроме 0, нет, ложь, false, False включает автоответчики\n"
                                  f"`автоответчик-неактивен` - строка для автоответчика, когда вы неактивны\n"
                                  f"`автоответчик-оффлайн` - строка для автоответчика, когда вы оффлайн\n"
                                  f"`автоответчик-небеспокоить` - строка для автоответчика, когда у вас стоит статус не беспокоить.\n"
                                  f"Что бы отключить конкретный автоответчик - ничего не вписывайте в качестве значения.",
                            inline=False)
            embed.add_field(name="пол", value="`пол` - Указывает ваш (билогический) пол.\nВпишите `м` для мужского, `ж` для"
                                              " женского. Если ваш пол - ковролин, ламинат, плитка, другие строительные "
                                              "материалы, вы считаете что он не вписывается в то, что придумала природа "
                                              "или вы просто не хотите его говорить или хотите сбросить - впришите `-` "
                                              "(так же это будет \"не указано\", что идёт по умолчанию)", inline=False)
            embed.add_field(name="День рождения",value="`деньрождения` или `др` Указыват ваш день рождения. Впишите в формате дд.мм.гггг вашу НАСТОЯЩУЮ дату рождения. "
                                                       "Учтите, что возраст НЕ будет перерасчитан при дне рождения или установке. Для сброса впишите `-`.",inline=False)
            await ctx.reply(embed=embed)
        else:
            ctx.reply("Допустимые параметры:\n"
                      "- осебе (строка)\n"
                      "- часовойпояс (целое число)\n"
                      "- возраст (целое число)")


def setup(bot):
    bot.add_cog(social(bot))
