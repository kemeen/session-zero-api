import os
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.server_api import ServerApi

load_dotenv(find_dotenv())
url = f"mongodb+srv://{os.environ.get("MONGODB_USER")}:{os.environ.get("MONGODB_PWD")}@cluster69.cipqchr.mongodb.net/?appName=Cluster69", 

def get_database(url: str, db_name: str) -> Database:
    # Create a new client and connect to the server
    client = MongoClient(url, server_api=ServerApi('1'))
    return client[db_name]

def get_collection(db: Database, collection_name: str) -> Collection:
    return db[collection_name]

db = get_database(url=url, db_name=os.environ.get("DB_NAME"))
character_collection = get_collection(db=db, collection_name="characters")
beast_collection = get_collection(db=db, collection_name="beastiary")