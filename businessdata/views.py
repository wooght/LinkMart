from django.shortcuts import render, redirect
from businessdata.models import store_list, bs_data, goods_list, order_form, stock_width_goods, goods_quality, \
    operate_data, cd_store, cd_area, cd_label
from common_func.wooght_forms import *
from common_func.goods_sales_data import goods_sales_data
from common_func.turnover_data import turnover_data
from common_func.wooght_cd_math import *
from django.contrib.auth.decorators import login_required


# 首页
###
#   获取营业数据
#   选择门店
###
@login_required  # 需要登录
def index(request):
    store_id = get_storeid(request)
    store_name = store_list.objects.filter(id=store_id)[0].name  # 获取门店名称
    all_data = bs_data.objects.filter(store_id=store_id, date__gte=one_day_date(2000)).order_by('date')  # 获取所有数据

    # 营业数据处理
    business_data = turnover_data(all_data)
    business_data.week_sales()
    business_data.turnover_month_average()

    # 顶部展示简约数据
    month_average_dict = business_data.turnover_month_average_dict
    last_keys = list(month_average_dict.keys())[-1]
    top_data = month_average_dict[last_keys]
    return render(request, 'index.html', {'all_data': all_data,
                                          'store_id': int(store_id), 'store_name': store_name,
                                          'average': str(business_data.day_average_30), 'top_data': top_data,
                                          'totle_turnover': business_data.totle_turnover,
                                          'totle_gross': business_data.totle_gross,
                                          'week_money': business_data.week_sales_data,
                                          'month_average': business_data.turnover_month_average_data,
                                          'month_average_dict': business_data.turnover_month_average_dict,
                                          'month_gross': business_data.gross_month_total_data,
                                          'month_average_gross':business_data.gross_month_average_data,
                                          'year_turnover': business_data.year_turnover})


# 运营数据
@login_required  # 需要登录
def operate(request):
    store_id = get_storeid(request)
    # 生成月份
    month_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    year_list = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    store_name = store_list.objects.filter(id=store_id)[0].name  # 获取门店名称
    all_data = operate_data.objects.filter(store_id=store_id).order_by('id')  # 获取所有数据
    return render(request, 'operate.html',
                  {'all_data': all_data, 'store_name': store_name, 'month_list': month_list, 'year_list': year_list, 'store_id': int(store_id)})


# 获取门店ID方法
# function
def get_storeid(request):
    store_id = request.session['store_id']
    if request.method == 'GET':
        # 获取当前门店ID
        store_id = request.GET.get('store_id')
        if store_id:
            request.session['store_id'] = store_id
        else:
            store_id = request.session['store_id']
    return store_id


# 分类数据展示
def classify_page(request):
    return render(request, 'classify.html')


# 商品列表页面展示
# 默认显示默认分类
def goods_list_page(request, classify='默认分类'):
    classify_keys = []  # 类别列表 默认为空
    is_search = False
    if request.method == 'GET':
        goods_code = request.GET.get('goods_code')
        if not goods_code:
            # LinkMart类别
            for item in Linkclassfly.keys():
                classify_keys.append(item)
            # 查询类别
            classify_data = goods_list.objects.values('classify').filter(store_id=request.session['store_id'])
            for item in classify_data:
                if item['classify'] not in classify_keys:
                    classify_keys.append(item['classify'])
            if request.GET.get('classify'):
                classify = request.GET.get('classify')
            all_data = goods_list.objects.filter(store_id=request.session['store_id'], classify=classify)
        else:
            is_search = True
            # 通过条码查询
            all_data = goods_list.objects.filter(bar_code__contains=goods_code,
                                                 store_id=request.session['store_id'])  # # 字段名__contains 模糊查询 注意中间双划线
            if len(all_data) < 1:
                # 通过名称查询
                all_data = goods_list.objects.filter(name__contains=goods_code,
                                                     store_id=request.session['store_id'])
    else:
        all_data = goods_list.objects.all()
    return render(request, 'goods_list.html', {'goods_list': all_data, 'classify_keys': classify_keys,
                                               'is_search': is_search})


# 提交文件入口
# 获取提交类型
# 指定方法处理数据
# 返回数据处理结果
@login_required  # 需要登录
def upload_form(request):
    store_id = get_storeid(request)
    stores = store_list.objects.all()
    return render(request, 'upload_xls.html', {'stores': stores, 'file_type': file_type, 'store_id': int(store_id)})


# 商品订单销售查询
# 商品订单列表
# 计算销售数据
def goods_form(request, goods_id, return_info=''):
    # 查询商品属性
    goods = goods_list.objects.filter(id=goods_id)[0]
    # 查询商品订单数据
    form_list = order_form.objects.filter(goods_code=goods.bar_code, store_id=goods.store_id.id,
                                          form_date__gt=one_day_date(form_time['forms'])).order_by(
        '-form_date')  # -字段名 倒序排列

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
    quality_goods_list = goods_quality.objects.filter(state=1, store_id=store_id)
    goods_list = []
    # 商品列表组装    模型 goods_list
    for stock_good in quality_goods_list:
        good = the_goods()
        good.id = stock_good.id
        good.goods_list_id = stock_good.goods_id.id
        good.name = stock_good.goods_id.name
        good.bar_code = stock_good.goods_code
        good.stock_nums = stock_good.stock_nums
        good.classify = stock_good.goods_id.classify
        good.add_date = stock_good.add_date
        good.date_nums = stock_good.date_nums
        goods_list.append(good)
    form_list = order_form.objects.filter(store_id=store_id, form_date__gt=one_day_date(form_time['stock'])).order_by(
        '-form_date')
    goods_sales = goods_sales_data(form_list, form_time['stock'])
    goods_sales.mk_date()
    goods_sales.classify_screen(goods_list)
    return_quality_list = goods_sales.run_to_quality()
    return render(request, 'quality_list.html', {'store_id': store_id,
                                                 'goods_list': return_quality_list,
                                                 })


# 进货列表
@login_required  # 需要登录
def stock_list(request, store_id=0, stock_type=1):
    user = request.user
    # 默认查看当前状态门店
    if not store_id:
        store_id = int(request.session['store_id'])

    stock_goods_list = stock_width_goods.objects.filter(stock_type=stock_type, state=1, store_id=store_id)
    goods_list = []
    # 商品列表组装    模型 goods_list
    for stock_good in stock_goods_list:
        good = the_goods()
        good.id = stock_good.id
        good.goods_list_id = stock_good.goods_id.id
        good.name = stock_good.goods_id.name
        good.bar_code = stock_good.goods_code
        good.stock_nums = stock_good.goods_id.stock_nums
        good.classify = stock_good.goods_id.classify
        goods_list.append(good)
    form_list = order_form.objects.filter(store_id=store_id, form_date__gt=one_day_date(form_time['stock'])).order_by(
        '-form_date')
    goods_sales = goods_sales_data(form_list, form_time['stock'])
    goods_sales.mk_date()
    goods_sales.classify_screen(goods_list)
    return_stock_list = goods_sales.run_to_list()
    return render(request, 'stock_goods_list.html', {'store_id': store_id,
                                                     'goods_list': return_stock_list,
                                                     'stock_type': stock_type})


######################################################################################
# 功能模块操作部分
######################################################################################


# 标签管理
def barcodeprint(request, classify='默认分类'):
    classify_keys = []  # 类别列表 默认为空
    is_search = False
    if request.method == 'GET':
        goods_code = request.GET.get('goods_code')
        if not goods_code:
            # LinkMart类别
            for item in Linkclassfly.keys():
                classify_keys.append(item)
            # 查询类别
            classify_data = goods_list.objects.values('classify').filter(store_id=request.session['store_id'])
            for item in classify_data:
                if item['classify'] not in classify_keys:
                    classify_keys.append(item['classify'])
            if request.GET.get('classify'):
                classify = request.GET.get('classify')
            all_data = goods_list.objects.filter(store_id=request.session['store_id'], classify=classify)
        else:
            is_search = True
            # 通过条码查询
            all_data = goods_list.objects.filter(bar_code__contains=goods_code,
                                                 store_id=request.session['store_id'])  # # 字段名__contains 模糊查询 注意中间双划线
            if len(all_data) < 1:
                # 通过名称查询
                all_data = goods_list.objects.filter(name__contains=goods_code,
                                                     store_id=request.session['store_id'])
    else:
        all_data = goods_list.objects.all()
    return render(request, 'barcode.html', {'goods_list': all_data, 'classify_keys': classify_keys,
                                            'is_search': is_search})


# 执行标签打印
def barcode_toprint(request):
    goods = goods_list.objects.filter(id=request.GET.get('good_id'))
    return render(request, 'barcodeprint.html', {'good': goods[0]})


######################################################################################
# 地图操作
######################################################################################
# 地图展示
def show_map(request):
    areas = cd_area.objects.all()
    stores = cd_store.objects.all()
    new_stores = store_order_math(stores)
    new_areas = area_rate_math(areas, new_stores)
    cd_labels = cd_label.objects.all()
    return render(request, 'map.html', {'areas': new_areas, 'stores': new_stores, 'cd_labels': cd_labels})


# 添加踩点数据页
def save_cd_data(request):
    info = ''
    if request.method == 'POST':
        p = request.POST
        cd_store_id = p.get('cd_store_id')
        cd_order = cd_data(cd_store_id=p.get('cd_store_id'), cd_orders=p.get('cd_orders'), contrast_orders=p.get('contrast_orders'), road_orders=p.get('road_orders'),
                           contrast_total_orders=p.get('contrast_total_orders'), home_orders=p.get('home_orders'), business_orders=p.get('business_orders'))
        try:
            cd_order.save()
        except Exception as e:
            info = e.args
    else:
        cd_store_id = request.GET.get('id')
        if cd_store_id is None:
            cd_store_id = 1
    areas = cd_area.objects.all()
    stores = cd_store.objects.all()
    new_stores = store_order_math(stores)
    cd_data_list = cd_data.objects.filter(cd_store_id=cd_store_id)
    return render(request, 'save_cd_data.html', {'stores':new_stores, 'cd_store_id': int(cd_store_id), 'cd_data_list': cd_data_list, 'info':info, 'areas':areas})


# 执行添加商圈
def save_cd_area(request):
    info = ''
    if request.method == 'POST':
        p = request.POST
        form = cd_area_forms(request.POST)
        if form.is_valid():
            # 判断是修改还是添加
            if p.get('id'):
                # 修改
                the_area = cd_area.objects.filter(id=p.get('id'))[0]
                the_area.area_name = p.get('area_name')
                the_area.area_peoples = p.get('area_peoples')
                the_area.home_peoples = p.get('home_peoples')
                the_area.area_house = p.get('area_house')
                the_area.area_occ_rate = p.get('area_occ_rate')
                the_area.area_stores = p.get('area_stores')
                the_area.stores_occ_rate = p.get('stores_occ_rate')
                the_area.area_consumption_rate = p.get('area_consumption_rate')
                the_area.area_totle_orders = p.get('area_totle_orders')

                the_area.area_x = p.get('area_x')
                the_area.area_y = p.get('area_y')
                the_area.save()
                info = '保存成功'
            else:
                # 添加
                area_name = p.get('area_name')
                is_exists = cd_area.objects.filter(area_name=area_name)
                if is_exists:
                    info = '名称已经存在'
                else:
                    area = cd_area(area_name=area_name, area_house=p.get('area_house'),area_peoples=p.get('area_peoples'),
                                   area_occ_rate=p.get('area_occ_rate'),area_stores=p.get('area_stores'),stores_occ_rate=p.get('stores_occ_rate'),
                                   area_consumption_rate=p.get('area_consumption_rate'),area_totle_orders=p.get('area_totle_orders'),
                                   area_x=p.get('area_x'),area_y=p.get("area_y"))
                    try:
                        area.save()
                        info = '保存成功'
                    except Exception as e:
                        info = e.args
        else:
            info = form.errors
    areas = cd_area.objects.all()
    new_areas = area_rate_math(areas, store_order_math(cd_store.objects.all()))

    return render(request, 'save_cd_area.html', {'info': info, 'areas': new_areas})


# 执行添加踩点门店
def save_cd_store(request):
    info = ''
    if request.method == 'POST':
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
                the_store.store_orders = p.get('store_orders')
                the_store.store_turnover = p.get('store_turnover')
                the_store.contrast_orders = p.get('contrast_orders')
                the_store.store_size = p.get('store_size')
                the_store.store_waiters = p.get('store_waiters')
                the_store.door_header = p.get('door_header')

                the_store.store_x = p.get('store_x')
                the_store.store_y = p.get('store_y')
                the_store.save()
                info = '保存成功'
            else:
                # 添加
                store_name = p.get('store_name')
                is_exists = cd_store.objects.filter(store_name=store_name)
                if is_exists:
                    info = '名称已经存在'
                else:
                    store = cd_store(store_name=store_name, is_24h=p.get('is_24h'),is_smoke=p.get('is_smoke'),
                                   store_orders=p.get('store_orders'), store_turnover=p.get('store_turnover'), contrast_orders=p.get('contrast_orders'),
                                   store_size=p.get('store_size'), store_waiters=p.get('store_waiters'), cd_area=p.get('cd_area'),
                                   door_header=p.get('door_header'), store_x=p.get("store_x"), store_y=p.get('store_y'))
                    try:
                        store.save()
                        info = '保存成功'
                    except Exception as e:
                        info = e.args
        else:
            info = form.errors
    # 查询商圈
    areas = cd_area.objects.all()
    stores = cd_store.objects.all()
    cd_labels = cd_label.objects.all()
    f_idlist = {}
    for item in cd_labels:
        if item.label_type == 0:
            f_idlist[item.id] = []
    for item in cd_labels:
        if item.label_type > 0:
            f_idlist[item.f_id].append({'id': item.id, 'label_name': item.label_name, 'label_score': item.label_score, 'label_notes': item.label_notes})
    return render(request, 'save_cd_store.html', {'info': info, 'stores': stores, 'areas': areas, 'f_labels': f_idlist, 'cd_labels':cd_labels})


######################################################################################
# 后台操作部分
######################################################################################
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


class the_goods:
    id = None
    goods_list_id = None
    name = None
    bar_code = None
    stock_nums = None
    classify = None
    add_date = None
    date_nums = None
