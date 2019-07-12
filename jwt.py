# _*_ coding:UTF-8 _*_
# path:/home/tarena/桌面/study_file/...

"""
作者：朱文涛
邮箱：wtzhu_13@163.com

时间：2019/07
描述：JWT手动实现token
"""
import base64
import json
import hmac
import copy
import time


class Jwt:
    def __init__(self):
        pass

    @staticmethod
    def encode(payload, key, exp=300):
        # 创建header并JSON化
        header = {'alg': "HS256",
                  'type': 'JWT'}
        header_j = json.dumps(header, separators=(',', ':'), sort_keys=True)
        header_bs = Jwt.bs64encode(header_j.encode())

        # 创建payload并JSON化
        payload = copy.deepcopy(payload)
        payload['exp'] = int(time.time() + exp)
        payload_j = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        payload_bs = Jwt.bs64encode(payload_j.encode())

        # 生成sign预签串
        sign_str = header_bs + b'.' + payload_bs

        # 签名操作
        if isinstance(key, str):
            key = key.encode()
        h_obj = hmac.new(key, sign_str, digestmod='SHA256')
        sign = h_obj.digest()
        sign_bs = Jwt.bs64encode(sign)
        return header_bs + b'.' + payload_bs + b'.' + sign_bs

    @staticmethod
    def decode(token, key):
        """
            校验token
        :param token:
        :param key:
        :return:
        """
        # 拆解token, 拿出headers_bs, payload_bs, sign
        header_bs, payload_bs, sign = token.split(b'.')
        print(payload_bs)
        print(sign)
        if isinstance(key, str):
            key = key.encode()
        hm = hmac.new(key, header_bs + b'.' + payload_bs,
                      digestmod='SHA256')

        # base64 签名
        new_sign = Jwt.bs64encode(hm.digest())
        print(new_sign)
        if sign != new_sign:
            raise JwtSignError("error sign")
        # token合法，判断是否过期
        payload_j = Jwt.bs64decode(payload_bs)
        print(type(payload_j))
        payload = json.loads(payload_j.decode())
        exp = payload['exp']
        now = time.time()
        if exp < now:
            # token过期
            raise JwtSignError("error")
        return payload

    @staticmethod
    def bs64encode(s):
        """
            去掉字符串中的等于号
        :param s: 待处理字符串
        :return:
        """
        return base64.urlsafe_b64encode(s).replace(b'=', b'')

    @staticmethod
    def bs64decode(bs):
        """
            将去掉等号的字符串还原
        :param bs: 待处理字符串
        :return: 处理完毕字符串
        """
        rem = len(bs) % 4
        bs += b'=' * (4-rem)
        return base64.urlsafe_b64decode(bs)


class JwtSignError(Exception):
    """
        自定义异常类
    """
    def __init__(self, error_msg):
        self.error = error_msg

    def __str__(self):
        return '<JwtSignError>'


if __name__ == '__main__':
    res = Jwt.encode({'username': 'guoxiaonao'}, 'abcdef')
    print(res)
    print(Jwt.decode(res, 'abcdef'))

