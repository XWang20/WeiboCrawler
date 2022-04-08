# -*- coding: utf-8 -*-
import json
from datetime import datetime
from scrapy import Request, Spider
from WeiboCrawler.items import RepostItem
from WeiboCrawler.spiders.utils import extract_content, standardize_date

class RepostSpider(Spider):
    name = 'repost'
    base_url = 'https://api.weibo.cn/2/guest/statuses_repost_timeline?'

    def start_requests(self):
        mblog_ids = ['4750304827933227']    # 原微博id文件
        urls = [f"{self.base_url}c=android&s=746fd605&ft=0&id={mblog_id}&from=10A8195010&gsid=_2AkMomC38f8NhqwJRmf4dxWzgb49zzQrEieKexNwnJRM3HRl-wT9kqmkAtRV6AgOZPxlCXdki_q9a-GZtfNgXXwAhZ5en&page=1" for mblog_id in mblog_ids]
        for url in urls:
            yield Request(url, callback=self.parse, headers={'Host': 'api.weibo.cn'})

    def parse(self, response):
        js = json.loads(response.text)

        if js['next_cursor']:
            page_list = response.url.split("=")
            page_list[-1] = str(int(response.url.split("=")[-1])+1)
            page_url = '='.join(page_list)
            print(page_url)
            yield Request(page_url, self.parse, headers={'Host': 'api.weibo.cn'}, priority=1)
        
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
