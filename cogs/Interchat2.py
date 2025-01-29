import asyncio
import json
import os
import re
import time

import Data
import logger
import utils

# try:
import discord
from discord import Option, Webhook, Forbidden
from discord.ext import commands, tasks
# except:
#     import pycord as discord
#     from pycord import Option, Webhook, Forbidden
#     from discord.ext import commands, tasks


class Interchat2(commands.Cog):
    ''' Interchat2 | BOT COG'''
    name = "Interchat2"
    author = "Minemaster"
    cache = {}
    delete_queue = {}
    edit_queue = {}
    cache_size = 10
    cache_lifetime_sec = 120

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @tasks.loop(seconds=10)
    async def background(self):

        for hub in self.delete_queue:
            for msg in hub:
                if msg["timestamp"] + self.cache_lifetime_sec < time.time():
                    self.delete_queue[hub].remove(msg)

        for hub in self.edit_queue:
            for msg in hub:
                if msg["timestamp"] + self.cache_lifetime_sec < time.time():
                    self.edit_queue[hub].remove(msg)
        ...


    def inter_formatName(self, message):
        if not message:
            return ">» ???"
        if not message.guild:
            return ">» [???]"
        type = ""
        if message.webhook_id:
            type = "⚓"
        elif message.author.bot:
            type = "🤖"
        else:
            type = "😎"
        return ">» " + utils.formatStringLength(message.author.name, 48) + " | " + utils.formatStringLength(
            message.guild.name, 32) + " | " + type

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name="интерсервер", description="Помечает канал как интерсервер")
    async def interserver(self, ctx,
                          type: Option(str, description="Тип канала. Можно иметь одновременно несколько на сервер.",
                                       choices=Data.interhubs, required=True) = 0,
                          reset: Option(bool, description="True для отчистки поля", required=False) = False):
        channel = ctx.channel
        if await Data.parsePermissionFromUser(ctx.author.id, "root") or Data.parsePermissionFromUser(ctx.author.id, "verified"):  # (
            # ctx.author.permissions.administrator or ctx.author.permissions.manage_channels)):
            # with open('private/data.json', 'r') as file:
            #     try:
            #         data = json.load(file)
            #     except json.JSONDecodeError:
            #         data = {}
            #     except FileNotFoundError:
            #         data = {}
            #
            #
            #
            #
            #
            # with open('private/data.json', 'w') as file:
            #     json.dump(data, file)
            await logger.log(
                f"Making interchat. GUILD: {ctx.guild.name} {ctx.guild.id}, CHANNEL: {channel.name} {channel.id}, TYPE: {type}. Requested by: {ctx.author.name} {ctx.author.id}",
                logger.LogLevel.INFO)
            def update_json(data, array_name, delete=False):
                file_path = os.path.join('private', 'interchats.json')

                # Проверяем наличие файла
                if not os.path.exists(file_path):
                    # Если файла нет, создаем пустой JSON объект
                    json_data = {}
                else:
                    # Если файл существует, считываем его содержимое
                    with open(file_path, 'r') as file:
                        try:
                            json_data = json.load(file)
                        except json.JSONDecodeError:
                            # В случае ошибки при чтении файла (некорректный JSON), создаем пустой JSON объект
                            json_data = {}

                # Проверяем наличие массива с заданным именем
                if array_name not in json_data:
                    json_data[array_name] = []
                if len(json_data) > 0:
                    if type in json_data.keys():
                        if len(json_data[type]) > 0:
                            i = 0
                            for arr in json_data[type]:
                                if arr['guild'] == ctx.guild.id:
                                    json_data[type].pop(i)
                                    break
                                i += 1
                if delete:
                    # Удаление элемента из массива, если delete=True
                    # json_data[array_name] = [item for item in json_data[array_name] if item != data]
                    if len(json_data) > 0:
                        if type in json_data.keys():
                            if len(json_data[type]) > 0:
                                i = 0
                                for arr in json_data[type]:
                                    if arr['channel'] == channel.id:
                                        json_data[type].pop(i)
                                        break
                                    i += 1
                else:
                    # Добавление элемента в массив, если delete=False
                    json_data[array_name].append(data)
                Data.interchats = json_data
                # Записываем обновленные данные в файл
                with open(file_path, 'w') as file:
                    json.dump(json_data, file)

            isThread = isinstance(channel, discord.Thread)
            if isThread:
                data = {'guild': ctx.guild.id, 'channel': channel.parent_id, 'thread': channel.id}
            else:
                data = {'guild': ctx.guild.id, 'channel': channel.id}
            update_json(data, type, reset)
            found = False
            hooks = await ctx.channel.webhooks() if isinstance(channel,
                                                               discord.TextChannel) else await ctx.channel.parent.webhooks()
            hook_channel = ctx.channel if isinstance(channel, discord.TextChannel) else ctx.channel.parent
            for hook in hooks:
                if hook.user.id == self.bot.user.id:
                    found = True
            if not found:
                await hook_channel.create_webhook(name="RTB hook")
            await ctx.respond("Успешно!", ephemeral=True)
            embed = discord.Embed(title=f"Обновление интерчата",
                                  description=f"В канале {channel.name} {'установлен' if not reset else 'убран'} хаб межсерверного чата `{type}`!",
                                  colour=0xffffff)
            await ctx.respond(embed=embed)
            await logger.log(
                f"Interchat created!. GUILD: {ctx.guild.name} {ctx.guild.id}, CHANNEL: {channel.name} {channel.id}, TYPE: {type}. Requested by: {ctx.author.name} {ctx.author.id}",
                logger.LogLevel.INFO)

        else:
            await logger.log(
                f"Failed to create interchat - no permissions (author). GUILD: {ctx.guild.name} {ctx.guild.id}, CHANNEL: {channel.name} {channel.id}, TYPE: {type}. Requested by: {ctx.author.name} {ctx.author.id}",
                logger.LogLevel.INFO)

            await ctx.respond(
                "У Вас недостаточно прав для этого действия!!!\nНеобходима верификация пользователя (в боте, не в Discord) и право управления каналами/администратор",
                ephemeral=True)

    @commands.Cog.listener("on_message")
    async def interchat_on_message(self, message: discord.Message):

        if message.author.name.startswith(">»"): return
        if message.channel.type == discord.ChannelType.group or message.channel.type == discord.ChannelType.private: return
        hub_key = ""
        hub = None
        index = -1
        # print("Message detected")
        for hub_k in Data.interchats.keys(): #TODO заменить на асинхронный поиск
            # print(hub_k)
            for guild_interchat in Data.interchats[hub_k]:
                index += 1
                # print(guild_interchat)
                if guild_interchat["guild"] == message.guild.id:
                    # print("guild found")
                    hub_key = hub_k
                    hub = Data.interchats[hub_k]
                    break
            if hub_key != "": break
        else:
            if hub_key != "": return
        if hub is None: return
        try:
            if message.channel.id!= hub[index]["channel"]: return
        except:
            return
        # print("Hub: ", hub_key)
        # print(hub_key)
        try: #TODO: тут чё-то сломалось на сервере арбузов. Да, опять у них. Мнда.
            if "thread" in hub[index].keys():
                if isinstance(message.channel, discord.Thread):
                    if message.channel.id != hub[index]["thread"]:
                        return
                else:
                    return
            else:
                if isinstance(message.channel, discord.Thread): return
        except: ...
        # print(hub[index])

        if re.search(
                r"(https?:\/\/|http?:\/\/)?(www.)?(discord.(gg|io|me|li)|discordapp.com\/invite|discord.com\/invite)\/[^\s\/]+?(?=\b)",
                message.content):
            await message.author.send(
                "Приглашения рассылать по Интерчату запрещено!\nInvites are blocked in the Interchat!")
            embed = discord.Embed(title="Ваше сообщение | Your message",
                                  description=f"{message.content}",
                                  colour=Data.getEmbedColor(Data.EmbedColor.Error))
            await message.author.send(embed=embed)
            # await message.add_reaction("🚫")
            await message.delete()
            return
        # print("Caching...")
        # if not hub_key in self.cache.keys():
        #     self.cache[hub_key] = []
        # self.cache[hub_key].append(
        #     {"guild_id": message.guild.id, "channel_id": message.channel.id, "message_id": message.id, "clones": [],
        #      "total_chats_to_send": len(hub)-1, "total_sent_to":0})
        # cacheID = len(self.cache[hub_key]) - 1
        # if len(self.cache[hub_key]) > self.cache_size:
        #     self.cache[hub_key].pop(0)

        name = self.inter_formatName(message)
        avatar = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url

        for guild_interchat in hub:
            # print("Sent to: ", guild_interchat)
            if guild_interchat["guild"] == message.guild.id: continue

            try:
                guild = self.bot.get_guild(guild_interchat["guild"])
            except:
                continue
            if not guild: continue

            try:
                channel = guild.get_channel(guild_interchat["channel"])
            except:
                continue
            if not channel: continue

            webhook = None
            for hook in await channel.webhooks():
                if hook.user.id == self.bot.user.id:
                    webhook = hook
                    break
            else:

                try:
                    webhook = await channel.create_webhook(name="RTB hook")
                except:
                    continue

            try:
                # delete queue
                if hub_key in self.delete_queue.keys():
                    for msg_id in self.delete_queue[hub_key]:
                        if msg_id == message.id:
                            for msg in self.delete_queue[hub_key]:
                                if msg["id"] == message.id:
                                    self.delete_queue[hub_key].remove(msg)
                                    break
                            break

                content = ""
                if hub_key in self.edit_queue.keys():
                    for msg_id in self.edit_queue[hub_key]:
                        if msg_id == message.id:
                            for msg in self.edit_queue[hub_key]:
                                if msg["id"] == message.id:
                                    content = msg["content"]
                                    break
                            break
                if content == "":
                    content = message.content

                if message.reference:
                    embed = discord.Embed(
                        title=f"Ответ на: {utils.formatStringLength(message.reference.resolved.author.name, 16)}...{' (+🖼️)' if message.reference.resolved.attachments else ''}",
                        description=f"{message.reference.resolved.content if len(message.reference.resolved.content) > 0 else '*<в сообщении только вложение>*'}",
                        colour=Data.getEmbedColor(Data.EmbedColor.Neutral),
                        timestamp=message.reference.resolved.created_at)
                    embed.set_author(name=message.reference.resolved.author.name,
                                     icon_url=message.reference.resolved.author.avatar.url if message.reference.resolved.author.avatar else message.reference.resolved.author.default_avatar.url)
                    if message.reference.resolved.attachments:
                        embed.set_image(url=message.reference.resolved.attachments[0].url)




                    if "thread" in guild_interchat.keys():
                        await webhook.send(content=content, username=name,
                                           avatar_url=avatar,
                                           allowed_mentions=discord.AllowedMentions.none()
                                           ,
                                           files=[await i.to_file() for i in message.attachments],
                                           thread=discord.Object(guild_interchat["thread"]), embed=embed)
                    else:
                        await webhook.send(content=content, username=name,
                                           avatar_url=avatar,
                                           allowed_mentions=discord.AllowedMentions.none()
                                           ,
                                           files=[await i.to_file() for i in message.attachments],
                                           embed=embed)
                else:
                    if "thread" in guild_interchat.keys():
                        await webhook.send(content=content, username=name,
                                           avatar_url=avatar,
                                           allowed_mentions=discord.AllowedMentions.none()
                                           ,
                                           files=[await i.to_file() for i in message.attachments],
                                           thread=discord.Object(guild_interchat["thread"]))
                    else:
                        await webhook.send(content=content, username=name,
                                           avatar_url=avatar,
                                           allowed_mentions=discord.AllowedMentions.none()
                                           ,
                                           files=[await i.to_file() for i in message.attachments])
            except:
                ...

    @commands.Cog.listener("on_message_delete")
    async def interchat_on_message_delete(self, message: discord.Message):
        # print("Deleted something!")
        if message.author.name.startswith(">»"): return
        hub_key = ""
        hub = None
        index = -1
        # print("Message detected")
        for hub_k in Data.interchats.keys():
            # print(hub_k)
            for guild_interchat in Data.interchats[hub_k]:
                index += 1
                # print(guild_interchat)
                if guild_interchat["guild"] == message.guild.id:
                    # print("guild found")
                    hub_key = hub_k
                    hub = Data.interchats[hub_k]
                    break
            if hub_key != "": break
        else:
            if hub_key != "": return
        # print("Hub: ", hub_key)
        # print(hub_key)
        if hub is None: return
        if message.channel.id != hub[index]["channel"]: return
        if "thread" in hub[index].keys():
            if isinstance(message.channel, discord.Thread):
                if message.channel.id != hub[index]["thread"]:
                    return
            else:
                return
        else:
            if isinstance(message.channel, discord.Thread): return

        if not hub_key in self.delete_queue.keys():
            self.delete_queue[hub_key] = []
            self.delete_queue[hub_key].append({"id": message.id, "timestamp": time.time()})

        for guild_interchat in hub:
            # print("Deleted in: ", guild_interchat)
            if guild_interchat["guild"] == message.guild.id: continue
            # print("It is not this message, let's delete it!")
            try:
                guild = self.bot.get_guild(guild_interchat["guild"])
            except:
                continue
            if not guild: continue
            # print("Guild fetchded!")
            try:
                channel = guild.get_channel(guild_interchat["channel"])
            except:
                continue
            if not channel: continue
            # print("I got a channel object!")
            if "thread" in guild_interchat.keys():
                channel = channel.get_thread(guild_interchat["thread"])
                # print("It's a thread!")

            messages = await channel.history(limit=self.cache_size).flatten()
            # print("History fetched!")
            for msg in messages:
                # print(message.author.name, " | ", self.inter_formatName(message))
                # print(msg.channel.name," | ",message.author.name)
                # print(msg.channel.name," | ",message.content, " | ", msg)
                if msg.author.name == self.inter_formatName(message):
                    # print("Name the same, continue...")
                    # print("Content: ", msg.content)
                    if msg.content == message.content:
                        # print("DELETING!")
                        try: await msg.delete(reason="Interchat: deleted original message")
                        except: ...#print("Failed to delete!")
                        # print("EEEE, DELETED!!!")
                        break

    @commands.Cog.listener("on_message_edit")
    async def interchat_on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.name.startswith(">»"): return
        hub_key = ""
        hub = None
        index = -1
        # print("Message detected")
        for hub_k in Data.interchats.keys():
            # print(hub_k)
            for guild_interchat in Data.interchats[hub_k]:
                index += 1
                # print(guild_interchat)
                if guild_interchat["guild"] == before.guild.id:
                    # print("guild found")
                    hub_key = hub_k
                    hub = Data.interchats[hub_k]
                    break
            if hub_key != "": break
        else:
            if hub_key != "": return
        if hub is None: return
        try:
            if before is None: return
            if hub[index] is None: return
            if hub[index]["channel"] is None: return
            if before.channel.id != hub[index]["channel"]: return
        except:
            # print("Exception: ", before.channel.guild, "/", before.channel.id, ": None detected")
            return

        if "thread" in hub[index].keys():
            if isinstance(before.channel, discord.Thread):
                if before.channel.id != hub[index]["thread"]:
                    return
            else:
                return
        else:
            if isinstance(before.channel, discord.Thread): return

        if not hub_key in self.edit_queue.keys():
            self.edit_queue[hub_key] = []
            self.edit_queue[hub_key].append({"id": before.id, "timestamp": time.time(), "content":after.content})

        for guild_interchat in hub:
            # print("Edited in: ", guild_interchat)
            if guild_interchat["guild"] == before.guild.id: continue
            # print("It is not this message, let's edit it!")
            try:
                guild = self.bot.get_guild(guild_interchat["guild"])
            except:
                continue
            if not guild: continue
            # print("Guild fetchded!")
            try:
                channel = guild.get_channel(guild_interchat["channel"])
            except:
                continue
            if not channel: continue
            # print("I got a channel object!")
            if "thread" in guild_interchat.keys():
                channel = channel.get_thread(guild_interchat["thread"])
                # print("It's a thread!")

            webhook = None
            for hook in await channel.webhooks():
                if hook.user.id == self.bot.user.id:
                    webhook = hook
                    break
            else:
                try:
                    webhook = await channel.create_webhook(name="RTB hook")
                except:
                    continue

            messages = await channel.history(limit=self.cache_size).flatten()
            # print("History fetched!")
            for msg in messages:
                # print(message.author.name, " | ", self.inter_formatName(message))
                # print(msg.channel.name," | ",message.author.name)
                # print(msg.channel.name," | ",message.content, " | ", msg)
                if msg.author.name == self.inter_formatName(before):
                    # print("Name the same, continue...")
                    # print("Content: ", msg.content)
                    if msg.content == before.content:
                        # print("EDITING!")
                        try:
                            # await msg.edit(content=after.content)
                            await webhook.edit_message(msg.id, content=after.content)
                        except: ...#print("Failed to delete!")
                        # print("EEEE, EDITED!!!", channel.name, " | ", guild.name)
                        break

def setup(bot):
    bot.add_cog(Interchat2(bot))
