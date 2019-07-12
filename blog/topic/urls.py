# _*_ coding:UTF-8 _*_
# path:/home/tarena/桌面/study_file/...

"""
作者：朱文涛
邮箱：wtzhu_13@163.com

时间：2019/05
描述：
"""
from . import views
from django.conf.urls import url

urlpatterns = [
    # /v1/topic/author_id   -index首页
    url(r'/(?P<author_id>[\w]+)$',
        views.topics, name='topics'),
    # url(r'/(?P<author_id>[\w]+)?',
    #     views.topics, name='topics')
]
