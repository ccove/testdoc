from django.contrib import admin
from .models import *
# Register your models here.

class UserProAdmin(admin.ModelAdmin):
    # 显示的字段
    list_display = ["username","email","department","sex","date_joined","last_login"]
    # 过滤条件
    list_filter = ["username","department"]
    # 分页数量
    list_per_page = 10
    # 搜索
    search_fields = ["username", "department","sex"]
    # 排序
    ordering = ["-date_joined"]

class FileAdmin(admin.ModelAdmin):
    # 显示的字段
    list_display = ["file_name","file_format","file_time","file_owner","file_downloads"]
    # 过滤条件
    list_filter = ["file_owner"]
    # 分页数量
    list_per_page = 10
    # 搜索
    search_fields = ["file_name","file_time"]
    # 排序
    ordering = ["-file_time"]


admin.site.register(UserPro,UserProAdmin)
admin.site.register(files,FileAdmin)
