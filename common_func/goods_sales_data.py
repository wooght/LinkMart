# coding=utf-8
# @Explain  : 商品销售数据
# @Author   : wooght
# @File     : honc_live goods_sales_data
# @Time     : 2019/12/19 下午2:32
# 商品销售数据组装
# 接受order_form数据
# 返回数据对象【日均，近30日】
import pandas as pd
from common_func.wooght_forms import one_day_date


class goods_sales_data:
    def __init__(self, form_list, start_day, add_date=''):
        self.date_dict = {}
        self.form_list = form_list
        self.start_day = start_day
        self.day_average = 0  # 日均
        self.totle_num_30 = 0  # 近30天
        self.add_date = add_date

    def mk_date(self):
        # 组装时间轴
        date_list = pd.date_range(start=one_day_date(self.start_day), end=one_day_date())
        date_list = list(date_list.date)
        # 生成时间轴字典
        for i in date_list:
            self.date_dict[i.strftime('%Y-%m-%d')] = 0

    def run(self):
        self.mk_date()
        # 最开始售卖日期
        min_date = pd.to_datetime(one_day_date())
        # 30天开头日期
        if not self.add_date:
            date_30 = pd.to_datetime(one_day_date(30))
        else:
            date_30 = pd.to_datetime(self.add_date)
            last_day = pd.to_datetime(one_day_date())-date_30
            self.last_day = last_day.days
        # 销售总数量
        totle_num = 0
        # 近30天销售数量
        totle_num_30 = 0
        # 遍历订单列表
        for item in self.form_list:
            now_date = item.form_date
            # 相同日期 数量累加
            self.date_dict[now_date.strftime('%Y-%m-%d')] += item.goods_num
            # 总数量累加
            totle_num += item.goods_num
            if item.goods_num > 0:
                # __le__ datetime大小比较之 小于等于/  __ge__ 大于等于/  __eq__ 等于/  __gt__大于/ __ne__等于
                if now_date.__le__(min_date):
                    min_date = now_date
                if now_date.__ge__(date_30):
                    self.totle_num_30 += item.goods_num
        # 计算售卖天数
        count_day = pd.to_datetime(one_day_date()) - pd.to_datetime(min_date)
        # 避免0的情况报错
        if count_day.days == 0:
            self.day_average = 0
        else:
            self.day_average = float('%.2f' % (totle_num / count_day.days))


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
        day_hours[this_hour] += form.form_money_true

    return day_hours


# 计算一周销售情况
def week_sales_data(forms_list):
    weeks = range(1, 8)
    week_sales = {}
    for i in weeks:
        week_sales[i] = 0
    for form in forms_list:
        form_date = form.form_date
        pd_weekday = pd.to_datetime(form.form_date)
        this_weekday = pd_weekday.weekday()+1     # 0指星期一
        week_sales[this_weekday] += form.form_money_true

    return week_sales
