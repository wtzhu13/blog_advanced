from django.db import models

# Create your models here.
from topic.models import Topic
from user.models import UserProfile


class Message(models.Model):
    topic = models.ForeignKey(Topic, on_delete='CASCADE')
    content = models.CharField('留言', max_length=60)
    created_time = models.DateTimeField('留言时间')
    parent_message = models.IntegerField('父留言', null=True)
    # UserProfile外键
    publisher = models.ForeignKey(UserProfile, on_delete='CASCADE')
    objects = models.Manager()

    class Meta:
        db_table = 'message'











