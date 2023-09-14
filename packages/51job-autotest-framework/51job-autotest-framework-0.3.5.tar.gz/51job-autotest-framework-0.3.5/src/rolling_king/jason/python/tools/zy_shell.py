#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/3/16 12:01 PM
# @Author  : zhengyu.0985
# @FileName: zy_shell.py
# @Software: PyCharm

import os
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')  # logging.basicConfig函数对日志的输出格式及方式做相关配置
logger = logging.getLogger('zy_shell')


def check_if_has_rolling():
    flag = False
    res = os.popen("python3 -m pip list | grep rolling-in-the-deep")
    lines = res.readlines()
    if len(lines) == 1:
        logging.info("【已安装】{}".format("rolling-in-the-deep"))
        flag = True
    else:
        res = os.popen("python3 -m pip install --index-url https://pypi.org/simple/ --no-deps rolling-in-the-deep")
        lines = res.readlines()
        for val in lines:
            if 'Successfully installed rolling-in-the-deep' in val or 'Requirement already satisfied' in val:
                flag = True
                break
            else:
                pass
    return flag


if __name__ == '__main__':
    logger.info(check_if_has_rolling())
