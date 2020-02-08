# coding=utf-8
# @Explain  : 基本功能函数
# @Author   : wooght
# @File     : handbook base_function
# @Time     : 2020/2/7 下午10:39

import time


class base_function():
    # 返回当前时间
    def now(d=False):
        if d:
            now_str = time.strftime("%Y-%m-%d", time.localtime())
        else:
            now_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 格式化时间 2017-10-23 17:10:54
        return now_str