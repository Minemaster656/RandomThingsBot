import asyncio
from random import randint

import discord

import publicCoreData
from publicCoreData import cursor


def invertY(y, maxY):
    invertedY = maxY - y - 1
    return invertedY
def format_number(num):
    if num < 10000:
        return str(num)
    elif num < 1e15:
        if num < 1e3:
            return f"{num:.2f}"
        elif num < 1e6:
            return f"{num/1e3:.2f}K"
        elif num < 1e9:
            return f"{num/1e6:.2f}M"
        elif num < 1e12:
            return f"{num/1e9:.2f}B"
        else:
            return f"{num/1e12:.2f}T"
    else:
        return f"{num:.2e}".replace("+", "")

def convert_to_number(string):
    if string.endswith("K"):
        return int(float(string[:-1]) * 1e3)
    elif string.endswith("M"):
        return int(float(string[:-1]) * 1e6)
    elif string.endswith("B"):
        return int(float(string[:-1]) * 1e9)
    elif string.endswith("T"):
        return int(float(string[:-1]) * 1e12)
    elif "e" in string:
        return float(string)
    else:
        return int(string)
def throwDice(id, name):

    cursor.execute("SELECT karma, luck FROM users WHERE userid = ?", (id,))
    result = cursor.fetchone()
    if result:
        karma = result[0]
        luck = result[1]
    else:
        publicCoreData.writeUserToDB(id, name)
        karma = 0
        luck = 0

    def makeThrow():
        def genRandom():
            o = randint(1, 20) + luck
            if o > 20:
                o = 20
            if o < 1:
                o = 1
            return o

        out = genRandom()

        if karma < -1 and out > 10:
            out = genRandom()
        if karma > 1 and out < 10:
            out = genRandom()
        return out
    return makeThrow()
async def noPermission(ctx, permissions):
    cursor.execute('SELECT permissions FROM users WHERE userid = ?', (ctx.author.id,))
    perms = cursor.fetchone()
    permissions = permissions.replace("|", "или")
    permissions = permissions.replace("&", "и")
    permissions = "`"+permissions+"`"
    embed = discord.Embed(title="У Вас нет прав!", description="Нет разрешения!",
                          color=publicCoreData.embedColors["Error"])
    embed.add_field(name="Нет разрешения!", value=f"Вам необходимо(ы) разрешение(я): \n> {permissions}\n<@{ctx.author.id}>\n"
                                                  f"Ваши текущие разрешения: \n"
                                                  f"> {perms}")
    await ctx.respond(embed=embed, ephemeral=False)
# while True:
#     print(format_number((convert_to_number(input(">")))))
# asyncio.run(publicCoreData.setPermissionForUser(609348530498437140, "root", True))
