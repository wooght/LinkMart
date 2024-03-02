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
    price = models.FloatField(null=True,max_length=32)  # 售价
    classify = models.CharField(max_length=32)   # 分类
    cost = models.FloatField()  # 成本
    stock_nums = models.IntegerField()  # 库存
    store_id = models.ForeignKey(store_list, on_delete=models.CASCADE, db_column='store_id')  # 门店ID
    qgp = models.IntegerField(default=0)     # quality guarantee period 保质期
    place = models.CharField(max_length=64)     # 产地
    company = models.CharField(max_length=64)   # 单位

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


# 踩点区域表
# create table if not exists cd_area(
# id int not null auto_increment,
# area_name varchar(32) not null,
# area_house int(5) not null,
# area_peoples int(5) default 0,
# area_occ_rate float(5),
# area_stores int(5),
# stores_occ_rate float(5),
# area_consumption_rate float(5) default 0.0,
# area_totle_orders int(5) default 0.0,
# area_x double,
# area_y double,
# PRIMARY KEY (id))ENGINE=InnoDB CHARSET=utf8;
class cd_area(models.Model):
    area_name = models.CharField()                                  # 区域名称
    area_house = models.IntegerField(max_length=5, null=False)      # 户数
    home_peoples = models.FloatField(default=0.25)                  # 户均人数
    area_peoples = models.IntegerField(max_length=5)                # 区域人数
    area_occ_rate = models.FloatField(max_length=5)                 # 入住率
    area_stores = models.IntegerField(max_length=5)                 # 门店数量
    stores_occ_rate = models.FloatField(max_length=5)               # 门店入住率
    area_consumption_rate = models.FloatField(max_length=5)         # 消费概率
    area_totle_orders = models.IntegerField(max_length=5)           # 订单量
    area_x = models.FloatField()                                    # x坐标
    area_y = models.FloatField()                                    # y坐标

    def __str__(self):
        return self.area_name

    class Meta:
        db_table = 'cd_area'
        verbose_name_plural = '踩点区域表'


# 踩点门店表
# create table if not exists cd_store(
# id int not null auto_increment,
# store_name varchar(32) not null,
# cd_area int(4) not null,
# store_x double not null,
# store_y double not null,
# is_24h int(4) not null default 1,
# is_smoke int(4) not null default 1,
# store_orders int(4) not null default 0,
# store_turnover int(4) not null default 0,
# contrast_orders int(4) not null default 0,
# store_size int(4) not null default 0,
# store_waiters int(4) not null default 0,
# door_header float(4) not null default 0,
# PRIMARY KEY(id))ENGINE=InnoDB CHARSET=utf8;
class cd_store(models.Model):
    store_name = models.CharField(null=False)                                 # 门店名称
    cd_area = models.IntegerField(null=False)                                 # 所属商圈
    store_x = models.FloatField(null=False)                                   # x坐标
    store_y = models.FloatField(null=False)                                   # y坐标
    is_24h = models.IntegerField(null=False)                                  # 是否24小时
    is_smoke = models.IntegerField(default=1)                                 # 是否有烟
    store_orders = models.IntegerField(default=0, null=False)                 # 门店订单量
    store_turnover = models.IntegerField(default=0)                           # 预估营业额
    contrast_orders = models.IntegerField()                                   # 对标门店单数
    cd_label = models.CharField()                                             # 门店标签

    store_size = models.IntegerField(default=0)                               # 门店面积
    store_waiters = models.IntegerField(default=0)                            # 店员数量
    door_header = models.FloatField(default=0)                                # 门头宽度

    def __str__(self):
        return self.store_name

    class Meta:
        db_table = 'cd_store'
        verbose_name_plural = '踩点门店表'


# 踩点数据表
# create table if not exists cd_data(
# id int not null auto_increment,
# cd_store_id int(4) not null,
# cd_orders int(4) not null,
# contrast_orders int(4) not null,
# contrast_total_orders int(4) not null default 0,
# home_orders int(4) default 0,
# business_orders int(4) default 0,
# apartment_orders int(4) default 0,
# road_orders int(4) default 0,
# PRIMARY KEY (id))ENGINE=InnoDB CHARSET=utf8;
class cd_data(models.Model):
    cd_store_id = models.IntegerField(max_length=5, null=False)             # 门店ID
    cd_orders = models.IntegerField(max_length=5, null=False)               # 踩点时间段订单量
    contrast_orders = models.IntegerField(max_length=5, null=False)         # 对标门店时间段订单量
    contrast_total_orders = models.IntegerField(max_length=5, null=False)   # 对标门店当日总订单量

    home_orders = models.IntegerField(max_length=5, default=0)              # 住宅提供订单数
    business_orders = models.IntegerField(max_length=5, default=0)          # 商业提供订单数
    apartment_orders = models.IntegerField(max_length=5,default=0)          # 公寓提供订单数
    road_orders = models.IntegerField(max_length=5, default=0)              # 路人提供订单数
    cd_date = models.DateField()                                            # 踩点日期
    cd_stime = models.TimeField()                                           # 踩点时间

    def __str__(self):
        return self.cd_orders

    class Meta:
        db_table = 'cd_data'
        verbose_name_plural = '踩点数据表'


#  门店属性标签
# create table if not exists cd_label(
# id int not null auto_increment,
# label_name varchar(32) not null,
# label_score int(4) not null default 100,
# label_notes varchar(128) not null default '备注/解释',
# label_type int(2) not null default 1,
# PRIMARY KEY (id))ENGINE=InnoDB CHARSET=utf8;
class cd_label(models.Model):
    id = models.IntegerField()                  # ID
    label_name = models.CharField(max_length=32, null=False)                        # 标签名称
    label_score = models.IntegerField(max_length=4, null=False, default=100)        # 标签权重
    label_notes = models.CharField(default='备注/解释')                              # 标签备注/解释
    label_type = models.IntegerField(max_length=2, null=False, default=1)           # 标签类型。默认1 正面 -1未负面影响
    f_id = models.IntegerField(default=0)                                           # 父级ID

    def __str__(self):
        return self.label_name

    class Meta:
        db_table = 'cd_label'
        verbose_name_plural = '门店标签'


# 运营表
class operate_data(models.Model):
    # 属性
    store_id = models.IntegerField(max_length=2, null=False)        # 门店ID
    y_month = models.IntegerField(max_length=8, null=False)         # 月份
    # 收入
    profit = models.FloatField(max_length=8)                        # 利润
    income = models.FloatField(max_length=8)                        # 收入
    # 支出
    wages = models.FloatField(max_length=8)                         # 工资
    insurance = models.FloatField(max_length=8)                     # 社保
    meituan = models.FloatField(max_length=8)                       # 美团
    rent = models.FloatField(max_length=8)                          # 租金
    hydropower = models.FloatField(max_length=8)                    # 水电
    expenditure = models.FloatField(max_length=8)                   # 开支
    loss = models.FloatField(max_length=8)                          # 损耗
    # 财产
    stock = models.FloatField(max_length=8, default=0)                         # 库存
    assets = models.FloatField(max_length=8, default=0)                        # 资产

    def __str__(self):
        return self.store_id

    class Meta:
        db_table = 'operate'
        verbose_name_plural = '运营数据'