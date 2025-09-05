from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import random

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
]

class RotateUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        super().__init__(user_agent)
        self.user_agents = USER_AGENTS

    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(self.user_agents)
