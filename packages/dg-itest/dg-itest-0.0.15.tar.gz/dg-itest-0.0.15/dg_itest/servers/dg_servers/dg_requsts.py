#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/4/27 11:35
# @Author  : yaitza
# @Email   : yaitza@foxmail.com

import requests
import allure
from dg_itest import get_logger, host_url

class DgRequests(object):
	def __init__(self):
		self.server_url = host_url

	def http_request(self, method, url, headers=None, **kwargs):
		"""
		针对接口封装.
		"""
		method = method.upper()

		request_headers = {'finger': 'auto_test'}
		if headers is not None:
			request_headers.update(headers)
		get_logger().info(f'inputs params: {str(kwargs)}')
		result = requests.request(method, url=self.server_url + url, headers=request_headers, **kwargs)
		get_logger().info(f'response: {str(result.json())} \n')
		return result
