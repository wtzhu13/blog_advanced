# _*_ coding:UTF-8 _*_
# path:/home/tarena/桌面/study_file/...

"""
作者：朱文涛
邮箱：wtzhu_13@163.com

时间：2019/05
描述：
"""
from django.contrib import admin
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.users, name='users'),
    url(r'^/(?P<username>[\w]{1,11})$',
        views.users, name='user'),
    url(r'^/(?P<username>[\w]{1,11})/avatar$',
        views.user_avatar, name='user_avatar'),
]
