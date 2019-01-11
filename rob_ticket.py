#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2018 Kingsoft.com, Inc. All Rights Reserved
#

"""
    auther: limuyun(limuyun@kingsoft.com)
    descrip:

通过splinter刷12306火车票
进入登陆页面，可以选择扫码登陆或者账号密码登陆
登陆成功后，接下来的事情，交由脚本来做了，静静的等待抢票结果就好（刷票过程中，浏览器不可关闭）
抢票成功，会进行邮件的通知


"""

from splinter.browser import Browser
from time import sleep
import sys
from email.mime.text import MIMEText

from EmailUtils import Email
from configparser import ConfigParser


class BrushTicket(object):
    """买票类及实现方法"""

    def __init__(self, passengers_number):
        """定义实例属性，初始化"""
        cp= ConfigParser()
        cp.read("conf/city.conf", encoding='UTF-8')
        sections = cp.sections()
        city = sections[0]
        key_list = cp.options(city)
        self.city_dict={}
        for key in key_list:
            self.city_dict[key]=cp.get(city, key)

        cp= ConfigParser()
        cp.read("conf/12306.conf", encoding='UTF-8')
        sections = cp.sections()
        pessenger = sections[passengers_number]

        # 乘客姓名
        self.passengers = cp.get(pessenger, 'name')
        # 起始站和终点站
        self.from_station = self.city_dict[cp.get(pessenger, 'from_station')]
        self.to_station = self.city_dict[cp.get(pessenger, 'to_station')]
        # 乘车日期
        self.from_time = cp.get(pessenger, 'from_time')
        # 车次编号
        self.number = cp.get(pessenger, 'coach_number')
        seat_type = cp.get(pessenger, 'seat_type')
        # 座位类型所在td位置
        if seat_type == '商务座特等座':
            seat_type_index = 1
            seat_type_value = 9
        elif seat_type == '一等座':
            seat_type_index = 2
            seat_type_value = 'M'
        elif seat_type == '二等座':
            seat_type_index = 3
            seat_type_value = 0
        elif seat_type == '高级软卧':
            seat_type_index = 4
            seat_type_value = 6
        elif seat_type == '软卧':
            seat_type_index = 5
            seat_type_value = 4
        elif seat_type == '动卧':
            seat_type_index = 6
            seat_type_value = 'F'
        elif seat_type == '硬卧':
            seat_type_index = 7
            seat_type_value = 3
        elif seat_type == '软座':
            seat_type_index = 8
            seat_type_value = 2
        elif seat_type == '硬座':
            seat_type_index = 9
            seat_type_value = 1
        elif seat_type == '无座':
            seat_type_index = 10
            seat_type_value = 1
        elif seat_type == '其他':
            seat_type_index = 11
            seat_type_value = 1
        else:
            seat_type_index = 7
            seat_type_value = 3
        self.seat_type_index = seat_type_index
        self.seat_type_value = seat_type_value
        # 通知信息
        # self.receiver_mobile = receiver_mobile
        self.receiver_email = cp.get(pessenger, 'email')
        # 新版12306官网主要页面网址
        self.login_url = 'https://kyfw.12306.cn/otn/resources/login.html'
        self.init_my_url = 'https://kyfw.12306.cn/otn/view/index.html'
        self.ticket_url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc'
        # 浏览器驱动信息，驱动下载页：https://sites.google.com/a/chromium.org/chromedriver/downloads
        self.driver_name = 'chrome'
        self.driver = Browser(driver_name=self.driver_name)

    def do_login(self):
        """登录功能实现，识别验证码 可以使用12306APP 扫一扫登录"""
        self.driver.visit(self.login_url)
        sleep(1)
        # 选择登陆方式登陆
        print('请扫码登陆或者账号登陆……')
        while True:
            if self.driver.url != self.init_my_url:
                sleep(1)
            else:
                break

    def start_brush(self):
        """买票功能实现"""
        # 浏览器窗口最大化
        self.driver.driver.maximize_window()
        # 登陆
        self.do_login()
        # 跳转到抢票页面
        self.driver.visit(self.ticket_url)
        try:
            print('开始刷票……')
            # 加载车票查询信息
            self.driver.cookies.add({"_jc_save_fromStation": self.from_station})
            self.driver.cookies.add({"_jc_save_toStation": self.to_station})
            self.driver.cookies.add({"_jc_save_fromDate": self.from_time})
            self.driver.reload()
            count = 0
            while self.driver.url == self.ticket_url:
                self.driver.find_by_text('查询').click()
                sleep(1)
                count += 1
                print('第%d次点击查询……' % count)
                try:
                    current_tr = self.driver.find_by_xpath(
                        '//tr[@datatran="' + self.number + '"]/preceding-sibling::tr[1]')
                    if current_tr:
                        if current_tr.find_by_tag('td')[self.seat_type_index].text == '--':
                            print('无此座位类型出售，已结束当前刷票，请重新开启！')
                            sys.exit(1)
                        elif current_tr.find_by_tag('td')[self.seat_type_index].text == '无':
                            print('无票，继续尝试……')
                            sleep(1)
                        else:
                            # 有票，尝试预订
                            print('刷到票了（余票数：' + str(
                                current_tr.find_by_tag('td')[self.seat_type_index].text) + '），开始尝试预订……')
                            current_tr.find_by_css('td.no-br>a')[0].click()
                            sleep(1)
                            key_value = 1
                            for p in self.passengers:
                                # 选择用户
                                print('开始选择用户……')
                                self.driver.find_by_text(p).last.click()
                                # 选择座位类型
                                print('开始选择席别……')
                                if self.seat_type_value != 0:
                                    self.driver.find_by_xpath(
                                        "//select[@id='seatType_" + str(key_value) + "']/option[@value='" + str(
                                            self.seat_type_value) + "']").first.click()
                                key_value += 1
                                sleep(0.2)
                                if p[-1] == ')':
                                    self.driver.find_by_id('dialog_xsertcj_ok').click()
                            print('正在提交订单……')
                            self.driver.find_by_id('submitOrder_id').click()
                            sleep(2)
                            # 查看放回结果是否正常
                            submit_false_info = self.driver.find_by_id('orderResultInfo_id')[0].text
                            if submit_false_info != '':
                                print(submit_false_info)
                                self.driver.find_by_id('qr_closeTranforDialog_id').click()
                                sleep(0.2)
                                self.driver.find_by_id('preStep_id').click()
                                sleep(0.3)
                                continue
                            print('正在确认订单……')
                            self.driver.find_by_id('qr_submit_id').click()
                            print('预订成功，请及时前往支付……')
                            # 发送通知信息
                            title = '抢票票成功！！'
                            self.send_mail(self.receiver_email, '恭喜您，抢到了' + self.from_time + '的车票，请及时前往12306支付订单！',title)
                    else:
                        print('不存在当前车次【%s】，已结束当前刷票，请重新开启！' % self.number)
                        sys.exit(1)
                except Exception as error_info:
                    print(error_info)
        except Exception as error_info:
            print(error_info)

    def send_mail(self, receiver_address, content, title):
        mail_host = 'smtp.163.com'
        # 163用户名
        mail_user = 'limuyun1989'
        # 密码(部分邮箱为授权码)
        mail_pass = '*******'
        # 邮件发送方邮箱地址
        sender = 'limuyun1989@163.com'
        # 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
        receivers_list = ['******@qq.com', receiver_address]

        email = Email(mail_host, mail_user, mail_pass)

        for receiver in receivers_list:
            # 设置email信息
            # 邮件内容设置
            smtpObj = email.getConnection()
            message = MIMEText(str(content), 'plain', 'utf-8')
            # 邮件主题
            message['Subject'] = title
            # 发送方信息
            message['From'] = sender
            # 接受方信息
            message['To'] = receiver
            email.send_email(smtpObj, sender, receiver, message)


if __name__ == '__main__':

    pessenger_number = int(input('请输入12306.conf 配置文件中的第几个配置(从0开始)：'))

    # 开始抢票
    ticket = BrushTicket(pessenger_number)
    ticket.start_brush()
