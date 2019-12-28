# coding=utf-8
# @Explain  : 
# @Author   : wooght
# @File     : linkmart apis
# @Time     : 2019/12/28 下午10:40

from django.http import HttpResponse
from businessdata.models import store_list, bs_data, goods_list, order_form, stock_width_goods, goods_quality


# 改变进/补货状态
def stock_state(request, id):
    stock_goods = stock_width_goods.objects.filter(id=id, state=1)
    if stock_goods:
        # 设置为2 及已经处理
        stock_goods[0].state = 2
        stock_goods[0].save()
        result_str = 'success'
    else:
        result_str = 'fail'
    return HttpResponse(result_str)


# 改变保质观察状态
def quality_state(request, id):
    quality_good = goods_quality.objects.filter(id=id, state=1)
    if quality_good:
        # 设置为2 及已经处理
        quality_good[0].state = 2
        quality_good[0].save()
        result_str = 'success'
    else:
        result_str = 'fail'
    return HttpResponse(result_str)