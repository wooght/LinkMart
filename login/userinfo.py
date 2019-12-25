from django.db import models
from django.contrib.auth.models import AbstractUser
from businessdata.models import store_list


# Create your models here.


# 扩展用户表
class userinfo(AbstractUser, models.Model):
    nid = models.AutoField(primary_key=True)
    store_id = models.ForeignKey(store_list, on_delete=models.CASCADE)  # 所在门店id
    admin_type = models.IntegerField(default=2)  # 管理员类型 1管理员 2普通用户
    phone = models.CharField(max_length=64, blank=True)
    create_date = models.DateTimeField(verbose_name='创建实际', auto_now_add=True)


#
# # 信号传递 创建user的同时，创建profile
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         profile.objects.create(user=instance)
