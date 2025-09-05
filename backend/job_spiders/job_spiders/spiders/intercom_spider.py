import scrapy
from datetime import datetime
import uuid

class intercomSpider(scrapy.Spider):
    name = "intercom_spider"
    allowed_domains = ["boards-api.greenhouse.io"]
    start_urls = [
        "https://boards-api.greenhouse.io/v1/boards/intercom/jobs"
    ]

    def parse(self, response):
        try:
            jobs = response.json().get("jobs", [])
        except Exception as e:
            self.logger.error(f"❌ Failed to parse JSON: {e}")
            return

        for job in jobs:
            title = job.get("title")
            link = job.get("absolute_url")
            location = job.get("location", {}).get("name", "Remote")

            if not title or not link:
                self.logger.warning("⚠️ Skipping job due to missing title or link")
                continue

            yield {
                "job_id": str(uuid.uuid4()),
                "title": title,
                "company": "intercom",
                "location": location,
                "link": link,
                "posted_date": datetime.now().isoformat(),
                "source": "intercom"
            }
