import asyncio
import os.path

import discord
from discord.ext import commands, tasks
from discord import Option

# from pytube import YouTube
import Data
import libs.CachedTTS

class TTS(commands.Cog):
    ''' TTS | BOT COG'''
    name = "TTS"
    author = "Minemaster"
    SPEED = 1.5
    SPEED_TTS = 1.1

    tts_channels = {}

    tts_commands = discord.SlashCommandGroup(
        "говорилка", ""

    )
    def __init__(self, bot: discord.Bot):
        self.bot = bot



        self.tts_background.start()

    def cog_unload(self):
        self.tts_background.cancel()
    async def checkIsNameSpeaksPhraseRequired(self, message):
        prev_message = message
        async for msg in message.channel.history(limit=2):
            if msg.id != message.id:
                prev_message = msg
                break

        if prev_message.author.id == message.author.id:
            # Проверяем, что предыдущее сообщение было отправлено не более 2 минут назад
            time_diff = message.created_at - prev_message.created_at
            if time_diff.total_seconds() <= 120:
                # await message.channel.send(
                #     f"Предыдущее сообщение отправлено тем же пользователем меньше чем 2 минуты назад.")
                return False

        return True

    async def TTSify(self, message:discord.Message):
        # if message.content.startswith(("$yt", "$youtube", "$ютуб", "$йт")):
        #
        #     if 'youtube.com' in message.content or 'youtu.be' in message.content:
        #         await message.channel.send("Идет загрузка аудио...")
        #         # Скачиваем аудио
        #         yt = YouTube(message.content.split(" ")[1])
        #         audio_stream = yt.streams.filter(only_audio=True).first()
        #         file_path = audio_stream.download(filename='audio.mp4')
        #         self.tts_channels[message.channel.id]["vc"].play(discord.FFmpegPCMAudio(file_path), after=lambda e: os.remove(file_path))
        #     else:
        #         await message.channel.send("Ссылка должна быть в формате youtube.com или youtu.be")

        # print(message.content)
        # vc = message.guild.me.voice.channel

        # print(TTS.path_to_audio)
        # print(TTS)
        # print(os.getcwd())
        # else:
        async def play_audio(vc, audio_files):
            for file in audio_files:
                # print(file)
                # print(file.__class__)
                # print(isinstance(file, libs.CachedTTS.TTS_phrase))
                if file == audio_files[-1]:
                    vc.play(discord.FFmpegPCMAudio(f"{file.path}/{file.filename}.mp3",
                                                   options=f"-filter:a 'atempo={self.SPEED_TTS}'"), after=lambda e: ...)
                else:
                    vc.play(discord.FFmpegPCMAudio(f"{file.path}/{file.filename}.mp3",
                                                   options=f"-filter:a 'atempo={self.SPEED}'"), after=lambda e: ...)
                while vc.is_playing():
                    await asyncio.sleep(0.01)
        sequence = []
        if message.content != "":
            TTS = libs.CachedTTS.CachedTTS(f"files/TTS", f"files/db/TTS.db")
            ttss = {}

            ttss["tts"] = await TTS.tts(message.clean_content())
            ttss["name_tts"] = await TTS.tts(message.author.display_name)
            ttss["speaks_tts"] = await TTS.tts("говорит")
            if message.reference:
                ttss["reply_author_name_tts"] = await TTS.tts(message.reference.resolved.author.display_name)
                ttss["reply_content_tts"] = await TTS.tts(message.reference.resolved.clean_content())
                ttss["reply_tts"] = await TTS.tts("в ответ на сообщение")
                ttss["by_tts"] = await TTS.tts("от")

                if await self.checkIsNameSpeaksPhraseRequired(message):
                    sequence.append(ttss["name_tts"])
                sequence.append(ttss["reply_tts"])
                sequence.append(ttss["reply_content_tts"])
                sequence.append(ttss["by_tts"])
                sequence.append(ttss["reply_author_name_tts"])
                sequence.append(ttss["speaks_tts"])
                sequence.append(ttss["tts"])
            else:
                if await self.checkIsNameSpeaksPhraseRequired(message):
                    sequence.append(ttss["name_tts"])
                    sequence.append(ttss["speaks_tts"])
                sequence.append(ttss["tts"])
            # TODO: сделать что бы оно не повторяло имя если недавно писало
            # history = message.channel.history(limit=2)
            # if history[1].author.id == message.author.id:
            #     if message.created_at - history[1].created_at <= 60000:
            #         sequence.remove("name_tts")
            #         if not message.reference:
            #             sequence.remove("speaks_tts")

            # if not await self.checkIsNameSpeaksPhraseRequired(message):
            #     try:
            #         sequence.remove("name_tts")
            #     except:
            #         ...
            #     if not message.reference:
            #         try:
            #             sequence.remove("speaks_tts")
            #         except:
            #             ...

            for key in ttss.keys():
                if ttss[key] is None:
                    self.tts_channels[message.channel.id]["vc"].play(discord.FFmpegPCMAudio(f"assets/tts_error.mp3"),
                                                                     after=lambda e: ...)
            await play_audio(self.tts_channels[message.channel.id]["vc"], sequence)


        # else:
        #     print("empty message. looking for attachments")
        #     message: discord.Message = message
        #     if len(message.attachments) > 0:
        #         print(len(message.attachments))
        #         attachment = message.attachments[0]
        #         if attachment.filename.endswith('.mp3'):
        #             await attachment.save(attachment.filename)
        #             self.tts_channels[message.channel.id]["vc"].play(discord.FFmpegPCMAudio(attachment.filename))




    @commands.Cog.listener("on_voice_state_update")
    async def on_voice_state_update(self, member, before, after):
        if not member.bot:
            if before.channel is not None and after.channel is None:
                voice_channel = before.channel
                if len(voice_channel.members) == 1:  # Проверяем, что остался только один участник (бот)
                    await voice_channel.guild.voice_client.disconnect()
                    self.tts_channels.pop(voice_channel.id)
        # if member.bot:
        #     if before.channel is not None and after.channel is None:
        #         voice_channel = before.channel
        #         self.tts_channels.pop(voice_channel.id)

    @tasks.loop(seconds=0.1)
    async def tts_background(self):
        # print("bg loop")
        # print(self.tts_channels)
        for TTS_client in self.tts_channels.values():
            if not TTS_client["vc"].is_playing():
                # print(TTS_client)
                if len(TTS_client["queue"]) == 0:
                    continue
                else:
                    try:
                        await self.TTSify(TTS_client["queue"][0])
                    except:
                        ...
                    TTS_client["queue"].pop(0)


    @tts_commands.command(name="включить",description="Включает озвучку чата войса говорилкой от гугла. Если она работает, конечно же...")
    async def initTTS(self, ctx):
        member = ctx.guild.get_member(ctx.author.id)
        if not member:
            await ctx.respond("Вы должны быть на сервере!", ephemeral=True)
            return
        if not member.voice:
            await ctx.respond("Вы должны быть в голосовом чате!", ephemeral=True)
            return
        if not member.voice.channel:
            await ctx.respond("Вы должны быть в голосовом чате!", ephemeral=True)
            return
        channel = member.voice.channel
        if isinstance(channel, discord.StageChannel):
            await ctx.respond("Вы можете использовать говорилку ТОЛЬКО в голосовых каналах. На сценах она отключена!", ephemeral=True)
            return
        if channel.guild.voice_client is not None:
            await channel.guild.voice_client.disconnect()
        vc = await channel.connect(cls=discord.VoiceClient)
        await ctx.respond("Говорилка включена!")
        self.tts_channels[channel.id] = {"vc":vc, "queue":[]}
        # print("ГОВОРИЛКА", vc)
    @tts_commands.command(name="отключить",description="выкидывает бота из войса и выключает эту ваши говорилку")
    async def disconnectSpeaker(self, ctx: discord.ApplicationContext):
        member = ctx.guild.get_member(ctx.author.id)
        if not member:
            await ctx.respond("Вы должны быть на сервере!", ephemeral=True)
            return
        if not member.voice:
            await ctx.respond("Вы должны быть в голосовом чате!", ephemeral=True)
            return
        if not member.voice.channel:
            await ctx.respond("Вы должны быть в голосовом чате!", ephemeral=True)
            return
        channel = member.voice.channel
        if member.guild.me.voice.channel.id != channel.id:
            await ctx.respond("Вы должны быть в голосовом чате с ботом!", ephemeral=True)
            return
        await channel.guild.voice_client.disconnect()
        await ctx.respond("Говорилка выключена!")
    @tts_commands.command(name="пропустить",description="пропускает текущую фразу в говорилке")
    async def skipTTS(self, ctx):
        member = ctx.guild.get_member(ctx.author.id)
        if not member:
            await ctx.respond("Вы должны быть на сервере!", ephemeral=True)
            return
        if not member.voice:
            await ctx.respond("Вы должны быть в голосовом чате!", ephemeral=True)
            return
        if not member.voice.channel:
            await ctx.respond("Вы должны быть в голосовом чате!", ephemeral=True)
            return
        channel = member.voice.channel
        if member.guild.me.voice.channel.id != channel.id:
            await ctx.respond("Вы должны быть в голосовом чате с ботом!", ephemeral=True)
            return
        if len(self.tts_channels[channel.id]["queue"]) == 0:
            await ctx.respond("Говорилка пуста!")
            return
        # self.tts_channels[channel.id]["queue"].pop(0)
        self.tts_channels[channel.id]["vc"].stop()
        await ctx.respond("Текущая фраза говорилки пропущена!")


    @commands.Cog.listener("on_message")
    async def TTS_on_message(self, message: discord.Message):
        if not isinstance(message.channel, discord.VoiceChannel):
            return
        if not message.guild.me.voice or not message.channel.id in self.tts_channels.keys():
            return
        # if len(message.content) == 0:
        #     if message.attachments:
        #         print(message.attachments[0].filename)
        #         if message.attachments[0].filename.endswith(".mp3"):# or message.attachments[0].filename.endswith(".wav"):
        #             self.tts_channels[message.channel.id]["queue"].append(message)
        #
        #     return
        if message.author.id == self.bot.user.id:
            # print("ids are same")
            return
        # print(self.tts_channels)
        # print(message.content)
        if message.content == "":
            return
        self.tts_channels[message.channel.id]["queue"].append(message)
        # print(self.tts_channels)














def setup(bot):
    bot.add_cog(TTS(bot))
