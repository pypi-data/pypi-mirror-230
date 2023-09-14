#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os
import time
import logging
import uuid
import platform
from rolling_king.autotest.tests.base.base_test import BaseTest


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')  # logging.basicConfig函数对日志的输出格式及方式做相关配置
logger = logging.getLogger('requests.http_sender_module')


"""
此类暂时未使用
"""


class BaseConfTest(object):

    @staticmethod
    def make_report(item, call, out):  # item是测试用例，call是测试步骤。
        # setup、call、teardown三个阶段，每个阶段都会返回 Result 对象和 TestReport 对象以及对象属性。
        logger.info('------------------------------------')

        call_dict = call.__dict__
        logger.info("call['when'] = %s" % call_dict['when'])
        start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(call_dict['start']))
        logger.info("【%s】阶段 开始时间 = %s " % (call_dict['when'], start))
        stop = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(call_dict['stop']))
        logger.info("【%s】阶段 结束时间 = %s " % (call_dict['when'], stop))
        duration_in_sec = call_dict['duration']
        logger.info("【%s】阶段 耗时 = %f 秒" % (call_dict['when'], duration_in_sec))

        # 获取钩子方法的调用结果
        # out = yield # 这个out从函数调用中来。
        # logger.info('用例执行结果 %s' % out.__dict__)
        # 从钩子方法的调用结果中获取测试报告
        report = out.get_result()

        if report.when == "setup":
            logger.info("report.when = setup")
            pass

        # 若只获取call这一步的结果，则可以加个判断：if report.when == "call"即可。
        if report.when == "call":
            logger.info('测试报告：%s' % report)
            logger.info(
                '步骤：%s' % report.when)  # 每个测试用例执行都有三步：setup、call、teardown。（注意与setup_class方法和teardown_class方法相区分）
            logger.info('nodeid：%s' % report.nodeid)
            logger.info('description: %s' % str(item.function.__doc__))
            logger.info(('运行结果: %s' % report.outcome))
            # 以上是查看监听器获取的信息。下面是组装准备落库的dict。
            file_class_method_list = report.nodeid.split("::")
            case_record_dict = {
                "uid": '0',  # uid默认赋值'0'，因为用例记录会通过此值来判断是否是新增的用例，所以不能在此就赋uuid.uuid4().hex这个值。
                "test_class": file_class_method_list[0] + "::" + file_class_method_list[1],
                "test_method": file_class_method_list[2],
                "version": 1  # 用例版本默认存1
            }
            logger.info("测试用例 = %s" % case_record_dict)
            project_conf_dict = BaseTest.get_project_conf_dict()
            case_record_dict.update(project_conf_dict)  # 增加项目配置参数dict
            interface_dict = BaseTest.analyze_func_desc(str(item.function.__doc__))
            case_record_dict.update(interface_dict)  # 增加被测接口信息dict
            logger.info("case_record_dict = %s" % case_record_dict)
            # 把用例case_record_dict添加至BaseTest.case_record_dict_list中。
            BaseTest.case_record_dict_list.append(case_record_dict)

            # 判断是否有用到断言
            test_case_name = case_record_dict['test_method'].split("[")[0] if "[" in case_record_dict[
                'test_method'] else case_record_dict['test_method']

            # ###### 上面是测试用例信息，下面是执行结果信息。######
            execution_call_dict = {
                'uid': uuid.uuid4().hex,
                'test_unique_tag': str(BaseTest.unique_tag)
            }
            execution_call_dict.update(project_conf_dict)  # 增加项目配置参数dict
            execution_call_dict['test_interface'] = interface_dict['test_interface']
            execution_call_dict['test_inter_type'] = interface_dict['test_inter_type']
            execution_call_dict['test_class'] = file_class_method_list[0] + "::" + file_class_method_list[1]
            execution_call_dict['test_method'] = file_class_method_list[2]
            params_dict = BaseConfTest._get_params_dict(item.__dict__, execution_call_dict['test_method'])
            execution_call_dict['test_params'] = json.dumps(params_dict)  # 若仍报错可设置='{}'
            execution_call_dict['test_result'] = report.outcome
            execution_call_dict['test_assert'] = BaseConfTest.analyze_assert_by_test_method(case_record_dict['test_class'], test_case_name)  # True/False
            if "fail" in report.outcome:
                execution_call_dict['test_error_msg'] = call_dict['excinfo'].value  # <class '_pytest._code.code.ExceptionInfo'>
            else:
                execution_call_dict['test_error_msg'] = ""
            execution_call_dict['test_start_time'] = start
            execution_call_dict['test_finish_time'] = stop
            execution_call_dict['test_duration'] = int(duration_in_sec * 1000)
            # 打印并加入到List中。
            logger.info("curr_execution_call_dict = %s" % execution_call_dict)  # 打印当前用例执行记录dict。
            BaseTest.execution_record_dict_list.append(execution_call_dict)  # 将当前用例的执行记录添加至list中。

        if report.when == "teardown":
            logger.info("report.when = teardown")
            pass  # 如果在 teardown阶段添加dict到List会缺失最后一次添加的值。所以要在call阶段完成对list的添加。

        logger.info('------------------------------------')

    @staticmethod
    def function_before():
        logger.info("--- before_after_test func in conftest--Setup Section.---")
        start_time = time.time()
        start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
        logger.info("当前用例-测试开始时间 = %s" % start_time_str)

    @staticmethod
    def function_after():
        finish_time = time.time()
        finish_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(finish_time))
        logger.info("当前用例-测试结束时间 = %s" % finish_time_str)
        logger.info("--- before_after_test func in conftest--Teardown Section.---")

    @staticmethod
    def session_before(test_project_name, test_psm):
        logger.info("=== setup 前置操作：开始Pytest本次整体测试 ===")
        BaseTest.case_record_dict_list.clear()
        BaseTest.execution_record_dict_list.clear()
        BaseTest.unique_tag = int(time.time())
        BaseTest.test_project_name = test_project_name
        BaseTest.test_psm = test_psm

    @staticmethod
    def session_after():
        logger.info("=== teardown 后置操作：结束Pytest本次整体测试 ===")
        logger.info(
            "通过BaseTest.case_record_dict_list收集到本次共执行 %d 个测试用例。" % len(BaseTest.case_record_dict_list))
        BaseTest.insert_update_delete()  # Case记录的DB逻辑。
        logger.info("通过BaseTest.execution_record_dict_list收集到本次 %d 个测试结果。" % len(
            BaseTest.execution_record_dict_list))
        BaseTest.insert_execution_record()  # 执行记录的DB逻辑。

    @staticmethod
    def summary(terminalreporter, exitstatus, config):
        logger.info("=================================")
        terminal_reporter_dict = terminalreporter.__dict__
        logger.info(terminal_reporter_dict)  # Python自省，输出terminalreporter对象的属性字典
        total_case_dict = BaseConfTest._get_total_case_dict(terminal_reporter_dict['stats'])
        for key, record_list in total_case_dict.items():
            if len(record_list) > 0:
                for report in record_list:
                    logger.info("%s : %s = %s" % (key, report.nodeid, report.outcome))
        logger.info("---------------------------------")
        # 基于PSM，获取未测试到的接口，并落入未测试覆盖的MySQL库。
        # CoverDiff.get_diff_result(protocol="BOTH")
        logger.info("---------------------------------")
        duration = time.time() - terminalreporter._sessionstarttime
        logger.info('Total Time Cost: %.2f seconds.' % duration)
        logger.info(exitstatus)
        logger.info(config)
        logger.info("=================================")

    @staticmethod
    def _get_total_case_dict(terminal_reporter_stats_dict):
        passed_case_report_list = []
        failed_case_report_list = []
        skipped_case_report_list = []
        for key, val in terminal_reporter_stats_dict.items():
            if key == '':
                logger.info("当前key = %s，代表 %s" % (key, "setup_teardown"))
            elif key == 'passed' or key == 'xpassed':
                logger.info("当前key = %s, 共计 %d 个" % (key, len(val)))
                passed_case_report_list.extend(val)
            elif key == 'failed' or key == 'xfailed':
                logger.info("当前key = %s, 共计 %d 个" % (key, len(val)))
                failed_case_report_list.extend(val)
            elif key == 'skipped':
                logger.info("当前key = %s, 共计 %d 个" % (key, len(val)))
                skipped_case_report_list.extend(val)
        total_record_count = len(passed_case_report_list) + len(failed_case_report_list) + len(skipped_case_report_list)
        logger.info("本次测试一共执行了 %d 个用例。" % total_record_count)
        return {
            "passed": passed_case_report_list,
            "failed": failed_case_report_list,
            "skipped": skipped_case_report_list
        }

    @staticmethod
    def _get_params_dict(item_dict, test_method):
        params_dict = {}  # 要返回的值
        for mark in item_dict['own_markers']:
            if mark.name == 'parametrize':
                args_tuple = mark.args  # ('code_id, exp_resp_code', [('py-autotest-top-baidu-2021-12-06_20:43:52', 'PG0000'), ('py-autotest-top-baidu-1', '207007')])
                if isinstance(args_tuple[0], list):
                    params_key_list = args_tuple[0]
                else:
                    params_key_list = args_tuple[0].split(",")
                key_count = len(params_key_list)
                params_value_list = args_tuple[1]

                node_key_words = item_dict['keywords']  # .<class '_pytest.mark.structures.NodeKeywords'>
                function_node = node_key_words.node  # .<class '_pytest.python.Function'>
                real_test_func_name = function_node.name
                logger.info(
                    "real_test_func_name = %s" % real_test_func_name)  # test_post_with_python3[py-autotest-top-baidu-2021-12-06_21:19:07-PG0000]
                index_left = real_test_func_name.find("[")
                if index_left != -1:
                    index_left += 1
                    index_right = len(real_test_func_name) - 1
                    real_parametrize_name = real_test_func_name[
                                            index_left: index_right]  # py-autotest-top-baidu-2021-12-06_21:19:07-PG0000
                else:
                    real_parametrize_name = ""
                logger.info("real_parametrize_name = %s" % real_parametrize_name)
                if key_count > 1:
                    for curr_param_values in params_value_list:
                        if type(curr_param_values).__name__ == 'tuple':  # 有多个参数化参数。
                            curr_params_join_name = "-".join(curr_param_values)  # 此时curr_param_values是个tuple
                            logger.info("curr_params_join_name = %s" % curr_params_join_name)
                            if curr_params_join_name == real_parametrize_name:  # 找到了本次执行的参数化值，相匹配
                                logger.info("参数化变量只有 %d 个，参数化值类型为 %s" % (
                                key_count, type(curr_param_values).__name__))
                                for index in range(0, key_count):
                                    curr_val = curr_param_values[index]
                                    params_dict[params_key_list[index].strip()] = str(curr_val) if type(curr_val).__name__ == 'datetime' else curr_val
                                logger.info("params_dict = %s" % params_dict)
                                break
                            else:
                                pass
                        else:
                            logger.info("参数化变量只有 %d 个，参数化值类型为 %s" % (
                            key_count, type(curr_param_values).__name__))
                    # End For
                elif key_count == 1:  # 只有一个参数化参数
                    logger.info("params_key_list[0] = %s" % params_key_list[0])  # custom_param_dict
                    logger.info("test_method = %s" % test_method)  # test_post_with_python3[custom_param_dict0]
                    if params_key_list[0] in test_method:
                        index = test_method.find(params_key_list[0])
                        length = len(params_key_list[0])
                        exact_position = index + length
                        count_index = int(test_method[exact_position:-1])
                        logger.info("当前是第 %d 次参数化执行" % count_index)
                        curr_param_values = params_value_list[count_index]
                        if type(curr_param_values).__name__ == 'dict':  # 一个dict作为参数化参数。
                            logger.info("参数化变量只有 %d 个，参数化值类型为 %s" % (
                            key_count, type(curr_param_values).__name__))
                            params_dict[params_key_list[0]] = curr_param_values
                            logger.info("params_dict = %s" % params_dict)
                        else:
                            logger.info("参数化变量只有 %d 个，参数化值类型为 %s" % (
                            key_count, type(curr_param_values).__name__))
                            params_dict[params_key_list[0]] = str(curr_param_values) if type(curr_param_values).__name__ == 'datetime' else curr_param_values
                            logger.info("params_dict = %s" % params_dict)
                    else:
                        logger.error("不包含 %s" % (params_key_list[0]))
                else:
                    logger.info("该测试方法没有参数，非参数化执行。")
                break
            else:
                pass
        return params_dict

    @staticmethod
    def _get_parametrize_name_list(item_func_dict):
        if 'pytestmark' in item_func_dict.keys():
            mark_list = item_func_dict['pytestmark']
            parametrize_name_list = []
            for curr_mark in mark_list:
                if curr_mark.name == 'parametrize':
                    args_tuple = curr_mark.args
                    print(args_tuple)
                    if args_tuple[0].find(",") != -1:  # 有多个参数
                        for curr_param_name in args_tuple[0].split(","):
                            parametrize_name_list.append(curr_param_name.strip())
                    else:
                        parametrize_name_list.append(args_tuple[0])  # 只有一个参数
                    break
                else:
                    pass
            return parametrize_name_list
        else:
            return []
            # End For Loop

    @staticmethod
    def analyze_assert_by_test_method(pytest_file_class: str, test_case_name: str) -> bool:
        logger.info("analyze_assert_by_test_method")
        assertion_flag: bool = False
        # if "::" in pytest_file_class:
        #     file_path = pytest_file_class.split("::")[0]
        #     test_class = pytest_file_class.split("::")[1]
        #     curr_sys_path = os.getcwd()
        #     logger.info(f"curr_sys_path={curr_sys_path}")
        #     index_of_com = curr_sys_path.find("com")
        #     if index_of_com != -1:
        #         # 下面一行是绝对路径传入获取配置文件的方法。
        #         test_file_abs_path = curr_sys_path[0:index_of_com] + file_path
        #     else:
        #         logger.info("被测路径不包含com")
        #         if str(platform.system().lower()) == 'windows':
        #             test_file_abs_path = curr_sys_path + '\\' + file_path
        #         else:
        #             test_file_abs_path = curr_sys_path + '/' + file_path
        #     logger.info(f"test_file_abs_path={test_file_abs_path}")
        #     with open(file=test_file_abs_path, mode='r', encoding="utf8") as f:
        #         file_content = f.read()
        #         line_list = file_content.split("\n")
        #         test_class_line_num: int = 0
        #         test_case_start_line_num: int = 0
        #         test_case_line_indent_count = 0
        #         line_num = 0
        #         for curr_line in line_list:
        #             line_num += 1
        #             if curr_line.strip().startswith("#"):
        #                 logger.info(f"第{line_num}行是纯注释行")
        #             elif test_class in curr_line:
        #                 logger.info(f"测试类={test_class}，在第{line_num}行。")
        #                 test_class_line_num = line_num
        #             elif "def "+test_case_name in curr_line and line_num > test_class_line_num > 0:
        #                 logger.info(f"测试类={test_class}，用例={test_case_name}，从第{line_num}行开始。")
        #                 test_case_start_line_num = line_num
        #                 test_case_line_indent_count = BaseConfTest.__count_space(curr_line)
        #             elif line_num > test_case_start_line_num > test_class_line_num and test_case_line_indent_count == BaseConfTest.__count_space(curr_line):
        #                 logger.info(f"测试类={test_class}，用例={test_case_name}，到第{line_num-1}行结束。")
        #                 break
        #             else:  # 测试方法体中的内容
        #                 if line_num > test_case_start_line_num and curr_line.strip().startswith("assert"):
        #                     logger.info(f"测试类={test_class}，用例={test_case_name}，在第{line_num}行使用了断言。")
        #                     assertion_flag = True
        #                 else:
        #                     continue
        # else:
        #     logger.warning(f"pytest_file_class={pytest_file_class}, 不包含::")
        return assertion_flag

    @staticmethod
    def __count_space(content: str):
        for i, j in enumerate(content):
            if j != ' ':
                return i

