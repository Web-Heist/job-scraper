from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["job_tracker"]

def get_jobs_collection():
    return db["jobs"]