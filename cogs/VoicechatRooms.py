import discord
from discord.ext import commands, tasks
from discord import Option

import Data
import d


class VoicechatRooms(commands.Cog):
    ''' VoicechatRooms | BOT COG'''
    name = "VoicechatRooms"
    author = ""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

        self.vc_rooms_loop.start()

    vc_rooms_commands = discord.SlashCommandGroup(
        "комнаты-войсов", ""

    )

    @tasks.loop(seconds=10)
    async def vc_rooms_loop(self):
        # finding every guild vhere in voiceRooms more than 0 elements:
        for guild in Data.db.ds_guilds.find({'voiceRooms.0': {"$exists": True}}):

            for voice_room in guild["voiceRooms"]:
                vc = self.bot.get_channel(voice_room)

                if vc is None:
                    guild["voiceRooms"].remove(voice_room)
                    Data.db.ds_guilds.update_one({"_id": guild["_id"]}, {"$set": {"voiceRooms": guild["voiceRooms"]}})
                # if channel is empty, delete it from voiceRooms and guild
                if len(vc.members) == 0:
                    guild["voiceRooms"].remove(voice_room)
                    Data.db.ds_guilds.update_one({"_id": guild["_id"]}, {"$set": {"voiceRooms": guild["voiceRooms"]}})
                    await vc.delete(reason="Room is empty.")

    @commands.Cog.listener("on_voice_state_update")
    async def on_voice_state_update(self, member: discord.Member, before, after):
        if not member.bot:
            guild_doc = d.getGuildByID(member.guild.id)
            for creator in guild_doc["voiceRoomCreatorChannels"]:
                if member.voice is None: continue
                if creator != member.voice.channel.id: continue
                channel: discord.VoiceChannel = member.voice.channel
                room = await channel.guild.create_voice_channel(f"Войс {member.display_name}", category=channel.category, reason="Voicechat room creation",
                                                         bitrate=channel.bitrate, user_limit=channel.user_limit,
                                                         rtc_region=channel.rtc_region, video_quality_mode=channel.video_quality_mode,
                                                         overwrites=channel.overwrites)
                perms = channel.overwrites_for(member)
                perms.manage_channels = True
                await channel.set_permissions(member, overwrite=perms)
                await member.move_to(room, reason="Voicechat room creation")
                guild_doc["voiceRooms"].append(room.id)
                Data.db.ds_guilds.update_one({"_id": guild_doc["_id"]}, {"$set": {"voiceRooms": guild_doc["voiceRooms"]}})








    @commands.has_permissions(administrator=True)
    @vc_rooms_commands.command(name="настроить",description="Позволяет создавать, настраивать и удалять комнаты голосовых чатов.")
    async def setupRoomCreator(self, ctx: discord.ApplicationContext,
                               channel: Option(discord.VoiceChannel, description="канал", required=True),
                               option = Option(str, description="настройка", required=True,
                                               choices=["задать как создатель комнат", "удалить создание комнат"])):

        if isinstance(ctx.channel, discord.channel.DMChannel) :#! DOES NOT EXISTS!!! or isinstance(ctx.channel, discord.channel.GroupDMChannel):
            await ctx.respond("Эта команда работает только на серверах!", ephemeral=True)

        guild_data = d.getGuild(ctx)

        if option == "задать как создатель комнат":

            creator_channels = guild_data["voiceRoomCreatorChannels"]

            if channel.id in creator_channels:
                await ctx.respond(f"Канал {channel.name} уже является создателем комнаты!", ephemeral=True)
            else:
                creator_channels.append(channel.id)
                guild_data["voiceRoomCreatorChannels"] = creator_channels
                Data.db.ds_guilds.update_one({"_id": guild_data["_id"]}, {"$set": {"voiceRoomCreatorChannels": guild_data["voiceRoomCreatorChannels"]}})
                await ctx.respond(f"Канал {channel.name} теперь является создателем комнаты!", ephemeral=False)

        elif option == "удалить создание комнат":

            creator_channels = guild_data["voiceRoomCreatorChannels"]

            if channel.id not in creator_channels:
                await ctx.respond(f"Канал {channel.name} не является создателем комнаты!", ephemeral=True)
            else:
                creator_channels.remove(channel.id)
                guild_data["voiceRoomCreatorChannels"] = creator_channels
                Data.db.ds_guilds.update_one({"_id": guild_data["_id"]}, {"$set": {"voiceRoomCreatorChannels": guild_data["voiceRoomCreatorChannels"]}})
                await ctx.respond(f"Канал {channel.name} больше не является создателем комнаты!", ephemeral=False)




        





def setup(bot):
    bot.add_cog(VoicechatRooms(bot))
