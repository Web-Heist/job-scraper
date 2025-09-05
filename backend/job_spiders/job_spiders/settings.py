BOT_NAME = "job_spiders"
SPIDER_MODULES = ["job_spiders.spiders"]
NEWSPIDER_MODULE = "job_spiders.spiders"

ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 2


TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}


# Pipelines
ITEM_PIPELINES = {
    'job_spiders.pipelines.MongoDBPipeline': 300,
}

# Mongo settings
MONGO_URI = "mongodb+srv://jobdb:jobdb1@cluster0.r9zke9a.mongodb.net/jobtracker"
MONGO_DATABASE = "jobtracker"
MONGO_COLLECTION = "jobs"
