#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/21 14:44
# @Author  : yaitza
# @Email   : yaitza@foxmail.com
import json
import re

class Replace:
	@staticmethod
	def replace(pattern: str, source, update : dict):
		if isinstance(source, str):
			result = Replace.replace_str(pattern, source, update)
		elif isinstance(source, dict):
			result = Replace.replace_dict(pattern, source, update)
		else:
			result = source
		return result


	@classmethod
	def replace_str(cls, pattern: str, source: str, update: dict) -> str:
		re_pattern = re.compile(pattern, re.DOTALL)
		match_results = re_pattern.findall(source)

		for item in match_results:
			source = source.replace(item, update.get(item))
		return source

	@classmethod
	def replace_dict(cls, pattern: str, source: dict, update) -> dict:
		re_pattern = re.compile(pattern, re.DOTALL)
		match_results = re_pattern.findall(json.dumps(source))
		result = {}
		for match_item in match_results:
			result = replace(source, match_item, update.get(match_item))
		return result


def replace(source: dict, match_item: str, update) -> dict:
	for k, v in source.items():
		if isinstance(v, dict):
			source[k] = replace(v, match_item, update)
		elif isinstance(v, list):
			if match_item in v:
				match_index = v.index(match_item)
				v[match_index] = update
				source.update({k: v})
		elif isinstance(v, str):
			if v == match_item:
				source.update({k: update})
			elif v.__contains__(match_item):
				replace_v = v.replace(match_item, str(update))
				source.update({k: replace_v})
			else:
				pass
		else:
			pass

	return source