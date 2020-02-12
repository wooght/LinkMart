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

    # api
    path('upload_xls', api.upload_xls),  # 上传数据
    path('stock_state/<int:id>', api.stock_state),                          # 改变进货补货状态
    path('quality_state/<int:id>', api.quality_state),                      # 改变保质状态
    path('day_sales_trend', api.day_sales_trend),                           # 获一天24小时数据趋势
    path('classify_sales_ratio', api.classify_sales_ratio),                 # 获取类别比例
    path('one_classify_sales', api.one_classify_sales),                     # 某类别销量情况
    path('data_update/<int:store_id>/<str:up_type>', api.data_update),      # 通过爬虫更新数据
    path('stock_exists/<int:id>', api.stock_exists),                        # 询问库存状态

    # 登录
    path('login', login_view.login),
    path('login_verify', login_view.login_verify),
    path('login_out', login_view.login_out, name='login_out'),
    path('register', login_view.register, name='register'),
    # path('verify_code', caijing_api.verification_code, name='verify_code'),
]
