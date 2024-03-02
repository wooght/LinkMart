# coding=utf-8
# @Explain  : 文本替换
# @Author   : wooght
# @File     : honc_live store_list
# @Time     : 2019/12/21 下午2:25

replace_dict = {
    '5,0自然浑浊型小麦啤酒500ml': '5.0自然浑浊型小麦啤酒500ml',
    '统一阿萨姆奶茶原味': '统一阿萨姆 奶茶原味500ml',
}


# 执行替换操作
def str_replace(old_str):
    new_str = ''
    for key, value in replace_dict.items():
        old_str = old_str.replace(key, value)
    return old_str


# 获取模型字段列表
def get_model_fields(model):
    fields = [field.name for field in model._meta.get_fields()]
    return fields
