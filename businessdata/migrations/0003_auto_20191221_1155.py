# Generated by Django 2.0.5 on 2019-12-21 11:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('businessdata', '0002_auto_20191221_1150'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goods_quality',
            name='goods_id',
        ),
        migrations.RemoveField(
            model_name='stock_width_goods',
            name='store_id',
        ),
    ]
