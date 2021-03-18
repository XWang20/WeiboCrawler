# -*- coding: utf-8 -*-
import json
from datetime import datetime
from scrapy import Request, Spider
from WeiboCrawler.items import CommentItem
from WeiboCrawler.spiders.utils import standardize_date, extract_content

class CommentSpider(Spider):
    name = 'comment'
    base_url = 'https://m.weibo.cn/comments/hotflow?'

    def start_requests(self):
        mblog_ids = ['4615345245261002']
        urls = [f"{self.base_url}id={mblog_id}&mid={mblog_id}" for mblog_id in mblog_ids]
        for url in urls:
            yield Request(url, callback=self.parse)

    def parse(self, response):
        js = json.loads(response.text)

        if js['ok']:
            comments = js['data']['data']
            for comment in comments:
                commentItem = CommentItem()
                commentItem['_id'] = comment['id']
                commentItem['comment_user_id'] = comment['user']['id']
                commentItem['mblog_id'] = comment['mid']
                commentItem['created_at'] = standardize_date(comment['created_at']).strftime('%Y-%m-%d')
                commentItem['like_num'] = comment['like_count']
                commentItem['content'] = extract_content(comment['text'])
                commentItem['root_comment_id'] = ''
                yield commentItem

                if comment['total_number']:
                    secondary_url = 'https://m.weibo.cn/comments/hotFlowChild?cid=' + comment['id']
                    yield Request(secondary_url, callback=self.parse_secondary_comment)

    
    def parse_secondary_comment(self, response):
        js = json.loads(response.text)
        if js['ok']:
            print(type(js))
            seccomments = js['data']
            for seccomment in seccomments:
                commentItem = CommentItem()
                commentItem['_id'] = seccomment['id']
                commentItem['comment_user_id'] = seccomment['user']['id']
                commentItem['mblog_id'] = seccomment['mid']
                commentItem['created_at'] = standardize_date(seccomment['created_at']).strftime('%Y-%m-%d')
                commentItem['like_num'] = seccomment['like_count']
                commentItem['content'] = extract_content(seccomment['text'])
                commentItem['root_comment_id'] = seccomment['rootid']
                yield commentItem

