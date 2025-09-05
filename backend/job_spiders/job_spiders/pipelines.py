import sys
import os
from datetime import datetime
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Append backend directory (where database.py lives)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))

try:
    from database import get_jobs_collection
    use_database_file = True
except ImportError:
    use_database_file = False

class MongoDBPipeline:
    def open_spider(self, spider):
        try:
            if use_database_file:
                self.collection = get_jobs_collection()
            else:
                self.client = pymongo.MongoClient(
                    os.getenv("MONGO_URI"),
                    connectTimeoutMS=30000,
                    serverSelectionTimeoutMS=30000
                )
                self.db = self.client["jobtracker"]
                self.collection = self.db["jobs"]
                self.collection.create_index("link", unique=True)
                self.collection.create_index("posted_date")
            spider.logger.info("✅ Connected to MongoDB.")
        except Exception as e:
            spider.logger.error(f"❌ MongoDB connection failed: {str(e)}")
            raise e

    def close_spider(self, spider):
        if not use_database_file and hasattr(self, 'client'):
            self.client.close()
            spider.logger.info("🔌 MongoDB connection closed.")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Validation: Ensure required fields
        if not adapter.get("title") or not adapter.get("link"):
            raise DropItem("❌ Missing required job fields.")

        # Ensure posted_date is a valid datetime
        try:
            posted = adapter.get("posted_date")
            adapter["posted_date"] = datetime.fromisoformat(posted) if posted else datetime.now()
        except Exception:
            adapter["posted_date"] = datetime.now()

        # Save or update in MongoDB
        try:
            self.collection.update_one(
                {"link": adapter["link"]},
                {"$set": adapter.asdict()},
                upsert=True
            )
            spider.logger.info(f"✅ Job saved: {adapter.get('title')} | {adapter.get('link')}")
        except Exception as e:
            spider.logger.error(f"❌ Error saving job to MongoDB: {e}")
            raise DropItem(f"MongoDB error: {e}")

        return adapter.item
