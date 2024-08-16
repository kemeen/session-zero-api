from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
uri = "mongodb+srv://bumble:sloth@cluster69.cipqchr.mongodb.net/?appName=Cluster69"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["session_zero"]
# for col in db.list_collection_names():
#     print(col)

for doc in db["beastiary"].find():
    if "name" in doc:
        print(doc["name"])