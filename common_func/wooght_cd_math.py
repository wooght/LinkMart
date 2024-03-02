# coding=utf-8
# @Explain  : 踩点数据计算
# @Author   : wooght
# @File     : honc_live wooght_math
# @Time     : 2023/06/01 上午11:45
from businessdata.models import cd_data


# 门店订单计算
def store_order_math(stores):
    # 营业时间对应比例 【7-23,24,7-01】
    is24h = [0.72, 1, 0.85]
    return_list = []
    # 遍历门店
    for item in stores:
        day_orders = item.store_orders
        # 如果门店数据无订单量，则表示需统计计算
        if day_orders == 0:
            # 查询门店踩点数据
            the_cd_data = cd_data.objects.filter(cd_store_id=item.id)
            the_total = 0
            contrast_total = 0
            # 两种思维
            # 1：每一次踩点数据算比例，然后比例求平均比例
            # 2：把每一次的踩点数据加起来，总和求比例
            # 目前来看，平均比例和实际比例差距较大，而总和求比例与实际差距较小
            # 踩点权重，高峰时段大于平静时段，
            for i in the_cd_data:
                # 踩点单量求和
                the_total += i.cd_orders
                # 对标单量求和
                contrast_total += i.contrast_orders
            # 日单量 = 踩点单量和/对标单量和×对标日单量*营业时间比例
            day_orders = int((the_total/contrast_total*item.contrast_orders*is24h[item.is_24h]) if contrast_total > 0 else 0)
        return_list.append({'store_name':item.store_name,'id':item.id,'cd_area':item.cd_area,'store_orders':day_orders,
                            'store_x':item.store_x,'store_y':item.store_y,'store_size':item.store_size,'cd_label':item.cd_label,
                            'door_header':item.door_header,'store_waiters': item.store_waiters})
    return return_list


# 商圈频率计算
def area_rate_math(area_list, store_list):
    new_areas = {}
    # 商圈字典化
    for item in area_list.values():
        new_areas[item['id']] = item
    # 遍历所有门店，将同一个商圈门店的订单量求和
    for store in store_list:
        if new_areas[store['cd_area']]['area_consumption_rate'] == 0.0:
            new_areas[store['cd_area']]['area_totle_orders'] += store['store_orders']
    # 计算商圈消费频率 频率=总人数/总单数   总人数=户数×户均人口×入住率+门店数量×门店均人口
    for item in new_areas.values():
        if item['area_consumption_rate'] == 0.0:
            totle_people = item['area_house']*item['home_peoples']*item['area_occ_rate']+item['area_stores']*5*item['stores_occ_rate']
            new_areas[item['id']]['area_consumption_rate'] = round(item['area_totle_orders']/totle_people, 2)
    return new_areas.values()