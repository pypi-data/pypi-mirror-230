#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/21 17:02
# @Author  : yaitza
# @Email   : yaitza@foxmail.com

from dg_itest.utils.replace import Replace

def test_replace():
	pattern = r'\$.*?\$'
	source = {'test': '123', 'key': {'key1': {'key1': ['$change1$', '$change2$']}, 'key2': ['change1', 'change2']}}
	update = {'$change1$': {'key': 'source_file.png', 'value': '/data/test1.png'}, '$change2$': {'key': 'target_file.png', 'value': '/data/test1.png'}}

	result = Replace.replace_dict(pattern, source, update)
	print(result)

