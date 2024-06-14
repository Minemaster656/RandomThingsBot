import Data
from Data import db
import d

for document in db.users.find():
    document = d.schema(document, d.Schemes.user)
    db.users.update_one({"_id": document["_id"]}, {"$set": document})