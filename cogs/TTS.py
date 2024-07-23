import asyncio
import os.path

import discord
from discord.ext import commands, tasks
from discord import Option
import libs.CachedTTS

class TTS(commands.Cog):
    ''' TTS | BOT COG'''
    name = "TTS"
    author = "Minemaster"

    tts_channels = {}
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener("on_voice_state_update")
    async def on_voice_state_update(self, member, before, after):
        if not member.bot:
            if before.channel is not None and after.channel is None:
                voice_channel = before.channel
                if len(voice_channel.members) == 1:  # Проверяем, что остался только один участник (бот)
                    await voice_channel.guild.voice_client.disconnect()
                    self.tts_channels.pop(voice_channel.id)
    @commands.slash_command(name="включить-говорилку",description="Включает озвучку чата войса говорилкой от гугла. Если она работает, конечно же...")
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
        await channel.send("Говорилка включена!")
        self.tts_channels[channel.id] = vc
        # print("ГОВОРИЛКА", vc)

    @commands.Cog.listener("on_message")
    async def TTS_on_message(self, message: discord.Message):
        if not isinstance(message.channel, discord.VoiceChannel):
            return
        if not message.guild.me.voice or not message.channel.id in self.tts_channels:
            return
        if len(message.content) == 0:
            return
        # vc = message.guild.me.voice.channel
        TTS = libs.CachedTTS.CachedTTS(f"files/TTS", f"files/db/TTS.db")
        # print(TTS.path_to_audio)
        # print(TTS)
        # print(os.getcwd())
        ttss = {}
        sequence = []
        ttss["tts"] = await TTS.tts(message.content)
        ttss["name_tts"] = await TTS.tts(message.author.display_name)
        ttss["speaks_tts"] = await TTS.tts("говорит")
        if message.reference:
            ttss["reply_author_name_tts"] = await TTS.tts(message.reference.resolved.author.display_name)
            ttss["reply_content_tts"] = await TTS.tts(message.reference.resolved.content)
            ttss["reply_tts"] = await TTS.tts("в ответ на сообщение")
            ttss["by_tts"] = await TTS.tts("от")

            sequence.append(ttss["name_tts"])
            sequence.append(ttss["reply_tts"])
            sequence.append(ttss["reply_content_tts"])
            sequence.append(ttss["by_tts"])
            sequence.append(ttss["reply_author_name_tts"])
            sequence.append(ttss["speaks_tts"])
            sequence.append(ttss["tts"])
        else:
            sequence.append(ttss["name_tts"])
            sequence.append(ttss["speaks_tts"])
            sequence.append(ttss["tts"])
        for key in ttss.keys():
            if ttss[key] is None:
                self.tts_channels[message.channel.id].play(discord.FFmpegPCMAudio(f"assets/tts_error.mp3"), after=lambda e: ...)
        async def play_audio(vc, audio_files):
            for file in audio_files:
                # print(file)
                # print(file.__class__)
                # print(isinstance(file, libs.CachedTTS.TTS_phrase))
                vc.play(discord.FFmpegPCMAudio(f"{file.path}/{file.filename}.mp3"), after=lambda e: ...)
                while vc.is_playing():
                    await asyncio.sleep(0.15)
        await play_audio(self.tts_channels[message.channel.id], sequence)













def setup(bot):
    bot.add_cog(TTS(bot))
