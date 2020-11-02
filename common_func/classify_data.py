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

    # 获取类别比例
    def get_ratio(self):
        totle_sales = 0
        totle_nums = 0
        for forms in self.forms:
            # if forms.goods_code in self.code_to_classify.keys():
            self.classify_sales[self.code_to_classify[forms.goods_code]] += forms.goods_num
            totle_nums += forms.goods_num
        classify_ratio = {}
        for key, value in self.classify_sales.items():
            classify_ratio[key] = float('%.2f' % (value/90))
        return classify_ratio

    # 获取烟，水占比 序列
    def get_ratio_list(self):
        # 包含全部香烟的分类列表
        smoke = ['中烟', '川烟', '外烟', '整条烟']
        water = ['饮料']
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
            # smoke_ratio[key.strftime('%Y-%m-%d')] = float('%.2f' % (value[1] / value[0]))
            smoke_ratio[key.strftime('%Y-%m-%d')] = [float('%.2f' % (value[1]/value[0])), float('%.2f' % (value[2]/value[0]))]
        return smoke_ratio

    ## 组装时间轴
    # 组装过去一年的时间轴 截止日期是今天
    def mk_date(self):
        # 组装时间轴
        date_list = pd.date_range(start=one_day_date(365), end=one_day_date())
        date_list = list(date_list.date)
        # 生成时间轴字典
        date_dict = {}
        for i in date_list:
            date_dict[i.strftime('%Y-%m-%d')] = [0,0]
        return date_dict