# coding=utf-8
# @Explain  : form 模块
# @Author   : wooght
# @File     : xyyp forms
# @Time     : 18-5-23 下午9:27


from django import forms


# 用户注册表单验证
class UserForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=32)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    phone = forms.CharField(label='电话', max_length=19, min_length=8)
    email = forms.EmailField(label='邮箱')
    store_id = forms.IntegerField(label='门店')