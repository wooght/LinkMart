# -*- coding: utf-8 -*-
#
# @method   : 模板标签，模板函数--》查询板块
# @Time     : 2018/5/17
# @Author   : wooght
# @File     : select_plate.py

'''
模板标签函数
文件夹名：templatetags
必须在settings的TEMPLATES中注册
'''

from django import template
from businessdata.models import store_list
from django.conf import settings

register = template.Library()


@register.simple_tag()
def all_stores():
    stores = store_list.objects.all()
    return stores


@register.simple_tag()
def site_info(info_id):
    return settings.SITE_NAME[info_id]