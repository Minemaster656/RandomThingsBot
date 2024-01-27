import enum

from Data import db


class Schemes(enum.Enum):
    user = 0
    character = 1
    logconfig = 2
    server = 3


def schema(document, scheme):
    fields = {}
    if scheme == Schemes.user:
        fields = {"userid": None, "username": " ", "about": None,
                  "age": None, "timezone": None, "color": None,
                  "karma": None, "luck": None, "permissions": None,
                  "money": None, "money_bank": None, "xp": 0}

    # if scheme == Schemes.logconfig:
    #     fields = {"id":0}
    if scheme == Schemes.server:
        fields = {

            "serverid": None,
            "name":None, "icon":None,

            "muteroleid": None,

            "mutes": None,

            "bumpcolor": None,

            "bumptext": None,

            "invitelink": None,

            "ownerid": None, "ownername":None,

            "apocalypseChannel": None,

            "apocalypseChannelHook": None,

            "apocalypseLastSendDay": None,

            "parentID": None,

            "autoPublish": None,

            "isAPchannelThread": None

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
