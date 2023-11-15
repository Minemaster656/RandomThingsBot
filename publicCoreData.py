import json
import sqlite3

import discord
import pymongo
from pymongo import MongoClient

import INIT
from private import coreData

# from discord.app_commands import commands

secret_guilds = []

webhook_avatar_url = "https://images-ext-2.discordapp.net/external/-1-6AJKBQh38RYGz6D3j-IgURlKEfFifX5LeJ8h-TBw/%3Fsize%3D4096/https/cdn.discordapp.com/avatars/1126887522690142359/0767783560eee507f86c95a4b09f120a.png?width=437&height=437"
permissions_user = ["root", "edit_characters", "say_as_bot", "edit_permissions", "---"]
embedColors = {"Error": 0xf03255, "Exception": 0xff2f00, "Success": 0x29ff4d, "Warp": 0x00b3ff,
               "Neutral": discord.Color.blue(), "Economy": 0xffcc12}
WPG_whitelist = [609348530498437140]
permission_root_whitelist = [609348530498437140, 617243612857761803]
# preffix = "!!"
preffix = ".!!"  # TODO: SET IF BETA
currency = "<:catalist:1076130269867819099>"
infectionRolesID = [1151515080219967498, 1135925890182807552, 1152163431869329468]
apocalypseDLC = "Самый странный апокалипсис⁶™"
hook_names = {"apocalypse": apocalypseDLC}
data_DB_path = "private/data.db"
INIT.initDB(data_DB_path)
conn = sqlite3.connect(data_DB_path)
cursor = conn.cursor()
client = MongoClient(coreData.mongo_url)
db = client[coreData.mongo_db_name]
collections = {"users": db["users"], "servers": db["servers"], "countries": ["countries"]}


async def parsePermissionFromUser(id: int, permission: str):
    string = db.users.find({"userid": id}, {"permissions": 1})[0]

    if string is None or string == "":

        return False
    else:
        dictitonary = json.loads(string["permissions"])
        if permission in dictitonary:
            return dictitonary[permission]
        else:
            return False

    return False


async def setPermissionForUser(id: int, permission: str, value: bool):
    # cursor.execute('SELECT permissions FROM users WHERE userid = ?', (id,))
    perms = db.users.find({"userid": id}, {"permissions": 1})[0]  # cursor.fetchone()
    if perms[0] is None or perms[0] == "":
        dictionary = {permission: value}
    else:
        dictionary = json.loads(perms[0])

        dictionary[permission] = value
    _dictstr = json.dumps(dictionary)
    # cursor.execute('UPDATE users SET permissions = ? WHERE userid = ?', (_dictstr, id))
    # conn.commit()
    db.users.update_one({"userid": id}, {"$set": {"permissions": _dictstr}})


def insertRoot(id):
    # import sqlite3
    # conn = sqlite3.connect('data.db')
    # cursor = conn.cursor()
    # cursor.execute("UPDATE users SET permissions = ? WHERE userid = ?", ("root:True", 609348530498437140))
    # conn.commit()
    db.users.update_one({"userid": id}, {"$set": {"permissions": "root:True"}})
    # conn.close()


# def writeUserToDB(user):
#     cursor.execute("INSERT INTO users (userid, username) VALUES (?, ?)", (user.id, user.name))
#     conn.commit()
def writeUserToDB(id: int, name: str):
    # cursor.execute("INSERT INTO users (userid, username) VALUES (?, ?)", (id, name))
    # conn.commit()
    db.users.insert_one({"userid": id, "username": name, "about": None, "age": None,
                         "timezone": None,
                         "color": None,

                         "karma": 0,
                         "luck":
                             0,
                         "permissions": None,
                         "money":
                             0,
                         "money_bank":
                             0})


def findServerInDB(ctx):
    ownerid = ctx.guild.owner_id
    serverid = ctx.guild.id

    result = db.servers.find_one({"serverid": serverid})[0]

    if result is None:
        db.servers.insert_one({"serverid": serverid, "ownerid": ownerid, "bumpcolor": None,
                               "bumptext": None,
                               "invitelink": None,
                               "apocalypseChannel": None,

                               "apocalypseChannelHook": None,

                               "apocalypseLastSendDay": None,

                               "parentID": None,

                               "autoPublish": True,

                               "isAPchannelThread": True})
        # print(f"Server added: serverID: {serverid}, ownerID: {ownerid}")
        return False
    else:
        return True


def initTables():  # SQL ONLY!!!
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


'''CREATE TABLE servers (
    serverid   INTEGER,
    muteroleid INTEGER,
    mutes      TEXT,
    bumpcolor  TEXT,
    bumptext   TEXT,
    invitelink TEXT,
    ownerid    INTEGER
);'''
