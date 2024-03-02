# coding=utf-8
# @Explain  : 商品销售数据
# @Author   : wooght
# @File     : honc_live goods_sales_data
# @Time     : 2019/12/19 下午2:32

import pandas as pd
from common_func.wooght_forms import one_day_date, month_compare


# 统计目标：单个商品，某类商品
# 商品销售趋势统计
# 统计日均，近30天
# 商品销售数据组装
# 接受order_form数据
# 返回数据对象【日均，近30日】
class goods_sales_data:
    def __init__(self, form_list, start_day, add_date=''):
        self.month_price_list = None    # 月订单单价均线字典
        self.month_order_list = None    # 月订单均线字典
        self.month_data_list = None     # 月商品销量均线字典

        self.date_dict = {}         # 日期：销售数量
        self.time_dict = {}         # 小时：销售数量
        self.date_order_dict = {}   # 日期：订单数量
        self.price_order_dict = {}  # 日期：订单单价
        self.totleprice_order_dict = {}  # 日期：订单总价

        self.form_list = form_list
        self.start_day = start_day
        self.day_average = 0        # 日均
        self.totle_num_30 = 0       # 近30天
        self.add_date = add_date

    # #生成时间轴
    # 根据统计天数 组装线性时间字典 日期:数量
    def mk_date(self):
        # 组装日期轴
        date_list = pd.date_range(start=one_day_date(self.start_day), end=one_day_date())
        date_list = list(date_list.date)
        # 生成日期轴字典
        for i in date_list:
            self.date_dict[i.strftime('%Y-%m-%d')] = 0
            self.date_order_dict[i.strftime('%Y-%m-%d')] = 0
            self.price_order_dict[i.strftime('%Y-%m-%d')] = 0
            self.totleprice_order_dict[i.strftime('%Y-%m-%d')] = 0
        # 组装小时序列
        hours = range(24)
        for i in hours:
            self.time_dict[i] = 0

    # #运行统计结果->一个图表使用
    # 日期线性组装销量字典 date_dict{[date:goods_num],...}
    # 时间线性组装销量字典 time_dict{[hour:goods_num],...}
    # 计算平均值-> 月均，近30日
    def run(self):
        self.mk_date()
        # 最开始售卖日期
        min_date = pd.to_datetime(one_day_date())
        # 30天开头日期
        if not self.add_date:
            date_30 = pd.to_datetime(one_day_date(30))
        else:
            date_30 = pd.to_datetime(self.add_date)
            last_day = pd.to_datetime(one_day_date()) - date_30
            self.last_day = last_day.days
        # 销售总数量
        totle_num = 0

        # 遍历订单列表
        # 按日期统计销售数量/销售价格/订单数
        for item in self.form_list:
            now_date = item.form_date.strftime('%Y-%m-%d')
            now_time = int(str(item.form_time).split(':')[0])
            #
            # 商品销售情况
            #
            # 相同日期 数量累加
            self.date_dict[now_date] += item.goods_num
            # 相同小时 数量累加
            self.time_dict[now_time] += item.goods_num
            # 总数量累加
            totle_num += item.goods_num
            #
            # 订单情况
            #
            self.date_order_dict[now_date] += 1                         # 订单加一
            self.totleprice_order_dict[now_date] += item.form_money_true     # 订单价格累加
            #
            # 判断开始售卖日期
            # 判断是否近30日销售
            if item.goods_num > 0:
                # __le__ datetime大小比较之 小于等于/  __ge__ 大于等于/  __eq__ 等于/  __gt__大于/ __ne__等于
                if item.form_date.__le__(min_date):
                    min_date = item.form_date
                if item.form_date.__gt__(date_30):
                    self.totle_num_30 += item.goods_num
        # 计算售卖天数
        count_day = pd.to_datetime(one_day_date()) - pd.to_datetime(min_date)
        # 计算日均销售数量-》避免0的情况报错
        if count_day.days == 0:
            self.day_average = 0
        else:
            self.day_average = float('%.2f' % (totle_num / count_day.days))

        # 平均订单单价 当天订单总价/当天订单数
        for day, value in self.date_order_dict.items():
            if value > 0:
                self.price_order_dict[day] = float('%.2f' % (self.totleprice_order_dict[day] / value))
            else:
                self.price_order_dict[day] = 0

        # 获取月均序列
        self.month_data_list = self.month_average_data('goods')
        self.month_order_list = self.month_average_data('orders')
        self.month_price_list = self.month_average_data('price')

    # ###
    # #多个商品统计
    # 返回商品列表 模型为goods_sales_list[code:sales_data_models,]
    def run_to_list(self):
        goods_sales_list = {}  # 返回数据字典 code->sales_data_models
        min_date = pd.to_datetime(one_day_date())  # 第一次售卖日期
        date_30 = pd.to_datetime(one_day_date(30))  # 30日起步日期
        # 初始化数据列表
        for good in self.goods_list:
            sales_data_models = dict(id=good.id, name=good.name, code=good.bar_code, stock=good.stock_nums,
                                     classify=good.classify, day_average=0, totle_num_30=0,
                                     totle_num=0, min_date=min_date)
            # 解决几个地方传递的ID不一样的问题 库存及补货处传递的ID为库存表中的ID
            if hasattr(good, 'goods_list_id'):
                sales_data_models['goods_list_id'] = good.goods_list_id
            else:
                sales_data_models['goods_list_id'] = 0

            goods_sales_list[good.bar_code] = sales_data_models

        # 遍历订单
        for item in self.form_list:
            now_date = item.form_date
            code = item.goods_code
            # 添加数量
            goods_sales_list[code]['totle_num'] += item.goods_num
            # 如果有销售数据
            if item.goods_num > 0:
                # __le__ datetime大小比较之 小于等于/  __ge__ 大于等于/  __eq__ 等于/  __gt__大于/ __ne__等于
                # 找到开始售卖日期
                if now_date.__le__(goods_sales_list[code]['min_date']):
                    goods_sales_list[code]['min_date'] = now_date
                # 近30日销售量累加
                if now_date.__ge__(date_30):
                    goods_sales_list[code]['totle_num_30'] += item.goods_num

        # pandas 组装
        new_list = []
        for item in goods_sales_list.values():
            count_day = pd.to_datetime(one_day_date()) - pd.to_datetime(item['min_date'])
            if count_day.days > 0:
                item['day_average'] = float('%.2f' % (item['totle_num'] / count_day.days))
            new_list.append(item)
        pd_goods_sales = pd.DataFrame(new_list)
        # 按照30日销量排序
        if len(pd_goods_sales) > 0:
            pd_goods_sales.sort_values(by='totle_num_30', ascending=False, inplace=True)
        return_list = []
        for item, row in pd_goods_sales.iterrows():
            return_list.append([row['classify'], row['name'], row['totle_num'], row['id'], row['code'], row['stock'],
                                row['day_average'], row['totle_num_30'], row['goods_list_id']])
        return return_list

    # ###
    # #保质销量统计
    # 返回商品列表 模型为goods_sales_list[code:sales_data_models,]
    def run_to_quality(self):
        goods_sales_list = {}  # 返回数据字典 code->sales_data_models
        min_date = pd.to_datetime(one_day_date())  # 第一次售卖日期
        date_30 = pd.to_datetime(one_day_date(30))  # 30日起步日期
        # 初始化数据列表
        for good in self.goods_list:
            sales_data_models = dict(id=good.id, name=good.name, code=good.bar_code, stock=good.stock_nums,
                                     classify=good.classify, day_average=0, totle_num_30=0, add_date=good.add_date,
                                     totle_num=0, min_date=min_date, after_sales=0, date_nums=good.date_nums)
            sales_data_models['goods_list_id'] = good.goods_list_id
            goods_sales_list[good.bar_code] = sales_data_models

        # 遍历订单
        for item in self.form_list:
            now_date = item.form_date
            code = item.goods_code
            # 添加数量
            goods_sales_list[code]['totle_num'] += item.goods_num
            # 如果有销售数据
            if item.goods_num > 0:
                # __le__ datetime大小比较之 小于等于/  __ge__ 大于等于/  __eq__ 等于/  __gt__大于/ __ne__等于
                if now_date.__le__(goods_sales_list[code]['min_date']):
                    goods_sales_list[code]['min_date'] = now_date
                if now_date.__ge__(date_30):
                    goods_sales_list[code]['totle_num_30'] += item.goods_num
                if now_date.__ge__(goods_sales_list[code]['add_date']):
                    goods_sales_list[code]['after_sales'] += item.goods_num

        # pandas 组装
        new_list = []
        for item in goods_sales_list.values():
            loss_day = pd.to_datetime(one_day_date()) - pd.to_datetime(item['add_date'])    # 过去天数
            left_over = item['date_nums'] - loss_day.days                                   # 剩下天数
            item['left_over'] = left_over
            count_day = pd.to_datetime(one_day_date()) - pd.to_datetime(item['min_date'])
            if count_day.days > 0:
                item['day_average'] = float('%.2f' % (item['totle_num'] / count_day.days))
            new_list.append(item)
        pd_goods_sales = pd.DataFrame(new_list)
        # 按照30日销量排序
        if len(pd_goods_sales) > 0:
            pd_goods_sales.sort_values(by='left_over', ascending=True, inplace=True)
        return_list = []
        for item, row in pd_goods_sales.iterrows():
            return_list.append([row['classify'], row['name'], row['totle_num'], row['id'], row['code'], row['stock'],
                                row['day_average'], row['totle_num_30'], row['goods_list_id'],
                                row['add_date'], row['left_over'], row['after_sales']])
        return return_list

    # #订单筛选
    # 得到制定一类/部分商品的订单
    # 返回订单列表form_list
    def classify_screen(self, goods_list):
        self.goods_list = goods_list
        # 组装某类别下的商品条码列表
        goods_to_classify = []
        for good in goods_list:
            goods_to_classify.append(good.bar_code)

        # 根据条码列表筛选订单 组装新订单列表 属于某个类
        classify_forms = []
        for form in self.form_list:
            if form.goods_code in goods_to_classify:
                classify_forms.append(form)
        self.form_list = classify_forms

    # 每月平均值序列
    def month_average_data(self, math_type):
        result_list = []        # 总序列
        year_month = {}         # 每月序列 计数用
        everymonth_dict = {}    # 月字典{月份：平均值}
        last_keys = 0
        month_totle = 0
        if math_type == 'goods':
            math_data = self.date_dict
        elif math_type == 'orders':
            math_data = self.date_order_dict
        else:
            math_data = self.price_order_dict
        length = len(math_data)
        i = 0
        for day, num in math_data.items():
            i += 1  # 计数
            date = day
            pd_monthday = pd.to_datetime(date)
            month_keys = str(pd_monthday.year) + '_' + str(pd_monthday.month)
            # 初始化
            if i == 1:
                last_keys = month_keys
                year_month[month_keys] = []
            # 月份交替
            if (month_keys != last_keys) or (i == length):
                # 一月有多少天，就得到多少个相同值的序列
                month_average = float('%.2f' % (month_totle / len(year_month[last_keys])))
                for month_day in year_month[last_keys]:
                    result_list.append(month_average)
                everymonth_dict[last_keys] = month_average
                # 新月 计算数据清零
                year_month[month_keys] = []
                last_keys = month_keys
                month_totle = 0
            month_totle += num
            year_month[month_keys].append(month_totle)

        return [result_list, month_compare(everymonth_dict)]


# 计算一天24小时销售情况
def day_sales_data(forms_list):
    hours = range(24)
    day_hours = {}
    # 组装时间序列
    for i in hours:
        day_hours[i] = 0

    for form in forms_list:
        form_hour = form.form_time
        this_hour = int(str(form_hour).split(':')[0])
        day_hours[this_hour] += form.goods_money

    return day_hours


# 计算一周销售情况
def week_sales_data(all_data):
    weeks = range(1, 8)
    week_sales = {}
    for i in weeks:
        week_sales[i] = 0
    for day in all_data:
        date = day.date
        pd_weekday = pd.to_datetime(date)
        this_weekday = pd_weekday.weekday() + 1  # 0指星期一
        week_sales[this_weekday] += day.turnover

    return week_sales


# 计算一周每天24销售销售情况
def week_hours_sales_data(all_data):
    weeks = range(0, 7)
    hours = range(0, 24)
    result_dict = []
    for i in weeks:
        for h in hours:
            result_dict.append([i, h, 0])
    for form in all_data:
        form_hour = form.form_time
        this_hour = int(str(form_hour).split(':')[0])
        date = form.form_date
        pd_weekday = pd.to_datetime(date)
        this_weekday = pd_weekday.weekday()  # 0指星期一
        # 订单加一
        result_dict[this_weekday * 24 + this_hour][2] += 1/4
    return result_dict


# 每月平均值序列
def month_average_data(all_data):
    result_list = []
    year_month = {}
    last_keys = 0
    month_totle = 0
    length = len(all_data)
    i = 0
    for day in all_data:
        i += 1              # 计数
        date = day.date
        pd_monthday = pd.to_datetime(date)
        month_keys = str(pd_monthday.year)+'_'+str(pd_monthday.month)
        # 初始化
        if i==1:
            last_keys = month_keys
            year_month[month_keys] = []
        # 月份交替
        if (month_keys != last_keys) or (i==length):
            # 一月有多少天，就得到多少个相同值的序列
            month_average = float('%.2f'%(month_totle/len(year_month[last_keys])))
            for month_day in year_month[last_keys]:
                result_list.append(month_average)
            # 新月 计算数据清零
            year_month[month_keys] = []
            last_keys = month_keys
            month_totle = 0
        month_totle += day.turnover
        year_month[month_keys].append(month_totle)

    return result_list