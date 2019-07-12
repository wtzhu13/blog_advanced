import datetime
import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from comment.models import Message
from tools.logging_decorator import logging_check
from topic.models import Topic


@logging_check('POST')
def messages(request, topic_id):
    if request.method == 'POST':
        user = request.user
        json_str = request.body
        print(json_str)
        if not json_str:
            result = {
                'code': 402,
                'error': 'Please give me json str'
            }
            return JsonResponse(result)
        json_obj = json.loads(json_str)
        content = json_obj.get('content')
        parent_id = json_obj.get('parent_id', 0)
        if not content:
            result = {
                'code': 403,
                'error': 'Please give me content'
            }
            return JsonResponse(result)
        now = datetime.datetime.now()
        try:
            topic = Topic.objects.get(id=topic_id)
        except Exception as e:
            print(e)
            result = {
                'code': 404,
                'error': 'this topic is not existed'
            }
            return JsonResponse(result)
        if topic.limit == 'private':
            if user.username != topic.author.username:
                result = {
                    'code': 405,
                    'error': 'please go out'
                }
                return JsonResponse(result)
        Message.objects.create(topic=topic, content=content,
                               parent_message=parent_id,
                               created_time=now, publisher=user)
        return JsonResponse({'code': 200, 'data': {}})












