# coding=utf-8
# @Explain  : 营业数据
# @Author   : wooght
# @File     : handbook turnover_data
# @Time     : 2020/3/9 下午11:40

# 接受营业数据
# 返回平均值（日期组装）
# 返回周数据，月数据
# 返回毛利数据
import pandas as pd
from common_func.wooght_forms import one_day_date

class turnover_data:
    def __init__(self, all_data):
        self.data = all_data                    # 营业数据
        self.turnover_month_average_data = []   # 每月平均值->序列
        self.turnover_month_average_dict = []   # 每月平均值
        self.gross_month_total_data = {}        # 没月总毛利额
        self.week_sales_data = []               # 周数据

    # 一周销售对比数据
    def week_sales(self):
        weeks = range(1, 8)
        week_sales = {}
        last_day = pd.to_datetime(self.data[len(self.data)-1].date)
        for i in weeks:
            week_sales[i] = 0
        for day in self.data:
            date = day.date
            pd_weekday = pd.to_datetime(date)
            cha_day = last_day - pd_weekday
            if cha_day.days < 56:
                this_weekday = pd_weekday.weekday() + 1  # 0指星期一
                week_sales[this_weekday] += day.turnover

        self.week_sales_data = week_sales

    # 月毛利额
    def gross_month_total(self):
        result_dict = {}    # result_dict[年月]=毛利额
        for day in self.data:
            date = day.date
            the_day = pd.to_datetime(date)
            month_key = str(the_day.year)+str(the_day.month)
            if month_key not in result_dict.keys():
                result_dict[month_key] = 0
            result_dict[month_key] += day.gross_profit

        self.gross_month_total_data = result_dict

    # 每月平均值
    # 每月平均值序列
    def turnover_month_average(self):
        result_list = []    # 运行结果1：平均值/日期 的序列
        result_month_dict = {}  # 运行结果2： 每月平均值字典
        year_month = {}
        last_keys = 0
        month_totle = 0
        length = len(self.data)
        i = 0
        for day in self.data:
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
                result_month_dict[last_keys] = month_average
                # 一月有多少天，就得到多少个相同值的序列
                for month_day in year_month[last_keys]:
                    result_list.append(month_average)
                # 新月 计算数据清零
                year_month[month_keys] = []
                last_keys = month_keys
                month_totle = 0
            month_totle += day.turnover
            year_month[month_keys].append(month_totle)

        self.turnover_month_average_data = result_list
        self.turnover_month_average_dict = result_month_dict

    # 每月涨幅（同比，环比）
    def turnover_month_average_func(self):
        result_dict = {}
        average_list = []
        i = 0
        for key, value in self.turnover_month_average_dict.items():
            average_list.append(value)
            result_dict[key] = [0, 0, 0]    # [平均值，同比，环比]
            # 同比 上周期同一个月做对比
            if i >11:
                result_dict[key][1] = value/average_list[i-12] - 1
            # 环比 被周期上一个月作对比
            if i > 0:
                result_dict[key][2] = value/average_list[i-1] - 1
            result_dict[key][0] = value
            i += 1
        self.turnover_month_average_dict = result_dict
