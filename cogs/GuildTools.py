import time

# try:
import discord
from discord import Option, Webhook, Forbidden
from discord.ext import commands
# except:
#     import pycord as discord
#     from pycord import Option, Webhook, Forbidden
#     from discord.ext import commands

import Data
import d
import utils
from Data import db


class ConfirmSavePreset(discord.ui.View):
    def __init__(self, slot, category):
        super().__init__()
        self.value = None
        self.slot = slot
        self.category = category

    @discord.ui.button(label="Да", style=discord.ButtonStyle.green)
    async def confirm_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Подтверждено.", view=None)
        guildid = interaction.guild_id
        print(self.slot, self.category)
        doc = d.getGuildByID(guildid)
        result = {}
        if self.category == "channels":
            for channel in interaction.guild.channels:
                result[str(channel.id)] = channel.name
        elif self.category == "roles":
            for role in interaction.guild.roles:
                result[str(role.id)] = role.name
        doc['presets'][self.category][self.slot] = result
        db.servers.update_one({"serverid": guildid}, {"$set": doc})
        self.value = True
        self.stop()

    @discord.ui.button(label="Нет", style=discord.ButtonStyle.red)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Отменено.", view=None)
        self.value = False
        self.stop()


class ConfirmLoadPreset(discord.ui.View):
    def __init__(self, slot, category):
        super().__init__()
        self.value = None
        self.slot = slot
        self.category = category

    @discord.ui.button(label="Да", style=discord.ButtonStyle.green)
    async def confirm_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="Выполняется. К сожалению, вывести сообщение о выполнении не удастся.", view=None)

        guildid = interaction.guild_id
        print(self.slot, self.category)
        doc = d.getGuildByID(guildid)
        # result = {}
        # for channel in interaction.guild.channels:
        #     result[channel.id]=channel.name
        result = doc['presets'][self.category][self.slot]
        print(result)
        print(result.keys())
        print(self.category)
        if self.category == "channels":
            for k in result.keys():
                try:
                    await interaction.guild.get_channel(int(k)).edit(name=result[k])
                    print(k, " ", result[k])
                except:
                    print(f"Excepted on {k}")
        elif self.category == "roles":
            for k in result.keys():
                try:
                    await interaction.guild.get_role(int(k)).edit(name=result[k])

                    print(k, " ", result[k])

                except:
                    print(f"Excepted on {k}: {result[k]}")

        self.value = True
        self.stop()

    @discord.ui.button(label="Нет", style=discord.ButtonStyle.red)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Отменено.", view=None)
        self.value = False
        self.stop()


class GuildTools(commands.Cog):
    ''' GuildTools | BOT COG'''
    name = "GuildTools"
    author = ""

    def __init__(self, bot):
        self.bot = bot

    cmds = discord.SlashCommandGroup(
        "сервер",
        "",

    )

    @commands.has_permissions(administrator=True)
    @cmds.command(name="сохранить-пресет", description="Сохранение названий ролей, каналов и прочего в слот.")
    async def savePreset(self, ctx: discord.ApplicationContext, category: Option(str, description="Категория",
                                                                                 choices=["Названия каналов",
                                                                                          "Названия ролей"],
                                                                                 required=True) = 0,
                         slot: Option(str, description="Слот сохранения", choices=[
                             "Основной", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                             "✨11", "✨12", "✨13", "✨14", "✨15", "✨16", "✨17", "✨18", "✨19", "✨20"
                         ], required=True) = "Основной"):
        doc = d.getGuild(ctx)
        categories = {"Названия каналов": "channels", "Названия ролей": "roles"}
        slots = {"Основной": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
                 "✨11": 11, "✨12": 12, "✨13": 13, "✨14": 14, "✨15": 15, "✨16": 16, "✨17": 17, "✨18": 18, "✨19": 19,
                 "✨20": 20}
        slot_num = slots[slot]
        category_key = categories[category]
        userdoc = d.getUser(ctx.author.id, ctx.author.name)
        ownerdoc = d.getUser(ctx.guild.owner.id, ctx.guild.owner.name)
        if slot_num > 10:
            if not ownerdoc['premium_end'] > time.time() * 1000 and not userdoc['premium_end'] > time.time() * 1000:
                await ctx.respond("Для доступа к слотам 11-20 нужен премиум у Вас или владельца сервера!",
                                  ephemeral=True)
                return
        embed = discord.Embed(title="Вы уверены?",
                              description=f"Вы уверены? Это действие перезапишет слот {slot} в категории {str(category).lower()}!\nПосмотреть содержимое слота можно командой /сервер посмотреть-пресет",
                              colour=Data.getEmbedColor(Data.EmbedColor.Economy))
        view = ConfirmSavePreset(slot_num, category_key)
        await ctx.respond(embed=embed, view=view)

    @commands.has_permissions(administrator=True)
    @cmds.command(name="загрузить-пресет", description="Загрузка названий ролей, каналов и прочего в слот.")
    async def savePreset(self, ctx: discord.ApplicationContext, category: Option(str, description="Категория",
                                                                                 choices=["Названия каналов",
                                                                                          "Названия ролей"],
                                                                                 required=True) = 0,
                         slot: Option(str, description="Слот сохранения", choices=[
                             "Основной", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                             "✨11", "✨12", "✨13", "✨14", "✨15", "✨16", "✨17", "✨18", "✨19", "✨20"
                         ], required=True) = "Основной"):
        doc = d.getGuild(ctx)
        categories = {"Названия каналов": "channels", "Названия ролей": "roles"}
        slots = {"Основной": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
                 "✨11": 11, "✨12": 12, "✨13": 13, "✨14": 14, "✨15": 15, "✨16": 16, "✨17": 17, "✨18": 18, "✨19": 19,
                 "✨20": 20}
        slot_num = slots[slot]
        category_key = categories[category]
        userdoc = d.getUser(ctx.author.id, ctx.author.name)
        ownerdoc = d.getUser(ctx.guild.owner.id, ctx.guild.owner.name)
        if slot_num > 10:
            if not ownerdoc['premium_end'] > time.time() * 1000 and not userdoc['premium_end'] > time.time() * 1000:
                await ctx.respond("Для доступа к слотам 11-20 нужен премиум у Вас или владельца сервера!",
                                  ephemeral=True)
                return
        embed = discord.Embed(title="Вы уверены?",
                              description=f"Вы уверены? Это действие сменит все {str(category).lower()}, которые имеют запись в слоте сохранения!\nПосмотреть содержимое слота можно командой /сервер посмотреть-пресет",
                              colour=Data.getEmbedColor(Data.EmbedColor.Economy))
        view = ConfirmLoadPreset(slot_num, category_key)
        await ctx.respond(embed=embed, view=view)

    @commands.has_permissions(administrator=True)
    @cmds.command(name="посмотреть-пресет", description="Просмотр пресета названий ролей, каналов и прочего в слот.")
    async def savePreset(self, ctx: discord.ApplicationContext, category: Option(str, description="Категория",
                                                                                 choices=["Названия каналов",
                                                                                          "Названия ролей"],
                                                                                 required=True) = 0,
                         slot: Option(str, description="Слот сохранения", choices=[
                             "Основной", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                             "✨11", "✨12", "✨13", "✨14", "✨15", "✨16", "✨17", "✨18", "✨19", "✨20"
                         ], required=True) = "Основной"):
        doc = d.getGuild(ctx)
        categories = {"Названия каналов": "channels", "Названия ролей": "roles"}
        slots = {"Основной": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
                 "✨11": 11, "✨12": 12, "✨13": 13, "✨14": 14, "✨15": 15, "✨16": 16, "✨17": 17, "✨18": 18, "✨19": 19,
                 "✨20": 20}
        slot_num = slots[slot]
        category_key = categories[category]
        userdoc = d.getUser(ctx.author.id, ctx.author.name)
        ownerdoc = d.getUser(ctx.guild.owner.id, ctx.guild.owner.name)
        if slot_num > 10:
            if not ownerdoc['premium_end'] > time.time() * 1000 and not userdoc['premium_end'] > time.time() * 1000:
                await ctx.respond("Для доступа к слотам 11-20 нужен премиум у Вас или владельца сервера!",
                                  ephemeral=True)
                return
        # embed = discord.Embed(title="Вы уверены?",
        #                       description="Вы уверены? Это действие перезапишет слот!\nПосмотреть содержимое слота можно командой /сервер посмотреть-пресет",
        #                       colour=Data.getEmbedColor(Data.EmbedColor.Economy))
        # view = ConfirmSavePreset(slot_num, category_key)
        result = doc["presets"][category_key][slot_num]
        value = ""
        for v in result.values():
            value += v + "\n"
        if value == "":
            value = "Слот пуст!"
        embed = discord.Embed(title=f"Содержимое пресета {category}:{slot}",
                              description=f"{utils.formatStringLength(value, 3990)}",
                              colour=Data.getEmbedColor(Data.EmbedColor.Success))
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(GuildTools(bot))
