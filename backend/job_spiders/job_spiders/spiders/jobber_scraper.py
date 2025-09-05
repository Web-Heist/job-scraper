import scrapy
from datetime import datetime
import uuid


class JobberSpider(scrapy.Spider):
    name = "jobber_spider"
    allowed_domains = ["boards-api.greenhouse.io"]
    start_urls = ["https://boards-api.greenhouse.io/v1/boards/jobber/jobs"]

    custom_settings = {
        "PLAYWRIGHT_INCLUDE_PAGE": True,
        "PLAYWRIGHT_PAGE_METHOD": "goto",
        "PLAYWRIGHT_PAGE_GOTO_OPTIONS": {"wait_until": "networkidle"},
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={"playwright": True},
                callback=self.parse
            )

    def parse(self, response):
        job_cards = response.css(".opening")

        if not job_cards:
            self.logger.warning("⚠️ No job cards found.")
            return

        for card in job_cards:
            anchor = card.css("a")
            title = anchor.css("::text").get(default="").strip()
            link = anchor.attrib.get("href", "").strip()

            # Fix relative links
            if link and not link.startswith("http"):
                link = response.urljoin(link)

            location = card.css(".location::text").get(default="Remote").strip()

            if not title or not link:
                self.logger.warning(f"⚠️ Skipping job due to missing title or link: {title}, {link}")
                continue

            yield {
                "job_id": str(uuid.uuid4()),
                "title": title,
                "company": "Jobber",
                "location": location,
                "link": link,
                "posted_date": datetime.now().isoformat(),
                "source": "jobber"
            }
