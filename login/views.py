from django.shortcuts import render, redirect   # redirect 模块切换
from django.contrib import auth     # django auth用户认证模块
from .forms import UserForm
from django.contrib import messages
from businessdata.models import store_list
from .models import UserInfo
# Create your views here.


# 登录页面
def login(request):
    return render(request, 'login.html', {'error': '请登录'})


# 执行登录
def login_verify(request):
    if request.method == 'POST':
        user_name = request.POST['user']
        user_password = request.POST['password']
        verify = auth.authenticate(username=user_name, password=user_password)  # 返回user_obj对象
        if verify:
            auth.login(request, verify)     # 执行登录，修改登录状态，设置session
            request.session['store_id'] = verify.store_id.id
        else:
            return render(request, 'login.html', {'error': '用户名或密码错误'})

    return redirect('/')


# 退出登录
def login_out(request):
    auth.logout(request)
    return redirect('/login')


# 注册用户
def register(request):
    if request.method == 'POST':
        userform = UserForm(request.POST)  # 数据验证

        if userform.is_valid():
            username = userform.cleaned_data['username']
            password = userform.cleaned_data['password']
            is_exists = UserInfo.objects.filter(username=username)
            if is_exists:
                messages.error(request, '用户已经存在', extra_tags='err_input')  # 消息组件，extra_tags 指携带的属性 如CSS样式
                return render(request, 'register.html')
            else:
                email = userform.cleaned_data['email']
                phone = userform.cleaned_data['phone']
                admin_type = request.POST.get('admin_type')
                if not admin_type:
                    admin_type = 1
                store_id = int(request.POST.get('store_id'))
                store = store_list.objects.filter(id=store_id)[0]
                user = UserInfo.objects.create_user(username=username, password=password, email=email, phone=phone,
                                                    admin_type=admin_type, store_id=store)
                # user.groups.set([2])  # 设置组别，多对多的关系
                user.save()
                return redirect('/login')
        else:
            messages.error(request, '信息填写不完整', 'err_input')  # 消息组件
            return render(request, 'register.html')
    else:
        stores = store_list.objects.all()  # 获取所有门店数据 供选择下拉列表使用
        return render(request, 'register.html', {'stores': stores})
