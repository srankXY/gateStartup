# -*- coding: utf-8 -*-

import requests
import time
import random, configparser
from selenium.webdriver import ActionChains
from chaojiying import Chaojiying_Client
from selenium.webdriver.common.by import By
from python_authentiator import TOTP


# 日志模块
class LOG(object):

    def __init__(self):
        pass

    @staticmethod
    def info(msg):

        # 控制台打印
        print(time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time())), msg)

        with open("log.txt", "a") as f:

            # 写入日志文件
            print(time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time())), msg, file=f, end='\n')
            f.close()

# 代理
class PROXY(object):
    # 获取代理ip

    def __init__(self):
        pass

    def get(self):
        pass


# 谷歌验证器
class GOOGLE_VERIF(object):

    def __init__(self):
        pass

    def getCODE(self):

        conf = configparser.ConfigParser()
        conf.read('gate.conf', 'utf-8')

        g_auth = TOTP(
            origin_secret='',
        )
        secret = conf.get('gate', 'google_secret')
        # 生成一次性密码
        return g_auth.generate_code(secret)


# 滑块验证码
class VERIF(object):

    def __init__(self):
        conf = configparser.ConfigParser()
        conf.read('gate.conf', 'utf-8')

        cjyUser = conf.get('cjy', 'cjyUser')
        cjyPassword = conf.get('cjy', 'cjyPassword')
        softId = conf.get('cjy', 'softId')
        self.chaojiying = Chaojiying_Client(username=cjyUser, password=cjyPassword, soft_id=softId)

    def gate_code(self, browser, codeImg, cjyData):

        """这里需要访问，带有滑动验证码的页面，然后会获取滑块对其进行滑动"""
        # 获取dex
        dex = int(str(cjyData['pic_str']).split(',')[0])     # 计算移动距离

        # print(cjyData, dex)

        # 根据坐标计算移动轨迹
        track_list = self.get_track(dex)
        time.sleep(0.5)

        slid_ing = browser.find_element(By.CLASS_NAME, 'geetest_btn')  # 滑块定位
        ActionChains(browser).click_and_hold(on_element=slid_ing).perform()  # 鼠标按下
        time.sleep(0.2)
        # print('轨迹', track_list)
        LOG.info("滑动轨迹：%s" % track_list)

        # 开始滑动
        for track in track_list:
            ActionChains(browser).move_by_offset(xoffset=track, yoffset=0).perform()  # 鼠标移动到距离当前位置（x,y）
        time.sleep(1)

        # 跳过鼠标释放异常
        try:
            ActionChains(browser).release(on_element=slid_ing).perform()  # print('第三步,释放鼠标')
        except:
            pass

        time.sleep(1)
        return True

    def get_pos(self):
        im = open('bg.jpeg', 'rb').read()
        result = self.chaojiying.PostPic(im, 9101)
        return {
            'pic_id': result['pic_id'],
            'pic_str': result['pic_str']
        }

    def cjyReportErr(self, im_id):

        self.chaojiying.ReportError(im_id)


    @staticmethod
    def save_img(codeImg):
        """保存图片"""
        conf = configparser.ConfigParser()
        conf.read('gate.conf', 'utf-8')

        try:
            if conf.get('proxy', 'enable') == '1':
                img = requests.get(codeImg, proxies={'https': 'http://%s' % conf.get('proxy', 'addr')}).content
            else:
                img = requests.get(codeImg).content

            with open('bg.jpeg', 'wb') as f:
                f.write(img)
            return True
        except:
            return False

# def get_pos():
    #     """识别缺口
    #     注意：网页上显示的图片为缩放图片，缩放 50% 所以识别坐标需要 0.5
    #     """
    #     image = cv.imread('bg.jpeg')
    #     blurred = cv.GaussianBlur(image, (5, 5), 0)
    #     canny = cv.Canny(blurred, 200, 400)
    #     contours, hierarchy = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    #     for i, contour in enumerate(contours):
    #         m = cv.moments(contour)
    #         if m['m00'] == 0:
    #             cx = cy = 0
    #         else:
    #             cx, cy = m['m10'] / m['m00'], m['m01'] / m['m00']
    #         if 6000 < cv.contourArea(contour) < 8000 and 370 < cv.arcLength(contour, True) < 390:
    #             if cx < 400:
    #                 continue
    #             x, y, w, h = cv.boundingRect(contour)  # 外接矩形
    #             cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
    #             # cv.imshow('image', image)  # 显示识别结果
    #             print('【缺口识别】 {x}px'.format(x=x/2))
    #             return x/2
    #     return 0

    @staticmethod
    def get_track(distance):
        """模拟轨迹
        """
        distance -= 36  # 初始位置
        # 初速度
        v = 0
        # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        t = 0.2
        # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        tracks = []
        # 当前的位移
        current = 0
        # 到达mid值开始减速
        mid = distance * 7 / 8

        distance += 10  # 先滑过一点，最后再反着滑动回来
        # a = random.randint(1,3)
        while current < distance:
            if current < mid:
                # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
                a = random.randint(2, 4)  # 加速运动
            else:
                a = -random.randint(3, 5)  # 减速运动

            # 初速度
            v0 = v
            # 0.2秒时间内的位移
            s = v0 * t + 0.5 * a * (t ** 2)
            # 当前的位置
            current += s
            # 添加到轨迹列表
            tracks.append(round(s))

            # 速度已经达到v,该速度作为下次的初速度
            v = v0 + a * t

        # 反着滑动到大概准确位置
        for i in range(4):
            tracks.append(-random.randint(2, 3))
        for i in range(4):
            tracks.append(-random.randint(1, 3))
        return tracks
