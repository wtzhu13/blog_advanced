# _*_ coding:UTF-8 _*_
# path:/home/tarena/桌面/study_file/...

"""
作者：朱文涛
邮箱：wtzhu_13@163.com

时间：2019/05
描述：
"""
from django.http import JsonResponse


def test_api(request):
    # JsonResponse 1将返回内容序列化成json
    #
    return JsonResponse({'code': 200})



