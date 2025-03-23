from pymongo import MongoClient
import os

#Mongo DB schema:

# Document structure for the 'users' collection:
# {
#   "_id": "google_user_id_123", // String: User ID (sub claim from ID token)
#   "collections": [
#     {
#       "collectionId": "collection_id_abc", // String: Unique ID for the collection
#       "chatHistory": [
#         {
#           "role": "user", // String: "user" or "assistant"
#           "content": "Hello, LLM!", // String: Message content
#           "timestamp": ISODate("2023-10-27T10:00:00Z") // Date: Timestamp of the message
#         },
#         // ... more chat messages ...
#       ]
#     },
#     // ... more collections ...
#   ]
# }

# Get the MongoDB connection string from environment variables
mongo_uri = os.environ.get("MONGODB_URI")

# Create a MongoDB client
client = MongoClient(mongo_uri)

# Get the database
db = client.Capstone #Change your_database_name

# Get the users collection
users_collection = db.users


from bson.objectid import ObjectId

def add_collection(user_id, collection_name):
    collection_id = str(ObjectId())  # Generate a unique ID for the collection
    new_collection = {
        "collectionId": collection_id,
        "name": collection_name,
        "chatHistory": []
    }
    users_collection.update_one(
        {"_id": user_id},
        {"$push": {"collections": new_collection}}
    )
    return collection_id

def delete_collection(user_id, collection_id):
    users_collection.update_one(
        {"_id": user_id},
        {"$pull": {"collections": {"collectionId": collection_id}}}
    )


def get_collections(user_id):
    user = users_collection.find_one({"_id": user_id})
    return user["collections"] if user else []



def makeUser(user_id):
    user = users_collection.find_one({"_id": user_id})
    if not user:
        user_data = {
            "_id": user_id,
            "collections": []
        }
        users_collection.insert_one(user_data)
        print(f"User {user_id} created in database.", flush=True)
    else:
        print(f"User {user_id} found in database.", flush=True)


def get_chat_history(user_id, collection_id):
    user = users_collection.find_one({"_id": user_id})
    if not user:
        return []
    for collection in user["collections"]:
        if collection["collectionId"] == collection_id:
            return collection["chatHistory"]
    return []


from datetime import datetime

def add_message(user_id, collection_id, role, content):
    message = {
        "role": role,  # "user" or "assistant"
        "content": content,
        "timestamp": datetime.utcnow()
    }
    users_collection.update_one(
        {"_id": user_id, "collections.collectionId": collection_id},
        {"$push": {"collections.$.chatHistory": message}}
    )
