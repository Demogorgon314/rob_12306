#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2018 Kingsoft.com, Inc. All Rights Reserved
#

"""
    auther: limuyun(limuyun@kingsoft.com)
    descrip:
"""
import smtplib
from email.mime.text import MIMEText


class Email():
    def __init__(self, mail_host, mail_user, mail_pass):
        self.mail_host = mail_host
        self.mail_user = mail_user
        self.mail_pass = mail_pass

    def getConnection(self):
        try:
            smtpObj = smtplib.SMTP()
            # 连接到服务器
            smtpObj.connect(self.mail_host, 25)
            # 登录到服务器
            smtpObj.login(self.mail_user, self.mail_pass)
            return smtpObj
        except smtplib.SMTPException as e:
            print('error', e)  # 打印错误

    def send_email(self, smtpObj, sender, receivers, message):
        try:
            # 发送
            smtpObj.sendmail(
                sender, receivers, message.as_string())
            print(receivers + " 发送成功!")
        except smtplib.SMTPException as e:
            print('error', e)  # 打印错误
        finally:
            # 退出
            smtpObj.quit()


if __name__ == '__main__':
    # 163邮箱服务器地址
    mail_host = 'smtp.163.com'
    # 163用户名
    mail_user = 'limuyun1989'
    # 密码(部分邮箱为授权码)
    mail_pass = '**********'
    # 邮件发送方邮箱地址
    sender = 'limuyun1989@163.com'
    # 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
    receivers = ['83363436@qq.com']

    # 设置email信息
    # 邮件内容设置
    message = MIMEText('content', 'plain', 'utf-8')
    # 邮件主题
    message['Subject'] = 'title'
    # 发送方信息
    message['From'] = sender
    # 接受方信息
    message['To'] = receivers[0]

    email = Email(mail_host, mail_user, mail_pass)

    smtpObj = email.getConnection()
    email.send_email(smtpObj,sender,receivers,message)

