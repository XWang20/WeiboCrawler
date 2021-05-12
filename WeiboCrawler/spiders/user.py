# -*- coding: utf-8 -*-
import json
from scrapy import Request, Spider
from WeiboCrawler.items import UserItem


class UserSpider(Spider):
    name = 'user'
    base_url = 'https://m.weibo.cn/api/container/getIndex?'

    def start_requests(self):
        # file_path = '' #用户id文件
        # with open(file_path, 'rb') as f:
        #     try:
        #         lines = f.read().splitlines()
        #         lines = [line.decode('utf-8-sig') for line in lines]
        #     except UnicodeDecodeError:
        #         logger.error(u'%s文件应为utf-8编码，请先将文件编码转为utf-8再运行程序', file_path)
        #         sys.exit()
        user_ids = ['6588611299'] # 用户id列表
        urls = [f'{self.base_url}containerid=100505{user_id}' for user_id in user_ids]
        for url in urls:
            yield Request(url, callback=self.parse)

    def parse(self, response):
        userItem = UserItem()
        js = json.loads(response.text)
        if js['ok']:
            userInfo = js['data']['userInfo']
            userItem['_id'] = userInfo['id']
            userItem['nick_name'] = userInfo['screen_name']
            userItem['gender'] = userInfo['gender']
            userItem['brief_introduction'] = userInfo['description']
            userItem['mblogs_num'] = userInfo['statuses_count']
            userItem['follows_num'] = userInfo['follow_count']
            userItem['fans_num'] = userInfo['followers_count']
            userItem['authentication'] = userInfo['verified']
            userItem['vip_level'] = userInfo['mbrank']
            userItem['person_url'] = userInfo['profile_url'].split('?')[0]
            profile_url = f"{self.base_url}containerid=230283{userInfo['id']}"
            yield Request(profile_url, callback=self.parse_location, meta={'item': userItem}, priority=1)
    
    def parse_location(self,response):
        userItem = response.meta['item']
        js = json.loads(response.text)
        if js['ok']:
            userItem['location']=js['data']['cards'][0]['card_group'][0]['item_content']
            print(userItem['location'])
        yield userItem
