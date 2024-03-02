# coding=utf-8
# @Explain  : 分类数据统计
# @Author   : wooght
# @File     : linkmart classify_data
# @Time     : 2020/1/1 下午1:11
import pandas as pd
from common_func.wooght_forms import one_day_date


# 分类计数
# 分类销量
# 分类比例
class classify_data:
    def __init__(self, goods_list, form_list):
        self.forms = form_list
        self.goods = goods_list
        # 类别列表
        self.classify = []
        # 类别对应销售额
        self.classify_sales = {}
        # 条码对应类别
        self.code_to_classify = {}
        for item in goods_list:
            if item.bar_code not in self.code_to_classify.keys():
                # if '烟' not in item.classify:
                self.code_to_classify[item.bar_code] = item.classify
                self.classify.append(item.classify)
                self.classify_sales[item.classify] = 0

    # 获取类别对应销售数量
    # classify_ratio[类别]=数量
    def get_ratio(self, days):
        self.set_sales_empty()
        totle_nums = 0
        for forms in self.forms:
            if forms.goods_code in self.code_to_classify.keys():
                # 判断订单中商品是否在商品列表中，排除商品被删除的可能
                self.classify_sales[self.code_to_classify[forms.goods_code]] += forms.goods_num
                totle_nums += forms.goods_num
        classify_ratio = {}
        for key, value in self.classify_sales.items():
            classify_ratio[key] = float('%.2f' % (value / days))
        return classify_ratio

    # 获取月份比较
    def get_compare(self, last_forms, same_forms, first_forms):
        self.forms = last_forms
        last_sales_nums = self.get_ratio(30)
        self.forms = same_forms
        same_sales_nums = self.get_ratio(30)
        self.forms = first_forms
        first_sales_nums = self.get_ratio(30)
        # compare{类别：[同比，环比]}
        compare = {}
        for key, value in last_sales_nums.items():
            if last_sales_nums[key] == 0 and same_sales_nums[key] == 0:
                same_ratio = 0
            else:
                same_ratio = ((last_sales_nums[key] - same_sales_nums[key]) / (same_sales_nums[key])) if \
                same_sales_nums[key] > 0 else 1
            if last_sales_nums[key] == 0 and first_sales_nums[key] == 0:
                month_ratio = 0
            else:
                month_ratio = ((last_sales_nums[key] - first_sales_nums[key]) / first_sales_nums[key]) if \
                first_sales_nums[key] > 0 else 1
            compare[key] = [float('%.2f' % same_ratio), float('%.2f' % month_ratio)]
        return compare

    # 清空 classify_sales数据 及类别-》销售数量为0
    def set_sales_empty(self):
        for key in self.classify_sales.keys():
            self.classify_sales[key] = 0

    # 获取烟，水占比 序列
    def get_ratio_list(self):
        # 包含全部香烟的分类列表
        smoke = ['中烟', '川烟', '外烟', '整条烟']
        water = ['饮料', '碳酸饮料', '乳饮料', '茶饮料', '饮用水', '功能饮料']
        # 时间序列字典 日期：[总量, 烟量, 水量]
        day_list = {}
        # 遍历订单，获取总数，烟数，水数 列表【总数，烟数，水数】
        for forms in self.forms:
            # 时间序列组成 字典
            if forms.form_date not in day_list.keys():
                day_list[forms.form_date] = [0, 0, 0]
            # 总数计量
            day_list[forms.form_date][0] += 1
            # 烟计量
            # print(self.code_to_classify[forms.goods_code])
            if forms.goods_code not in self.code_to_classify.keys():
                continue
            if self.code_to_classify[forms.goods_code] in smoke:
                # 整条烟 计量为10
                if self.code_to_classify[forms.goods_code] == '整条烟':
                    day_list[forms.form_date][1] += 10
                else:
                    day_list[forms.form_date][1] += 1
            elif self.code_to_classify[forms.goods_code] in water:
                day_list[forms.form_date][2] += 1
        smoke_ratio = self.mk_date()
        for key, value in day_list.items():
            smoke_ratio[key.strftime('%Y-%m-%d')] = [float('%.2f' % (value[1] / value[0])),
                                                     float('%.2f' % (value[2] / value[0]))]
        return smoke_ratio

    ## 组装时间轴
    # 组装过去一年的时间轴 截止日期是今天
    def mk_date(self):
        # 组装时间轴
        date_list = pd.date_range(start=one_day_date(400), end=one_day_date())
        date_list = list(date_list.date)
        # 生成时间轴字典
        date_dict = {}
        for i in date_list:
            date_dict[i.strftime('%Y-%m-%d')] = [0, 0]
        return date_dict
