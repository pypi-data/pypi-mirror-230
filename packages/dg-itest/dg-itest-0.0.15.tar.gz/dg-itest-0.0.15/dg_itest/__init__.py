#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/20 11:16
# @Author  : yaitza
# @Email   : yaitza@foxmail.com

__all__ = ["DgItest"]

import os
import logging
import sys
from pathlib import *
from dg_itest.utils.env_generater import EnvGenerater

import pytest

_logger = logging.root

def set_logger(new_logger):
    global _logger
    _logger = new_logger


def get_logger():
    global _logger
    return _logger

host_url = ""
local_test_res = ""

class DgItest:
    '''
    接口自动化测试框架
    '''
    def __init__(self, url, test_src, test_res):
        '''
        url: 测试地址Host
        test_src: 测试用例归档目录
        test_res: 测试资源归档目录
        '''
        global host_url
        host_url = url
        global local_test_res
        local_test_res = test_res
        self.test_src = test_src


    def __generate_conftest__(self, test_src):
        if Path(f'{test_src}/conftest.py').exists():
            return

        python_code ='''
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/20 16:06
# @Author  : dg-itest
# @Email   : yaitza@foxmail.com

from dg_itest.servers.test_handler.test_file import *

def pytest_collect_file(parent, path):
    if path.ext in [".yml", ".xls", ".xlsx"] and path.basename.startswith("test"):
        return TestFile.from_parent(fspath=path, parent=parent)
        '''

        with Path(f'{test_src}/conftest.py').open(mode='w') as f:
            f.write(python_code)

    def run(self):
        self.__generate_conftest__(self.test_src)

        test_report = 'test_report/result/'

        if not Path(test_report).exists():
            Path(test_report).mkdir(parents=True)

        pytest.main(['-s', self.test_src, '--alluredir', Path(test_report).resolve().as_posix()])

        try:
            # 生成allure report中environment相关配置
            EnvGenerater.generate_env_file(host_url, Path(test_report))

            # 本地生成allure report 使用; 本地生成报告使用，commit时请注释
            os.system("allure generate ./test_report/result/ -o ./test_report/report --clean")
        except Exception:
            get_logger().error("请确保本地安装有allure，参考：https://docs.qameta.io/allure/")

if __name__ == '__main__':
    url = sys.argv[0]
    test_src = sys.argv[1]
    test_res = sys.argv[2]

    DgItest(url, test_src, test_res).run()