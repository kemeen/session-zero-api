from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())


# Create a new client and connect to the server
client = MongoClient(
    host=os.getenv("HOST"), 
    username=os.getenv("USERNAME"), 
    password=os.getenv("PASSWORD"), 
    appname=os.getenv("APPNAME"),
    document_class=dict,
    tz_aware=True,
    connect=True,
    server_api=ServerApi('1'))