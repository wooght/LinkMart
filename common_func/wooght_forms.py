# coding=utf-8
# @Explain  : 表单验证/属性配置
# @Author   : wooght
# @File     : honc_live wooght_forms
# @Time     : 2019/12/1 上午12:23

from django import forms
from django.forms import fields
import time


# 踩点区域字段验证
class cd_area_forms(forms.Form):
    area_name = fields.CharField(
        max_length=64,
        min_length=2,
        required=True,
        error_messages={'required': '名字不能为空', 'max_length': '最长64', 'min_length': '最短2'}
    )
    area_house = fields.IntegerField(
        required=True,
        error_messages={'required':'户数必填写'}
    )
    area_x = fields.FloatField(
        required=True,
        error_messages={'required':'坐标必填写'}
    )


# 踩点门店字段验证
class cd_store_forms(forms.Form):
    store_name = fields.CharField(
        max_length=64,
        min_length=2,
        required=True,
        error_messages={'required': '名字不能为空', 'max_length': '最长64', 'min_length': '最短2'}
    )
    store_x = fields.FloatField(
        required=True,
        error_messages={'required': '未填写坐标'}
    )


# 踩点数据验证
class cd_data_forms(forms.Form):
    cd_store_id = fields.IntegerField(
        required=True,
        error_messages={'required': '请选择门店'}
    )
    contrast_orders = fields.IntegerField(
        required=True,
        error_messages={'required': '对标订单量'}
    )
    cd_orders = fields.IntegerField(
        required=True,
        error_messages={'required': '踩点订单量'}
    )


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


# 月涨幅（同比，环比）
def month_compare(everymonth_dict):
    average_list = []
    result_dict = {}
    i = 0
    for key, value in everymonth_dict.items():
        average_list.append(value)
        result_dict[key] = [value, 0, 0]  # [平均值，同比，环比]
        # 同比 总月份大于12
        if i > 11:
            compare_same = (value / average_list[i - 12] - 1) if average_list[i - 12] > 0 else 1
            result_dict[key][1] = float('%.2f' % compare_same)
        if i > 0:
            compare_first = (value / average_list[i - 1] - 1) if average_list[i - 1] > 0 else 1
            result_dict[key][2] = float('%.2f' % compare_first)
        i += 1
    return result_dict


# 关于订单时间的配置
form_time = {
    'stock': 120,   # 进货补货查看最近4个月的数据
    'quality': 90,  # 过期商品 查看最近3个月的数据
    'forms': 400,   # 订单，查询最近1年的数据
}

# 自定义大类对应几个小类
Linkclassfly = {
    '-香烟类-': ['中烟', '川烟', '外烟'],
    '-饮料类-': ['饮料', '碳酸饮料', '功能饮料', '乳饮料', '茶饮料', '咖啡饮料', '果汁', '饮用水', '咖啡'],
    '-酒类-': ['啤酒', '红酒', '葡萄酒', '白酒', '清酒烧酒', '鸡尾酒', '洋酒', '白酒黄酒'],
    '-居家类-': ['厨卫清洁', '洗衣洗手', '餐具厨具', '家用工具', '水杯', '洁厕', '洗衣清洁',
              '杯子', '碗', '厨具', '衣物清洁', '牙护', '护理工具', '洗发水', '沐浴露', '牙膏', '香皂', '出行'],
    '-粮油类-': ['米', '面', '油', '调味', '鸡蛋', '榨菜', '杂粮干货', '杂粮'],
    '-鲜食类-': ['关东煮', '烤肠', '包子', '蒸煮', '豆浆'],
    '-零食类-': ['坚果零食', '薯片零食', '巧克力', '巧克力零食', '饼干零食', '麻辣零食', '糖果零食', '小食零食', '小食', '海苔零食', '海苔', '面包零食']
}