from dotenv import load_dotenv
from motor import motor_asyncio
from typing import Optional
import os

load_dotenv()

DEFAULT_MONGO_DATABASE = "db"
RAW_MONGO_URL = os.getenv("RAW_MONGO_URL")
RAW_MONGO_DATABASE = os.getenv("RAW_MONGO_DATABASE") if os.getenv("RAW_MONGO_DATABASE") else DEFAULT_MONGO_DATABASE
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DATABASE = os.getenv("MONGO_DATABASE") if os.getenv("MONGO_DATABASE") else DEFAULT_MONGO_DATABASE

raw_client = motor_asyncio.AsyncIOMotorClient(RAW_MONGO_URL)
raw_db = raw_client[RAW_MONGO_DATABASE]

client = motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DATABASE]
        
def new_client(raw: bool = False):
    mongo_url = MONGO_URL
    mongo_db = MONGO_DATABASE
    if raw:
        mongo_url = RAW_MONGO_URL
        mongo_db = RAW_MONGO_DATABASE

    client = motor_asyncio.AsyncIOMotorClient(mongo_url)
    db = client[mongo_db]
    return client, db
    