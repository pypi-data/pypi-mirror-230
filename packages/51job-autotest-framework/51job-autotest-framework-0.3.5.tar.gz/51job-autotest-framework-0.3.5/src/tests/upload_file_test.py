#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/8/20 8:19 PM
# @Author  : zhengyu.0985
# @FileName: upload_file_test.py
# @Software: PyCharm
import pytest
import requests


class TestUploadFile(object):

    # def test_upload_file_by_form_data(self):
    #     host_url = "XXX"
    #     sub_uri = "xx/xx/xx"
    #     data = {
    #         "modelId": 10,
    #         "file": "MODEL.xlsx"
    #     }
    #     files = {
    #         "file": open("/Users/zy/Desktop/MODEL.xlsx", "rb")
    #     }
    #     headers = {
    #         "token": "token_value",
    #         "currentId": "5",
    #     }
    #     requests.request("POST", host_url+sub_uri, headers=headers, data=data, files=files)

    # 下面这个测试用例是我自己springboot服务的上传接口仅用于测试验证。
    def test_my_upload_file_by_form_data(self):
        host_url = "http://127.0.0.1:8082"
        sub_uri = "/upload"
        file_obj = open("/Users/admin/Desktop/Empty.xlsx", mode='rb', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)
        data = { # data里这两种写法均可。
            "uploadFile": "/Users/admin/Desktop/Empty.xlsx"
            # "uploadFile": file_obj
        }
        files = {
            "uploadFile": open("/Users/admin/Desktop/Empty.xlsx", "rb")
        }
        headers = {
            "token": "token_value",
            "currentId": "5",
        }
        requests.post(host_url+sub_uri, headers=headers, data=data, files=files)


if __name__ == '__main__':
    pytest.main(["-s",  "upload_file_test.py"])
