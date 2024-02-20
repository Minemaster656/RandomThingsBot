import enum
import json
import sqlite3

import discord
import pymongo
from pymongo import MongoClient

import INIT
from private import coreData
import os


# from discord.app_commands import commands
class Icons(enum.Enum):
    verified = 0
    root = 1
    edit_characters = 2
    banned1=3
    banned2=4

secret_guilds = []
test_guilds = [1019180616731873290, 1076117733428711434, 855045703235928094, 1033752522306883715, 1111235284558950402,
               1153367008247812188]
webhook_avatar_url = "https://images-ext-2.discordapp.net/external/-1-6AJKBQh38RYGz6D3j-IgURlKEfFifX5LeJ8h-TBw/%3Fsize%3D4096/https/cdn.discordapp.com/avatars/1126887522690142359/0767783560eee507f86c95a4b09f120a.png?width=437&height=437"
permissions_user = ["root", "edit_characters", "say_as_bot", "edit_permissions", "---", "edit_economy", "verified",
                    "mnl_console"]
embedColors = {"Error": 0xf03255, "Exception": 0xff2f00, "Success": 0x29ff4d, "Warp": 0x00b3ff,
               "Neutral": discord.Color.blue(), "Economy": 0xffcc12, "Notification":0xfad243}
WPG_whitelist = [609348530498437140]
permission_root_whitelist = [609348530498437140, 617243612857761803]
preffix = "!!"
# preffix = ".!!"  # TODO: SET IF BETA
currency = "<:catalist:1076130269867819099>"
icons = {Icons.verified: "✅", Icons.root: "🔨", Icons.edit_characters: "🕵️",
         Icons.banned1:"❌", Icons.banned2:"‼️"}
discord_logo = "https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png"
infectionRolesID = [1151515080219967498, 1135925890182807552, 1152163431869329468]
apocalypseDLC = "Самый странный апокалипсис⁶™"
hook_names = {"apocalypse": apocalypseDLC}
data_DB_path = "private/data.db"
INIT.initDB(data_DB_path)
conn = None#sqlite3.connect(data_DB_path)
cursor = None#conn.cursor()
client = MongoClient(coreData.mongo_url)
db = client[coreData.mongo_db_name]
collections = {"users": db["users"], "servers": db["servers"], "countries": ["countries"]}

file_path = os.path.join('private', 'interchats.json')
interchats = {}
team_server_id = 1019180616731873290
blanks_moderation_channel_id = 1193178847923929108
botIDs = [1126887522690142359, 1169691387562835968]

ideasChannel = 1203626395377475634


devs=[609348530498437140, 639066140957736971]


if not os.path.exists(file_path):
    interchats = {}
else:
    with open(file_path, 'r') as file:
        try:
            interchats = json.load(file)
        except json.JSONDecodeError:
            interchats = {}

interhubs = ["normal", "rp", "rp2", "rp_bottomOfTheAbyss", "rp_void", "admins", "normal2", "normal_en", "rp_tavern",
             "rp_cafe", "tests", "rp_mysteriousShop", "memes", "rp_space", "media"]
interbans = [897193427479973961]


class EmbedColor(enum.Enum):
    Error = 0
    Exception = 1
    Success = 2
    Warp = 3
    Neutral = 4
    Economy = 5
    Notification = 6


def getEmbedColor(color: EmbedColor) -> discord.Color:
    colors = {
        EmbedColor.Error: embedColors["Error"],
        EmbedColor.Exception: embedColors["Exception"],
        EmbedColor.Success: embedColors["Success"],
        EmbedColor.Warp: embedColors["Warp"],
        EmbedColor.Neutral: embedColors["Neutral"],
        EmbedColor.Economy: embedColors["Economy"],
        EmbedColor.Notification: embedColors["Notification"]
    }
    return colors[color]


async def parsePermissionFromUser(id: int, permission: str):
    usr = db.users.find_one({"userid": id})
    if not usr:
        return False
    try:
        string = db.users.find_one({"userid": id}, {"permissions": 1})
        if string:
            if len(string["permissions"]) > 2:
                print(string["permissions"])
                dictitonary = json.loads(string["permissions"])

                if permission in dictitonary:
                    return dictitonary[permission]
                else:
                    return False
        else:
            return False
    except:
        return False

    return False


async def setPermissionForUser(id: int, permission: str, value: bool):
    # cursor.execute('SELECT permissions FROM users WHERE userid = ?', (id,))
    perms = db.users.find_one({"userid": id})  # cursor.fetchone()
    dictionary = {}
    if not perms:
        writeUserToDB(id, "unknown")
    if not perms["permissions"] or perms["permissions"] == "" or perms["permissions"] == " ":
        dictionary = {permission: value}
    else:
        # print("Perms: ",perms)
        try:
            dictionary = json.loads(perms["permissions"])
        except:
            ...
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
    db.users.update_one({"userid": id}, {"$set": {"permissions": '{"root": true}'}})
    print(f"INSERTED ROOT TO {id}")
    # conn.close()


# def writeUserToDB(user):
#     cursor.execute("INSERT INTO users (userid, username) VALUES (?, ?)", (user.id, user.name))
#     conn.commit()
def writeUserToDB(id: int, name: str):
    '''Добавляет в базу данных полдьзователя. ТРЕБУЕТСЯ ФОРМАТИРОВАНИЕ СХЕМЫ!!!'''
    # cursor.execute("INSERT INTO users (userid, username) VALUES (?, ?)", (id, name))
    # conn.commit()\
    doc = db.users.find_one({"userid": id})
    if not doc:
        doc = {"userid": id, "username": name, "about": None, "age": None,
               "timezone": None,
               "color": None,

               "karma": 0,
               "luck":
                   0,
               "permissions": None,
               "money":
                   0,
               "money_bank":
                   0, "xp": 0, 'banned': 0, 'autoresponder': False,
                  "autoresponder-offline": None, "autoresponder-inactive": None, "autoresponder-disturb": None}
        db.users.insert_one(doc)
    return doc


def findServerInDB(ctx):
    ownerid = ctx.guild.owner_id
    serverid = ctx.guild.id

    result = db.servers.find_one({"serverid": serverid})

    if not result:
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
    ...
    # cursor.execute('''CREATE IF NOT EXISTS TABLE countries (
#     userid         INTEGER,
#     countryname    TEXT,
#     government     TEXT,
#     ideology       TEXT,
#     currency       TEXT,
#     about          TEXT,
#     flagURL        TEXT,
#     extraSymbols   TEXT,
#     ownerdata      TEXT,
#     id             TEXT,
#     money          INTEGER DEFAULT (0),
#     population     INTEGER DEFAULT (0),
#     agreement      INTEGER DEFAULT (0),
#     area           INTEGER DEFAULT (0),
#     infrastructure INTEGER DEFAULT (0),
#     medicine       INTEGER DEFAULT (0),
#     eudication     INTEGER DEFAULT (0),
#     attack         INTEGER DEFAULT (0),
#     armor          INTEGER DEFAULT (0),
#     fuel           INTEGER DEFAULT (0),
#     fuel_space     INTEGER DEFAULT (0),
#     fuel_star      INTEGER DEFAULT (0),
#     fuel_void      INTEGER DEFAULT (0),
#     transport      INTEGER DEFAULT (0),
#     tech_index     INTEGER DEFAULT (0),
#     tech           TEXT,
#     food           INTEGER DEFAULT (0),
#     materials      INTEGER DEFAULT (0)
# )''')


# '''CREATE TABLE servers (
#     serverid   INTEGER,
#     muteroleid INTEGER,
#     mutes      TEXT,
#     bumpcolor  TEXT,
#     bumptext   TEXT,
#     invitelink TEXT,
#     ownerid    INTEGER
# );'''


def getUserNameByID(user_id: int, ctx):
    user = ctx.guild.get_member(int(user_id))
    if user:
        return user.name
    else:
        user_data = db.users.find_one({"userid": user_id})
        if user_data:
            return user_data['username']
        else:
            return user_id


async def addXP(userid: int,
                value: float, username: str):
    '''Добавляет опыт пользователю'''

    def schema(doc):
        fields = {"userid": 0, "username": " ", "about": None,
                  "age": None, "timezone": None, "color": None,
                  "karma": 0, "luck": 0, "permissions": None,
                  "money": 0, "money_bank": 0, "xp": 0}
        fields_check = {}
        if not doc:
            document = fields
        for k in fields.keys():
            fields_check[k] = False
        for k in doc.keys():
            if k in fields.keys():
                fields_check[k] = True
        for k in fields_check:
            if not fields_check[k]:
                doc[k] = fields[k]
                fields_check[k] = True
        return doc

    doc = db.users.find_one({"userid": userid})
    if doc:
        # doc = db.users.find_one({"id":user.id})
        doc = schema(doc)
        doc["xp"] += value
        db.users.update_one({"userid": userid}, {"$set": doc})
        print("Found")
    else:
        writeUserToDB(userid, username)
        doc = db.users.find_one({"userid": userid})
        doc = schema(doc)
        doc["xp"] += value
        db.users.update_one({"id": userid}, {"$set": doc})

