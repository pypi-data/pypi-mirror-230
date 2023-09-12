#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   ip.py
@Time    :   2023-04-03 15:46
@Author  :   坐公交也用券
@Version :   1.0
@Contact :   liumou.site@qq.com
@Homepage : https://liumou.site
@Desc    :   当前文件作用
"""
from src.pbm_liumou_Stable import IsIpv4, IpStrDraw, IPMaskTransformCode

# i = IsIpv4("10.1.1.2")
# if i:
# 	print("is ip")

i = IsIpv4("10.1.s.02")
if i[0]:
	print("is ip: ", i[1])

print(IPMaskTransformCode("255.255.255.0"))

t = "akjwdh10.1.2.4kajh10.1.2.4ww192.34.5.3akhka192.333.12.45"
ip = IpStrDraw(txt=t)
print(ip)
