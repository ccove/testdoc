import os
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class UserPro(AbstractUser):
    gender = (
        ("1", "男"),
        ("0", "女")
    )
    sex = models.CharField(
        max_length=32,
        choices=gender,
        default="1",
        verbose_name="性别"
    )
    department = models.CharField(
        max_length=32,
        verbose_name="院系"
    )
    person = models.TextField(
        max_length=1024,
        null=True,
        verbose_name="个人信息"
    )

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["date_joined"]
        verbose_name = "所有用户"
        verbose_name_plural = "用户"


def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    return os.path.join("files", filename)


class files(models.Model):
    selvalue = (
        ('one', '教学资源'),
        ('two', '课程内容'),
        ('three', '学生作业'),
        ('four', '普通文档'),
        ('five', '其他文档'),
    )
    file_owner = models.ForeignKey(
        UserPro,
        on_delete=models.CASCADE,
        verbose_name="文档属主"
    )
    file_name = models.CharField(
        max_length=128,
        verbose_name="文档名称"
    )
    file_file = models.FileField(
        upload_to=user_directory_path,
        verbose_name="文档路径"
    )
    file_classify = models.CharField(
        choices=selvalue,
        default="five",
        max_length=32,
        verbose_name="文档分类"
    )
    file_format = models.CharField(
        null=True,
        max_length=32,
        verbose_name="文档格式"
    )
    file_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="上传时间"
    )
    file_delete = models.BooleanField(
        default=False,
        verbose_name="文档删除"
    )
    file_share = models.BooleanField(
        default=False,
        verbose_name="文档共享"
    )
    file_downloads = models.IntegerField(
        default=0,
        verbose_name="下载次数"
    )

    def __str__(self):
        return self.file_name

    class Meta:
        ordering = ["file_time"]
        verbose_name = "所有文档"
        verbose_name_plural = "文档"
