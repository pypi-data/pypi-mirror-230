#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/19 18:55
# @Author  : yaitza
# @Email   : yaitza@foxmail.com
import traceback
from pathlib import Path
from .yaml_handler import YamlHandler
from .xlsx_handler import XlsxHandler

class FileHandler:
	def __init__(self, file_path):
		self.file_path = file_path

	def load(self):
		try:
			file = Path(self.file_path)
			if file.suffix == '.yml':
				return YamlHandler(self.file_path).load()
			if file.suffix in [".xls", ".xlsx"]:
				return XlsxHandler(self.file_path).load()
		except Exception:
			traceback.print_exc()



