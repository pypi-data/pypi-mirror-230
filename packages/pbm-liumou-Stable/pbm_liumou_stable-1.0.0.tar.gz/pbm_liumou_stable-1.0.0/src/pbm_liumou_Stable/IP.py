#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   IP.py
@Time    :   2023-04-03 15:25
@Author  :   坐公交也用券
@Version :   1.0
@Contact :   liumou.site@qq.com
@Homepage : https://liumou.site
@Desc    :   当前文件作用
"""
import re
import socket


def _dic():
	info = {16: "255.255.0.0",
	        17: "255.255.128.0",
	        18: "255.255.192.0",
	        19: "255.255.224.0",
	        20: "255.255.240.0",
	        21: "255.255.248.0",
	        22: "255.255.252.0",
	        23: "255.255.254.0",
	        24: "255.255.255.0",
	        25: "255.255.255.128",
	        26: "255.255.255.192",
	        27: "255.255.255.224",
	        28: "255.255.255.240",
	        29: "255.255.255.248",
	        30: "255.255.255.252",
	        31: "255.255.255.254",
	        32: "255.255.255.255"}
	return info


def IPMaskTransformCode(mask: str):
	"""
	通过IP掩码地址获取掩码位数,例如: 255.255.255.0返回24
	:param mask:
	:return: int
	"""
	info = _dic()
	for i in info:
		if mask == info[i]:
			return int(i)
	return False


def IPMaskTransformIp(mask: int):
	"""
	通过掩码数获取掩码地址,例如: 24返回255.255.255.0
	:param mask:
	:return: int
	"""
	info = _dic()
	for i in info:
		if mask == i:
			return info[i]
	return False


def IsIpv4(ip: str):
	"""
	检查是否属于标准的IPV4地址,返回布尔值和最终IP地址
	:param ip: 需要判断的IP地址
	:return: (bool, ip)
	"""
	tmp = ""
	s = 1
	sp = str(ip).split(".")
	if len(sp) != 4:
		print("IP格式错误")
		return False, "IP格式错误"
	for i in sp:
		try:
			i = int(i)
		except Exception as e:
			print(e)
			print("IP格式错误,请传入由整数和.组成的IPV4地址")
			return False, "IP格式错误,请传入由整数和.组成的IPV4地址"
		if int(i) > 255:
			print("存在值大于255的IP元素")
			return False, "存在值大于255的IP元素"
		if int(i) < 0:
			print("存在负整数")
			return False, "存在负整数"
		if len(str(i)) == 2:
			if str(i)[0] == 0:
				print("存在0开头的元素")
				return False, "存在0开头的元素"
		if s == 4:
			tmp = tmp + str(i)
		else:
			tmp = tmp + str(i) + "."
		s += 1
	return True, tmp


def IpCutSub(ip: str):
	"""
	:param ip:
	:return: str/bool
	"""
	if IsIpv4(ip=ip)[0]:
		sp = str(ip).split(".")
		sub = str(sp[0]) + "." + str(sp[1]) + "." + str(sp[2])
		return sub
	return False


def IpStrDraw(txt: str):
	"""
	从一串字符串中提取匹配的IPV4地址
	:param txt: 需要提取的文本字符串
	:return:
	"""
	result = re.findall(r'\D(?:\d{1,3}\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\D', txt)
	ret_start = re.match(r'(\d{1,3}\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\D', txt)
	if ret_start:
		result.append(ret_start.group())
	ret_end = re.search(r'\D(\d{1,3}\.){3}(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$', txt)
	if ret_end:
		result.append(ret_end.group())
	ip_list = []
	if len(result) >= 1:
		for r in result:
			ret = re.search(r'((25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)', r)
			if ret:
				ip_list.append(ret.group())
	return ip_list


def get_local_ip(server="119.29.29.29", port=53):
	"""
	通过请求一个地址获取本机IP地址(局域网)
	:return:
	"""
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		# 连接到一个公网地址，这里以百度的服务器为例
		s.connect((server, port))
		# 获取本地IP
		local_ip = s.getsockname()[0]
	except Exception as e:
		print("无法获取公网IP，错误信息：", e)
		return None
	finally:
		s.close()
	return local_ip