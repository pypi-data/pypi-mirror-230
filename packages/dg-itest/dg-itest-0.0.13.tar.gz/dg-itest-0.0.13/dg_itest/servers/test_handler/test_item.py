#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/19 18:25
# @Author  : yaitza
# @Email   : yaitza@foxmail.com
import json
import re
import pytest
import jsonpath
from pathlib import *
from dg_itest import local_test_res
from dg_itest.utils.diff_helper import DiffHelper
from dg_itest.servers.dg_servers.dg_singleton import DgSingleton
from dg_itest.utils.cache import local_cache
from dg_itest.utils.replace import Replace


class TestItem(pytest.Item):
    def __init__(self, name, parent, values):
        super(TestItem, self).__init__(name, parent)
        self.name = name
        self.values = values
        self.request = self.values.get("request")
        self.validate = self.values.get("validate")
        self.expect = self.values.get('expect')

    def runtest(self):
        request_data = self.replace(self.values['request'])
        params = request_data.get("params")
        if "files" in params.keys():
            params.update({"files": self.get_files(params.get("files"))})
        request_data.pop("params")
        request_data.update(params)

        try:
            api = DgSingleton().apis
            response = api.http_request(**request_data)
        except Exception as ex:
            print("request Error！\n" + str(ex))

        self.assert_response(response)

    # todo 断言类型需要增加，目前只支持eq(相等)。
    def assert_response(self, response):
        for item in self.validate:
            if "eq" in item.keys():
                validate_rule = item.get("eq")
                actual_result = jsonpath.jsonpath(response.json(), validate_rule)
                expect_result = jsonpath.jsonpath(self.expect.get('json'), validate_rule)

                if isinstance(actual_result, list) and isinstance(expect_result, list):
                    actual_result = sorted(actual_result)
                    expect_result = sorted(expect_result)
                assert actual_result == expect_result, '\n' + DiffHelper.diff(str(actual_result), str(expect_result))
            if "sa" in item.keys():
                sa_value = item.get("sa")
                for sa_item_key in sa_value.keys():
                    sa_item_value =  jsonpath.jsonpath(response.json(), sa_value.get(sa_item_key))
                    assert type(sa_item_value) is list and len(sa_item_value) > 0, '\n' + '未获取到值'
                    local_cache.put(f"${sa_item_key}$", sa_item_value[0])

    def replace(self, source):
        pattern_str = r'\$.*?\$'
        source_str = json.dumps(source)
        pattern = re.compile(pattern_str, re.DOTALL)
        match_items = pattern.findall(source_str)
        update = {}
        for items in match_items:
            update.update({items: local_cache.get(items)})
        if len(update.keys()) > 0:
            result = Replace.replace(pattern_str, source, update)
            return result
        else:
            return source

    def get_files(self, files_array):
        all_resource_files = Path(local_test_res).rglob("*.*")
        files_buffer = []
        for file_name in files_array:
            file = [file_item for file_item in all_resource_files if file_item.name == file_name]
            if len(file) > 0:
                suffix = file[0].suffix
                if suffix in ['.jpg', '.jpeg', '.png']:
                    content_type = f'image/{suffix.lstrip(".")}'
                else:
                    content_type = f'application/{suffix.lstrip(".")}'

                files_buffer.append(('file', (file_name, open(file[0].resolve(), 'rb'), content_type)))
            else:
                continue
        return files_buffer

