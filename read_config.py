#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2018 Kingsoft.com, Inc. All Rights Reserved
#

from configparser import ConfigParser


city_conf = ConfigParser()
city_conf.read("conf/city.conf")
sections = city_conf.sections()
city = sections[0]

key_list = city_conf.options(city)

for key in key_list:
    print(city_conf.get(city,key))



# #初始化类
# cp = ConfigParser()
# cp.read("12306.conf")

# #得到所有的section，以列表的形式返回
# sections = cp.sections()
# passenger1 = sections[0]
# print(passenger1)
#
# #得到该section的所有option
# print(cp.options(passenger1))
#
# #得到该section的所有键值对
# print(type(cp.items(passenger1)))
# print(cp.items(passenger1))
#
# print("***********")
# # for tuple_ in cp.items(passenger1):
# #     print(cp.get(passenger1, tuple_))
# #得到该section中的option的值，返回为string类型
# print(cp.get(passenger1, "name"))
#
# #得到该section中的option的值，返回为int类型
# print(cp.get(passenger1, "from_station"))
#
# print(cp.get(passenger1, "from_station"))