from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    client = MongoClient(
        os.getenv("MONGO_URI"),
        connectTimeoutMS=30000,
        serverSelectionTimeoutMS=30000,
        socketTimeoutMS=30000
    )
    return client.jobtracker

def get_jobs_collection():
    db = get_db()
    collection = db.jobs
    collection.create_index("link", unique=True)
    collection.create_index("posted_date")
    return collection
