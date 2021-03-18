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
        url = 'http://waang20.v4.dailiyun.com/query.txt?key=NP4E33345E&word=&count=1&rand=true&ltime=0&norepeat=false&detail=false'

        proxyaddr = requests.get(url).text.split(':')[0]   #代理IP地址
        proxyport = 57114               #代理IP端口
        proxyusernm = "waang20"        #代理帐号
        proxypasswd = "Password5555"        #代理密码
        proxyurl="http://"+proxyusernm+":"+proxypasswd+"@"+proxyaddr+":"+"%d"%proxyport
        return proxyurl

    def process_request(self, request, spider):
        proxy_data = self.fetch_proxy()
        if proxy_data:
            current_proxy = proxy_data
            spider.logger.debug(f"current proxy:{current_proxy}")
            request.meta['proxy'] = current_proxy