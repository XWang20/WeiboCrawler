# -*- coding: utf-8 -*-
import json
import psycopg2
from datetime import datetime
from scrapy import Request, Spider
from WeiboCrawler.items import MblogItem
from WeiboCrawler.spiders.utils import standardize_date

class MblogSpider(Spider):
    name = 'mblog'
    base_url = 'https://m.weibo.cn/api/container/getIndex?'
    base_comment_url = 'https://api.weibo.cn/2/comments/build_comments?'
    base_repost_url = 'https://m.weibo.cn/api/statuses/repostTimeline?'

    # 连接数据库
    connection = psycopg2.connect(host='localhost', user='xing', dbname='weibo')
    cur = connection.cursor()

    # 定义要删除的字段
    del_mblog_fields = ['visible', 'pending_approval_count', 'pic_ids', 'pic_types', 'thumbnail_pic', 'show_additional_indication', 'can_edit', 'favorited', 'is_paid', 'mblog_vip_type', 'reward_exhibition_type', 'reward_scheme', 'hide_flag', 'mlevel',
    'darwin_tags', 'rid', 'mblogtype', 'more_info_type', 'cardid', 'extern_safe', 'number_display_strategy', 'enable_comment_guide', 'content_auth', 'alchemy_params', 'mblog_menu_new_style', 'version']
    del_retweet_fields = ['repost_type']
    del_user_fields = ['badge', 'cover_image_phone', 'like_me', 'like']

    def start_requests(self):

        def init_url_by_user_id():
            # crawl mblogs post by users from postgresql 
            # 从数据库中读取userid和上次爬取时间
            self.cur.execute("SELECT id, last_crawl FROM userid;")
            user_ids = self.cur.fetchall()
            urls = [f'{self.base_url}containerid=107603{user_id[0]}&page=1' for user_id in user_ids]
            return urls, user_ids
        
        urls, user_ids = init_url_by_user_id()
        now_time = datetime.now().date()
        for i, url in enumerate(urls):
            self.cur.execute('''UPDATE userid 
                                SET last_crawl = %s
                                where id = %s;''', (now_time, user_ids[i][0]))
            self.connection.commit()
            yield Request(url, meta={'date_start': user_ids[i][1], 'date_end': now_time}, callback=self.parse)

        # def init_url_by_test():
        #     user_ids = ['1749127163']
        #     urls = [f'{self.base_url}containerid=107603{user_id}&page=1' for user_id in user_ids]
        #     return urls    
        # now_time = datetime.now().date()
        # urls = init_url_by_test()
        # for url in urls:
        #     yield Request(url, meta={'date_start': None, 'date_end': now_time}, callback=self.parse)

    def parse(self, response):

        js = json.loads(response.text)
        page_num = int(response.url.split('=')[-1])
        # 设定采集的时间段，开始时间：上次爬取时间（如果为NULL可以自行设定）；结束时间：现在时间
        date_start = response.meta['date_start'] if response.meta['date_start'] else datetime.strptime("2009-8-14", '%Y-%m-%d').date()
        date_end = response.meta['date_end']
        if js['ok']:
            mblogs = js['data']['cards']
            for mblog in mblogs:
                if mblog['card_type'] == 9:
                    mblog_info = mblog['mblog']
                    retweeted_status = mblog_info.get('retweeted_status') # 判断是否为转发
                    created_at = standardize_date(mblog_info['created_at']).date()
                    if date_start <= created_at and created_at <= date_end:
                        mblog_id = mblog_info['id']
                        mblogItem = MblogItem()
                        # 删除无关字段
                        for field in self.del_mblog_fields:
                            try:
                                del mblog_info[field]
                            except:
                                pass
                        for field in self.del_user_fields:
                            del mblog_info['user'][field]
                        if retweeted_status:
                            for field in self.del_retweet_fields:    
                                del mblog_info[field]
                            for field in self.del_mblog_fields:
                                try:
                                    del mblog_info['retweeted_status'][field]
                                except:
                                    pass
                            for field in self.del_user_fields:
                                del mblog_info['retweeted_status']['user'][field]

                        mblogItem['lang'] = 'cn'
                        mblogItem['src'] = 'm.weibo.cn'
                        mblogItem['cat'] = '微博'
                        mblogItem['subcat'] = '微博'
                        mblogItem['body'] = mblog_info
                        mblogItem['meta'] = {'repost': [], 'comment':[], 'longText': ''}
                        # 获取meta信息
                        is_long = True if mblog_info.get('pic_num') > 9 else mblog_info.get('isLongText') # 判断是否为长微博
                        # if is_long:
                        #     mblog_url = 'https://m.weibo.cn/detail/'+mblog_id
                        #     Request(mblog_url, callback=self.parse_all_content, meta={'item': mblogItem})
                        # if mblog_info['comments_count'] > 0:
                        #     comment_url = f'{self.base_comment_url}is_show_bulletin=2&c=android&s=746fd605&id={mblog_id}&from=10A8195010&gsid=_2AkMolNMzf8NhqwJRmf4dxWzgb49zzQrEieKeyCLoJRM3HRl-wT9jqmwMtRV6AgOZP3LqGBH-29qGRB4vP3j-Hng6DkBJ&count=50&max_id_type=1'
                        #     yield Request(comment_url, callback=self.parse_all_comment, dont_filter=True, headers={'Host': 'api.weibo.cn'}, meta={'mblog_id':mblog_id})
                        if mblog_info['reposts_count'] > 0:
                            repost_url = f"{self.base_repost_url}id={mblog_id}&page=1"
                            mblogItem =  Request(repost_url, callback=self.parse_all_repost)
                        yield mblogItem

                    elif date_end < created_at: # 微博在采集时间段后
                        continue
                    else:   # 微博超过需采集的时间
                        page_num = 0 # 退出采集该用户
                        break

        if js['ok'] and page_num: 
            next_url = response.url.replace('page={}'.format(page_num), 'page={}'.format(page_num+1))
            yield Request(next_url, meta={'date_start': date_start, 'date_end': date_end}, callback=self.parse)

    def parse_all_content(self,response):
        mblogItem = response.meta['item']
        html = response.text
        html = html[html.find('"status":'):]
        html = html[:html.rfind('"hotScheme"')]
        html = html[:html.rfind(',')]
        html = '{' + html + '}'
        js = json.loads(html, strict=False)
        mblog_info = js.get('status')
        if mblog_info:
            mblogItem['meta']['longText'] = mblog_info['text']
            yield mblogItem

    def parse_all_comment(self,response):

        js = json.loads(response.text)
        comment_field = ['disable_reply', 'liked', 'readtimetype', 'rootidstr']
        for comment in js['root_comments']:
            for field in comment_field:
                try:
                    del comment[field]
                except:
                    pass
            for field in self.del_user_fields:
                del comment['user'][field]

            # 把评论中的userid加入数据库，防止重复
            try:
                self.cur.execute('''INSERT INTO userid (id) VALUES (%s);'''%comment['user']['idstr'])
            except:
                pass
        self.connection.commit()
        
        # 请求comment下一页
        max_id = js['max_id']
        if max_id > 0:
            max_id_type = js['max_id_type']
            mblog_id = response.meta['mblog_id']
            next_url = f'{self.base_url}is_show_bulletin=2&c=android&s=746fd605&id={mblog_id}&from=10A8195010&gsid=_2AkMolNMzf8NhqwJRmf4dxWzgb49zzQrEieKeyCLoJRM3HRl-wT9jqmwMtRV6AgOZP3LqGBH-29qGRB4vP3j-Hng6DkBJ&count=50&max_id={max_id}&max_id_type={max_id_type}'
            Request(next_url, callback=self.parse_all_comment, meta={'mblog_id':mblog_id}, dont_filter=True, headers={'Host': 'api.weibo.cn'}, priority=3)

    def parse_all_repost(self, response):
        js = json.loads(response.text)

        if response.url.endswith('page=1'):
            all_page = js['data']['max']
            if all_page > 1:
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    Request(page_url, self.parse_all_repost, dont_filter=True)

        if js['ok']:
            for repost in js['data']['data']:
                for field in self.del_mblog_fields:
                    try:
                        del repost[field]
                        del repost['retweeted_status'][field]
                    except:
                        pass
                for field in self.del_user_fields:
                    del repost['user'][field]
                    del repost['retweeted_status']['user'][field]
                for field in self.del_retweet_fields:
                    del repost[field]

                # 把转发中的userid加入数据库
                try:
                    self.cur.execute('''INSERT INTO userid (id) VALUES (%s);'''%repost['user']['idstr'])
                except:
                    pass
            self.connection.commit()