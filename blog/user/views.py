import hashlib
import time
import jwt
from django.shortcuts import render
from django.http import JsonResponse
import json
from btoken.views import make_token
from tools.logging_decorator import logging_check
from user.models import UserProfile
from . import models
# Create your views here.


@logging_check('PUT')
def users(request, username=None):
    if request.method == 'GET':
        # 取数据
        # /v1/users/***?info=1
        if username:
            try:
                user = UserProfile.objects.get(
                    username=username
                )
            except UserProfile.DoesNotExist:
                user = None
            if not user:
                result = {
                    'code': 208,
                    'error': 'The user is not exist'
                }
                return JsonResponse(result)
            if request.GET.keys():
                data = {}
                for k in request.GET.keys():
                    # 数据库中最好有默认值
                    if hasattr(user, k):
                        data[k] = getattr(user, k)
                result = {
                    'code': 200,
                    'username': username,
                    'data': data
                }
                return JsonResponse(result)
            else:
                # 证明指定查询用户全量数据
                result = {
                    'code': 200,
                    'username': username,
                    'data': {
                        'info': user.info,
                        'sign': user.sign,
                        'nickname': user.nickname,
                        'avatar': str(user.avatar)
                    }
                }
                return JsonResponse(result)
        else:
            # 全部用户数据
            all_users = UserProfile.objects.all()
            res = []
            for u in all_users:
                dic = {}
                dic['username'] = u.username
                dic['email'] = u.email
                res.append(dic)
            result = {
                'code': 200,
                'data': res
            }
            return JsonResponse(result)

    elif request.method == 'POST':
        # 注册用户
        json_str = request.body
        if not json_str:
            # 前端异常提交数据
            result = {'code': '202',
                      'error': 'Please POST'}
            return JsonResponse(result)
        # 序列化JSON字符串
        json_obj = json.loads(json_str)
        username = json_obj.get('username')
        email = json_obj.get('email')
        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')
        if not username:
            # 判断用户名是否为空
            result = {'code': 203,
                      'error': 'Please give name'}
            return JsonResponse(result)
        if not email:
            # 判断邮箱是否为空
            result = {'code': 204,
                      'error': 'Please give email'}
            return JsonResponse(result)
        if not password_1 or not password_2:
            # 判断两次密码是否有为空
            result = {'code': 205,
                      'error': 'Please give password'}
            return JsonResponse(result)
        if password_1 != password_2:
            # 判断两次密码是否一致
            result = {'code': 206,
                      'error': 'The password is wrong'}
            return JsonResponse(result)
        old_user = models.UserProfile.objects.filter(
            username=username
        )
        if old_user:
            # 判断用户名是否已存在s
            result = {
                'code': 207,
                'error': 'this username is existed'
            }
            return JsonResponse(result)
        # 对密码进行散列操作
        h = hashlib.sha1()
        h.update(password_1.encode())
        try:
            # 在数据库中创建用户
            models.UserProfile.objects.create(
                username=username,
                nickname=username,
                email=email,
                password=h.hexdigest(),
            )
        except Exception as e:
            # 创建异常则返回异常信息
            print('UserProfile create error i %s' % e)
            result = {
                'code': 207,
                'error': 'this username is existed'
            }
            return JsonResponse(result)
        # 创建成功则返回一个token信息
        token = make_token(username)
        result = {
            'code': 200,
            'username': username,
            'data': {'token': token.decode()}
        }
        return JsonResponse(result)
    elif request.method == 'PUT':
        # 修改用户数据
        # 'form enctype='
        # 前端返回的JSON格式{'nickname':****, 'sign':***, 'info':***}
        users = request.user
        json_str = request.body
        if not json_str:
            result = {
                'code': 202,
                'error': 'data null'
            }
            return JsonResponse(result)
        json_obj = json.loads(json_str)
        nickname = json_obj.get('nickname')
        if not nickname:
            # 昵称不能为空
            result = {
                'code': 209,
                'error': 'nickname is null'
            }
            return JsonResponse(result)
        sign = json_obj.get('sign', '')
        info = json_obj.get('info', '')
        # 存
        users.sign = sign
        users.info = info
        users.nickname = nickname
        users.save()

        result = {
            'code': 200,
            'username': username
        }
        return JsonResponse(result)

    return JsonResponse({'code': 200, 'data': {'username': 1}})


@logging_check('POST')
def user_avatar(request, username):
    # 上传图片思路
    # 1.前端-> form post 提交文件，并且content-type要改成multipart/form-data
    # 2.后端只要拿到post提交，request.FILES['avatar']
    # 注意：由于目前django获取put请求multipart数据较为复杂，古该为post请求
    if not request.method == 'POST':
        result = {'code': 210, 'error': 'Please use POST'}
        return JsonResponse(result)

    users = UserProfile.objects.filter(username=username)
    print(users)
    if not users:
        result = {'code': 208, 'error': 'The user is not existed !'}
        return JsonResponse(result)

    if request.FILES.get('avatar'):
        # 正常提交图片信息，进行存储
        users[0].avatar = request.FILES['avatar']
        users[0].save()
        result = {'code': 200, 'username': username}
        return JsonResponse(result)
    else:
        # 没有提交图片信息
        result = {'code': 211, 'error': 'Please give me avatar'}
        return JsonResponse(result)


