import sqlite3

import discord
# from discord.app_commands import commands



embedColors = {"Error":0xf03255, "Exception":0xff2f00, "Success":0x29ff4d, "Warp":0x00b3ff, "Neutral": discord.Color.blue(), "Economy": 0xffcc12}
WPG_whitelist = [609348530498437140]
permission_root_whitelist = [609348530498437140, 617243612857761803]
preffix = "."
currency = "[placeholders:currency]"

async def parsePermissionFromUser(id : int, permission : str):
    # await ctx.respond("Проверка...")
    cursor.execute('SELECT permissions FROM users WHERE userid = ?', (id,))
    string = cursor.fetchone()

    if string is None or string == "":
        # await ctx.respond("None")
        return False

    if f"{permission}:True" in string:
        # await ctx.respond(f"{permission}:True")
        return True
    return False

def insertRoot():
    # import sqlite3
    # conn = sqlite3.connect('data.db')
    # cursor = conn.cursor()
    cursor.execute("UPDATE users SET permissions = ? WHERE userid = ?", ("root:True", 609348530498437140))
    conn.commit()
    # conn.close()
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

def writeUserToDB(user):
    cursor.execute("INSERT INTO users (userid, username) VALUES (?, ?)", (user.id, user.name))
    conn.commit()
def writeUserToDB(id : int, name : str):
    cursor.execute("INSERT INTO users (userid, username) VALUES (?, ?)", (id, name))
    conn.commit()
def initTables():
    cursor.execute('''CREATE IF NOT EXISTS TABLE countries (
    userid         INTEGER,
    countryname    TEXT,
    government     TEXT,
    ideology       TEXT,
    currency       TEXT,
    about          TEXT,
    flagURL        TEXT,
    extraSymbols   TEXT,
    ownerdata      TEXT,
    id             TEXT,
    money          INTEGER DEFAULT (0),
    population     INTEGER DEFAULT (0),
    agreement      INTEGER DEFAULT (0),
    area           INTEGER DEFAULT (0),
    infrastructure INTEGER DEFAULT (0),
    medicine       INTEGER DEFAULT (0),
    eudication     INTEGER DEFAULT (0),
    attack         INTEGER DEFAULT (0),
    armor          INTEGER DEFAULT (0),
    fuel           INTEGER DEFAULT (0),
    fuel_space     INTEGER DEFAULT (0),
    fuel_star      INTEGER DEFAULT (0),
    fuel_void      INTEGER DEFAULT (0),
    transport      INTEGER DEFAULT (0),
    tech_index     INTEGER DEFAULT (0),
    tech           TEXT,
    food           INTEGER DEFAULT (0),
    materials      INTEGER DEFAULT (0) 
)''')
