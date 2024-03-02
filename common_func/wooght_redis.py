# coding=utf-8
# @Explain  : redis 缓存
# @Author   : wooght
# @File     : linkmart apis
# @Time     : 2021/01/15 上午午09:40

import redis


class wooght_redis:
    def __init__(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0, socket_connect_timeout=2)  # 连接池
        self.r = redis.Redis(connection_pool=pool)  # 连接,指定连接池

    def set(self, name, status_str):
        self.r.set(name, status_str)

    def get(self, name):
        try:
            return self.r.get(name).decode('utf8')
        except Exception as e:
            return None