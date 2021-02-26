#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
帮助类
"""
import hashlib


def read_by_lines(path, encoding="utf-8"):
	"""read the data by line"""
	result = list()
	with open(path, "r", encoding="utf-8") as infile:
		for line in infile:
			if line and line.strip():
				result.append(line.strip())
	return result


def write_by_lines(path, data, t_code="utf-8"):
	"""write the data"""
	with open(path, "w") as outfile:
		[outfile.write(d + "\n") for d in data]


def cal_md5(str):
	"""calculate string md5"""
	str = str.decode("utf-8", "ignore").encode("utf-8", "ignore")
	return hashlib.md5(str).hexdigest()


def md5(s: str):
	"""
	md5加密生成32位小写字符串
	:param s:
	:return:
	"""
	m = hashlib.md5()
	m.update(s.encode(encoding='utf-8'))
	return m.hexdigest()
