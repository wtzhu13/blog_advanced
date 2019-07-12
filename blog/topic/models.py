from django.db import models

# Create your models here.
# 做迁移操作时可以指定模块
# python3 manage.py makemigrations topic
# python3 manage.py migrate topic
from user.models import UserProfile


class Topic(models.Model):
    title = models.CharField(
        '题目', max_length=50
    )
    author = models.ForeignKey(UserProfile, on_delete='CASCADE')
    # tec:技术类  no-tec:非技术类
    category = models.CharField(
        '分类', max_length=20
    )
    # limit:  pubic - 公开的  private - 私有的
    limit = models.CharField('权限',
                             max_length=10)
    created_time = models.DateTimeField('创建时间')
    modified_time = models.DateTimeField('修改时间')
    content = models.TextField('博客内容')
    introduce = models.CharField('介绍', max_length=90)
    objects = models.Manager()

    class Meta:
        db_table = 'topic'


