# coding=utf-8
# @Explain  : businessdata api
# @Author   : wooght
# @File     : linkmart apis
# @Time     : 2019/12/28 下午10:40

from django.http import HttpResponse
from businessdata.models import store_list, bs_data, goods_list, order_form, stock_width_goods, goods_quality, \
    operate_data,cd_store, cd_area, cd_data
from django.contrib.auth.decorators import login_required
from common_func.goods_sales_data import goods_sales_data, day_sales_data, week_sales_data, week_hours_sales_data
from common_func.wooght_forms import one_day_date, goods_quality_forms, form_time, Linkclassfly, cd_data_forms, cd_store_forms
from common_func.classify_data import classify_data
from common_func.wooght_pickle import wooght_pickle
from common_func.wooght_redis import wooght_redis
from common_func.str_replace import *
from common_func.wooght_cd_math import *
import json
import xlrd
import pandas as pd


# 上传XLS
# 解析数据
# API
@login_required  # 需要登录
def upload_xls(request):
    xls_tmp = 'downfile/xls_tmp.xls'  # 临时文件路径
    return_content = {'ok': [], 'fail': [], 'info': 'on file', 'err': []}  # 返回处理结果信息
    # 获取门店ID
    store_id = int(request.POST.get('store_id'))
    # 判断是否提交
    if request.method == 'POST':
        if not request.FILES:
            return HttpResponse('(' + json.dumps(return_content) + ')')
        file = request.FILES['xls']
        with open(xls_tmp, 'wb') as f:
            for i in file.chunks():
                f.write(i)
            f.close()
        for t in range(5):
            try:
                data = xlrd.open_workbook(xls_tmp)
            except Exception as e:
                if t == 4:
                    raise FileNotFoundError()  # 抛出文件异常
        table = data.sheet_by_index(0)
        result_list = []
        # 逐行读取
        for i in range(table.nrows):
            result_list.append(','.join(table.row_values(i)))  # 逗号间隔组成字符串 模拟csv格式

        upload_type = request.POST.get('file_type')
        if upload_type == 'turnover':
            return_content = save_turnover(store_id, result_list)
        elif upload_type == 'goods':
            return_content = save_goods(store_id, result_list, request)
        elif upload_type == 'order':
            return_content = save_form(store_id, result_list)
        else:
            return_content['info'] = 'file type error'
    else:
        return_content['info'] = 'error'
    return HttpResponse('(' + json.dumps(return_content) + ')')


# 改变进/补货状态
# API
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
# API
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
# API
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
    return HttpResponse('(' + json.dumps(return_dict) + ')')


# 上传XLS
# 解析数据
# 旧上传文件方法 only csv
# API
@login_required  # 需要登录
def old_upload_xls(request):
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
# API
@login_required  # 需要登录
def data_update(request, store_id, up_type):
    from spider.email_spider import email_spider

    is_qrcode = request.GET['is_qrcode']
    return_content = {'ok': [], 'fail': [], 'info': 'on file', 'err': []}
    spider = email_spider()
    qr_code = False
    # 传递扫码登录判断
    if int(is_qrcode) == 1:
        qr_code = True
    # 判断是否已经启动，同一时间仅仅能启动一个,管理员除外。管理员目的是系统崩溃后，改变up_status的状态
    r = wooght_redis()
    if not r.get('up_status'):
        r.set('up_status', '完成')
    if r.get('up_status') != "完成" and request.user.admin_type != 1:
        return_content['info'] = '系统繁忙，请稍后再试一试'
        return HttpResponse('(' + json.dumps(return_content, ensure_ascii=False) + ')')
    r.set('up_status', '爬虫启动')
    # 启动爬虫
    try:
        spider.run(qr_code)
    except Exception as e:
        return_content['info'] = e.args
        return HttpResponse('(' + json.dumps(return_content, ensure_ascii=False) + ')')
    # 调用数据处理接口
    r.set('up_status', '数据处理')
    body = spider.body
    if up_type == 'turnover':
        return_content = save_turnover(store_id, body)
    elif up_type == 'goods':
        return_content = save_goods(store_id, body, request)
    elif up_type == 'order':
        return_content = save_form(store_id, body)
    r.set('up_status', '完成')
    return HttpResponse('(' + json.dumps(return_content, ensure_ascii=False) + ')')


@login_required  # 需要登录
# 获取上传文件状态
# API
def get_status(request):
    r = wooght_redis()
    status = r.get('up_status')
    return HttpResponse('(' + json.dumps(status, ensure_ascii=False) + ')')


# 营业数据处理
# 营业数据保存
# function
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
# function
def save_goods(store_id, data_list, request):
    return_content = {'ok': [], 'fail': [], 'info': '没有指定文件', 'err': []}

    # 获取所有商品 作后期判断是否存在商品使用 codes_list[商品名称]=条码
    all_goods = goods_list.objects.filter(store_id=store_id)
    codes_list = {}
    for item in all_goods:
        codes_list[str(item.name)] = item.bar_code

    for line in data_list[1:-1]:
        items = line.split(',')
        goods_name = items[1]  # 名称
        try:
            # 如果商品存在 只修改部分数据
            if goods_name in codes_list.keys():
                # 仅仅管理员能修改数据
                if request.user.admin_type == 1:
                    is_exists = goods_list.objects.filter(name=goods_name, store_id=store_id)
                    goods = is_exists[0]
                    goods.stock_nums = items[7]
                    goods.classify = items[3]
                    goods.cost = float(items[5])  # 成本
                    goods.price = items[2]  # 售价
                    goods.company = items[4]  # 单位
                    goods.place = items[9]  # 产地
                    goods.save()
                return_content['fail'].append(goods_name)
            else:
                bar_code = items[0]  # 条码
                price = items[2]  # 售价
                qgp = items[8]  # 保质期
                classify = items[3]  # 分类
                stock_nums = items[7]  # 库存
                cost = float(items[5])  # 成本
                company = items[4]  # 单位
                place = items[9]  # 产地
                if not qgp:
                    qgp = 0
                id = store_list.objects.filter(id=store_id)[0]
                to_save = goods_list(name=goods_name, bar_code=bar_code, qgp=qgp, store_id=id,
                                     stock_nums=stock_nums, classify=classify, cost=cost, price=price,
                                     company=company, place=place)
                to_save.save()
                return_content['ok'].append(store_id)
        except Exception as e:
            return_content['err'].append(goods_name)
    return_content['info'] = 'success'
    return return_content


# 订单数据处理
# 订单数据保存
# 商品订单号绑定，时间绑定
# function
def save_form(store_id, data_list, form_time=form_time):
    return_content = {'ok': [], 'fail': [], 'info': '没有指定文件', 'err': []}

    # 获取已经有的订单
    all_forms = order_form.objects.filter(store_id=store_id,
                                          form_date__gte=one_day_date(form_time['forms'])).order_by('form_date')
    # 已经存在订单序列号{[订单号+商品名称]}
    forms_cache = []
    for item in all_forms:
        cache_str = item.form_code + item.goods_name + str(item.goods_money)
        forms_cache.append(cache_str)
    # 获取所有商品 作后期判断是否存在商品使用 codes_list[商品名称]=条码
    all_goods = goods_list.objects.filter(store_id=store_id)
    codes_list = {}
    for item in all_goods:
        codes_list[str(item.name)] = item.bar_code

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
            return_content['fail'].append('重复订单：' + form_code)
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

            # 名字不在系统里
            # 记录错误条码
            if goods_name not in codes_list.keys():
                return_content['err'].append('商品不存在：' + form_code + '名称：' + goods_name)
            else:
                to_save = order_form(form_code=form_code, goods_name=goods_name, goods_num=goods_num,
                                     goods_code=codes_list[goods_name],
                                     goods_money=goods_money, form_date=form_date, form_time=form_time,
                                     form_money=form_money, form_money_true=form_money_true, store_id=store_id)
                try:
                    to_save.save()
                    return_content['true'].append(store_id)
                except Exception as e:
                    # 可能遇到问题 编码问题，整数问题，日期时间问题
                    return_content['err'].append('存储问题：' + codes_list[goods_name] + goods_name+form_code)
        last_form_datetime = date_time
        last_form_code = form_code
    r = wooght_redis()
    r.set('up_status', '数据分析')
    return_content['info'] = 'success'
    # 序列化订单单价、订单数量
    totle_forms_pickle(all_forms, store_id)
    # 序列化类别同期、环期数据结构
    compare_forms_pickle(all_goods, all_forms, store_id)
    return return_content


# 一天24小时营业数据
# trend 趋势
# API
# result_dict{时间序列,本月,上月,同期}
def day_sales_trend(request):
    # 获取订单数据
    # 最近一月订单
    last_month_forms = order_form.objects.filter(store_id=request.session['store_id'],
                                                 form_date__gte=one_day_date(30))  # 最近一月
    # 上一月订单
    first_month_forms = order_form.objects.filter(store_id=request.session['store_id'],
                                                  form_date__gte=one_day_date(60), form_date__lt=one_day_date(30))
    # 去年同期订单
    same_month_forms = order_form.objects.filter(store_id=request.session['store_id'],
                                                 form_date__gte=one_day_date(365), form_date__lt=one_day_date(335))
    last_day_money = day_sales_data(last_month_forms)
    first_day_money = day_sales_data(first_month_forms)
    same_day_money = day_sales_data(same_month_forms)
    week_hours_num = week_hours_sales_data(last_month_forms)

    # 返回数据组装
    last_month_arr = []
    first_month_arr = []
    same_month_arr = []
    day_times = []
    for times, value in last_day_money.items():
        day_times.append(times)
        last_month_arr.append(value)
    for times, value in same_day_money.items():
        same_month_arr.append(value)
    for times, value in first_day_money.items():
        first_month_arr.append(value)
    return_dict = {}
    return_dict['day_times'] = day_times
    return_dict['last_month'] = last_month_arr
    return_dict['first_month'] = first_month_arr
    return_dict['same_month'] = same_month_arr
    return_dict['week_hours_num'] = week_hours_num

    return HttpResponse('(' + json.dumps(return_dict) + ')')


# 分类销量对比
# 同类同比，环比
# API
# return_dict = [sales_sort_dict, compare]
def classify_sales_ratio(request):
    store_id = request.session['store_id']
    pke = wooght_pickle('pickle_files/store_id' + str(store_id) + 'compare_forms_pickle.txt')
    if not pke.exists:
        compare_forms_pickle(store_id)
    return_dict = pke.load()
    return HttpResponse('(' + json.dumps(return_dict) + ')')


# 烟，水占比 时间序列
# API smoke_ratio[date]={总量，烟量，水量}
def smoke_water_ratio(request):
    # 获取所有商品数据
    all_goods = goods_list.objects.filter(store_id=request.session['store_id'])
    # 获取销售数据
    all_forms = order_form.objects.filter(store_id=request.session['store_id'],
                                          form_date__gte=one_day_date(form_time['forms']))  # 最近二年
    class_data = classify_data(all_goods, all_forms)
    sales_list_data = class_data.get_ratio_list()
    # return_dict = sorted(sales_list_data.items(), key=lambda x: x[0], reverse=True)
    return HttpResponse('(' + json.dumps(sales_list_data) + ')')


# 某类销售趋势
# 某搜索相关内容销售趋势
# API
# api_json  dict->[datelist,day_average,totle_num_30,goods_list]
def one_classify_sales(request, classify='默认分类'):
    # 通过类别查询
    if request.GET.get('classify'):
        classify = request.GET.get('classify')
        if classify in Linkclassfly.keys():
            now_classify = Linkclassfly[classify]
            all_goods = goods_list.objects.filter(store_id=request.session['store_id'], classify__in=now_classify)
        else:
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
    # 获取所有订单
    all_forms = order_form.objects.filter(store_id=request.session['store_id'],
                                          form_date__gte=one_day_date(form_time['forms']))  # 大于一年

    goods_sales = goods_sales_data(all_forms, form_time['forms'])
    goods_sales.classify_screen(all_goods)  # 订单筛选
    goods_sales.run()
    goods_sales_list = goods_sales.run_to_list()  # 每个商品的销售概况
    all_cost = 0  # 总成本
    all_price = 0  # 总可售额
    for good in all_goods:
        all_cost += good.cost * good.stock_nums
        if not good.price:
            all_price += 0
        else:
            all_price += good.price * good.stock_nums

    return_dict = {}
    return_dict['cost'] = all_cost
    return_dict['price'] = all_price
    return_dict['date_dict'] = goods_sales.date_dict
    return_dict['time_dict'] = goods_sales.time_dict
    return_dict['day_average'] = goods_sales.day_average
    return_dict['totle_num_30'] = goods_sales.totle_num_30
    return_dict['goods_sales_list'] = goods_sales_list  # goods_list
    return_dict['month_data_list'] = goods_sales.month_data_list
    return HttpResponse('(' + json.dumps(return_dict) + ')')


# function 订单数及订单单价
# API dict->[时间序列list，订单量list，订单单价list]
def totle_forms(request):
    store_id = request.session['store_id']
    pke = wooght_pickle('pickle_files/store_id' + str(store_id) + 'totle_forms_pickle.txt')
    if not pke.exists:
        totle_forms_pickle(store_id)
    all_data = pke.load()
    # 数据组装
    return_dict = {}
    return_dict['date_dict'] = all_data[0]  # 日订单量
    return_dict['price_dict'] = all_data[1]  # 日订单单价
    return_dict['average_data'] = all_data[2]  # 月订单均线
    return_dict['average_price_data'] = all_data[3]  # 月订单单价均线

    return HttpResponse('(' + json.dumps(return_dict) + ')')


# 所有订单数据序列化（最近2年）
def all_forms_pickle(store_id):
    # 获取所有商品
    all_forms = order_form.objects.filter(store_id=store_id,
                                          form_date__gte=one_day_date(form_time['forms']))  # 时间根据配置时间而定
    pke = wooght_pickle('pickle_files/store_id' + str(store_id) + 'all_forms_pickle.txt')
    pke.dump(all_forms)


# 订单数及订单单价
# 数据序列化
# function
def totle_forms_pickle(all_forms, store_id):
    # 获取指定时间范围内订单
    all_forms = order_form.objects.filter(store_id=store_id, form_money__gt=0,
                                          form_date__gte=one_day_date(form_time['forms'])).order_by('form_date')
    goods_sales = goods_sales_data(all_forms, form_time['forms'])
    goods_sales.run()
    date_dict = goods_sales.date_order_dict  # 日订单量
    price_dict = goods_sales.price_order_dict  # 日订单单价
    average_data = goods_sales.month_order_list  # 月订单均线
    average_price_data = goods_sales.month_price_list  # 月订单单价均线
    totle_forms_data = [date_dict, price_dict, average_data, average_price_data]

    pke = wooght_pickle('pickle_files/store_id' + str(store_id) + 'totle_forms_pickle.txt')
    pke.dump(totle_forms_data)


# # 分类销量对比
# # 同类同比，环比
# #
# # return_dict = [sales_sort_dict, compare]
# function
def compare_forms_pickle(all_goods, forms, store_id):
    # all_goods = goods_list.objects.filter(store_id=store_id)
    # 获取最近1年所有订单数据
    # django 查询数据库大小比较 gt大于 lt小于 gte大于等于 lte小于等于
    # forms = order_form.objects.filter(store_id=store_id, form_date__gte=one_day_date(395))
    # 获取分时间段订单
    last_month_date = [pd.to_datetime(one_day_date(30)), pd.to_datetime(one_day_date())]  # 最近30天
    first_month_date = [pd.to_datetime(one_day_date(60)), pd.to_datetime(one_day_date(30))]  # 上一个30天
    same_month_date = [pd.to_datetime(one_day_date(395)), pd.to_datetime(one_day_date(365))]  # 去年同期
    forms_data = {'last_forms': [], 'first_forms': [], 'same_forms': []}
    for form in forms:
        this_date = form.form_date
        if this_date.__ge__(last_month_date[0]) and this_date.__lt__(last_month_date[1]):
            forms_data['last_forms'].append(form)
        elif this_date.__ge__(first_month_date[0]) and this_date.__lt__(first_month_date[1]):
            forms_data['first_forms'].append(form)
        elif this_date.__ge__(same_month_date[0]) and this_date.__lt__(same_month_date[1]):
            forms_data['same_forms'].append(form)
    class_data = classify_data(all_goods, forms_data['last_forms'])
    sales_data = class_data.get_ratio(30)
    sales_sort_dict = sorted(sales_data.items(), key=lambda x: x[1], reverse=False)
    #
    # 同比、环比销售 compare
    #
    compare = class_data.get_compare(forms_data['last_forms'], forms_data['same_forms'], forms_data['first_forms'])
    return_dict = [sales_sort_dict, compare]

    pke = wooght_pickle('pickle_files/store_id' + str(store_id) + 'compare_forms_pickle.txt')
    pke.dump(return_dict)


# 功能模块
# 单个商品信息
# API
def one_good(request, id):
    goods = goods_list.objects.filter(id=id)[0]
    result_dict = {'name': goods.name, 'bar_code': goods.bar_code, 'price': goods.price,
                   'place': goods.place if goods.place is not None else '四川',
                   'company': goods.company if goods.company is not None else '个', 'classify': goods.classify}
    return HttpResponse('(' + json.dumps(result_dict) + ')')


# 保存运营数据
# API
def save_operate(request):
    store_id = int(request.POST.get('store_id'))
    this_post = request.POST
    result_style = "添加成功"
    is_exists = operate_data.objects.filter(store_id=store_id, y_month=this_post.get('y_month'))
    if not is_exists:
        # 执行添加
        to_save = operate_data(store_id=store_id, y_month=this_post.get('y_month'), profit=this_post.get('profit'),
                               income=this_post.get('income'), rent=this_post.get('rent'), wages=this_post.get('wages'),
                               insurance=this_post.get('insurance'), hydropower=this_post.get('hydropower'),
                               expenditure=this_post.get('expenditure'), loss=this_post.get('loss'),
                               meituan=this_post.get('meituan'))
        try:
            to_save.save()
        except Exception as e:
            result_style = e.args
        # to_save.save()
    else:
        result_style = '重复添加'
    return HttpResponse('(' + json.dumps(result_style) + ')')


# 获取运营数据
# api
def get_operate_data(request):
    store_id = request.session['store_id']
    all_data = operate_data.objects.filter(store_id=store_id)
    month_data_list = []
    for d in all_data:
        one_month_models = dict(y_month=d.y_month, profit=d.profit, income=d.income,
                                wages=d.wages, insurance=d.insurance, meituan=d.meituan, rent=d.rent,
                                hydropower=d.hydropower, expenditure=d.expenditure, stock=d.stock, assets=d.assets,
                                loss=d.loss, store_id=d.store_id)
        month_data_list.append(one_month_models)
    return HttpResponse('(' + json.dumps(month_data_list) + ')')


# 踩点API
# 获取门店列表
def get_cd_stores(request, id=0):
    if id == 0:
        stores = cd_store.objects.all()
        result_list = store_order_math(stores)
    else:
        stores = cd_store.objects.filter(cd_area=id)
        result_list = []
        for item in stores:
            the_dict = {
                'name': item.store_name,
                'id': item.id,
                'area_id': item.cd_area
            }
            result_list.append(the_dict)
    return HttpResponse('('+json.dumps(result_list)+')')


# 获取踩点数据列表
def get_cd_data(request, id):
    import datetime
    data_list = cd_data.objects.filter(cd_store_id=id).order_by('-id')  # -倒序排列
    fildes = get_model_fields(cd_data)
    result_list = []
    for the_dict in data_list.values():
        now_dict = {}
        for item in fildes:
            if isinstance(the_dict[item], datetime.time):
                now_dict[item] = str(the_dict[item].strftime('%H:%M:%S'))
            elif isinstance(the_dict[item], datetime.date):
                now_dict[item] = str(the_dict[item].strftime('%Y-%m-%d'))
            else:
                now_dict[item] = the_dict[item]
        result_list.append(now_dict)
    return HttpResponse('('+json.dumps(result_list)+')')


# 保存踩点数据
def to_save_cd_data(request):
    from datetime import datetime
    info = ''
    form = cd_data_forms(request.POST)
    if form.is_valid():
        p = request.POST
        the_date = datetime.strptime(p.get('cd_date'), '%m/%d/%Y')
        cd_order = cd_data(cd_store_id=p.get('cd_store_id'), cd_orders=p.get('cd_orders'), contrast_orders=p.get('contrast_orders'), road_orders=p.get('road_orders'),
                           contrast_total_orders=p.get('contrast_total_orders'), home_orders=p.get('home_orders'), business_orders=p.get('business_orders'),
                           cd_date=the_date.strftime('%Y-%m-%d'), cd_stime=p.get('cd_stime'))
        try:
            cd_order.save()
            info = 'save ok'
        except Exception as e:
            info = e.args
    else:
        info = form.errors
    return HttpResponse('('+json.dumps(info)+')')


# 获取单个踩点门店数据
def get_one_cd_store(request, id=0):
    stores = cd_store.objects.filter(id=id)
    fildes = get_model_fields(cd_store)
    one_store = stores.values()[0]
    result_list = {}
    for item in fildes:
        result_list[item] = one_store[item]
    return HttpResponse('('+json.dumps(result_list)+')')


# 执行门店信息修改
def to_update_store(request):
    info = ''
    p = request.POST
    form = cd_store_forms(request.POST)
    if form.is_valid():
        # 判断是修改还是添加
        if p.get('id'):
            # 修改
            the_store = cd_store.objects.filter(id=p.get('id'))[0]
            the_store.store_name = p.get('store_name')
            the_store.cd_area = p.get('cd_area')
            the_store.is_24h = p.get('is_24h')
            the_store.is_smoke = p.get('is_smoke')
            # 填写了订单量才修改 0 不做修改
            # if int(p.get('store_orders')) > 0:
            the_store.store_orders = p.get('store_orders')
            the_store.store_turnover = p.get('store_turnover')
            the_store.contrast_orders = p.get('contrast_orders')
            the_store.store_size = p.get('store_size')
            the_store.store_waiters = p.get('store_waiters')
            the_store.door_header = p.get('door_header')

            the_store.store_x = p.get('store_x')
            the_store.store_y = p.get('store_y')
            the_store.cd_label = p.get('cd_label')
            the_store.save()
            info = 'udpate ok'
        else:
            # 添加
            store_name = p.get('store_name')
            is_exists = cd_store.objects.filter(store_name=store_name)
            if is_exists:
                info = '名称已经存在'
            else:
                store = cd_store(store_name=store_name, is_24h=p.get('is_24h'), is_smoke=p.get('is_smoke'),
                                 store_orders=p.get('store_orders'), store_turnover=p.get('store_turnover'),
                                 contrast_orders=p.get('contrast_orders'),
                                 store_size=p.get('store_size'), store_waiters=p.get('store_waiters'),
                                 cd_area=p.get('cd_area'),
                                 door_header=p.get('door_header'), store_x=p.get("store_x"),
                                 store_y=p.get('store_y'))
                try:
                    store.save()
                    info = 'save ok'
                except Exception as e:
                    info = e.args
    else:
        info = form.errors

    return HttpResponse('(' + json.dumps(info) + ')')
