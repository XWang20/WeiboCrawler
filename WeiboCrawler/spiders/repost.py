# -*- coding: utf-8 -*-
import json
from datetime import datetime
from scrapy import Request, Spider
from WeiboCrawler.items import RepostItem
from WeiboCrawler.spiders.utils import extract_content, standardize_date

class RepostSpider(Spider):
    name = 'repost'
    base_url = 'https://api.weibo.cn/2/statuses/repost_timeline'

    def start_requests(self):
        mblog_ids = ['4750304827933227']    # 原微博id
        urls = [f"{self.base_url}?aid=01A_NRPbxqZ_cWdRq_vaWFNwalT6hxQsgXtyBQMp-N69iE9eA.&c=weicoabroad&count=50&from=1246893010&gsid=_2A25PP5yNDeRxGeRP7lAV9ifOzDmIHXVqbJdFrDV6PUJbkdAKLWrxkWpNUAqlfRSd0j97oQmhaBDNgeMQRsDYuDEM&i=256a048&id={mblog_id}&lang=zh_CN&s=db684cf5" for mblog_id in mblog_ids]
        for url in urls:
            yield Request(url, callback=self.parse, dont_filter=True, headers={'Host': 'api.weibo.cn'})

    def parse(self, response):
        js = json.loads(response.text)

        if js:
            reposts = js['reposts']
            for repost in reposts:
                repostItem = RepostItem()
                repostItem['_id'] = repost['id']
                repostItem['repost_user_id'] = repost['user']['id']
                repostItem['mblog_id'] = repost['retweeted_status']['id']
                repostItem['created_at'] = standardize_date(repost['created_at']).strftime('%Y-%m-%d')
                repostItem['content'] = repost['text']
                repostItem['source'] = extract_content(repost['source'])
                yield repostItem
        
        # 获取下一页
        if js["next_cursor"]:
            max_id = js['next_cursor']
            next_url = f"{response.url}&max_id={max_id}"
            yield Request(next_url, callback=self.parse, dont_filter=True, headers={'Host': 'api.weibo.cn'})