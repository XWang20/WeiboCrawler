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
    _id = Field()  # 微博id
    bid = Field()
    weibo_url = Field()  # 微博URL
    created_at = Field()  # 微博发表时间
    like_num = Field()  # 点赞数
    repost_num = Field()  # 转发数
    comment_num = Field()  # 评论数
    content = Field()  # 微博内容
    user_id = Field()  # 发表该微博用户的id
    tool = Field()  # 发布微博的工具

class CommentItem(Item):
    """ Mblog Comment Information """
    _id = Field()
    comment_user_id = Field()  # 评论用户的id
    content = Field()  # 评论的内容
    mblog_id = Field()  # 评论的微博的id
    created_at = Field()  # 评论发表时间
    like_num = Field()  # 点赞数
    root_comment_id = Field()   # 根评论id，只有二级评论有该项
    img_url = Field()
    img_name = Field()

class RepostItem(Item):
    """ Mblog Repost Information """
    _id = Field()
    repost_user_id = Field()  # 转发用户的id
    content = Field()  # 转发的内容
    mblog_id = Field()  # 转发的微博的id
    created_at = Field()  # 转发时间
    source = Field()    # 转发工具
