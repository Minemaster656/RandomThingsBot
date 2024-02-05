import Data
from Data import db
import d

for document in db.characters.find():
    document = d.schema(document, d.Schemes.character)
    db.characters.update_one({"_id": document["_id"]}, {"$set": document})