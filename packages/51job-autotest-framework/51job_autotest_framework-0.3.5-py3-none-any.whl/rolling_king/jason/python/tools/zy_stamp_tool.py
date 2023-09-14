#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/3/8 4:08 下午
# @Author  : zhengyu.0985
# @FileName: zy_stamp_tool.py
# @Software: PyCharm

from datetime import datetime
import time


class TimeStampExchange(object):

    @staticmethod
    def stamp2datetime(stamp_val=None) -> str:
        if stamp_val is None:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif len(str(stamp_val)) == 13:
            return datetime.fromtimestamp(stamp_val/1000).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return datetime.fromtimestamp(stamp_val).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def datetime2stamp(date_time_str=None, stamp_digits=10) -> int:
        if date_time_str is None:
            date_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
        if stamp_digits == 13:
            return int(time.mktime(date_time_obj.timetuple()) * 1000 + date_time_obj.microsecond / 1000)
        else:
            return int(date_time_obj.timestamp())


if __name__ == '__main__':
    val = TimeStampExchange.stamp2datetime(1646201351000)
    print(val)
    print('-----------')
    val = TimeStampExchange.datetime2stamp("2022-03-02 14:09:11", 13)
    print(val)
