import datetime

import discord
from discord.ext import commands
from discord import Option

from discord import SlashCommandGroup

import d
import utils
from logger import log, LogLevel


class WPG(commands.Cog):
    ''' WPG | BOT COG'''
    name = "WPG"
    author = "Minemaster for Crepil"

    wpg_commands = discord.SlashCommandGroup(
        "впи", ""

    )
    wpg_masters = [
        723854737497128970,  # crepil
        663010344150499368,  # john
        609348530498437140,  # minemaster
    ]

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @wpg_commands.command(name="создать-город", description="Добавляет город в базу данных")
    async def add_city(self, ctx: discord.ApplicationContext,
                       owner: Option(discord.Member, description="Чей город", required=True),
                       name: Option(str, description="Название города", required=True),
                       starting_unemployed: Option(int, description="Начальное количество безработных", required=True),
                       starting_children: Option(int, description="Начальное количество детей", required=True)):
        if not ctx.author.id in self.wpg_masters:
            await ctx.respond("Вы не можете этого сделать.", ephemeral=True)
            await log(
                f"{ctx.author.name} ({ctx.author.id}) (GUILD: {ctx.guild.id}) пытался создать город, но у него нет прав",
                LogLevel.WARNING)
            return

        collection = d.db.get_collection("wpg_cities")
        scheme = d.Schemes.WPG_city

        same_name = collection.find_one({"city_name": name})
        if same_name:
            await ctx.respond("Город с таким названием уже есть!", ephemeral=True)
            await log(
                f"{ctx.author.name} ({ctx.author.id}) (GUILD: {ctx.guild.id}) пытался создать город с уже существующим названием",
                LogLevel.WARNING)
            return
        doc = d.schema({
            "city_name": name,
            "owner_id": owner.id,
            "unemployed": starting_unemployed,
            "children": starting_children,
            "created_timestamp": datetime.datetime.now().timestamp(),
            "edited_timestamp": datetime.datetime.now().timestamp(),
        }, scheme=scheme)
        collection.insert_one(doc)

        await ctx.respond(f"Город **{name}** создан и принадлежит <@{owner.id}>!", ephemeral=False)
        await log(f"{ctx.author.name} ({ctx.author.id}) (GUILD: {ctx.guild.id}) создал город **{name}**", LogLevel.INFO)

    @wpg_commands.command(name="посмотреть-город", description="Показывает город из базы данных")
    async def view_city(self, ctx: discord.ApplicationContext,
                        city_name: Option(str, description="Название города", required=True)):
        collection = d.db.get_collection("wpg_cities")

        city = collection.find_one({"city_name": city_name})
        if not city:
            await ctx.respond("Города с таким названием нет!", ephemeral=True)
            await log(
                f"{ctx.author.name} ({ctx.author.id}) (GUILD: {ctx.guild.id}) пытался посмотреть город, но такого нет: {city_name}",
                LogLevel.WARNING)
            return
        city = d.schema(city, scheme=d.Schemes.WPG_city)
        # print(city)

        if not ctx.author.id in self.wpg_masters:
            await ctx.respond("Вы не можете этого сделать.", ephemeral=True)
            return
        title = f"# {city_name}\n-# UUID: {city['UUID']}\nОснован <t:{utils.unix_sec2ds_timestamp_number(city['created_timestamp'])}:R>\nВладелец: <@{city['owner_id']}>"
        if city["owner_id"] != ctx.author.id:
            await ctx.respond(title, ephemeral=False)
            await log(f"{ctx.author.name} ({ctx.author.id}) (GUILD: {ctx.guild.id}) посмотрел чужой город {city_name}",
                      LogLevel.INFO)
            return
        captures = {
            # resources
            "wood": "🪵 Древесина",
            "food": "🍖 Еда",
            "iron": "⛏️ Железо",
            "coal": "⚫ Уголь",
            "oil": "🛢️ Нефть",

            # people
            "workers": "👷‍♂️ Рабочие",
            "engineers": "👨‍🏭 Инженер",
            "children": "👶 Дети",
            "doctors": "🧑‍🔬 Доктора",
            "unemployed": "🫃 Безработные",
            "dead": "💀 Трупы",
            "sick": "👳 Больные",

            # stats
            "hate": "🔻 Недовольство",  # на свержение
            "hope": "🔷 Надежда",  # БУНД!!!
            "outposts": "🏕️ Аванпосты",
        }
        fields_queue = ["# Ресурсы", "wood", "food", "iron", "coal", "oil",
                        "# Люди", "workers", "engineers", "children", "doctors", "unemployed", "dead", "sick",
                        "# Статистика", "hate", "hope", "outposts"]
        title += f"\nПоследнее изменение: <t:{utils.unix_sec2ds_timestamp_number(city['edited_timestamp'])}:R>\n"
        for field in fields_queue:
            if field.startswith("#"):
                title += f"{field}\n"
            elif field in city:
                title += f"{captures[field]}: {city[field]}\n"
        await ctx.respond(title, ephemeral=False)
        await log(f"{ctx.author.name} ({ctx.author.id}) (GUILD: {ctx.guild.id}) посмотрел город {city_name}", LogLevel.INFO)

    @wpg_commands.command(name="удалить-город", description="Удаляет город из базы данных")
    async def delete_city(self, ctx: discord.ApplicationContext,
                          city_name: Option(str, description="Название города", required=True)):
        await ctx.respond("Эта команда временно недоступна!", ephemeral=True)
        await log(f"{ctx.author.name} ({ctx.author.id}) (GUILD: {ctx.guild.id}) пытался удалить город {city_name}, "
                  f"но эта команда еще не существует!", LogLevel.WARNING)

    #     if not ctx.author.id in self.wpg_masters:
    #         await ctx.respond("Вы не можете этого сделать.", ephemeral=True)
    #         return
    #     city = self.collection.find_one({"city_name": city_name})
    #     if not city:
    #         await ctx.respond("Города с таким названием нет!", ephemeral=True)
    #         return
    #     self.collection.delete_one({"city_name": city_name})
    #     await ctx.respond(f"Город **{city_name}** удален!", ephemeral=True)

    @wpg_commands.command(name="переименовать-город", description="Переименовывает город")
    async def rename_city(self, ctx: discord.ApplicationContext,
                          name: Option(str, description="Название города", required=True),
                          new_name: Option(str, description="Новое название", required=True)):
        await ctx.respond("Эта команда временно недоступна!", ephemeral=True)
        await log(f"{ctx.author.name} ({ctx.author.id}) (GUILD: {ctx.guild.id}) переименовал бы город {name} в {new_name}, но увы и ах, эта команда еще не существует", LogLevel.WARNING)

    @wpg_commands.command(name="передать-город", description="Передает город другому игроку")
    async def transfer_city(self, ctx: discord.ApplicationContext,
                            name: Option(str, description="Название города", required=True),
                            new_owner: Option(discord.Member, description="Новое название", required=True)):
        await ctx.respond("Эта команда временно недоступна!", ephemeral=True)
        await log(f"{ctx.author.name} ({ctx.author.id}) (GUILD: {ctx.guild.id}) передал бы город {name} другому игроку {new_owner}, но увы и ах, эта команда еще не существует", LogLevel.WARNING)

    @wpg_commands.command(name="изменить-статы", description="Изменяет статы города")
    async def edit_city_stats(self, ctx: discord.ApplicationContext,
                              name: Option(str, description="Название города", required=True),
                              field: Option(str, description="Поле", choices=["wood", "food", "iron", "coal", "oil",
                                                                              "workers", "engineers", "children",
                                                                              "doctors", "unemployed", "dead", "sick",
                                                                              "hate", "hope", "outposts"],
                                            required=True), value: Option(int, description="Значение", required=True),
                              mode: Option(str, description="Режим", choices=["+", "-", "="], required=True)):
        # await ctx.respond("Эта команда временно недоступна!", ephemeral=True)
        if not ctx.author.id in self.wpg_masters:
            await ctx.respond("Вы не можете этого сделать.", ephemeral=True)
            await log(f"{ctx.author.name} ({ctx.author.id}) (GUILD: {ctx.guild.id}) пытался изменить статы города {name}, но у него недостаточно прав!", LogLevel.WARNING)
            return
        collection = d.db.get_collection("wpg_cities")
        city = collection.find_one({"city_name": name})
        if not city:
            await ctx.respond("Города с таким названием нет!", ephemeral=True)
            await log(f"{ctx.author.name} ({ctx.author.id}) (GUILD: {ctx.guild.id}) пытался изменить статы города {name}, но такого города нет!", LogLevel.WARNING)
            return
        city = d.schema(city, d.Schemes.WPG_city)
        starting_value = city[field]
        if mode == "+":
            city[field] += value
        elif mode == "-":
            city[field] -= value
        elif mode == "=":
            city[field] = value
        city["edited_timestamp"] = datetime.datetime.now().timestamp()
        collection.update_one({"city_name": name}, {"$set": city})
        await ctx.respond(
            f"Статы города **{name}** изменены: {field} {mode} {value} ({starting_value} -> {city[field]})",
            ephemeral=False)
        await log(f"{ctx.author.name} ({ctx.author.id}) (GUILD: {ctx.guild.id}) изменил статы города {name}: {field} {mode} {value} ({starting_value} -> {city[field]})", LogLevel.INFO)

    @wpg_commands.command(name="мои-города", description="Выводит список ваших городов")
    async def my_cities(self, ctx: discord.ApplicationContext):
        collection = d.db.get_collection("wpg_cities")
        cities = collection.find({"owner_id": ctx.author.id})
        if not cities:
            await ctx.respond("У вас нет городов!", ephemeral=True)
            await log(f"{ctx.author.name} ({ctx.author.id}) (GUILD: {ctx.guild.id}) пытался вывести список городов, но у него нет городов!", LogLevel.WARNING)
            return
        message = "Ваши города:\n"
        for city in cities:
            message += f"{city['city_name']} основан <t:{utils.unix_sec2ds_timestamp_number(city['created_timestamp'])}:R>\n"
        await ctx.respond(message, ephemeral=True)
        await log(f"{ctx.author.name} ({ctx.author.id}) (GUILD: {ctx.guild.id}) запросил список своих городов", LogLevel.INFO)

    @wpg_commands.command(name="города-пользователя", description="Выводит список городов пользователя")
    async def user_cities(self, ctx: discord.ApplicationContext,
                          user: Option(discord.Member, description="Пользователь", required=True)):
        collection = d.db.get_collection("wpg_cities")
        cities = collection.find({"owner_id": user.id})
        if not cities:
            await ctx.respond("Пользователь не имеет городов!", ephemeral=True)
            await log(f"Пользователь {user.name} ({user.id}) (GUILD: {ctx.guild.id}) пытался вывести список городов {user.name} ({user.id}), но у него нет городов!", LogLevel.WARNING)
            return
        message = f"Города пользователя {user.mention}:\n"
        for city in cities:
            message += f"{city['city_name']} основан <t:{utils.unix_sec2ds_timestamp_number(city['created_timestamp'])}:R>\n"
        await ctx.respond(message, ephemeral=False)


        await log(
            f"Пользователь {user.name} ({user.id}) (GUILD: {ctx.guild.id}) запросил список городов {user.name} ({user.id})",
            LogLevel.INFO)


def setup(bot):
    bot.add_cog(WPG(bot))
