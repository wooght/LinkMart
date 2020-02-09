# coding=utf-8
# @Explain  : 主下载中间件
# @Author   : wooght
# @File     : handbook IndexMiddleweare
# @Time     : 2020/2/7 下午10:16

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from spider.common.base_function import base_function as func


class IndexMiddleweare(object):
    body = ''                  # 网页body内容
    url = ''                   # 目标地址
    headless = True            # 无头模式默认开启
    webdriver = webdriver
    options = Options()
    save_error_pic = True

    def set_ini(self):
        if self.headless:
            self.options.add_argument('--headless')
            self.options.add_argument('--disable-gpu')                      # 以上两项为开启无头模式
        self.options.add_argument('--window-size=1360,800')                 # 默认窗口大小
        self.options.add_argument('--no-sandbox')                           # 沙盒模式
        # self.options.add_argument('blink-settings=imagesEnabled=false')     # 禁止加载图片
        # pyCharm运行时候无效，命令运行时有效？？？
        prefs = {
            'profile.default_content_settings.popups': 0,              # 禁止弹出下载窗口
            'download.default_directory': 'downfile',                  # 下载目录
        }
        self.options.add_experimental_option('prefs', prefs)
        self.driver = self.webdriver.Chrome(chrome_options=self.options)    # 启动chromedriver

    def open(self, url):
        self.driver.get(url)

    def echo(self, char):
        print(func.now(), ':', str(char))

    # 隐藏按钮点击 只支持ID
    def readonly_click(self, id):
        readonlyjs = "var readonlyjs = document.getElementById('"+id+"');readonlyjs.removeAttribute('readOnly');"
        self.driver.execute_script(readonlyjs)
        self.driver.find_element_by_id(id).click()
