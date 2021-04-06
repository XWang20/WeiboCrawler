# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from scrapy import signals
import time

# class IPProxyMiddleware(object):

#     def fetch_proxy(self):
#         # You need to rewrite this function if you want to add proxy pool
#         # the function should return a ip in the format of "ip:port" like "12.34.1.4:9090"
#         pass

#     def process_request(self, request, spider):
#         proxy_data = self.fetch_proxy()
#         if proxy_data:
#             current_proxy = proxy_data
#             spider.logger.debug(f"current proxy:{current_proxy}")
#             request.meta['proxy'] = current_proxy

class TooManyRequestsRetryMiddleware(RetryMiddleware):

    def __init__(self, crawler):
        super(TooManyRequestsRetryMiddleware, self).__init__(crawler.settings)
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)
    
    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        elif response.status == 429 or response.status == 418 or response.status == 418:
            self.crawler.engine.pause()
            time.sleep(60) # If the rate limit is renewed in a minute, put 60 seconds, and so on.
            self.crawler.engine.unpause()
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        elif response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response 