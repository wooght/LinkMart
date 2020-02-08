# coding=utf-8
# @Explain  : 
# @Author   : wooght
# @File     : handbook email
# @Time     : 2020/2/7 下午10:52

from spider.downloadmiddle.EmailMiddleweare import EmailMiddleweare


# 附件下载爬虫
class email_spider:
    start_url = 'http://126.com'
    middleweare = EmailMiddleweare()

    def run(self):
        self.middleweare.process_request(self.start_url)
        self.body = self.middleweare.body



