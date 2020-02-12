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
    all_data = bs_data.objects.filter(store_id=store_id, date__gte=one_day_date(365)).order_by('date')  # 获取所有数据
    average_data = []   # 平均数据
    all_bsd_data = []   # 所有数据

    totle_turnover = 0  # 总营业额
    totle_gross = 0     # 总毛利
    i = 0               # 周期计数
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

    # 获取一周数据
    week_money = week_sales_data(all_data)

    return render(request, 'index.html', {'all_data': all_data,
                                          'store_id': int(store_id), 'store_name': store_name,
                                          'average': str(average_data),
                                          'totle_turnover': totle_turnover,
                                          'totle_gross': totle_gross,
                                          'week_money': week_money})


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
            # 查询类别 在没有搜索时 显示类别
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
    stores = store_list.objects.all()
    return render(request, 'upload_xls.html', {'stores': stores, 'file_type': file_type})


# 商品订单销售查询
# 商品订单列表
# 计算销售数据
def goods_form(request, goods_id, return_info=''):
    # 查询商品属性
    goods = goods_list.objects.filter(id=goods_id)[0]
    # 查询商品订单数据
    form_list = order_form.objects.filter(goods_code=goods.bar_code, store_id=goods.store_id.id,
                                          form_date__gt=one_day_date(form_time['forms'])).order_by('-form_date')    # -字段名 倒序排列

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
    form_list = order_form.objects.filter(store_id=store_id, form_date__gt=one_day_date(form_time['stock'])).order_by('-form_date')
    goods_sales = goods_sales_data(form_list, form_time['stock'])
    goods_sales.mk_date()
    goods_sales.classify_screen(goods_list)
    return_stock_list = goods_sales.run_to_list()
    return render(request, 'stock_goods_list.html', {'store_id': store_id,
                                                     'goods_list': return_stock_list,
                                                     'stock_type': stock_type})


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


class the_goods:
    id = None
    goods_list_id = None
    name = None
    bar_code = None
    stock_nums = None
    classify = None
    add_date = None
    date_nums = None
