# _*_ coding:UTF-8 _*_
# path:/home/tarena/桌面/study_file/...

"""
作者：朱文涛
邮箱：wtzhu_13@163.com

时间：2019/05
描述：
"""
import jwt
from django.http import JsonResponse
from user.models import UserProfile

KEY = 'abcdef1234'


def logging_check(*methods):
    def _logging_check(func):
        def wrapper(request, *args, **kwargs):
            # token 放在 request header -> authorization
            # token = request.META.get('HTTP_AUTHORIZATION')
            token = request.META.get('HTTP_AUTHORIZATION')
            if not methods:
                # 没有上传Method参数，则直接返回视图
                return func(request, *args, **kwargs)

            # method有值
            if request.method not in methods:
                # 如果当前的请求方法不在Method内，则直接返回视图
                return func(request, *args, **kwargs)
            # 严格检查参数大小写，统一大写
            # 严格检查Method里的参数是POST, GET, PUT, DELETE
            # 判断当前method是否在*Method参数中，如果在则进行token校验
            if not token or token == 'null':
                result = {
                    'code': 107,
                    'error': 'please give me token'
                }
                return JsonResponse(result)

            # 校验token, pyjwt 注意异常检测
            try:
                res = jwt.decode(token, KEY, algorithms='HS256')
            except jwt.ExpiredSignatureError:
                result = {
                    'code': 108,
                    'error': 'please login'
                }
                return JsonResponse(result)
            except Exception as e:
                print('error is %s' % e)
                result = {
                    'code': 108,
                    'error': 'please login'
                }
                return JsonResponse(result)
            # token  校验成功，根据用户名取出用户
            username = res['username']
            user = UserProfile.objects.get(username=username)
            # request.user = user
            request.user = user
            return func(request, *args, **kwargs)
        return wrapper
    return _logging_check


def get_user_by_request(request):
    """
        通过request获取用户
    :param request:
    :return:
    """
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token or token == 'null':
        # 判断是否携带token
        return None
    # 教研token
    try:
        res = jwt.decode(token, KEY, algorithms='HS256')
    except Exception as e:
        print(e)
        return None
    # token  校验成功，根据用户名取出用户
    username = res['username']
    user = UserProfile.objects.get(username=username)
    return user





