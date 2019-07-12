import datetime
import json

from django.db.models import F
from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.
from comment.models import Message
from tools.logging_decorator import logging_check, get_user_by_request
from topic.models import Topic
from user.models import UserProfile


@logging_check('POST', 'DELETE')
def topics(request, author_id=None):
    if request.method == "POST":
        author = request.user
        json_str = request.body
        if not json_str:
            # 返回的内容缺失
            result = {
                'code': 301,
                'error': 'data is null'
            }
            return JsonResponse(result)
        json_obj = json.loads(json_str)

        title = json_obj.get('title')
        category = json_obj.get('category')
        if category not in ['tec', 'no-tec']:
            # 判断分类是够正确
            result = {
                'code': 302,
                'error': 'use right cat'
            }
            return JsonResponse(result)
        # 权限
        limit = json_obj.get('limit')
        if limit not in ['public', 'private']:
            result = {
                'code': 303,
                'error': 'use right limit'
            }
            return JsonResponse(result)
        # 携带全部样式的内容，如加粗颜色等
        content = json_obj.get('content')
        # 纯文本的内容，用来做introduce的截取
        content_text = json_obj.get('content_text')
        # 简介取纯文本的前三十个字符
        introduce = content_text[:30]
        if not title or not category or not limit or not content or not content_text:
            # 必填项缺失
            result = {
                'code': 304,
                'error': 'some data necessary'
            }
            return JsonResponse(result)

        # 当前时间
        now = datetime.datetime.now()

        # 创建存储topic

        Topic.objects.create(
            title=title, content=content,
            limit=limit, category=category,
            author=author, created_time=now,
            modified_time=now, introduce=introduce
        )

        result = {
            'code': 200,
            'username': author.username
        }
        return JsonResponse(result)

    elif request.method == 'DELETE':
        # 删除博主的博客文章
        author = request.user.username
        print(author)
        print(author_id)
        if author != author_id:
            result = {
                'code': 305,
                'error': 'You can not do it'
            }
            return JsonResponse(result)
        # 当token中用户名和URL中的严格一致时；方可执行
        topic_id = request.GET.get('topic_id')
        if not topic_id:
            result = {
                'code': 307,
                'error': "you can't do it"
            }
            return JsonResponse(result)
        try:
            topic = Topic.objects.get(id=topic_id)
        except Exception as e:
            print(e)
            result = {
                'code': 308,
                'error': 'your topic is not existed'
            }
            return JsonResponse(result)
        topic.delete()
        return JsonResponse({'code': 200})

    elif request.method == 'GET':
        # 获取用户的博客列表 或 具体内容
        # 访问者 visitor
        # 当前博客的博主author
        author = get_author(author_id)
        visitor = get_user_by_request(request)
        visitor_username = None
        if visitor:
            visitor_username = visitor.username

        # 尝试获取id，存在则是获取指定的内容
        t_id = request.GET.get('t_id')
        if t_id:
            t_id = int(t_id)
            # 访问者身份标识
            is_self = False
            if visitor_username == author_id:
                # True 标识博主访问自己的博客
                is_self = True
                try:
                    author_topic = Topic.objects.get(id=t_id)
                except Exception as e:
                    print(e)
                    result = {
                        'code': 309,
                        'error': 'No topic'
                    }
                    return JsonResponse(result)
            else:
                try:
                    author_topic = Topic.objects.get(id=t_id, limit='public')
                except Exception as e:
                    print(e)
                    result = {
                        'code': 309,
                        'error': 'No topic'
                    }
                    return JsonResponse(result)

            res = make_topics_res(author, author_topic, is_self)
            return JsonResponse(res)

        else:
            # 获取某一类别的值
            # url中没有category时返回None
            category = request.GET.get('category')
            if category in ['tec', 'no-tec']:
                # 指定了范围则在指定范围搜索
                author_topic = Topic.objects.filter(
                    author_id=author_id,
                    category=category
                )
            else:
                if visitor_username == author_id:
                    # 博主在访问自己的博客，获取全部权限博客
                    author_topic = Topic.objects.filter(
                        author_id=author_id
                    )
                else:
                    author_topic = Topic.objects.filter(
                        author_id=author_id,
                        limit='public'
                    )

            res = make_topic_res(author, author_topic)

            return JsonResponse(res)


def make_topic_res(author, author_topic):
    """
        拼凑返回值
    :param author:
    :param author_topic:
    :return:
    """
    res = {
        'code': 200,
        'data': {}
    }
    topics_res = []
    for topic in author_topic:
        dic = {}
        dic['id'] = topic.id
        dic['title'] = topic.title
        dic['category'] = topic.category
        dic['created_time'] = topic.created_time.strftime(
            '%Y-%m-%d %H:%m:%S'
        )
        dic['content'] = topic.content
        dic['introduce'] = topic.introduce
        dic['author'] = topic.author.nickname
        topics_res.append(dic)
    res['data']['topics'] = topics_res
    res['data']['nickname'] = author.nickname
    return res


def get_author(author_id):
    """
        通过author_id 找到author对象
    :param author_id:
    :return:
    """
    authors = UserProfile.objects.filter(
        username=author_id
    )
    if not authors:
        result = {
            'code': 305,
            'error': 'The current'
                     'author is not existed'
        }
        return JsonResponse(result)
    return authors[0]


def make_topics_res(author, author_topic, is_self):
    """
        生成具体博客内容的返回值
    :param author: 博客内容的作者
    :param author_topic: 当前方位的博文对象
    :return:
    """
    if is_self:

        # 博主自己访问
        # 取出id大于当前id的第一个
        next_topic = Topic.objects.filter(id__gt=author_topic.id,
                                          author_id=author.username).first()
        # 取出id小于当前id的最后一个
        last_topic = Topic.objects.filter(id__lt=author_topic.id,
                                          author=author).last()

        if next_topic:
            # 下一个博客内容的id
            next_id = next_topic.id
            # 下一个博客内容的title
            next_title = next_topic.title
        else:
            next_id = None
            next_title = None
        # 上一篇文章id和题目
        if last_topic:
            last_id = last_topic.id
            last_title = last_topic.title
        else:
            last_id = None
            last_title = None

        # 生成message返回结构
        # 取出所有评论并按时间倒序排序
        all_message = Message.objects.filter(
            topic=author_topic
        ).order_by('-created_time')
        msg_list = []
        level1_msg = {}
        # 留言数
        m_count = 0
        for msg in all_message:
            m_count += 1
            if msg.parent_message:
                # 有parent_id为回复
                level1_msg.setdefault(msg.parent_message, [])
                level1_msg[msg.parent_message].append(
                    {
                        'msg_id': msg.id,
                        'publisher': msg.publisher.nickname,
                        'publisher_avatar': str(
                            msg.publisher.avatar
                        ),
                        'content': msg.content,
                        'created_time': msg.created_time.strftime(
                            '%Y-%m-%d'
                        )
                    }
                )

            else:
                # 没有parent_id则为留言
                msg_list.append(
                    {
                        'id': msg.id,
                        'content': msg.content,
                        'publisher': msg.publisher.nickname,
                        'publisher_avatar': str(msg.publisher.avatar),
                        'created_time': msg.created_time.strftime(
                            '%Y-%m-%d'),
                        'reply': []
                    }
                )

        for m in msg_list:
            if m['id'] in level1_msg:
                m['reply'] = level1_msg[m['id']]

        result = {'code': 200, 'data': {}}
        result['data']['nickname'] = author.nickname
        result['data']['title'] = author.nickname
        result['data']['category'] = author_topic.category
        result['data']['created_time'] = \
            author_topic.created_time.strftime("%Y-%m-%d")
        result['data']['content'] = author_topic.content
        result['data']['introduce'] = author_topic.introduce
        result['data']['author'] = author.nickname
        result['data']['next_id'] = next_id
        result['data']['next_title'] = next_title
        result['data']['last_id'] = last_id
        result['data']['last_title'] = last_title
        result['data']['messages'] = msg_list
        result['data']['messages_count'] = m_count
        # 返回拼凑好的结果
        return result

    else:
        next_topic = next_topic = Topic.objects.filter(id__gt=author_topic.id,
                                                       limit='public').first()
        return "ok"


















