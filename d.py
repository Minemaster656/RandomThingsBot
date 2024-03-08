import enum

import discord.ext.commands

import Data
from Data import db


class Schemes(enum.Enum):
    user = 0
    character = 1
    logconfig = 2
    server = 3
    AI_conversation = 4


def schema(document, scheme):
    fields = {}
    if scheme == Schemes.user:
        fields = {"userid": None, "username": " ", "about": None,
                  "age": None, "timezone": None, "color": None,
                  "karma": None, "luck": None, "permissions": None,
                  "money": None, "money_bank": None, "xp": 0, 'banned': 0, 'autoresponder': False,
                  "autoresponder-offline": None, "autoresponder-inactive": None, "autoresponder-disturb": None,
                  "premium_end": 0, "total_reminders": 0, "inventory": {},
                  "birthday_day": 0, "birthday_month": 0, "birthday_year": 0, "activity_changes":[], "access_token": None, "access_token_expires": 0}
        '''banned: 0 - нет бана, 1 - нет команд, 2 - опасный пользователь'''

    # if scheme == Schemes.logconfig:
    #     fields = {"id":0}
    if scheme == Schemes.server:
        '''status - обычный/партнёрский/сервер GDT'''
        fields = {

            "serverid": None,
            "name": None, "icon": None,

            "muteroleid": None,

            "mutes": None,

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
                "roles": [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]}

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
    if scheme==Schemes.AI_conversation:
      fields={"type":"","userid":0,
      "username":"",
      "model":"",
      "tokens_cutoff":1500,
      "symbols_cutoff":4000,
      "last_message_utc":0,
      "system_prompt":"",
      "history":[],
      "memory":[],
      "total_messages":0,
      "last_tokens":0,
      "total_tokens":0
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
    return document


def getGuild(ctx) -> dict:
    doc = db.servers.find_one({"serverid": ctx.guild.id})
    new = False
    if not doc:
        doc = {}
        doc["serverid"] = ctx.guild.id
        new = True
    doc["name"] = ctx.guild.name
    doc["icon"] = ctx.guild.icon.url if ctx.guild.icon else Data.discord_logo
    doc["ownerid"] = ctx.guild.owner.id
    doc["ownername"] = ctx.guild.owner.name

    doc = schema(doc, Schemes.server)
    if new:
        db.servers.insert_one(doc)
    return doc


def getGuildByID(id: int) -> dict:
    doc = db.servers.find_one({"serverid": id})
    new = False
    if not doc:
        doc = {}
        doc["serverid"] = id
        new = True

    doc = schema(doc, Schemes.server)
    if new:
        db.servers.insert_one(doc)
    return doc


def getUser(id, name) -> dict:
    doc = db.users.find_one({"userid": id})
    new = False
    updated = False
    if not doc:
        doc = {"userid": id}
        new = True
    doc = schema(doc, Schemes.user)
    if not new and doc["username"] != name:
        updated = True
    doc["username"] = name
    if new:
        db.users.insert_one(doc)
    if updated:
        db.users.update_one({"userid": id}, {"$set": doc})
    return doc
