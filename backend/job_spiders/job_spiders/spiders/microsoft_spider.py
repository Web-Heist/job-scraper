import scrapy
from datetime import datetime


class MicrosoftSpider(scrapy.Spider):
    name = "microsoft_spider" 
    allowed_domains = ["careers.microsoft.com"]

    def start_requests(self):
        for page in range(1, 6):
            yield scrapy.Request(
                url=f"https://gcsservices.careers.microsoft.com/search/api/v1/search?l=en_us&pg={page}&pgSz=50&o=Relevance&flt=true",
                callback=self.parse
            )

    def parse(self, response):
        try:
            jobs = response.json()["operationResult"]["result"]["jobs"]
        except Exception as e:
            self.logger.error(f"❌ Failed to parse JSON: {e}")
            return

        for job in jobs:
            job_id = job.get("jobId")
            title = job.get("title")
            location_list = job.get("properties", {}).get("locations", [])
            location = location_list[0] if location_list else None
            posted_date = job.get("postingDate")

            if not all([job_id, title, location]):
                self.logger.warning(f"⚠️ Dropped job: Missing fields\n{job}")
                continue

            yield {
                "job_id": job_id,
                "title": title,
                "company": "Microsoft",
                "location": location,
                "link": f"https://jobs.careers.microsoft.com/global/en/job/{job_id}",
                "posted_date": posted_date or datetime.now().isoformat(),
                "source": "microsoft"
            }