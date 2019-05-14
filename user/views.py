from time import sleep
import os
import execjs
from django.conf import settings
import random
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from django.core.paginator import EmptyPage
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse, Http404
from django.shortcuts import render, redirect

from .forms import FileUploadForm
from .models import *


PER_PAGE = 10
# 登陆
def Login(req):
    if req.method == "GET":
        return render(req,'login.html')
    else:
        params = req.POST
        name = params.get("name")
        pwd = params.get("pwd")
        # 认证
        user = authenticate(username = name,password=pwd)
        # 判断是否验证成功
        if user:
            login(req, user)
            return redirect('/user/index',locals())
        else:
            message = "账号或密码输入有误，请重新输入！"
            return render(req,'login.html',locals())

# 注册
def Register(req):
    if req.method == "GET":
        return render(req,'register.html')
    else:
        params = req.POST
        username = params.get("name")
        password1 = params.get("pwd1")
        password2 = params.get("pwd2")
        email = params.get("email")
        department = params.get("department")
        sex = params.get("sex")
        if username and password1 and password2 and email and department:
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同,请重新输入！"
                return render(req, 'register.html', locals())
            else:
                same_email_user = UserPro.objects.filter(email=email)
                same_name_user = UserPro.objects.filter(username=username)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请重新输入邮箱！'
                    return render(req, 'register.html', locals())
                if same_name_user:  # 姓名唯一
                    message = '该姓名已被注册，请重新输入姓名！'
                    return render(req, 'register.html', locals())
                    #当一切都OK的情况下，创建新用户
                UserPro.objects.create_user(username=username,password=password2,email=email,department=department,sex=sex)
                # ctx = execjs.compile( '''
                #     function add(){
                #     alert('注册成功')
                #     }
                # ''').eval

                return redirect('/user/login',locals())  # 自动跳转到登录页面
        else:
            message = "请填入所有必填项！"
            return render(req, 'register.html', locals())

# 找回密码
def Find_pwd(req):
    if req.method == "GET":
        return render(req,'find_pwd.html')
    else:
        params = req.POST
        email = params.get("email")
        if not UserPro.objects.filter(email=email):
            message = "该邮箱账号不存在，请重新输入！"
            return render(req,"find_pwd.html",locals())
        num = random.randrange(100000, 1000000)
        template = loader.get_template("findpwd_verify.html")
        html = template.render({"title": "教学文档管理系统", "verify_code": num})
        title = "教学文档管理系统"
        receivers = [
            email
        ]
        email_from = settings.DEFAULT_FROM_EMAIL
        send_mail(title, "", email_from, receivers, html_message=html)
        user = UserPro.objects.get(email=email)
        user.set_password(num)
        user.save()
        # 设置缓存
        # cache.set(email,num, settings.VERIFY_CODE_MAX_AGE)
        return redirect('/user/login',locals())

# 重设密码
@login_required
def Reset(req):
    user = req.user
    if req.method == "GET":
        return render(req,'reset.html')
    else:
        params = req.POST
        old_password = params.get("old_pwd")
        newpassword1 = params.get("newpwd1")
        newpassword2 = params.get("newpwd2")

        if user.check_password(old_password):
            if not newpassword1:
                message = "新密码不能为空！"
                return render(req, "reset.html", locals())
            if newpassword1 != newpassword2:
                message = "您两次输入的密码不同，请重新输入！"
                return render(req, "reset.html", locals())
            else:
                user.set_password(newpassword1)
                user.save()
                message = "密码更改成功，请牢记新的密码，正在跳转至登陆界面..."
                return redirect("/user/login",locals())
        else:
            message = "您输入的旧密码或临时密码错误！"
            return render(req,"reset.html",locals())

# 退出登陆
def Logout(req):
    logout(req)
    return redirect('/user/login')

# 首页
@login_required
def Index(req):
    user = req.user

    file = files.objects.filter(file_owner__username=user.username, file_delete=False).order_by("-id")
    page_num = req.GET.get("page", 1)
    paginator = Paginator(file, PER_PAGE)
    page = None
    try:
        page = paginator.page(page_num)
        result = page.object_list
    except:
        result = []
    res = {
        "files": result,
        "page_range": paginator.page_range,
        "page":page,
        "page_count":paginator.num_pages, # 总页码
    }
    if user:
        req.session["is_login"] = True
        req.session["user_name"] = user.username
        req.session["user_id"] = user.id
        print(user.username)

    return render(req, 'index.html', res)

# 上传文档
def file_upload(req):
    user = req.user
    if req.method == "POST":
        form = FileUploadForm(req.POST, req.FILES)
        if form.is_valid():
            # get cleaned data
            filename = form.cleaned_data.get("file_name")
            raw_file = form.cleaned_data.get("file")
            classify = req.POST.get("file_classify")
            print(classify)
            file_format = raw_file.name.split(".")[-1]
            file_name = filename + "." + raw_file.name.split(".")[-1]
            new_file = files.objects.create(
                file_owner=user,
                file_name=file_name,
                file_file=handle_uploaded_file(raw_file),
                file_classify=classify,
                file_format=file_format
            )
            new_file.save()
            return redirect("/user/show")
    else:
        form = FileUploadForm()
        return render(req, 'upload_form.html', {'form': form,'heading': '文档上传'})

# 上传文件的路径
def handle_uploaded_file(file):
    ext = file.name.split('.')[-1]
    file_name = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    # file path relative to 'media' folder
    file_path = os.path.join('files', file_name)
    absolute_file_path = os.path.join('media', 'files', file_name)

    directory = os.path.dirname(absolute_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(absolute_file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return file_path

# 下载文件
def file_download(req,file_path):
    file_name = "files/" + file_path.split('/')[-1]
    file = files.objects.get(file_file=file_name)
    # 当点击下载时 ，下载次数加一
    file.file_downloads += 1
    file.save()
    try:
        response = FileResponse(open(file_path, 'rb'))
        response['content_type'] = "application/octet-stream"
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
        return response
    except Exception:
        raise Http404

# 全部文档
@login_required
def file_list(req):
    user = req.user
    file = files.objects.filter(file_owner__username=user.username,file_delete=False).order_by("-id")
    page_num = req.GET.get("page", 1)
    paginator = Paginator(file, PER_PAGE)
    page = None
    try:
        page = paginator.page(page_num)
        result = page.object_list
    except:
        result = []
    res = {
        "files": result,
        "page_range": paginator.page_range,
        "page":page,
        "page_count":paginator.num_pages, # 总页码
    }
    return render(req, 'file_list.html', res)

# 教学资源one
@login_required
def one(req):
    user = req.user
    file = files.objects.filter(file_owner__username=user.username,file_classify="one",file_delete=False).order_by("-id")
    page_num = req.GET.get("page", 1)
    paginator = Paginator(file, PER_PAGE)
    page = None
    try:
        page = paginator.page(page_num)
        result = page.object_list
    except:
        result = []
    res = {
        "files": result,
        "page_range": paginator.page_range,
        "page":page,
        "page_count":paginator.num_pages, # 总页码
    }
    return render(req, 'doc_one.html', res)

# 课程内容two
def two(req):
    user = req.user
    file = files.objects.filter(file_owner__username=user.username,file_classify="two",file_delete=False).order_by("-id")
    page_num = req.GET.get("page", 1)
    paginator = Paginator(file, PER_PAGE)
    page = None
    try:
        page = paginator.page(page_num)
        result = page.object_list
    except:
        result = []
    res = {
        "files": result,
        "page_range": paginator.page_range,
        "page":page,
        "page_count":paginator.num_pages, # 总页码
    }
    return render(req, 'doc_two.html', res)

# 学生作业three
def three(req):
    user = req.user
    file = files.objects.filter(file_owner__username=user.username,file_classify="three",file_delete=False).order_by("-id")
    page_num = req.GET.get("page", 1)
    paginator = Paginator(file, PER_PAGE)
    page = None
    try:
        page = paginator.page(page_num)
        result = page.object_list
    except:
        result = []
    res = {
        "files": result,
        "page_range": paginator.page_range,
        "page":page,
        "page_count":paginator.num_pages, # 总页码
    }
    return render(req, 'doc_three.html',res)

# 普通文档four
def four(req):
    user = req.user
    file = files.objects.filter(file_owner__username=user.username,file_classify="four",file_delete=False).order_by("-id")
    page_num = req.GET.get("page", 1)
    paginator = Paginator(file, PER_PAGE)
    page = None
    try:
        page = paginator.page(page_num)
        result = page.object_list
    except:
        result = []
    res = {
        "files": result,
        "page_range": paginator.page_range,
        "page":page,
        "page_count":paginator.num_pages, # 总页码
    }
    return render(req, 'doc_four.html', res)

# 其他文档five
def five(req):
    user = req.user
    file = files.objects.filter(file_owner__username=user.username,file_classify="five",file_delete=False).order_by("-id")
    page_num = req.GET.get("page", 1)
    paginator = Paginator(file, PER_PAGE)
    page = None
    try:
        page = paginator.page(page_num)
        result = page.object_list
    except:
        result = []
    res = {
        "files": result,
        "page_range": paginator.page_range,
        "page":page,
        "page_count":paginator.num_pages, # 总页码
    }
    return render(req, 'doc_five.html',res)

# 共享文件
@login_required
def file_share(req,id):
    user = req.user
    file = files.objects.get(id = id)
    file.file_share = True
    file.save()
    return redirect("/user/me_share")

# 取消共享
@login_required
def file_share_cacle(req,id):
    user = req.user
    print(id)
    file = files.objects.get(id = id)
    file.file_share = False
    file.save()
    return redirect("/user/me_share")

# 所有共享
@login_required
def file_all_share(req):
    user = req.user
    file = files.objects.filter(file_share=True).order_by("-id")
    page_num = req.GET.get("page", 1)
    paginator = Paginator(file, PER_PAGE)
    page = None
    try:
        page = paginator.page(page_num)
        result = page.object_list
    except:
        result = []
    res = {
        "files": result,
        "page_range": paginator.page_range,
        "page":page,
        "page_count":paginator.num_pages, # 总页码
    }
    return render(req,'all_share.html',res)
# 我的共享
@login_required
def file_me_share(req):
    user = req.user
    file = files.objects.filter(file_owner__username=user.username, file_share=True).order_by("-id")
    page_num = req.GET.get("page", 1)
    paginator = Paginator(file, PER_PAGE)
    page = None
    try:
        page = paginator.page(page_num)
        result = page.object_list
    except:
        result = []
    res = {
        "files": result,
        "page_range": paginator.page_range,
        "page":page,
        "page_count":paginator.num_pages, # 总页码
    }
    return render(req,'me_share.html',res)


# 回收站
@login_required
def file_recycle(req):
    user = req.user
    file = files.objects.filter(file_owner__username=user.username, file_delete=True).order_by("-id")
    page_num = req.GET.get("page", 1)
    paginator = Paginator(file, PER_PAGE)
    page = None
    try:
        page = paginator.page(page_num)
        result = page.object_list
    except:
        result = []
    res = {
        "files": result,
        "page_range": paginator.page_range,
        "page":page,
        "page_count":paginator.num_pages, # 总页码
    }
    return render(req,'recycle.html',res)

# 删除文档
@login_required
def file_delete(req,id):
    user = req.user
    file = files.objects.get(id = id)
    file.file_delete = True
    file.file_share = False
    file.save()
    return redirect("/user/recycle")

# 还原文档
@login_required
def file_recover(req,id):
    user = req.user
    file = files.objects.get(id = id)
    file.file_delete = False
    file.save()
    return redirect("/user/recycle")
# 个人信息
@login_required
def person(req):
    user = req.user
    if req.method == "GET":
        name1 = user.username
        email1 = user.email
        department1 = user.department
        sex1 = user.sex
        per1 = user.person
        print(sex1)
        return render(req, "person.html", locals())
    else:
        params = req.POST
        name = params.get("username")
        email = params.get("email")
        dep = params.get("dep")
        sex = params.get("sex")
        per = params.get("per")
        print(sex)

        user.username = name
        user.email = email
        user.department = dep
        user.sex = sex
        user.person = per
        user.save()

        name1 = user.username
        email1 = user.email
        department1 = user.department
        sex1 = user.sex
        per1 = user.person
        return render(req, "person.html", locals())


# 搜索
def serach(req):
    user = req.user
    params = req.GET.get("keyword")
    file = files.objects.filter(file_owner__username=user.username,file_name__icontains=params,file_delete=False)
    page_num = req.GET.get("page", 1)
    paginator = Paginator(file, PER_PAGE)
    page = None
    try:
        page = paginator.page(page_num)
        result = page.object_list
    except:
        result = []
    res = {
        "files": result,
        "page_range": paginator.page_range,
        "page":page,
        "page_count":paginator.num_pages, # 总页码
        "keyword":params
    }
    return render(req, 'result.html',res)





