# -*- coding: utf-8 -*-
import re
import json
from datetime import datetime
from scrapy import Request, Spider
from WeiboCrawler.items import CommentItem
from WeiboCrawler.spiders.utils import standardize_date, extract_content

class CommentSpider(Spider):
    name = 'comment'
    base_url = 'https://api.weibo.cn/2/comments/build_comments?'

    def start_requests(self):
        mblog_ids = ['4704564999620631']
        urls = [f'{self.base_url}is_show_bulletin=2&c=android&s=746fd605&id={mblog_id}&from=10A8195010&gsid=_2AkMolNMzf8NhqwJRmf4dxWzgb49zzQrEieKeyCLoJRM3HRl-wT9jqmwMtRV6AgOZP3LqGBH-29qGRB4vP3j-Hng6DkBJ&count=50&max_id_type=1' for mblog_id in mblog_ids]
        for url in urls:
            yield Request(url, callback=self.parse, dont_filter=True, headers={'Host': 'api.weibo.cn'})

    def parse(self, response):
        js = json.loads(response.text)
        mblog_id = re.search(r'[\d]{16}', response.url).group(0)

        comments = js['root_comments']
        for comment in comments:
            commentItem = CommentItem()
            commentItem['_id'] = comment['idstr']
            commentItem['comment_user_id'] = comment['user']['id']
            commentItem['mblog_id'] = mblog_id
            commentItem['created_at'] = standardize_date(comment['created_at']).strftime('%Y-%m-%d')
            commentItem['like_num'] = comment['like_counts']
            commentItem['content'] = extract_content(comment['text'])
            commentItem['root_comment_id'] = ''
            img_url = []
            if 'pic_infos' in comment:
                for pic in comment['pic_infos']:
                    img_url.append(comment['pic_infos'][pic]['original']['url'])
            commentItem['img_url'] = img_url
            yield commentItem

            if comment['total_number']:
                cid = comment['idstr']
                secondary_url = f'https://weibo.com/ajax/statuses/buildComments?is_reload=1&id={cid}&is_show_bulletin=2&is_mix=1&fetch_level=1&count=20&flow=1'
                yield Request(secondary_url, callback=self.parse_secondary_comment, meta={"mblog_id": mblog_id}, headers={'Host': 'weibo.com'})
                
        max_id = js['max_id']
        if max_id > 0:
            max_id_type = js['max_id_type']
            next_url = f'{self.base_url}is_show_bulletin=2&c=android&s=746fd605&id={mblog_id}&from=10A8195010&gsid=_2AkMolNMzf8NhqwJRmf4dxWzgb49zzQrEieKeyCLoJRM3HRl-wT9jqmwMtRV6AgOZP3LqGBH-29qGRB4vP3j-Hng6DkBJ&count=50&max_id={max_id}&max_id_type={max_id_type}'
            yield Request(next_url, callback=self.parse, dont_filter=True, headers={'Host': 'api.weibo.cn'})
    
    def parse_secondary_comment(self, response):
        js = json.loads(response.text)
        max_id = js['max_id']

        if js['ok']:
            seccomments = js['data']
            for seccomment in seccomments:
                commentItem = CommentItem()
                commentItem['_id'] = seccomment['id']
                commentItem['comment_user_id'] = seccomment['user']['id']
                commentItem['mblog_id'] = response.meta['mblog_id']
                commentItem['created_at'] = standardize_date(seccomment['created_at']).strftime('%Y-%m-%d')
                commentItem['like_num'] = seccomment['like_counts']
                commentItem['content'] = extract_content(seccomment['text'])
                commentItem['reply_comment_id'] = seccomment['reply_comment']['idstr']
                commentItem['root_comment_id'] = seccomment['rootidstr']
                yield commentItem
                
        while max_id:
            next_url = f'{response.url}&max_id={max_id}'
            yield Request(next_url, callback=self.parse_secondary_comment, meta={"mblog_id": response.meta['mblog_id']}, headers={'Host': 'weibo.com'})
