from django.contrib import admin
from django.urls import path
from businessdata import views as busd_view
from businessdata import apis as api
from login import views as login_view

urlpatterns = [
    # 营业数据
    path('', busd_view.index),
    path('/<int:store_id>', busd_view.index),
    path('upload_form', busd_view.upload_form),
    path('new_store', busd_view.new_store),
    path('add_new_store', busd_view.add_new_store),
    path('goods_list', busd_view.goods_list_page),
    path('goods_form/<int:goods_id>', busd_view.goods_form),
    path('add_stock/<str:goods_code>/<str:store_id>/<int:stock_type>', busd_view.add_stock),
    path('stock_list', busd_view.stock_list),
    path('stock_list/<int:stock_type>', busd_view.stock_list),
    path('stock_list/<int:stock_type>/<int:store_id>', busd_view.stock_list),
    path('goods_quality_add/<int:goods_id>', busd_view.goods_quality_add),
    path('goods_quality_save', busd_view.goods_quality_save),
    path('quality_list', busd_view.quality_list),
    path('quality_list/<int:store_id>', busd_view.quality_list),
    path('classify_page', busd_view.classify_page),
    # 运营数据
    path('operate', busd_view.operate),
    path('operate/<int:store_id>', busd_view.operate),

    # 功能模块
    path('barcodeprint', busd_view.barcodeprint),
    path('barcode_toprint', busd_view.barcode_toprint),

    # 地图模块
    path('map', busd_view.show_map),                                            # 展示地图
    path('save_cd_area', busd_view.save_cd_area),                               # 执行添加踩点商圈
    path('save_cd_store', busd_view.save_cd_store),                             # 执行添加门店
    path('save_cd_data', busd_view.save_cd_data),                               # 添加踩点数据

    # api
    path('upload_xls', api.upload_xls),                                     # 上传数据
    path('stock_state/<int:id>', api.stock_state),                          # 改变进货补货状态
    path('quality_state/<int:id>', api.quality_state),                      # 改变保质状态
    path('day_sales_trend', api.day_sales_trend),                           # 获一天24小时数据趋势
    path('classify_sales_ratio', api.classify_sales_ratio),                 # 获取类别比例
    path('smoke_water_ratio', api.smoke_water_ratio),                       # 烟，水占比
    path('one_classify_sales', api.one_classify_sales),                     # 某类别销量情况
    path('data_update/<int:store_id>/<str:up_type>', api.data_update),      # 通过爬虫更新数据
    path('stock_exists/<int:id>', api.stock_exists),                        # 询问库存状态
    path('totle_forms', api.totle_forms),                                   # 单数及单价
    path('one_good/<int:id>', api.one_good),                                # 单个商品数据
    path('save_operate', api.save_operate),                                 # 保存运营数据
    path('get_operate_data', api.get_operate_data),                         # 获取运营数据
    path('get_status', api.get_status),                                     # 获取上传数据状态

    # 踩点API
    path('get_cd_stores/<int:id>', api.get_cd_stores),                      # 获取单个门店信息
    path('get_cd_stores', api.get_cd_stores),                               # 获取门店列表
    path('get_cd_data/<int:id>', api.get_cd_data),                          # 获取踩点数据列表
    path('to_save_cd_data',api.to_save_cd_data),                            # 踩点数据提交
    path('get_one_cd_store/<int:id>',api.get_one_cd_store),                 # 获取单个踩点门店数据
    path('to_update_store', api.to_update_store),                           # 执行踩点门店修改
    # path('get_label_list', api.get_label_list),                             # 获取门店标签列表

    # 登录
    path('login', login_view.login),
    path('login_verify', login_view.login_verify),
    path('login_out', login_view.login_out, name='login_out'),
    path('register', login_view.register, name='register'),
    # path('verify_code', caijing_api.verification_code, name='verify_code'),
]
