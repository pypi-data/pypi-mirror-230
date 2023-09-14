#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/1/28 4:20 下午
# @Author  : zhengyu.0985
# @FileName: zy_schedule.py
# @Software: PyCharm

import schedule
import time
import threading
import functools
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')  # logging.basicConfig函数对日志的输出格式及方式做相关配置
logger = logging.getLogger('com.autotest.db.sqlalchemy_util')


# def job():
#     print("I'm working...")
#
#
# schedule.every(10).seconds.do(job)
#
# while True:
#     schedule.run_pending()  # 检测是否执行
#     time.sleep(1)
#     logger.info("Waiting for 1 second...")

def job():
    print("I'm working...")


# 每十分钟执行任务
schedule.every(10).minutes.do(job)
# 每个小时执行任务
schedule.every().hour.do(job)
# 每天的10:30执行任务
schedule.every().day.at("10:30").do(job)
# 每个月执行任务
schedule.every().monday.do(job)
# 每个星期三的13:15分执行任务
schedule.every().wednesday.at("13:15").do(job)
# 每分钟的第17秒执行任务
schedule.every().minute.at(":17").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)


# 只运行一次
def job_that_executes_once():
    # 此处编写的任务只会执行一次...
    return schedule.CancelJob


schedule.every().day.at('22:30').do(job_that_executes_once)

while True:
    schedule.run_pending()
    time.sleep(1)


# 参数传递
def greet(name):
    print('Hello', name)


# do() 将额外的参数传递给job函数
schedule.every(2).seconds.do(greet, name='Alice')
schedule.every(4).seconds.do(greet, name='Bob')


# 获取所有作业 and 取消所有作业
def hello():
    print('Hello world')


schedule.every().second.do(hello)

all_jobs = schedule.get_jobs()  # 获取
schedule.clear()  # 取消


# .tag 打标签
schedule.every().day.do(greet, 'Andrea').tag('daily-tasks', 'friend')
schedule.every().hour.do(greet, 'John').tag('hourly-tasks', 'friend')
schedule.every().hour.do(greet, 'Monica').tag('hourly-tasks', 'customer')
schedule.every().day.do(greet, 'Derek').tag('daily-tasks', 'guest')

# get_jobs(标签)：可以获取所有该标签的任务
friends = schedule.get_jobs('friend')

# 取消所有 daily-tasks 标签的任务
schedule.clear('daily-tasks')


# 设定截止时间
# 每个小时运行作业，18:30后停止
schedule.every(1).hours.until("18:30").do(job)

# 每个小时运行作业，2030-01-01 18:33 today
schedule.every(1).hours.until("2030-01-01 18:33").do(job)

# 每个小时运行作业，8个小时后停止
schedule.every(1).hours.until(timedelta(hours=8)).do(job)

# 每个小时运行作业，11:32:42后停止
schedule.every(1).hours.until(time(11, 33, 42)).do(job)

# 每个小时运行作业，2020-5-17 11:36:20后停止
schedule.every(1).hours.until(datetime(2020, 5, 17, 11, 36, 20)).do(job)


# 立即运行所有作业，而不管其安排如何
schedule.run_all()
# 立即运行所有作业，每次作业间隔10秒
schedule.run_all(delay_seconds=10)


# 装饰器安排作业
# 此装饰器效果等同于 schedule.every(10).minutes.do(job)
@repeat(every(10).minutes)
def job():
    print("I am a scheduled job")


while True:
    run_pending()
    time.sleep(1)


# 并行执行
# 默认情况下，Schedule 按顺序执行所有作业
# 通过多线程的形式来并行每个作业

def job1():
    print("I'm running on thread %s" % threading.current_thread())
def job2():
    print("I'm running on thread %s" % threading.current_thread())
def job3():
    print("I'm running on thread %s" % threading.current_thread())

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


schedule.every(10).seconds.do(run_threaded, job1)
schedule.every(10).seconds.do(run_threaded, job2)
schedule.every(10).seconds.do(run_threaded, job3)

while True:
    schedule.run_pending()
    time.sleep(1)


# 异常处理
# Schedule 不会自动捕捉异常，它遇到异常会直接抛出

def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback
                print(traceback.format_exc())
                if cancel_on_failure:
                    return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator


@catch_exceptions(cancel_on_failure=True)
def bad_task():
    return 1 / 0


# 这样，bad_task 在执行时遇到的任何错误，都会被 catch_exceptions  捕获，这点在保证调度任务正常运转的时候非常关键。
schedule.every(5).minutes.do(bad_task)
