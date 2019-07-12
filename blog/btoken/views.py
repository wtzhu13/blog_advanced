import hashlib
import json
import time

import jwt
from django.http import JsonResponse
from django.shortcuts import render
from user.models import UserProfile

# Create your views here.


def btoken(request):
    # 验证登录
    # 判断是否为post请求
    if not request.method == 'POST':
        result = {'code': 101,
                  'error': 'Please use post'}
        return JsonResponse(result)
    json_str = request.body
    # 判断是否有数据穿过来
    if not json_str:
        result = {'code': 102,
                  'error': 'Please post data'}
        return JsonResponse(result)
    json_obj = json.loads(json_str)
    username = json_obj.get('username')
    password = json_obj.get('password')
    if not username:
        # 判断用户名是否传过来
        result = {'code': 103,
                  'error': 'Please give username'}
        return JsonResponse(result)
    if not password:
        # 判断密码是否传过来
        result = {'code': 104,
                  'error': 'Please give password'}
        return JsonResponse(result)
    # 通过用户名搜索数据库
    users = UserProfile.objects.filter(username=username)
    if not users:
        # 判断用户是否存在
        result = {
            'code': 105,
            'error': 'The user is not existed'
        }
        return result
    # 散列密码
    p_m = hashlib.sha1()
    p_m.update(password.encode())
    # 判断密码是否正确
    if p_m.hexdigest() != users[0].password:
        result = {
            'code': 106,
            'error': 'The username or password error'
        }
        return JsonResponse(result)
    token = make_token(username)
    result = {
        'code': 200,
        'username': username,
        'data': {
            'token': token.decode()
        }
    }
    return JsonResponse(result)


def make_token(username, expire=3600*24):
    """
        生成token
    :param username:
    :param expire:
    :return:
    """
    key = 'abcdef1234'
    now_t = time.time()
    payload = {
        'username': username,
        'exp': int(now_t+expire)
    }
    return jwt.encode(payload, key, algorithm='HS256')
