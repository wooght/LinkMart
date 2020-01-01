# coding=utf-8
# @Explain  : 分类数据统计
# @Author   : wooght
# @File     : linkmart classify_data
# @Time     : 2020/1/1 下午1:11


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
            classify_ratio[key] = float('%.4f' % (value / totle_nums))*100
        return classify_ratio
