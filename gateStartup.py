# utf-8
import pickle
import time
import os
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import srkTools, configparser


class GATE(object):

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        conf = configparser.ConfigParser()
        conf.read('gate.conf', 'utf-8')

        options = Options()

        # 代理配置
        if conf.get('proxy', 'enable') == '1':
            options.add_argument('--proxy-server=%s' % conf.get('proxy', 'addr'))
        if os.name == "posix":
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('log-level=3')
        options.add_argument('--disable-gpu')

        options.page_load_strategy = 'normal'
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"]
            # 'excludeSwitches', ['enable-logging']
        )
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.browser = webdriver.Chrome(options=options)
        self.browser.set_window_size(width=945, height=1020)
        self.browser.implicitly_wait(30)

    def spider(self):
        # 浏览器JS伪装
        self.browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'delete navigator.__proto__.webdriver',
        })

        self.browser.get(self.url)
        # 加载session
        if os.path.exists('gate.session'):
            with open('gate.session', 'rb') as s:
                cookies = pickle.load(s)
                for c in cookies:
                    self.browser.add_cookie(c)
            srkTools.LOG.info(msg="[ gate.io ] 检测到session文件，并已完成加载")
            time.sleep(1)
            self.browser.refresh()
        # 判断是否登录
        self.login()
        srkTools.LOG.info("登录成功，进入startup页面")

        # 打新
        while 1:
            self.gate_startup()
            time.sleep(float(CRON) * 3600)

    def gate_startup(self):

        # 进入startup 页面
        time.sleep(0.5)
        self.browser.get(self.url + "/startup")
        time.sleep(0.5)

        srkTools.LOG.info("已刷新startup列表，地址：%s" % self.browser.current_url)

        startup_list_find_str = '//*[@id="startupRoot"]/div[2]/div[1]/div[2]/div'
        startup_list = self.browser.find_elements(By.XPATH, startup_list_find_str)
        item_idx = 0
        while item_idx < len(startup_list):
            # 获取项目名称
            coin = startup_list[item_idx].find_element(By.TAG_NAME, 'h5').text

            # 判断项目是否在进行中
            if startup_list[item_idx].find_element(By.CLASS_NAME, 'mantine-GateButton-inner').text == "$0免费领取": #"$0免费领取":

                # 进入项目
                startup_list[item_idx].click()
                time.sleep(1)
                # 判断项目是否认购成功
                try:

                    # 处理不弹出领取窗口的情况
                    try:
                        # 点击领取
                        self.browser.find_element(By.XPATH, '//span[text()="$0免费领取"]').click()
                        time.sleep(1)
                    except:
                        pass
                    # 同意协议
                    self.browser.find_element(By.CLASS_NAME, 'mantine-GateCheckBox-root').click()
                    time.sleep(1)
                    self.browser.find_element(By.XPATH, '//span[text()="立即领取"]').click()
                    # 点击领取
                    # ActionChains(self.browser).click(self.browser.find_element(By.XPATH, '//*[@id="startup-claim-shade"]/div/div[2]/div[6]/div[2]')).perform()

                    srkTools.LOG.info("%s 认购成功" % coin)

                except Exception as e:
                    srkTools.LOG.info("%s 认购失败" % coin)
                    srkTools.LOG.info(e)

                # 重新获取startup_list 实例
                time.sleep(1)
                self.browser.back()
                time.sleep(3)
                startup_list = self.browser.find_elements(By.XPATH, startup_list_find_str)

            # 下一个startup项目的下标
            item_idx += 1

    # 使用ID的形式判断DOM元素是否存在
    def isExistElement(self, elementStr):

        try:
            self.browser.find_element(By.XPATH, elementStr)
            return True
        except:
            return False

    def login(self):

        login_selector = '//*[@id="__next"]/div[1]/section/div[1]/div[1]/a'
        login_success = '//div[text()="%s"]' % self.username
        # 如果session登录成功则直接跳过登录判断
        if self.isExistElement(elementStr=login_success):
            return
        # 判断是否登录
        if self.isExistElement(elementStr=login_selector):

            srkTools.LOG.info("未登录，正在登录")

            # 没登录
            self.browser.find_element(By.XPATH, login_selector).click()

            # 判断跳转HK弹窗
            try:
                self.browser.find_element(By.XPATH, '//*[@id="hk_dialog_btn"]').click()
            except:
                pass

            # 点击手机号登录
            self.browser.find_element(By.XPATH, '//div[@class="login_tabs"]/div[2]').click()
            self.browser.find_element(By.CLASS_NAME, 'phone_select_body').click()
            self.browser.find_element(By.CLASS_NAME, 'mantine-TextInput-withIcon').send_keys(country)
            self.browser.find_element(By.XPATH,
                                      '//div[@class="phone_select_option_container"]//span[text()="%s"]' % country).click()

            # 输入账号密码
            self.browser.find_element(By.CLASS_NAME, 'mantine-jxmsru').send_keys(self.username)
            self.browser.find_element(By.CLASS_NAME, 'mantine-x4ic1j').send_keys(self.password)
            self.browser.find_element(By.XPATH, '//span[contains(@class,"mantine-Button-label") and text()="登录"]').click()

            # 验证码区域
            verif_count = 0
            while verif_count <= int(RETRIES):  # 重试5次

                # 获取滑动验证码图片
                codeImg = str(self.browser.find_element(By.CLASS_NAME, 'geetest_bg').get_attribute('style')).split('"')[1]
                srkTools.LOG.info("滑块验证码图片：%s" % codeImg)
                # 保存验证码图片
                srkTools.VERIF().save_img(codeImg)
                # 超级鹰获取缺口坐标
                cjyData = srkTools.VERIF().get_pos()  # 图片名称默认为bg.jpeg
                # 滑动滑块
                srkTools.VERIF().gate_code(browser=self.browser, codeImg=codeImg, cjyData=cjyData)

                # 判断是否成功
                try:

                    # 寻找谷歌验证器element
                    self.browser.find_element(By.ID, 'verify_input_0')
                    break  # 登录成功则退出循环

                except:

                    srkTools.LOG.info("滑块验证码验证失败，将重新验证")
                    srkTools.VERIF().cjyReportErr(cjyData['pic_id'])  # 超级鹰反馈失败验证情况，避免扣费
                    srkTools.LOG.info('超级鹰错误码： %s 已提交' % cjyData['pic_id'])
                    verif_count += 1

                    # 超过重试次数
                    if verif_count > int(RETRIES):
                        srkTools.LOG.info("滑块验证码重试超过5次，请重新运行程序")
                        exit(1)

            # 获取谷歌验证器key
            google_key = srkTools.GOOGLE_VERIF().getCODE()

            # 输入谷歌验证码
            self.browser.find_element(By.ID, 'verify_input_0').send_keys(google_key[0])
            self.browser.find_element(By.ID, 'verify_input_1').send_keys(google_key[1])
            self.browser.find_element(By.ID, 'verify_input_2').send_keys(google_key[2])
            self.browser.find_element(By.ID, 'verify_input_3').send_keys(google_key[3])
            self.browser.find_element(By.ID, 'verify_input_4').send_keys(google_key[4])
            self.browser.find_element(By.ID, 'verify_input_5').send_keys(google_key[5])

            # 保存session
            time.sleep(1)
            self.browser.refresh()
            with open('gate.session', 'wb') as s:
                pickle.dump(self.browser.get_cookies(), s)
                srkTools.LOG.info(msg="[ gate.io ] session 已保存")

        else:
                srkTools.LOG.info("gate.io 网页DOM结构已更新，请更新脚本")
                exit(0)


if __name__ == '__main__':

    conf = configparser.ConfigParser()
    conf.read('gate.conf', 'utf-8')

    url = conf.get('gate', 'url')
    username = conf.get('gate', 'username')
    password = conf.get('gate', 'password')
    country = conf.get('gate', 'country')

    CRON = conf.get('main', 'cron')
    RETRIES = conf.get('main', 'retries')

    gate = GATE(url=url, username=username, password=password)
    gate.spider()
