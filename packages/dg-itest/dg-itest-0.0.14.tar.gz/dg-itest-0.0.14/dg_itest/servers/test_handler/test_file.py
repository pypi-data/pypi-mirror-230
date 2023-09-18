#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/12 17:55
# @Author  : yaitza
# @Email   : yaitza@foxmail.com

import pytest
from dg_itest.servers.file_handler.file_handler import FileHandler
from dg_itest.servers.test_handler.test_item import TestItem

class TestFile(pytest.File):
    def collect(self):
        raw = FileHandler(self.fspath).load()
        for test_case in raw:
            name = test_case['test']['name']
            values = test_case['test']
            yield TestItem.from_parent(self, name=name, values=values)



