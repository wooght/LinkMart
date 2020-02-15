from django.db import models


# 营业数据测试表
class huayu_businessdata(models.Model):
    date = models.DateField(null=False, db_index=True)
    cost = models.FloatField()
    turnover = models.FloatField()
    gross_profit = models.FloatField()

    def __str__(self):
        return self.date

    class Meta:
        db_table = 'huayu_businessdata'
        verbose_name_plural = '营业数据'


# 门店列表
class store_list(models.Model):
    name = models.TextField(null=False)
    adds = models.TextField(null=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'store_list'
        verbose_name_plural = '门店列表'


# 营业数据
# 以每天为最小单位
class bs_data(models.Model):
    date = models.DateField(null=False, db_index=True)
    cost = models.FloatField()  # 成本
    turnover = models.FloatField()  # 营业额
    gross_profit = models.FloatField()  # 毛利
    store_id = models.ForeignKey(store_list, on_delete=models.CASCADE, db_column='store_id')  # 定义外键关系 db_column指字段名

    def __str__(self):
        return self.date

    class Meta:
        db_table = 'bs_data'
        verbose_name_plural = '营业数据'


# 商品列表
class goods_data(models.Model):
    name = models.CharField(null=False, max_length=64)  # 名称
    bar_code = models.CharField(null=False, db_index=True, max_length=32)  # 条码
    store_id = models.ForeignKey(store_list, on_delete=models.CASCADE, db_column='store_id')  # 门店ID
    qgp = models.IntegerField(default=0)     # quality guarantee period 保质期

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'goods_data'
        verbose_name_plural = '商品数据'


# 商品列表
# 商品数据
class goods_list(models.Model):
    name = models.CharField(null=False, max_length=64)  # 名称
    bar_code = models.CharField(null=False, db_index=True, max_length=32)  # 条码
    classify = models.CharField(max_length=32)   # 分类
    cost = models.FloatField()  # 成本
    stock_nums = models.IntegerField()  # 库存
    store_id = models.ForeignKey(store_list, on_delete=models.CASCADE, db_column='store_id')  # 门店ID
    qgp = models.IntegerField(default=0)     # quality guarantee period 保质期

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'goods_list'
        verbose_name_plural = '商品列表'


# 订单列表
# 订单数据，销售记录
# 考虑数量较多，门店ID没有建立外键
class order_form(models.Model):
    form_code = models.CharField(max_length=32)     # 订单号
    goods_name = models.CharField(max_length=64)     # 商品名称
    goods_code = models.CharField(max_length=64)    # 商品条码
    goods_num = models.IntegerField()   # 商品数量
    goods_money = models.FloatField()   # 商品金额
    form_date = models.DateField()  # 结账提起
    form_time = models.TimeField()  # 结账时间
    form_money = models.FloatField()    # 订单金额
    form_money_true = models.FloatField()   # 实际金额
    store_id = models.IntegerField()    # 门店ID

    def __str__(self):
        return self.goods_name

    class Meta:
        db_table = 'order_form'
        verbose_name_plural = '订单列表'


# 进货单-补货单
# 设置状态 1未处理  2已完成    3观察/等待
# 设置门店
class stock_width_goods(models.Model):
    goods_code = models.CharField(max_length=32, db_index=True)    # 商品条码
    goods_id = models.ForeignKey(goods_list, on_delete=models.CASCADE, db_column='goods_id', default=1)    # 对应商品ID 外键与商品表
    store_id = models.IntegerField(null=False)    # 门店ID
    state = models.IntegerField(default=1)   # 进货状态
    stock_type = models.IntegerField()  # 类型-》1进货，2为补货
    add_date = models.DateField()   # 添加时间

    def __str__(self):
        return self.goods_code

    class Meta:
        db_table = 'stock_width_goods'
        verbose_name_plural = '订货单'


# 保质期检查单
# 记录保质期检查时库存
class goods_quality(models.Model):
    goods_code = models.CharField(max_length=32, db_index=True)
    goods_id = models.ForeignKey(goods_list, on_delete=models.CASCADE, db_column='goods_id', default=1)
    stock_nums = models.IntegerField(default=2)     # 当前库存
    date_nums = models.IntegerField(default=30)     # 剩余保质天数
    add_date = models.DateField()   # 添加时间
    state = models.IntegerField(max_length=2, default=1)   # 处理状态 1未处理 2销售/报损完毕 3处理警报
    store_id = models.IntegerField(null=False)    # 门店ID

    def __str__(self):
        return self.goods_code

    class Meta:
        db_table = 'goods_quality'
        verbose_name_plural = '保质期检查单'