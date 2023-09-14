import pymongo
import random

def allocate_inventory_record():
    initials = '123456789abcdefghjkmnopqrstuvwxyz'
    prefix = random.choice(initials) + random.choice(initials)
    return prefix
    client = pymongo.MongoClient("mungo.local:27017")
    db = client["go"]
    collection = db["link"]
    matching_record = collection.find_one({"identifier": {"$regex": f"^{prefix}"}, "allocated": False})
print(allocate_inventory_record())
