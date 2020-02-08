# coding=utf-8
# @Explain  : chromedriver test
# @Author   : wooght
# @File     : handbook chromedriver_test
# @Time     : 2020/2/7 下午9:21

from pyvirtualdisplay import Display
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1366,768')
chrome_options.add_argument('--no-sandbox')
# display = Display(visible=0, size=(800, 600))   # 初始化屏幕
# display.start()
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='/usr/local/share/chromedriver')
driver.get('http://www.baidu.com')
print(driver.title)