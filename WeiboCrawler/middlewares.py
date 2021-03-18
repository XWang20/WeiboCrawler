# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import requests

class IPProxyMiddleware(object):

    def fetch_proxy(self):
        # You need to rewrite this function if you want to add proxy pool
        # the function should return a ip in the format of "ip:port" like "12.34.1.4:9090"

    def process_request(self, request, spider):
        proxy_data = self.fetch_proxy()
        if proxy_data:
            current_proxy = proxy_data
            spider.logger.debug(f"current proxy:{current_proxy}")
            request.meta['proxy'] = current_proxy