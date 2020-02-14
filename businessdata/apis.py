# coding=utf-8
# @Explain  : 
# @Author   : wooght
# @File     : linkmart apis
# @Time     : 2019/12/28 下午10:40

from django.http import HttpResponse
from businessdata.models import store_list, bs_data, goods_list, order_form, stock_width_goods, goods_quality
from django.contrib.auth.decorators import login_required
from common_func.str_replace import str_replace
from common_func.goods_sales_data import goods_sales_data, day_sales_data, week_sales_data
from common_func.wooght_forms import one_day_date, goods_quality_forms, form_time
from common_func.classify_data import classify_data
import json
import os
import pandas as pd


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


# 是否在库存操作表中 进/补/保 单中
def stock_exists(request, id):
    is_stock = stock_width_goods.objects.filter(goods_id=id, state=1)
    is_quality = goods_quality.objects.filter(goods_id=id, state=1)
    return_dict = {'stock': None, 'quality': None}
    if is_stock:
        return_dict['stock'] = is_stock[0].stock_type
    if is_quality:
        add_date = is_quality[0].add_date
        date_nums = is_quality[0].date_nums
        now_date = one_day_date()
        loss_date = pd.to_datetime(now_date) - pd.to_datetime(add_date)
        left_over = date_nums - loss_date.days
        return_dict['quality'] = left_over
    return HttpResponse('('+json.dumps(return_dict)+')')


@login_required  # 需要登录
def upload_xls(request):
    return_content = {'ok': [], 'fail': [], 'info': 'on file', 'err': []}  # 返回处理结果信息
    # 判断是否提交
    if request.method == 'POST':
        if not request.FILES:
            return HttpResponse('(' + json.dumps(return_content) + ')')
        file = request.FILES['xls']
        # 获取后缀名
        type_excel = file.name.split('.')[1]
        # 后缀名csv才进行数据解析
        if type_excel in ['csv']:
            # 获取门店ID
            store_id = int(request.POST.get('store_id'))
            # 编码读取方式
            file_read = file.read().decode('utf-8')
            file_new_str = str_replace(file_read)  # 特殊字符替换
            # 得到行组成列表
            data_list = file_new_str.split('\n')
            upload_type = request.POST.get('file_type')
            if upload_type == 'turnover':
                return_content = save_turnover(store_id, data_list)
            elif upload_type == 'goods':
                return_content = save_goods(store_id, data_list)
            elif upload_type == 'order':
                return_content = save_form(store_id, data_list)

        else:
            return_content['info'] = 'file type error'
    else:
        return_content['info'] = 'error'
    return HttpResponse('(' + json.dumps(return_content) + ')')


# 调用爬虫 下载文件
# 解析文件并组装数据-》保存到数据库
@login_required  # 需要登录
def data_update(request, store_id, up_type):
    from spider.email_spider import email_spider

    is_qrcode = request.GET['is_qrcode']
    return_content = {'ok': [], 'fail': [], 'info': 'on file', 'err': []}
    spider = email_spider()
    qr_code = False
    # 传递扫码登录判断
    if is_qrcode == str(1):
        qr_code = True
    spider.run(qr_code)
    body = spider.body
    if up_type == 'turnover':
        return_content = save_turnover(store_id, body)
    elif up_type == 'goods':
        return_content = save_goods(store_id, body)
    elif up_type == 'order':
        return_content = save_form(store_id, body)
    return HttpResponse('('+json.dumps(return_content, ensure_ascii=False)+')')


# 营业数据处理
# 营业数据保存
def save_turnover(store_id, data_list):
    return_content = {'ok': [], 'fail': [], 'info': '没有指定文件', 'err': []}
    # 遍历行 第一行为标题不要，最后一行为空不要
    for line in data_list[1:-1]:
        # csv是逗号隔开每个数据
        items = line.split(',')
        old_str = items[0]
        # 组装日期
        date = old_str[0:4] + '-' + old_str[4:6] + '-' + old_str[6:]
        # 判断是否已经提交该数据 防止重复
        is_exists = bs_data.objects.filter(date=date, store_id=store_id)
        if is_exists:
            return_content['fail'].append(date)
        else:
            cost = items[1]
            turnover = items[2]
            gross_profit = items[4]
            id = store_list.objects.filter(id=store_id)[0]  # 外键必须是传入外检对象
            save_bs = bs_data(date=date, cost=cost, turnover=turnover, gross_profit=gross_profit, store_id=id)
            save_bs.save()
            return_content['ok'].append(store_id)
            return_content['info'] = 'success'
    return return_content


# 商品数据梳理
# 商品数据保存
def save_goods(store_id, data_list):
    return_content = {'ok': [], 'fail': [], 'info': '没有指定文件', 'err': []}
    for line in data_list[1:-1]:
        items = line.split(',')
        goods_name = items[1]  # 名称
        try:
            is_exists = goods_list.objects.filter(name=goods_name, store_id=store_id)
            if is_exists:
                goods = is_exists[0]
                goods.stock_nums = items[7]
                goods.classify = items[3]
                goods.save()
                return_content['fail'].append(goods_name)
            else:
                bar_code = items[0]  # 条码
                qgp = items[8]  # 保质期
                classify = items[3]  # 分类
                stock_nums = items[7]
                if not qgp:
                    qgp = 0
                id = store_list.objects.filter(id=store_id)[0]
                to_save = goods_list(name=goods_name, bar_code=bar_code, qgp=qgp, store_id=id,
                                     stock_nums=stock_nums, classify=classify)
                to_save.save()
                return_content['ok'].append(store_id)
        except Exception as e:
            return_content['err'].append(goods_name)
    return_content['info'] = 'success'
    return return_content


# 订单数据处理
# 订单数据保存
# 商品订单号绑定，时间绑定
def save_form(store_id, data_list):
    return_content = {'ok': [], 'fail': [], 'info': '没有指定文件', 'err': []}

    # 获取已经有的订单
    all_forms = order_form.objects.filter(store_id=store_id)
    forms_cache = []
    for item in all_forms:
        cache_str = item.form_code + item.goods_name + str(item.goods_money)
        forms_cache.append(cache_str)

    # 一个订单只有一个单号，一个日期
    # 商品对应行不一定有单号和日期 没有的时候，就默认上一次数据
    last_form_code = ''
    last_form_datetime = ['', '']
    for line in data_list[1:-1]:
        items = line.split(',')
        form_code = items[0]
        goods_name = items[1]

        # 判断是否有单号，时间
        if not form_code:
            form_code = last_form_code
        date_time = items[4].split(' ')  # 获取日期 实际
        if not date_time[0]:
            date_time = last_form_datetime

        goods_money = items[3]  # 商品金额
        # 没有goods_money或者goods_name 则为单个商品自定义折扣 无实际意义
        if not goods_money:
            continue
        # 判断是否重复提交
        is_exists_str = form_code + goods_name + str(float(goods_money))
        # is_exists = order_form.objects.filter(form_code=form_code, goods_name=goods_name, goods_money=goods_money)
        # 订单号长度判断 避免采用科学计数法
        if len(form_code) < 24:
            return_content['err'].append('单号有误：' + form_code + goods_name)
            continue
        if is_exists_str in forms_cache:
            return_content['fail'].append('重复订单：'+form_code)
        else:
            if not items[2]:
                goods_num = 0
            else:
                goods_num = int(float(items[2]))  # 商品数量

            form_date = date_time[0]  # 日期
            form_time = date_time[1]  # 实际
            form_money = items[8]  # 订单金额
            if not form_money:
                form_money = 0  # 没有金额 默认0
            form_money_discount = items[17]  # 优惠金额
            if not form_money_discount:
                form_money_discount = 0  # 优惠金额默认0
            form_money_true = float(form_money) - float(form_money_discount)
            goods = goods_list.objects.filter(name=goods_name, store_id=store_id)
            # 名字不在系统里
            # 记录错误条码
            if not goods:
                return_content['err'].append('商品不存在：'+form_code + '名称：' + goods_name)
            else:
                goods_code = goods[0].bar_code
                to_save = order_form(form_code=form_code, goods_name=goods_name, goods_num=goods_num,
                                     goods_code=goods_code,
                                     goods_money=goods_money, form_date=form_date, form_time=form_time,
                                     form_money=form_money, form_money_true=form_money_true, store_id=store_id)
                try:
                    to_save.save()
                    return_content['true'].append(store_id)
                except Exception as e:
                    # 可能遇到问题 编码问题，整数问题，日期时间问题
                    return_content['err'].append('存储问题：' + goods_code + goods_name)
        last_form_datetime = date_time
        last_form_code = form_code

    return_content['info'] = 'success'
    return return_content


# 一天24小时营业数据 trend 趋势
def day_sales_trend(request):
    # 获取小时数据
    all_forms = order_form.objects.filter(store_id=request.session['store_id'], form_date__gte=one_day_date(30))  # 最近一月
    day_money = day_sales_data(all_forms)
    return_arr = []
    for day, value in day_money.items():
        return_arr.append([day, value])

    return HttpResponse('(' + json.dumps(return_arr) + ')')


# 分类销量对比
def classify_sales_ratio(request):
    # 获取所有商品数据
    all_goods = goods_list.objects.filter(store_id=request.session['store_id'])
    # 获取销售数据
    all_forms = order_form.objects.filter(store_id=request.session['store_id'], form_date__gte=one_day_date(90))  # 最近一月
    class_data = classify_data(all_goods, all_forms)
    sales_data = class_data.get_ratio()
    return_dict = sorted(sales_data.items(), key=lambda x: x[1], reverse=False)
    return HttpResponse('(' + json.dumps(return_dict) + ')')


# function  某类销售趋势
# function  某搜索相关内容销售趋势
# api_json  dict->[datelist,day_average,totle_num_30,goods_list]
def one_classify_sales(request, classify='默认分类'):
    # 通过类别查询
    if request.GET.get('classify'):
        classify = request.GET.get('classify')
        all_goods = goods_list.objects.filter(store_id=request.session['store_id'], classify=classify)
    # 通过搜索查询
    elif request.GET.get('goods_code'):
        goods_code = request.GET.get('goods_code')
        # 通过条码查询
        all_goods = goods_list.objects.filter(bar_code__contains=goods_code,
                                             store_id=request.session['store_id'])  # # 字段名__contains 模糊查询 注意中间双划线
        if len(all_goods) < 1:
            # 通过名称查询
            all_goods = goods_list.objects.filter(name__contains=goods_code,
                                                 store_id=request.session['store_id'])
    # 默认查询默认分类
    else:
        all_goods = goods_list.objects.filter(store_id=request.session['store_id'], classify=classify)
    # 获取所有商品
    all_forms = order_form.objects.filter(store_id=request.session['store_id'], form_date__gte=one_day_date(form_time['forms']))  # 最近一月

    goods_sales = goods_sales_data(all_forms, form_time['forms'])
    goods_sales.classify_screen(all_goods)  # 订单筛选
    goods_sales.run()
    goods_sales_list = goods_sales.run_to_list()    # 每个商品的销售概况

    return_dict = {}
    return_dict['date_dict'] = goods_sales.date_dict
    return_dict['day_average'] = goods_sales.day_average
    return_dict['totle_num_30'] = goods_sales.totle_num_30
    return_dict['goods_sales_list'] = goods_sales_list      # goods_list
    return HttpResponse('('+json.dumps(return_dict)+')')

