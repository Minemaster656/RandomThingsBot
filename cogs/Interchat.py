import asyncio
import re

import discord
from discord.ext import commands, tasks
from discord import Option, Forbidden

import Data
import utils


class Interchat(commands.Cog):
    ''' Interchat | BOT COG'''
    name = "Interchat"
    author = "Minemaster"

    def __init__(self, bot:commands.Bot):
        self.bot = bot
        # self.deleted_messages = {}
        # self.edited_messages = {}

    @tasks.loop(seconds=10)  # Указываете интервал в секундах
    async def background(self):
        # print("BG")
        # for doc in self.deleted_messages:
        #     if self.deleted_messages[doc]["expires"] < time.time():
        #         self.deleted_messages.pop(doc)
        # for doc in self.edited_messages:
        #     if self.edited_messages[doc]["expires"] < time.time():
        #         self.edited_messages.pop(doc)
        # print("BG")
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

    @commands.Cog.listener("on_message")
    async def interchat_on_message(self, message: discord.Message):
        # await asyncio.sleep(0.25)
        # print("MESSEGE")
        async def interchat(mode, message, hname, havatar, data_pair):  # h - webHook
            # print("DETECTED")

            if mode in Data.interchats:
                leng = len(Data.interchats[mode])
                i = 0
                for array in Data.interchats[mode]:
                    try:
                        i += 1
                        server_id = array['guild']
                        channel_id = array['channel']
                        if 'thread' in array.keys():
                            thread = array["thread"]
                        else:
                            thread = None

                        send = False
                        found = True
                        # Поиск сервера по ID
                        server = self.bot.get_guild(server_id)
                        if server is None:
                            found = False

                        # Поиск канала по ID
                        # server.get_channel(channel_id)
                        channel = await self.bot.fetch_channel(channel_id)
                        print(channel_id)
                        if channel is None:
                            found = False

                        isBotHook = False
                        try:
                            hooks = await channel.webhooks()
                            for hook in hooks:
                                isBotHook = hook.user.id in Data.botIDs
                                break
                        except Forbidden:
                            isBotHook = True

                        isInterchatter = str(message.author.name).startswith(
                            ">» ")

                        if channel_id != message.channel.id and server_id != message.guild.id and not isInterchatter:

                            if found and not send:

                                try:
                                    hooks = await channel.webhooks()

                                    async def send(hook):
                                        content = message.content
                                        if re.search(
                                                r"(https?:\/\/|http?:\/\/)?(www.)?(discord.(gg|io|me|li)|discordapp.com\/invite|discord.com\/invite)\/[^\s\/]+?(?=\b)",
                                                content):
                                            await message.author.send(
                                                "Приглашения рассылать по интерчату запрещено.\nInvites are blocked in the Interchat.")
                                            embed = discord.Embed(title="Ваше сообщение | Your message",
                                                                  description=f"{message.content}",
                                                                  colour=Data.getEmbedColor(Data.EmbedColor.Error))
                                            await message.author.send(embed=embed)
                                            await message.delete()
                                            return

                                        if message.reference:

                                            # udoc = Data.db.users.find_one({"id":message.reference.resolved.author.id})
                                            # print(udoc)
                                            embed = discord.Embed(title="⤴️ Reply",
                                                                  description=f"{message.reference.resolved.content}",
                                                                  colour=Data.embedColors["Neutral"]
                                                                  # if not udoc else int(udoc["color"])
                                                                  )
                                            embed.set_author(name=message.reference.resolved.author.name,
                                                             icon_url=message.reference.resolved.author.avatar.url if message.reference.resolved.author.avatar else message.reference.resolved.author.default_avatar.url)
                                            try:
                                                if thread:
                                                    await hook.send(content=message.content, username=hname,
                                                                    avatar_url=havatar,
                                                                    embed=embed, thread=discord.Object(thread),
                                                                    files=[await i.to_file() for i in message.attachments]
                                                                    )
                                                else:
                                                    await hook.send(content=message.content, username=hname,
                                                                    avatar_url=havatar, embed=embed,
                                                                    files=[await i.to_file() for i in message.attachments]
                                                                    )
                                            except:
                                                print("No hook?")
                                        else:

                                            try:
                                                if thread:

                                                    # TODO: ветки
                                                    await hook.send(content=message.content, username=hname,
                                                                    avatar_url=havatar,
                                                                    allowed_mentions=discord.AllowedMentions.none()
                                                                    ,
                                                                    files=[await i.to_file() for i in message.attachments],
                                                                    thread=discord.Object(thread))
                                                else:
                                                    await hook.send(content=message.content, username=hname,
                                                                    avatar_url=havatar,
                                                                    allowed_mentions=discord.AllowedMentions.none()
                                                                    ,
                                                                    files=[await i.to_file() for i in message.attachments])
                                            except:
                                                ...

                                        send = True

                                    for hook in hooks:
                                        if hook.user.id == self.bot.user.id:
                                            await send(hook)
                                            break
                                    if not send:
                                        print("No hook.")
                                        _hook = await channel.create_webhook(name="RTB hook")
                                        await send(_hook)

                                except Forbidden:
                                    ...

                                send = True
                        if i >= leng:

                            try:
                                # await message.add_reaction("🚀")
                                ...
                            except:
                                ...
                            break
                    except:
                        ...
        try:
            target = {'guild': message.guild.id, 'channel': message.channel.id}
            if isinstance(message.channel, discord.Thread):
                target['thread'] = message.channel.id
                target['channel'] = message.channel.parent.id

        except:
            target = {'guild': 0, 'channel': 0}
        name = self.inter_formatName(message)
        avatar = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url
        if not str(message.author.name).startswith(">» "):
            for hub in Data.interhubs:
                if hub in Data.interchats:
                    for object in Data.interchats[hub]:
                        if target['guild'] == object['guild'] and target['channel'] == object['channel']:
                            # найдено
                            # print("THIS IS INTERCHAT")
                            if message.author.id in Data.interbans:
                                await message.add_reaction("🔒")
                            else:
                                if ("thread" in object.keys() and "thread" in target.keys()) or (
                                        not "thread" in object.keys() and not "thread" in target.keys()):
                                    await interchat(hub, message, name, avatar, target)
                            # print("FOUND pair normal")
                            break
                            # print("BROKEN")


def setup(bot):
    bot.add_cog(Interchat(bot))
