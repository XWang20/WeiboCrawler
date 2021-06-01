# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class UserItem(Item):
    """ User Information """
    _id = Field()  # 用户ID
    nick_name = Field()  # 昵称
    gender = Field()  # 性别
    brief_introduction = Field()  # 简介
    location = Field()  # 首页链接
    mblogs_num = Field()  # 微博数
    follows_num = Field()  # 关注数
    fans_num = Field()  # 粉丝数
    vip_level = Field()  # 会员等级
    authentication = Field()  # 认证
    person_url = Field()  # 首页链接

class MblogItem(Item):
    """ Mblog information """
    lang = Field()
    src = Field()
    cat = Field()
    subcat = Field()
    meta = Field()
    body = Field()