# -*- coding: utf-8 -*-
import json
from datetime import datetime
from scrapy import Request, Spider
from WeiboCrawler.items import MblogItem
from WeiboCrawler.spiders.utils import standardize_date, extract_content

class MblogSpider(Spider):
    name = 'mblog'
    base_url = 'https://m.weibo.cn/api/container/getIndex?'

    def start_requests(self):
        
        def init_url_by_user_id():
            # crawl mblogs post by users
            user_ids = ['1699432410']
            urls = [f'{self.base_url}containerid=107603{user_id}&page=1' for user_id in user_ids]
            return urls
        
        urls = init_url_by_user_id()
        for url in urls:
            yield Request(url, callback=self.parse)

    def parse(self, response):
        js = json.loads(response.text)
        page_num = int(response.url.split('=')[-1])
        # 设定采集的时间段
        date_start = datetime.strptime("2019-12-01", '%Y-%m-%d')
        date_end = datetime.strptime("2021-4-6", '%Y-%m-%d')
        if js['ok']:
            weibos = js['data']['cards']
            for w in weibos:
                if w['card_type'] == 9:
                    weibo_info = w['mblog']
                    rembloged_status = weibo_info.get('rembloged_status') # 判断是否为转发
                    if not rembloged_status or not rembloged_status.get('id'):  # 非转发微博
                        created_at = standardize_date(weibo_info['created_at'])
                        if date_start <= created_at and created_at <= date_end:
                            mblogItem = MblogItem()
                            weiboid = mblogItem['_id'] = weibo_info['id']
                            mblogItem['bid'] = weibo_info['bid']
                            mblogItem['user_id'] = weibo_info['user']['id'] if weibo_info['user'] else ''
                            mblogItem['like_num'] = weibo_info['attitudes_count']
                            mblogItem['repost_num'] = weibo_info['reposts_count']
                            mblogItem['comment_num'] = weibo_info['comments_count']
                            mblogItem['tool'] = weibo_info['source']
                            mblogItem['created_at'] = created_at.strftime('%Y-%m-%d')
                            weibo_url = mblogItem['weibo_url'] = 'https://m.weibo.cn/detail/'+weiboid
                            text_body = mblogItem['content'] = ''
                            is_long = True if weibo_info.get('pic_num') > 9 else weibo_info.get('isLongText') # 判断是否为长微博
                            if is_long:
                                yield Request(weibo_url, callback=self.parse_all_content, meta={'item': mblogItem}, priority=1)
                            else:
                                mblogItem['content'] = extract_content(weibo_info['text'])
                                yield mblogItem

                        elif date_end < created_at: # 微博在采集时间段后
                            continue
                        else:   # 微博超过需采集的时间
                            page_num = 0 # 退出采集该用户
                            break

        if js['ok'] and page_num: 
            next_url = response.url.replace('page={}'.format(page_num), 'page={}'.format(page_num+1))
            print(next_url)

            yield Request(next_url, callback=self.parse)
                
    def parse_all_content(self,response):
        mblogItem = response.meta['item']
        html = response.text
        html = html[html.find('"status":'):]
        html = html[:html.rfind('"hotScheme"')]
        html = html[:html.rfind(',')]
        html = '{' + html + '}'
        js = json.loads(html, strict=False)
        weibo_info = js.get('status')
        if weibo_info:
            mblogItem['content'] = extract_content(weibo_info['text'])
            yield mblogItem
