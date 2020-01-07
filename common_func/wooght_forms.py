# coding=utf-8
# @Explain  : 表单验证模块
# @Author   : wooght
# @File     : honc_live wooght_forms
# @Time     : 2019/12/1 上午12:23

from django import forms
from django.forms import fields
import time


# 门店字段验证
class store_forms(forms.Form):
    name = fields.CharField(
        max_length=64,
        min_length=2,
        required=True,
        error_messages={'required': '名字不能为空', 'max_length': '最长64', 'min_length': '最短2'}
    )
    adds = fields.CharField(
        required=True,
        error_messages={'required': '地址不能为空'}
    )


# 保质期表单验证
class goods_quality_forms(forms.Form):
    stock_nums = fields.IntegerField(
        required=True,
        error_messages = {'required':'数量不能为空'}
    )
    date_nums = fields.IntegerField(
        required=True,
        error_messages={'required':'天数不能为空'}
    )


# 上传文件类型字典
file_type = {
    'turnover': '营业数据',
    'order': '订单数据',
    'goods': '商品数据'
}


# 返回当前时间datetime 或制定多少天之前的时间
def one_day_date(one=0):
    date_code = '%Y-%m-%d'
    day = 3600 * 24
    if not one:
        return time.strftime(date_code, time.localtime())
    else:
        return time.strftime(date_code, time.localtime(time.time() - one * day))


# 关于订单时间的配置
form_time = {
    'stock': 120,   # 进货补货查看最近4个月的数据
    'quality': 90,  # 过期商品 查看最近3个月的数据
    'forms': 360,   # 订单，查询最近1年的数据
}