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
from common_func.wooght_forms import one_day_date, month_compare


class turnover_data:
    def __init__(self, all_data):
        self.data = all_data                    # 营业数据
        self.totle_turnover = 0                 # 总营业额
        self.year_turnover = {}                 # 每年总营业额
        self.totle_gross = 0                    # 总毛利
        self.day_average_30 = []                # 30日平均线
        self.turnover_month_average_data = []   # 每月平均值->序列
        self.gross_month_average_data = []      # 每月毛利率平均值->序列
        self.turnover_month_average_dict = {}   # 每月平均值
        self.gross_month_total_data = {}        # 没月总毛利额
        self.week_sales_data = []               # 周数据
        self.run()

    def run(self):
        i = 0   # 周期计数
        cycle = 30  # 平均值计算周期
        all_bsd_data = []   # 营业额列表
        for item in self.data:
            i += 1
            self.totle_turnover += item.turnover
            self.totle_gross += item.gross_profit
            all_bsd_data.append(item.turnover)

            # # 30日平均值
            # 总天数小于30天 及平均值就等于已有的天数平均值
            if i < cycle:
                self.day_average_30.append(float('%.2f' % (self.totle_turnover/i)))
            else:
                self.day_average_30.append(float('%.2f' % (sum(all_bsd_data[i - cycle:i]) / cycle)))

            # # 每月毛利额
            the_day = pd.to_datetime(item.date)
            month_key = str(the_day.year) + str(the_day.month)  # 组装月份key值
            # 月份交替
            if month_key not in self.gross_month_total_data.keys():
                self.gross_month_total_data[month_key] = 0
            self.gross_month_total_data[month_key] += item.gross_profit

            # 每年总营业额
            if the_day.year not in self.year_turnover.keys():
                self.year_turnover[the_day.year] = 0
            self.year_turnover[the_day.year] += item.turnover

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
            # 只统计近8周数据
            if cha_day.days < 56:
                this_weekday = pd_weekday.weekday() + 1  # 0指星期一
                week_sales[this_weekday] += day.turnover

        self.week_sales_data = week_sales

    # 每月平均值
    # 每月平均值序列
    def turnover_month_average(self):
        result_list = []            # 运行结果1：[平均值序列]
        result_month_dict = {}      # 运行结果2： {月份：平均值}
        result_gross_list = []      # 运行结果3： [平均毛利率序列]
        year_month = {}
        last_keys = 0               # 当前月份key
        month_totle = 0             # 月合计营业额
        gross_totle = 0             # 月合计毛利额
        length = len(self.data)
        i = 0
        for day in self.data:
            i += 1                  # 计数
            date = day.date
            pd_monthday = pd.to_datetime(date)
            month_keys = str(pd_monthday.year)+'_'+str(pd_monthday.month)
            # 初始化
            if i==1:
                last_keys = month_keys
                year_month[month_keys] = []
            # 月份交替
            # 当前月份key不等于上一次月份key 即为月份交替
            if (month_keys != last_keys) or (i==length):
                # 一月有多少天，就得到多少个相同值的序列
                month_average = float('%.2f'%(month_totle/len(year_month[last_keys])))  # 月平均营业额
                gross_average = float('%.4f'%(gross_totle/month_totle))*100             # 月平均毛利率

                result_month_dict[last_keys] = month_average

                # 一月有多少天，就得到多少个相同值的序列
                for month_day in year_month[last_keys]:
                    result_list.append(month_average)
                    result_gross_list.append(gross_average)

                # 新月 计算数据清零
                year_month[month_keys] = []
                last_keys = month_keys
                month_totle = 0
                gross_totle = 0
            month_totle += day.turnover                 # 营业额累加
            gross_totle += day.gross_profit             # 毛利额累加
            year_month[month_keys].append(month_totle)  # 计数用，可知一个月有多少天

        self.turnover_month_average_data = result_list
        self.gross_month_average_data = result_gross_list
        self.turnover_month_average_dict = month_compare(result_month_dict)     # 月涨跌幅
