# -*- coding: utf-8 -*-
import json
from datetime import datetime
from scrapy import Request, Spider
from WeiboCrawler.items import RepostItem
from WeiboCrawler.spiders.utils import standardize_date, extract_content

class RepostSpider(Spider):
    name = 'repost'
    base_url = 'https://m.weibo.cn/api/statuses/repostTimeline?'

    def start_requests(self):
        mblog_ids = ['4615345245261002']    # 原微博id文件
        urls = [f"{self.base_url}id={mblog_id}&page=1" for mblog_id in mblog_ids]
        for url in urls:
            yield Request(url, callback=self.parse)

    def parse(self, response):
        js = json.loads(response.text)
        
        # 获取全部转发页
        if response.url.endswith('page=1'):
            all_page = js['data']['max']
            if all_page > 1:
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parse, dont_filter=True, meta=response.meta)

        if js['ok']:
            reposts = js['data']['data']
            for repost in reposts:
                repostItem = RepostItem()
                repostItem['_id'] = repost['id']
                repostItem['repost_user_id'] = repost['user']['id']
                repostItem['mblog_id'] = repost['retweeted_status']['id']
                repostItem['created_at'] = standardize_date(repost['created_at']).strftime('%Y-%m-%d')
                repostItem['content'] = repost['raw_text']
                repostItem['source'] = repost['source']
                yield repostItem