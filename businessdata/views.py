from django.shortcuts import render, redirect
from businessdata.models import store_list, bs_data, goods_list, order_form, stock_width_goods, goods_quality
from common_func.wooght_forms import store_forms, file_type, one_day_date, goods_quality_forms, form_time
from common_func.goods_sales_data import goods_sales_data, day_sales_data, week_sales_data
from common_func.str_replace import str_replace
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


# 首页
###
#   获取营业数据
#   选择门店
###
@login_required  # 需要登录
def index(request):
    store_id = request.session['store_id']
    if request.method == 'GET':
        # 获取当前门店ID
        store_id = request.GET.get('store_id')
        if store_id:
            request.session['store_id'] = store_id
        else:
            store_id = request.session['store_id']

    store_name = store_list.objects.filter(id=store_id)[0].name  # 获取门店名称
    all_data = bs_data.objects.filter(store_id=store_id, date__gte=one_day_date(366)).order_by('date')  # 获取所有数据
    average_data = []  # 平均数据
    all_bsd_data = []  # 所有数据

    totle_turnover = 0  # 总营业额
    totle_gross = 0  # 总毛利
    i = 0  # 周期计数
    # 遍历营业数据
    for item in all_data:
        totle_turnover += item.turnover
        totle_gross += item.gross_profit
        cycle = 30  # 品均值计算周期
        all_bsd_data.append(item.turnover)
        if i < cycle:
            average_data.append(0)
        else:
            now_average = sum(all_bsd_data[i - cycle:i]) / cycle  # 平均值
            average_data.append(now_average)
        i += 1

    # 获取小时数据
    all_forms = order_form.objects.filter(form_money__gt=0, store_id=store_id)
    day_money = day_sales_data(all_forms)
    print(day_money)

    # 获取一周数据
    week_money = week_sales_data(all_forms)

    stores = store_list.objects.all()  # 获取所有门店数据 供选择下拉列表使用
    return render(request, 'index.html', {'all_data': all_data, 'stores': stores,
                                          'store_id': int(store_id), 'store_name': store_name,
                                          'average': str(average_data),
                                          'totle_turnover': totle_turnover,
                                          'totle_gross': totle_gross,
                                          'day_money': day_money, 'week_money': week_money})


# 商品列表页面展示
def goods_list_page(request, classify='默认分类'):
    classify_keys = []
    if request.method == 'GET':
        goods_code = request.GET.get('goods_code')
        if not goods_code:
            # 查询类别 在没有搜索时 显示类别
            classify_data = goods_list.objects.values('classify')
            for item in classify_data:
                if item['classify'] not in classify_keys:
                    classify_keys.append(item['classify'])
            print(classify_keys)
            if request.GET.get('classify'):
                classify = request.GET.get('classify')
            all_data = goods_list.objects.filter(store_id=request.session['store_id'], classify=classify)
        else:
            all_data = goods_list.objects.filter(bar_code__contains=goods_code,
                                                 store_id=request.session['store_id'])  # # 字段名__contains 模糊查询 注意中间双划线
    else:
        all_data = goods_list.objects.all()
    return render(request, 'goods_list.html', {'goods_list': all_data, 'classify_keys': classify_keys})


# 提交文件入口
# 获取提交类型
# 指定方法处理数据
# 返回数据处理结果
@login_required  # 需要登录
def upload_xls(request):
    # 查询门店列表
    stores = store_list.objects.all()
    # 判断是否提交
    if request.method == 'POST':
        file = request.FILES['xls']
        info = 'no'
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
            return_content = {'true': [], 'false': [], 'info': '提交格式错误'}  # 返回提交成功数
        return render(request, 'upload_xls.html',
                      {'true_content': len(return_content['true']), 'false_content': str(return_content['false']),
                       'info': return_content['info'], 'stores': stores, 'file_type': file_type,
                       'error': str(return_content['error'])})
    else:
        return render(request, 'upload_xls.html', {'stores': stores, 'file_type': file_type})


# 营业数据处理
# 营业数据保存
def save_turnover(store_id, data_list):
    return_content = {'true': [], 'false': [], 'info': '', 'error': ''}  # 返回提交成功数
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
            return_content['false'].append(date)
        else:
            cost = items[1]
            turnover = items[2]
            gross_profit = items[4]
            id = store_list.objects.filter(id=store_id)[0]  # 外键必须是传入外检对象
            save_bs = bs_data(date=date, cost=cost, turnover=turnover, gross_profit=gross_profit, store_id=id)
            save_bs.save()
            return_content['true'].append(store_id)
            return_content['info'] = '成功导入'
    return return_content


# 商品数据梳理
# 商品数据保存
def save_goods(store_id, data_list):
    return_content = {'true': [], 'false': [], 'info': '', 'error': []}  # 返回提交成功数
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
                return_content['false'].append(goods_name)
            else:
                bar_code = items[0]  # 条码
                qgp = items[8]  # 保质期
                classify = items[3] # 分类
                stock_nums = items[7]
                if not qgp:
                    qgp = 0
                id = store_list.objects.filter(id=store_id)[0]
                to_save = goods_list(name=goods_name, bar_code=bar_code, qgp=qgp, store_id=id,
                                     stock_nums=stock_nums, classify = classify)
                to_save.save()
                return_content['true'].append(store_id)
        except Exception as e:
            return_content['error'].append(goods_name)
    return_content['info'] = '成功导入'
    return return_content


# 订单数据处理
# 订单数据保存
# 商品订单号绑定，时间绑定
def save_form(store_id, data_list):
    return_content = {'true': [], 'false': [], 'info': '', 'error': []}  # 返回提交成功数

    # 获取已经有的订单
    all_forms = order_form.objects.filter(store_id=store_id)
    forms_cache = []
    for item in all_forms:
        cache_str = item.form_code + item.goods_name + str(item.goods_money)
        forms_cache.append(cache_str)
    print(forms_cache)
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
        is_exists = order_form.objects.filter(form_code=form_code, goods_name=goods_name, goods_money=goods_money)
        # 订单号长度判断 避免采用科学计数法
        if len(form_code) < 24:
            return_content['error'].append(form_code + goods_name)
            continue
        if is_exists:
            return_content['false'].append(form_code)
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
            goods = goods_list.objects.filter(name=goods_name)
            # 名字不在系统里
            # 记录错误条码
            if not goods:
                return_content['error'].append(form_code + '名称：' + goods_name)
            else:
                goods_code = goods[0].bar_code
                to_save = order_form(form_code=form_code, goods_name=goods_name, goods_num=goods_num,
                                     goods_code=goods_code,
                                     goods_money=goods_money, form_date=form_date, form_time=form_time,
                                     form_money=form_money, form_money_true=form_money_true, store_id=store_id)
                # to_save.save()
                try:
                    to_save.save()
                    return_content['true'].append(store_id)
                except Exception as e:
                    # 可能遇到问题 编码问题，整数问题，日期时间问题
                    return_content['error'].append(goods_code + goods_name)
        last_form_datetime = date_time
        last_form_code = form_code

    return_content['info'] = '导入成功'
    return return_content


# 商品订单销售查询
# 商品订单列表
# 计算销售数据
def goods_form(request, goods_id, return_info=''):
    # 查询商品属性
    goods = goods_list.objects.filter(id=goods_id)[0]
    # 查询商品订单数据
    form_list = order_form.objects.filter(goods_code=goods.bar_code, store_id=goods.store_id.id, form_date__gt=one_day_date(form_time['forms'])).order_by('form_date')

    # 处理商品订单数据
    # 计算/组装前段所需数据
    goods_sales = goods_sales_data(form_list, form_time['forms'])
    goods_sales.run()

    return render(request, 'goods.html', {'form_list': form_list, 'goods': goods, 'goods_code': goods.bar_code,
                                          'date_dict': goods_sales.date_dict, 'store_id': goods.store_id.id,
                                          'info': return_info,
                                          'day_average': goods_sales.day_average,
                                          'totle_num_30': goods_sales.totle_num_30})


# 添加进/补货单
# 返回到对应商品页面
def add_stock(request, goods_code, store_id, stock_type):
    # 检查商品是否存在
    goods = goods_list.objects.filter(bar_code=goods_code, store_id=store_id)[0]
    return_info = ''
    if not goods:
        return_info = '商品不存在'
    elif not stock_type:
        return_info = '请选择补货进货选项'
    else:
        # 拒绝重复添加
        is_exists = stock_width_goods.objects.filter(goods_code=goods_code, state=1, store_id=store_id,
                                                     stock_type=stock_type)  # 商品，门店，状态为1
        if not is_exists:
            # 执行添加
            to_save = stock_width_goods(add_date=one_day_date(), goods_id=goods, store_id=store_id,
                                        stock_type=stock_type, goods_code=goods_code)
            to_save.save()
            return_info = '添加成功'
        else:
            return_info = '已经存在，重复了'
    return goods_form(request, goods.id, return_info)


# 添加过期检查单 表单
def goods_quality_add(request, goods_id):
    goods = goods_list.objects.filter(id=goods_id)[0]
    return render(request, 'goods_quality_add.html', {'goods': goods})


# 执行添加过期检查单
def goods_quality_save(request):
    return_info = ''
    quality_forms = goods_quality_forms(request.POST)
    goods = goods_list.objects.filter(id=request.POST['goods_id'])[0]
    if quality_forms.is_valid():
        goods_id = request.POST['goods_id']
        stock_nums = quality_forms.cleaned_data['stock_nums']
        date_nums = quality_forms.cleaned_data['date_nums']
        add_date = one_day_date()
        is_exists = goods_quality.objects.filter(goods_id=goods_id, state=1)
        if not is_exists:
            to_save = goods_quality(goods_id=goods, add_date=add_date, stock_nums=stock_nums,
                                    goods_code=goods.bar_code, store_id=goods.store_id.id, date_nums=date_nums)
            to_save.save()
            return_info = '添加成功'
        else:
            return_info = '重复添加'
    else:
        return_info = '内容填写有误'

    return goods_form(request, goods.id, return_info)


# 保质列表
def quality_list(request, store_id=0):
    user = request.user
    if store_id == 0:
        store_id = int(request.session['store_id'])

    return_quality_list = []
    goods_list = goods_quality.objects.filter(state=1, store_id=store_id)
    for good in goods_list:
        form_list = order_form.objects.filter(goods_code=good.goods_code, store_id=store_id, form_date__gt=one_day_date(form_time['quality'])).order_by('form_date')
        good_name = good.goods_id.name

        goods_sales = goods_sales_data(form_list, form_time['quality'], good.add_date)
        goods_sales.run()

        new_quality = {'goods_name': good_name, 'goods_code': good.goods_code, 'stock_nums': good.stock_nums,
                       'last_day': good.date_nums-goods_sales.last_day, 'goods_id': good.goods_id,
                       'totle_num_30': goods_sales.totle_num_30, 'add_date': good.add_date, 'id': good.id}
        return_quality_list.append(new_quality)
    return render(request, 'quality_list.html', {'store_id': store_id, 'goods_list': return_quality_list})


# 改变保质观察状态
def quality_state(request, id):
    quality_good = goods_quality.objects.filter(id=id, state=1)[0]
    # 设置为2 及已经处理
    quality_good.state = 2
    quality_good.save()
    return quality_list(request, quality_good.store_id)


# 进货列表
@login_required  # 需要登录
def stock_list(request, store_id=0, stock_type=1):
    user = request.user
    # 默认查看当前状态门店
    if not store_id:
        store_id = int(request.session['store_id'])
    # 返回进货单列表
    return_stock_list = []
    goods_list = stock_width_goods.objects.filter(stock_type=stock_type, state=1, store_id=store_id)
    for good in goods_list:
        form_list = order_form.objects.filter(goods_code=good.goods_code, store_id=store_id, form_date__gt=one_day_date(form_time['stock'])).order_by('form_date')
        goods_name = good.goods_id.name

        # 获取销售数据
        goods_sales = goods_sales_data(form_list, form_time['stock'])
        goods_sales.run()
        new_stock = {'goods_name': goods_name, 'good': good, 'day_average': goods_sales.day_average,
                     'totle_num_30': goods_sales.totle_num_30}
        return_stock_list.append(new_stock)
    return render(request, 'stock_goods_list.html', {'store_id': store_id,
                                                     'goods_list': return_stock_list,
                                                     'stock_type': stock_type})


# 改变进/补货状态
def stock_state(request, id, stock_type):
    stock_goods = stock_width_goods.objects.filter(id=id, state=1)[0]
    # 设置为2 及已经处理
    stock_goods.state = 2
    stock_goods.save()
    return stock_list(request, store_id=stock_goods.store_id, stock_type=stock_type)


###
# 后台操作部分
###
# 新门店添加入口
def new_store(request):
    stores = store_list.objects.all()
    return render(request, 'new_store.html', {'stores': stores})


# 执行门店添加
# 保存门店
def add_new_store(request):
    info = ''
    if request.method == 'POST':
        form = store_forms(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            adds = form.cleaned_data['adds']
            is_exists = store_list.objects.filter(name=name)
            if is_exists:
                info = '门店已经存在'
            else:
                store = store_list(name=name, adds=adds)
                store.save()
                info = '保存成功！'
        else:
            info = form.errors

    return render(request, 'new_store.html', {'info': info})
