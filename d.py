import enum
import uuid

import discord.ext.commands

import Data
from Data import db


class Schemes(enum.Enum):
    user = 0
    character = 1
    logconfig = 2
    guid = 3
    AI_conversation = 4
    location = 5
    rp_message = 6
    rp_message_v0 = 7


def schema(document, scheme):
    fields = {}
    if scheme == Schemes.user:
        fields = {"userid": None, "username": " ", "about": None,
                  "age": None, "timezone": None, "color": None,
                  "karma": None, "luck": None, "permissions": None,
                  "money": None, "money_bank": None, "xp": 0, 'banned': 0, 'autoresponder': False,
                  "autoresponder-offline": None, "autoresponder-inactive": None, "autoresponder-disturb": None,
                  "premium_end": 0, "total_reminders": 0, "inventory": {},
                  "birthday_day": 0, "birthday_month": 0, "birthday_year": 0, "activity_changes": [],
                  "access_token": None, "access_token_expires": 0, "LLM_memories": [], "LLM_system_prompt": "",
                  "NSFW_LLM_memories": [], "NSFW_LLM_system_prompt": [], "triggers_achieved":{},
                  "call_AI_on_mention":True,
                  "password":None, "email":None, "discord_auth":True,
                  "UUID":None,
                  "bio_gender":None
                  }
        '''banned: 0 - нет бана, 1 - нет команд, 2 - опасный пользователь'''

    # if scheme == Schemes.logconfig:
    #     fields = {"id":0}
    if scheme == Schemes.guid:
        '''status - обычный/партнёрский/сервер GDT'''
        fields = {

            "id": None,
            "name": None, "icon": None,

            "muteroleid": None,

            "mutes": {},

            "bumpcolor": None,

            "bumptext": None,

            "invitelink": None,

            "ownerid": None, "ownername": None,

            "apocalypseChannel": None,

            "apocalypseChannelHook": None,

            "apocalypseLastSendDay": None,

            "parentID": None,

            "autoPublish": None,

            "isAPchannelThread": None,
            "partnershipState": 0,
            "status": 0, "pr_channel": 0,
            "presets": {
                "channels": [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}],
                "roles": [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]},
            "voiceRoomCreatorChannels": [],
            "voiceRooms": [],
            "prisonCategoryId": None,
            "bans": {},

        }
    if scheme == Schemes.character:
        fields = {
            "name": None, "bodystats": None, "age": None,
            "abilities": None, "weaknesses": None, "character": None,
            "inventory": None, "bio": None, "appearances": None,
            "art": "https://media.discordapp.net/attachments/1018886769619505212/1176561157939662978/ad643992b38e34e2.png",
            "shortened": None, "id": None, "owner": 0,
            "prefix": None, "totalMessages": 0
        }
    if scheme == Schemes.AI_conversation:
        fields = {"type": "", "userid": 0,
                  "username": "",
                  "model": "",
                  "tokens_cutoff": 1500,
                  "symbols_cutoff": 4000,
                  "last_message_utc": 0,
                  "system_prompt": "",
                  "history": [],
                  "memory": [],
                  "total_messages": 0,
                  "last_tokens": 0,
                  "total_tokens": 0,
                  "NSFW":False,
                  "max_tokens": 512
                  }
        '''types: [user_conversation, user_conversation_nsfw]'''
    if scheme == Schemes.location:
        fields = {
            "UUID": None,
            "id":"",
            "channel_paths":[], # "discord:guild id:channel id:thread id or 0",
            "current_players": [], # character id or user id
            "description": "",
            "prompt": "",
            "title": "",
            "world_code": "" #letter.num3-flags: [e]arth-like, [t]emp, [T]est, [j]oke, [d]anger
        }

    if scheme == Schemes.rp_message:
        fields = {
            "UUID": None,
            "message_id": 0, #discord message id
            "location_id": "",
            "content":"",
            "author_id": 0,
            "author_name": "",
            "author_charid":"",
            "related_memories": {}, #APLR id: list of str
            "important_memories": {}, #APLR id: list of str
            "chunks": [],
            # "embeddingUUIDs":[],
            "timestamp": 0, #UNIX timestamp
        }
    if scheme == Schemes.rp_message_v0:
        fields = {
            "UUID": None,
            "message_id": 0, #discord message id
            "content":"",
            "author_id": 0,
            "author_charname": "", #CHARACTER NAME
            "author_charid":"",
            "actor": "",
            "timestamp": 0, #UNIX timestamp sec
            "chunks": {}, #chunk:uuid
            "memories": {}, #uuid:payload
        }

    fields_check = {}
    if not document:
        document = fields
    for k in fields.keys():
        fields_check[k] = False
    for k in document.keys():
        if k in fields.keys():
            fields_check[k] = True
    for k in fields_check:
        if not fields_check[k]:
            document[k] = fields[k]
            fields_check[k] = True
    if "UUID" in document.keys():
        if document["UUID"] is None:
            document["UUID"] = str(uuid.uuid4())
    return document


def getGuild(ctx, extra_query=None) -> dict:
    query = {"id": ctx.guild.id}
    if extra_query:
        query.update(extra_query)
    doc = db.ds_guilds.find_one(query)
    new = False
    if not doc:
        doc = {}
        doc["id"] = ctx.guild.id
        new = True
    doc["name"] = ctx.guild.name
    doc["icon"] = ctx.guild.icon.url if ctx.guild.icon else Data.discord_logo
    doc["ownerid"] = ctx.guild.owner.id
    doc["ownername"] = ctx.guild.owner.name

    doc = schema(doc, Schemes.guid)
    if new:
        db.ds_guilds.insert_one(doc)
    return doc


def getGuildByID(id: int, extra_query=None) -> dict:
    query = {"id": id}
    if extra_query:
        query.update(extra_query)
    doc = db.ds_guilds.find_one(query)
    new = False
    if not doc:
        doc = {}
        doc["id"] = id
        new = True

    doc = schema(doc, Schemes.guid)
    if new:
        db.ds_guilds.insert_one(doc)
    return doc


def getUser(id, name, extra_query=None) -> dict:
    query = {"userid": id}
    if extra_query:
        query.update(extra_query)
    doc = db.users.find_one(query)
    new = False
    updated = False
    if not doc:
        doc = {"userid": id}
        new = True
    doc = schema(doc, Schemes.user)
    if not new and doc["username"] != name:
        updated = True
    doc["username"] = name
    if "_id" in doc.keys():
        doc.pop("_id")
    if new:
        db.users.insert_one(doc)
    if updated:
        db.users.update_one({"userid": id}, {"$set": doc})
    return doc


def makeBasicConversation(userid, username):
    # fields={"type":"","userid":0,
    #       "username":"",
    #       "model":"",
    #       "tokens_cutoff":1500,
    #       "symbols_cutoff":4000,
    #       "last_message_utc":0,
    #       "system_prompt":"",
    #       "history":[],
    #       "memory":[],
    #       "total_messages":0,
    #       "last_tokens":0,
    #       "total_tokens":0
    #       }
    doc = {}
    doc = schema(doc, Schemes.AI_conversation)
    doc["userid"] = userid
    doc["username"] = username
    doc["model"] = "mistralai/Mistral-7B-Instruct-v0.3"
    doc["tokens_cutoff"] = 3000



    return doc
