#!/usr/bin/env python
# encoding: utf-8
import re
from datetime import datetime, timedelta

def standardize_date(created_at):
    """标准化微博发布时间"""
    if u'刚刚' in created_at:
        created_at = datetime.now().strftime('%Y-%m-%d')
    elif u'分钟' in created_at:
        minute = created_at[:created_at.find(u'分钟')]
        minute = timedelta(minutes=int(minute))
        created_at = (datetime.now() - minute).strftime('%Y-%m-%d')
    elif u'小时' in created_at:
        hour = created_at[:created_at.find(u'小时')]
        hour = timedelta(hours=int(hour))
        created_at = (datetime.now() - hour).strftime('%Y-%m-%d')
    elif u'昨天' in created_at:
        day = timedelta(days=1)
        created_at = (datetime.now() - day).strftime('%Y-%m-%d')
    else:
        created_at = created_at.replace('+0800 ', '')
        temp = datetime.strptime(created_at, '%c')
        created_at = datetime.strftime(temp, '%Y-%m-%d')
    return datetime.strptime(created_at, '%Y-%m-%d')


def extract_content(text):
    text_body = text
    dr = re.compile(r'<[^>]+>',re.S)    # 过滤html标签
    text_body = dr.sub('',text_body)
    return text_body
