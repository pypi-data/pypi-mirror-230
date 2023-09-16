#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import json
import os
import zipfile

import xmind

from xmind2testcasezen import const, xmind_to_dict


def parser_xmind_to_dict(path="demo2.xmind"):
    input_source = get_absolute_path(path)
    xmind_content_json_dict = {}
    xmind_content_xml_dict = {}

    with extract(input_source) as input_stream:
        for stream in input_stream.namelist():
            # 如果存在content.json文件，使用该文件进行解析并返回
            if stream == "content.json":
                xmind_content_json_dict = json.loads(input_stream.open(stream).read())
                # 使用的是“测试用例”lebels标记用例使用新方法
                if recurse_key_search(xmind_content_json_dict, "labels", const.TESTCASE_TAG):
                    return const.TAG_JSON, xmind_content_json_dict
                else:
                    return const.TAG_PRO, xmind_to_dict(input_source)
    if not xmind_content_json_dict:
        workbook = xmind.load(input_source)
        xmind_content_xml_dict = workbook.getData()

    return const.TAG_XML, xmind_content_xml_dict


def extract(path):
    return zipfile.ZipFile(path, "r")


def get_absolute_path(path):
    """
    Return the absolute path of a file

    If path contains a start point (eg Unix '/') then use the specified start point
    instead of the current working directory. The starting point of the file path is
    allowed to begin with a tilde "~", which will be replaced with the user's home directory.
    """
    fp, fn = os.path.split(path)
    if not fp:
        fp = os.getcwd()
    fp = os.path.abspath(os.path.expanduser(fp))
    return os.path.join(fp, fn)


def recurse_key_search(data, target_key, target_value):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key and target_value in value:
                return value
            elif isinstance(value, (dict, list)):
                result = recurse_key_search(value, target_key, target_value)
                if result is not None:
                    return result
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                result = recurse_key_search(item, target_key, target_value)
                if result is not None:
                    return result
    return None
