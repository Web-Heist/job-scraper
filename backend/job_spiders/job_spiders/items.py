import scrapy

class JobItem(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    link = scrapy.Field()
    description = scrapy.Field()
    posted_date = scrapy.Field()
    job_id = scrapy.Field()
    source = scrapy.Field()
