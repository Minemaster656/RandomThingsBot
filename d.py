import enum

from publicCoreData import db


class Schemes(enum.Enum):
    user = 0
    character = 1


def schema(document, scheme):
    if scheme == Schemes.user:
        fields = {"userid":0, "username":" ", "about":None,
                  "age":None, "timezone":None, "color":None,
                  "karma":0, "luck":0, "permissions":None,
                  "money":0, "money_bank":0, "xp":0}
        fields_check = {}
        for k in fields.keys():
            fields_check[k] = False
        for k in document:
            if k in fields.keys():
                fields_check[k]=True
        for k in fields_check:
            if not fields_check[k]:
                document[k]=fields[k]
                fields_check[k]=True
    return document

