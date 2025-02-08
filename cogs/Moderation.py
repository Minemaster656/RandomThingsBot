# try:
import time

import discord
from discord import Option, Webhook, Forbidden
from discord.ext import commands, tasks

import Data
# except:
#     import pycord as discord
#     from pycord import Option, Webhook, Forbidden
#     from discord.ext import commands

# import swearfilter as sw
import utils


class Moderation(commands.Cog):
    ''' Moderation | BOT COG'''
    name = "Moderation"
    author = ""

    def __init__(self, bot):
        self.bot = bot

    moderation_commands = discord.SlashCommandGroup(
        "модерация", ""

    )

    @tasks.loop(seconds=10)
    async def moderation_loop(self):
        #TODO: !!! НЕ ПРОВЕРЕНО!!!
        guilds = Data.db.ds_guilds.find({"bans": {'$exists': True, '$ne': {}}, "mutes": {'$exists': True, '$ne': {}}})
        for doc in guilds:
            guild:discord.Guild = self.bot.get_guild(doc['id'])
            if guild:
                for user_id in doc['bans'].keys():
                    bans = await guild.bans()
                    banned_users = [ban.user.id for ban in bans]
                    if user_id in banned_users:
                        if doc['bans'][user_id] <= time.time():
                            await guild.unban(user_id, reason="Ban time expired")
                            doc['bans'].pop(user_id)
                    else:
                        doc['bans'].pop(user_id)

                Data.db.ds_guilds.update_one({"id": doc['id']}, {"$set": {'bans': doc['bans']}})

                for user_id in doc['mutes'].keys():


                    if doc['mutes'][user_id] <= time.time():
                        member = await guild.fetch_member(user_id)
                        muterole = guild.get_role(doc['muteroleid'])
                        if not member:
                            doc['mutes'].pop(user_id)
                            continue
                        if muterole in member.roles:
                            await member.remove_roles(muterole, reason="Mute time expired")
                            await member.remove_timeout(reason="Mute time expired")
                            doc['mutes'].pop(user_id)
                Data.db.ds_guilds.update_one({"id": doc['id']}, {"$set": {'mutes': doc['mutes']}})





    # @commands.command(aliases=["маты", "брань", "swears", "swear"])
    # async def checkSwear(self, ctx, *, line):
    #     async with ctx.typing():
    #         line = line.replace("\n", "")
    #
    #         line_checked = sw.findSwear(str(line))
    #         # print("LINE: ", line)
    #         # print(line_checked)
    #         await ctx.reply(utils.formatStringLength("Ругань: \n" + line_checked, 1950))


def setup(bot):
    bot.add_cog(Moderation(bot))
