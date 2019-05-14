# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-04-07 06:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_auto_20190407_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='files',
            name='file_classify',
            field=models.CharField(choices=[('one', '教学资源'), ('two', '课程内容'), ('three', '学生作业'), ('four', '普通文档'), ('其他文档', 'five')], default='five', max_length=32, verbose_name='文件分类'),
        ),
    ]
