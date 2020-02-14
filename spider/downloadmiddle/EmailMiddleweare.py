# coding=utf-8
# @Explain  : 126邮箱下载件
# @Author   : wooght
# @File     : handbook EmailMiddleweare
# @Time     : 2020/2/7 下午10:30

from spider.downloadmiddle.IndexMiddleweare import IndexMiddleweare as Obj
import time
import xlrd
from selenium.webdriver.support.wait import WebDriverWait


class EmailMiddleweare(Obj):
    qr_code = False     # 是否扫描登录

    # 处理request启动函数
    def process_request(self, url):
        self.url = url
        self.headless = True   # 关闭无头模式
        self.set_ini()

        self.open(self.url)
        self.signin()
        self.getfile()
        self.open_file()

    # 执行登录
    def signin(self):
        time.sleep(1)
        self.driver.save_screenshot('static/pic/qr_code.png')
        # 等等扫码登录
        if self.qr_code:
            time.sleep(18)
        time.sleep(2)  # 等待二维码
        try:
            # 查找 ‘去登录’ 按钮
            self.driver.find_element_by_id('switchAccountLogin').click()
        except:
            # 扫描登录/自动登录 查找登录成功的标志
            # self.echo('no loginInput')
            # 避免无法点击或者被隐藏
            readonlyjs = "var readonlyjs = document.getElementById('_mail_component_104_104');readonlyjs.removeAttribute('readOnly');"
            self.driver.execute_script(readonlyjs)
            self.qr_code = True

        try:
            self.driver.save_screenshot('static/pic/file_center_button.png')
            self.driver.find_element_by_id('_mail_component_104_104').click()
            # 自动登录/扫码登录成功
            return None
        except:
            # self.echo('mast login...')
            pass

        time.sleep(2)
        self.driver.switch_to.frame(0)  # 直接switch iframe对象无法访问,采用iframe序列可以访问 ?????

        # 输入内容
        part_key = self.driver.find_element_by_name('email')  # 账户输入框
        password = self.driver.find_element_by_name('password')  # 密码输入框
        part_key.send_keys('wooght')
        password.send_keys('wooghtPUWENFENG5')

        # 提交
        self.driver.find_element_by_id('dologin').click()  # 提交按钮
        self.driver.switch_to_default_content()  # 切换出iframe 回到主窗口
        time.sleep(3)
        self.driver.save_screenshot('static/pic/loginresult.png')

    # 进入邮箱主界面
    def getfile(self):
        # self.echo('to getfile...')
        # 等待页面载入
        time.sleep(1)

        # 点击进入附件列表页面
        if not self.qr_code:
            self.driver.find_element_by_id('_mail_component_104_104').click()
            time.sleep(1)

        # 进入附件中心iframe
        iframe_xpath = '//div[@class="frame-main-cont-iframeCont"]/iframe'
        annex_url = self.driver.find_element_by_xpath(iframe_xpath).get_attribute('src')
        self.open(annex_url)
        time.sleep(1)

        # 点击附件 -> 进入附件下载页面
        # self.echo('enter to file_center...')
        # 获取文件名
        self.file_name = self.driver.find_element_by_xpath('//*[@id="mainContent"]/div[3]/div[2]/div[1]/div/div[2]/div[1]/div[2]/span[2]/span[2]').text
        # 获取文件fileid
        fileid_div = '//*[@id="mainContent"]/div[3]/div[2]/div[1]/div/div[2]/div[1]'
        fileid = self.driver.find_element_by_xpath(fileid_div).get_attribute('fileid')
        fileid_list = fileid.split('_')
        # 获取用户sid
        cookie = self.driver.get_cookie('Coremail.sid')
        # 组装下载地址
        download_link = 'https://mail.126.com/app/fj/getFile.jsp?sid='+cookie['value']+'&mode=download&mid='+fileid_list[0]+'&part=_'+fileid_list[1]
        # 打开下载
        self.open(download_link)

        # self.driver.find_element_by_xpath(xpathstr).click()
        # self.driver.switch_to_window(self.driver.window_handles[1])  # 窗口切换
        # self.echo(self.driver.current_url)

        # # 下载按钮
        # time.sleep(2)
        # xpathstr = '//*[@id="divHeader"]/div[1]/span[2]/a'
        # self.file_name = WebDriverWait(self.driver, 3, 0.2).until(lambda x: x.find_element_by_xpath('//*[@id="divHeader"]/div[1]/strong')).text
        # click = WebDriverWait(self.driver, 3, 0.2).until(lambda x: x.find_element_by_xpath(xpathstr)).click()
        # # self.driver.find_element_by_xpath(xpathstr).click()

    def open_file(self):
        # 等待下载完毕
        for t in range(10):
            try:
                data = xlrd.open_workbook('downfile/'+self.file_name)
                break
            except:
                if t == 9:
                    raise FileNotFoundError()   # 抛出文件异常
                time.sleep(1)
        table = data.sheet_by_index(0)
        # self.echo('总行数：'+str(table.nrows))
        # self.echo('总列数：'+str(table.ncols))
        result_list = []
        # 逐行读取
        for i in range(table.nrows):
            result_list.append(','.join(table.row_values(i)))   # 逗号间隔组成字符串 模拟csv格式
        self.body = result_list
        self.dele_file()

    # 删除临时文件
    def dele_file(self):
        import os
        os.remove('downfile/'+self.file_name)
        os.remove('static/pic/qr_code.png')
        os.remove('static/pic/file_center_button.png')