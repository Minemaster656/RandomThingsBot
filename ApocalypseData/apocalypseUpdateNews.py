import platform
import time

import aiohttp
import discord
from discord import Webhook

import data
import utils
from private import coreData

from private import coreData
from data import cursor
from data import conn
def sendNewsOfApocalypse():
    cursor.execute(
        "SELECT apocalypseChannelHook, apocalypseLastSendDay, serverid, isThread, apocalypseChannel FROM servers")
    urls = cursor.fetchall()

    # print("Loop tick")

    for hook_url in urls:
        url = hook_url[0]  # Извлечение значения из кортежа

        if hook_url[0] is not None and hook_url[1] is not None and hook_url[2] is not None and hook_url[
            3] is not None and hook_url[4] is not None:

            try:
                if url is not None:

                    async with aiohttp.ClientSession() as session:
                        webhook = Webhook.from_url(str(url), session=session)

                        embed = discord.Embed(title="Новости Самого странного апокалипсиса",description=" ",colour=0xffffff)


                        if hook_url[3]:
                            await webhook.send(f"Новости {publicCoreData.apocalypseDLC}", username=publicCoreData.hook_names["apocalypse"]+": новости",
                                               embed=list[1], thread=discord.Object(hook_url[4]))
                        else:
                            await webhook.send(f"Новости {publicCoreData.apocalypseDLC}", username=publicCoreData.hook_names["apocalypse"]+": новости",
                                               embed=list[1])
                        await webhook.send(f"Новости {publicCoreData.apocalypseDLC}", username=publicCoreData.hook_names["apocalypse"]+": новости", embed=list[1])

            except:
                ...


#TODO: сделать объявление о новом новом годе