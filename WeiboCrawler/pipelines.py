# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import pymongo
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request

class WeibocrawlerPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )
    
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
    
    def process_item(self, item, spider):
        name = item.__class__.__name__
        self.db[name].insert(dict(item))
        return item
    
    def close_spider(self, spider):
        self.client.close()

class ImagesnamePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if 'img_url' in item:
            for image_url in item['img_url']:
                # meta里面的数据是从spider获取，然后通过meta传递给下面方法：file_path
                yield Request(image_url, meta={'name':item['create_at']}, dont_filter=True, headers={'Host': 'wx1.sinaimg.cn'})
    
    def file_path(self, request, response=None, info=None):
        # 提取url前面名称
        image_guid = request.url.split('/')[-1]
        # 图片名称，默认为评论产生日期
        name = request.meta['name']
        name = re.sub(r'[？\\*|“<>:/]', '', name)
        # 图片存储默认位置：根目录/images/评论时间/评论时间_img_id.格式
        filename = u'{0}/{0}_{1}'.format(name, image_guid)
        return filename