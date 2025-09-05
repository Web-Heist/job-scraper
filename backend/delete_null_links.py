from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["jobtracker"]
result = db.jobs.delete_many({ "link": None })

print(f"Deleted {result.deleted_count} documents where link is None.")
