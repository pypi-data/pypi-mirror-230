#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/4/2 10:41 AM
# @Author  : zhengyu.0985
# @FileName: test_options.py
# @Software: PyCharm

import pytest
import os


def test_option(env):
    if env == 'dev':
        print("当前测试环境为：{}，域名切换为开发环境".format(env))
    elif env == 'test':
        print("当前测试环境为：{}，域名切换为测试环境".format(env))
    else:
        print("环境错误，当前环境{}不存在".format(env))


def test_param(cmdopt):
    print("current path={}".format(os.getcwd()))
    print(cmdopt)


if __name__ == '__main__':
    # pytest.main(['-s', './src/tests/test_options.py', '--env=test'])
    pytest.main(['-s', '--cmdopt=abc', '--env=test', 'test_options.py'])
