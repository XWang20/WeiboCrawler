# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import psycopg2
# import json

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

class PostgrePipeline(object):
    def __init__(self):
        self.hostname = ''
        self.username = ''
        self.password = ''
        self.database = ''
    
    def open_spider(self, spider):
        self.connection = psycopg2.connect(host=self.hostname, user=self.username, password=self.password, dbname=self.database)
        self.cur = self.connection.cursor()
    
    def process_item(self, item, spider):
        self.cur.execute("INSERT INTO mblog(lang, src, cat, subcat, meta, body) VALUES(%s, %s, %s, %s, %s, %s);", (item['lang'], item['src'], item['subcat'], item['cat'], str(item['meta']), str(item['body'])))
        self.connection.commit()
        return item
    
    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()