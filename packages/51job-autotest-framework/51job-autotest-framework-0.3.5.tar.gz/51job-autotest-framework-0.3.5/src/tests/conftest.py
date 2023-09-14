#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/4/2 10:37 AM
# @Author  : zhengyu.0985
# @FileName: conftest.py
# @Software: PyCharm

import pytest


def pytest_addoption(parser):
    print("pytest_addoption func executes...")
    parser.addoption(
        "--cmdopt", action="store", default="type1", help="my option: type1 or type2"
    )
    parser.addoption(
        "--env", action="store", default="dev", choices=['dev', 'test'], type=str, help="env：表示测试环境，默认dev环境"
    )


# @pytest.fixture(scope="module")
# def cmdopt(pytestconfig):
#     return pytestconfig.getoption("cmdopt")

@pytest.fixture(scope="module")
def cmdopt(request):
    return request.config.getoption("--cmdopt")


@pytest.fixture(scope="module")
def env(request):
    print("execute...")
    return request.config.getoption("--env")
