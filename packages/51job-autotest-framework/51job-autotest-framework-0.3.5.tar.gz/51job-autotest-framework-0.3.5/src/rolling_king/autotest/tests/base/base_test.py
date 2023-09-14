#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2021/12/8 3:26 下午
# @Author  : zhengyu.0985
# @FileName: base_test.py
# @Software: PyCharm
import uuid

from rolling_king.autotest.db.sqlalchemy_util import AlchemyUtil
from rolling_king.autotest.db.db_models import CaseRecordDecoder, CaseRecordModel, ExecutionRecordModel, ExecutionRecordDecoder, ExecutionStatisticModel
import logging
import configparser
import json
import os
import time

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')  # logging.basicConfig函数对日志的输出格式及方式做相关配置
logger = logging.getLogger('requests.http_sender_module')


class BaseTest(object):

    conf_absolute_path = "../../../conf/"  # 默认值是一个相对路径，但若测试类的python文件绝对路径包含com，则会被修改为绝对路径以适用。
    case_record_dict_list = []  # 每次测试执行收集测试用例信息的列表。
    # 以下属性是测试执行记录所用到
    unique_tag = None  # 每次测试执行的唯一标识。
    execution_record_dict_list = []  # 每次测试执行收集测试执行结果的列表。
    test_project_name = ''
    test_psm = ''

    @staticmethod
    def _get_project_param_dict(project_conf_file_path: str = ''):
        if project_conf_file_path == '':
            test_dict_val = {
                "test_project_name": BaseTest.test_project_name,
                "test_psm": BaseTest.test_psm
            }
        else:
            project_conf_file = open(project_conf_file_path)
            cf = configparser.ConfigParser()
            cf.read_file(project_conf_file)
            logger.info("从 %s 读取到 %d 个配置项。" % (project_conf_file_path, len(cf.items())))
            test_dict_val = {
                "test_project_name": cf.get("project", "TEST_PROJECT_NAME"),
                "test_psm": cf.get("project", "TEST_PSM")
            }
        logger.info("项目参数 = %s" % test_dict_val)
        return test_dict_val

    @staticmethod
    def get_project_conf_dict():
        curr_sys_path = os.getcwd()
        index_of_com = curr_sys_path.find("com")
        if index_of_com != -1:
            # 下面一行是绝对路径传入获取配置文件的方法。
            BaseTest.conf_absolute_path = curr_sys_path[0:index_of_com] + "com/conf/"
            project_param_dict = BaseTest._get_project_param_dict(BaseTest.conf_absolute_path + "project.conf")
        else:
            # 下面一行的相对路径会随测试py文件位置而变化，仅在测试文件绝对路径中不包含com时，做默认三层情况使用。
            project_param_dict = BaseTest._get_project_param_dict()
        return project_param_dict

    @staticmethod
    def analyze_func_desc(entire_desc):
        tested_inter_dict_val = {
            "test_interface": "",
            "test_inter_type": "",
            "test_description": "",
        }
        desc_list = entire_desc.split("\n")
        for seg in desc_list:
            if seg.find("desc") != -1:
                start_index_desc = seg.find("desc") + 5
                test_description = seg[start_index_desc:].strip()
                tested_inter_dict_val['test_description'] = test_description
            if seg.find("api_info") != -1:
                start_index_api_info = seg.find("api_info") + 9
                desc_dict_str = seg[start_index_api_info:].strip()
                api_dict = json.loads(desc_dict_str)
                protocol = str(api_dict['protocol_type']).upper().strip()
                if protocol == "HTTP":
                    if api_dict['method_name'] is None or len(str(api_dict['method_name'])) == 0:
                        tested_inter_dict_val['test_inter_type'] = protocol
                    else:
                        # 若是HTTP类型且method_name不为空，则用method_name的值PUT GET POST DELETE来存入DB的test_inter_type字段。
                        tested_inter_dict_val['test_inter_type'] = str(api_dict['method_name']).upper().strip()
                    tested_inter_dict_val['test_interface'] = api_dict['inter_name'] + "::" + api_dict['inter_path']
                elif protocol == "RPC":
                    tested_inter_dict_val['test_inter_type'] = protocol
                    tested_inter_dict_val['test_interface'] = api_dict['inter_name'] + "." + api_dict['method_name']
                else:
                    logger.error("传入的protocol既不是HTTP也不是RPC。")
                logger.info(f"test_inter_type={tested_inter_dict_val['test_inter_type']}")
        logger.info("被测接口 = %s" % tested_inter_dict_val)
        return tested_inter_dict_val

    @staticmethod
    def _get_db_rela_conf_path(db_conf_path=None):
        if db_conf_path is not None:
            return db_conf_path
        else:
            curr_sys_path = os.getcwd()
            logger.info(f"curr_sys_path={curr_sys_path}")
            index_of_com = curr_sys_path.find("com")
            if index_of_com != -1:
                # 下面一行是绝对路径传入获取配置文件的方法。
                BaseTest.conf_absolute_path = curr_sys_path[0:index_of_com] + "com/conf/"
            else:
                logger.warning("被测路径不包含com。")
                BaseTest.conf_absolute_path = curr_sys_path + "/com/conf/"
            return BaseTest.conf_absolute_path + "db.conf"

    @staticmethod
    def insert_update_delete():
        # db_dict_val = AlchemyUtil.get_db_param_dict("QA_DB", BaseTest._get_db_rela_conf_path())  # 旧用法
        db_dict_val = BaseTest.get_db_param_dict("QA_DB")
        site_rel_db_engine = AlchemyUtil.init_engine(db_dict_val)
        AlchemyUtil.init_db(site_rel_db_engine)  # 创建表（存在则不创建）
        site_rel_db_session = AlchemyUtil.get_session(site_rel_db_engine)
        # 先删除自身本地调试的用例记录
        deleted_debug_case_records_count = AlchemyUtil.delete_for_criteria_commit(
            site_rel_db_session, CaseRecordModel, criteria_set={
                CaseRecordModel.test_project_name == '',
                CaseRecordModel.test_psm == ''
            })
        logger.info(f'Totally delete previous {deleted_debug_case_records_count} debug case records')
        # 下面开始对本次测试的用例做分析。
        case_change_flag = False  # 用来判断是否本次执行相对于DB中的已存记录有变化（新增了或者删除了用例）
        project_conf_dict = BaseTest.get_project_conf_dict()
        # 查询
        criteria_set = {  # 这是<class 'set'>类型。
            CaseRecordModel.test_psm == project_conf_dict['test_psm'],  # 被测PSM
            CaseRecordModel.test_project_name == project_conf_dict['test_project_name']  #测试项目名
        }
        # 获取DB中的test_psm和test_project_name条件的用例记录。
        db_case_record_model_list = AlchemyUtil.query_obj_list(site_rel_db_session, CaseRecordModel, criteria_set=criteria_set)
        # 获取本次TEST的用例记录。
        test_case_record_model_list = []
        for curr_case_dict in BaseTest.case_record_dict_list:
            test_case_record_model_list.append(CaseRecordDecoder.dict_to_obj(curr_case_dict))
        # 将TEST与DB所存的用例记录做对比，以判断是要插入还是更新还是删除。
        logger.info("DB中现有记录：%d 个。" % len(db_case_record_model_list))
        logger.info("本次测试记录：%s 个。" % len(test_case_record_model_list))
        if len(db_case_record_model_list) == 0:  # DB中没有现存记录，全是新增，直接插入即可。
            # 在插入前为uid赋实际值。
            ready_insert_test_case_model_list: list[CaseRecordModel] = []
            for test_case_model in test_case_record_model_list:
                test_case_model.uid = uuid.uuid4().hex
                ready_insert_test_case_model_list.append(test_case_model)
            # 正式插入
            AlchemyUtil.insert_list_with_flush_only(site_rel_db_session, ready_insert_test_case_model_list)
            AlchemyUtil.do_commit_only(site_rel_db_session)
        elif len(test_case_record_model_list) > 0:  # DB中有现有记录且本次测试用例数>0
            curr_version_in_db = db_case_record_model_list[0].version  # 获取当前DB中相关用例的版本号。
            matched_db_record_uid_list = []
            disuse_db_record_uid_list = []
            for db_case_model in db_case_record_model_list:
                logger.info("***当前 db_case_model: test_class=%s, test_method=%s, uid=%s" % (db_case_model.test_class, db_case_model.test_method, db_case_model.uid))
                for test_case_model in test_case_record_model_list:
                    # 当前db记录跟每一个测试记录比较。
                    logger.info("---当前 test_case_model: test_class=%s, test_method=%s" % (test_case_model.test_class, test_case_model.test_method))
                    if db_case_model.test_class == test_case_model.test_class and db_case_model.test_method == test_case_model.test_method:
                        logger.info("找到 test_class=%s, test_method=%s 的 uid=%s DB记录：%s" % (db_case_model.test_class, db_case_model.test_method, db_case_model.uid, db_case_model.to_json()))
                        test_case_model.uid = db_case_model.uid  # 原本test_case_model.uid='0'，找到匹配的就存DB中的uid的值。
                        logger.info("当前 test_case_model: test_class=%s, test_method=%s 设为 uid=%s" % (test_case_model.test_class, test_case_model.test_method, test_case_model.uid))
                        matched_db_record_uid_list.append(db_case_model.uid)
                        logger.info("当前 db_case_model uid=%s 加入匹配列表中" % db_case_model.uid)
                        break
                    else:
                        pass
                    # End Inner For Loop
                if db_case_model.uid not in matched_db_record_uid_list:  # 跟所有测试记录比对之后还未匹配，说明该条DB记录跟所有测试记录都不匹配，已经作废。
                    case_change_flag = True
                    disuse_db_record_uid_list.append(db_case_model.uid)
                    logger.info("DB中的 uid = %s 的记录作废，并加入作废列表中。" % db_case_model.uid)
                    del_row = AlchemyUtil.delete_for_criteria_commit(site_rel_db_session, CaseRecordModel, {CaseRecordModel.uid == db_case_model.uid})  # 从数据库中也删除。
                    logger.info("DB中的 uid = %s 的 %d 条记录从DB数据库中删除：" % (db_case_model.uid, del_row))
                else:
                    pass
                # End Outer For Loop
            # 因全部循环已结束，所以打印匹配列表中的uid，看一看。
            logger.info("匹配列表中的uid如下:")
            for matched_uid in matched_db_record_uid_list:
                logger.info("matched_uid = %s" % matched_uid)
            logger.info("作废列表中的uid如下:")
            # 因全部循环已结束，所以打印作废列表中的uid，看一看。
            for disuse_uid in disuse_db_record_uid_list:
                logger.info("disuse_uid = %s" % disuse_uid)
            logger.info("本次测试一共作废 %d 个DB中的用例记录。" % len(disuse_db_record_uid_list))
            # 下面处理本次测试新增的用例情况。
            # test_case_record_model_list 中剩下的（没有匹配到的，也就是uid依然=0的那部分）是DB中没有的，也就是新增的，需要插入数据库。
            new_case_count = 0
            for test_case_model in test_case_record_model_list:
                if test_case_model.uid == '0':
                    case_change_flag = True
                    test_case_model.uid = uuid.uuid4().hex  # 在插入前为uid赋实际值。
                    AlchemyUtil.insert_obj_with_commit(site_rel_db_session, test_case_model)
                    new_case_count += 1
                else:
                    pass
            logger.info("本次测试一共新增 %d 个测试用例。" % new_case_count)
            # 依据 case_change_flag 标志位判断是否有用例的新增或删除，有变化则全部相关用例version增1
            if case_change_flag:
                logger.info("本次测试用例有变化。")
                new_version = curr_version_in_db + 1
                logger.info("new_version = %d" % new_version)
                update_dict = {
                    'version': new_version,
                    'gmt_modify': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                }
                affected_row = AlchemyUtil.update_for_criteria_with_commit(site_rel_db_session, CaseRecordModel, criteria_set, update_dict)
                logger.info("【Success】Totally, {0} Records have been updated with version = {1}.".format(affected_row, new_version))
            else:
                logger.info("本次测试毫无变化，无用例新增、无用例删除。")
            # End Elif
        else:
            logger.info("本次测试不包含任何测试用例。")
        # End Of insert_update_delete Method

    @staticmethod
    def insert_execution_record():
        # db_dict_val = AlchemyUtil.get_db_param_dict("QA_DB", BaseTest.conf_absolute_path + "db.conf")  # 旧用法
        db_dict_val = BaseTest.get_db_param_dict("QA_DB")
        site_rel_db_engine = AlchemyUtil.init_engine(db_dict_val)
        AlchemyUtil.init_db(site_rel_db_engine)  # 创建表（存在则不创建）
        site_rel_db_session = AlchemyUtil.get_session(site_rel_db_engine)
        # 先删除DB中因自身本地调试所存入的测试执行记录
        deleted_debug_exec_records_count = AlchemyUtil.delete_for_criteria_commit(
            site_rel_db_session, ExecutionRecordModel, criteria_set={
                ExecutionRecordModel.test_project_name == '',
                ExecutionRecordModel.test_psm == ''
            })
        logger.info(f'Totally delete previous {deleted_debug_exec_records_count} debug execution records')
        # 开始获取当前DB中最后一次执行的unique tag。
        project_conf_dict = BaseTest.get_project_conf_dict()
        # 查询
        criteria_set = {  # 这是<class 'set'>类型。
            ExecutionRecordModel.test_psm == project_conf_dict['test_psm'],  # 被测PSM
            ExecutionRecordModel.test_project_name == project_conf_dict['test_project_name']  # 测试项目名
        }
        last_exec_tag_records = AlchemyUtil.query_field_list_with_distinct_orderby_limit(
            site_rel_db_session, (ExecutionRecordModel.test_unique_tag,),
            criteria_set=criteria_set, distinct_columns=(ExecutionRecordModel.test_unique_tag,),
            sequence='DESC', order_by_columns=(ExecutionRecordModel.gmt_create,), limit_val=1
        )
        if last_exec_tag_records is not None and len(last_exec_tag_records) == 1:
            last_exec_unique_tag = last_exec_tag_records[0][0]
        else:
            last_exec_unique_tag = ''
        logger.info(f'last_exec_unique_tag={last_exec_unique_tag}')

        # 获取本次执行的测试用例数，只有大于0才执行相关操作。
        exec_record_num: int = len(BaseTest.execution_record_dict_list)
        logger.info(f"本次测试执行用例数=={exec_record_num}")
        if exec_record_num > 0:
            # 将本次测试之前DB中的最后一次执行的记录DB删除
            criteria_set.add(ExecutionRecordModel.test_unique_tag == last_exec_unique_tag)
            last_exec_count: int = AlchemyUtil.delete_for_criteria_commit(site_rel_db_session,
                                                                          ExecutionRecordModel,
                                                                          criteria_set=criteria_set
                                                                          )
            logger.info(f"从DB删除last_exec_unique_tag={last_exec_unique_tag}的{last_exec_count}条执行记录。")
            # 下面开始新插入执行记录至DB和统计DB
            exec_statistic_model: ExecutionStatisticModel = ExecutionStatisticModel()
            exec_statistic_model.uid = uuid.uuid4().hex
            exec_statistic_model.test_psm = project_conf_dict['test_psm']
            exec_statistic_model.test_project_name = project_conf_dict['test_project_name']
            exec_statistic_model.test_unique_tag = ''
            exec_statistic_model.test_cases_num = exec_record_num
            exec_statistic_model.test_duration = 0
            test_pass_count: float = 0.0
            test_interface_list: list[str] = []
            test_assert_true_count = 0.0
            # 原有代码供仅留存：开始插入新执行记录至DB
            # for curr_execution_dict in BaseTest.execution_record_dict_list:
            #     logger.info("curr_execution_dict = %s" % curr_execution_dict)
            #     curr_execution_model = ExecutionRecordDecoder.dict_to_obj(curr_execution_dict)
            #     AlchemyUtil.insert_obj_without_commit(session=site_rel_db_session, obj=curr_execution_model)
            for curr_execution_dict in BaseTest.execution_record_dict_list:
                # 开始插入新执行记录至DB
                logger.info("curr_execution_dict = %s" % curr_execution_dict)
                curr_execution_model = ExecutionRecordDecoder.dict_to_obj(curr_execution_dict)
                AlchemyUtil.insert_obj_without_commit(session=site_rel_db_session, obj=curr_execution_model)
                # 上一行插入一条执行记录（但未commit）后，开始本次执行的统计工作。
                # 累加用例执行时长
                exec_statistic_model.test_duration += curr_execution_model.test_duration
                # 获取本次通过的用例数
                if curr_execution_model.test_result == 'passed':
                    test_pass_count += 1
                # 获取本次测试的被测接口列表
                if curr_execution_model.test_interface not in test_interface_list:
                    test_interface_list.append(curr_execution_model.test_interface)
                # 获取使用了断言的数量
                logger.info(f'当前断言的类型={type(curr_execution_model.test_assert)}')  # <class 'bool'>
                logger.info(f'当前断言的值={curr_execution_model.test_assert}')
                if curr_execution_model.test_assert is True:  # True or False
                    test_assert_true_count += 1
                # 做本次测试所有记录具有相同值的字段的唯一一次提取
                if exec_statistic_model.test_unique_tag == '':
                    exec_statistic_model.test_unique_tag = curr_execution_model.test_unique_tag
            # 循环结束后，率先将已进行插入DB的执行记录，做commit。
            AlchemyUtil.do_commit_only(site_rel_db_session)
            logger.info("本次新增 %d 条测试执行记录并插入至DB。" % len(BaseTest.execution_record_dict_list))
            # 然后做剩余的本次执行统计数据
            exec_statistic_model.test_pass_rate = test_pass_count/exec_record_num
            exec_statistic_model.test_interface_num = len(test_interface_list)
            exec_statistic_model.test_assert_rate = test_assert_true_count/exec_record_num
            # 将本次执行的统计数据对象exec_statistic_model插入DB中。
            if exec_statistic_model.test_psm == '' or exec_statistic_model.test_project_name == '':
                logger.info(f"因[被测服务名]或[测试项目名]为空，遂本次test_unique_tag={exec_statistic_model.test_unique_tag}的执行统计信息不做落库操作。")
            else:
                logger.info(f"开始插入test_unique_tag={exec_statistic_model.test_unique_tag}的执行统计信息。")
                AlchemyUtil.insert_obj_with_commit(site_rel_db_session, exec_statistic_model)
        else:
            logger.warning("本次测试执行用例数为零。")

    @classmethod
    def get_db_param_dict(cls, db_key, db_conf_relative_path='', db_type: str = 'mysql'):
        from rolling_king.autotest.conf import db_conf
        if db_conf_relative_path == '':
            logger.info(f"os.path.dirname={os.path.abspath(os.path.dirname(__file__))}")
            if db_type == "postgresql":
                db_dict = db_conf.postgresql
            elif db_type == "sqlite":
                db_dict = db_conf.sqlite
            else:
                db_dict = db_conf.mysql
            db_dict_val = db_dict[db_key]
        else:  # 旧用法
            conf_file = open(db_conf_relative_path)
            cf = configparser.ConfigParser()
            cf.read_file(conf_file)
            if db_type == "postgresql":
                json_str = cf.get("postgresql", db_key)
            elif db_type == "sqlite":
                json_str = cf.get("sqlite", db_key)
            else:
                json_str = cf.get("mysql", db_key)
            db_dict_val = json.loads(json_str)
        logger.info("%s = %s" % (db_key, db_dict_val))
        return db_dict_val

###############################################################################


if __name__ == "__main__":
    # 旧的用法
    # dict_val = BaseTest.get_db_param_dict("QA_DB", "../../conf/db.conf", db_type="postgresql")
    # engine = AlchemyUtil.init_engine(dict_val, db_type="postgresql")
    # 新用法
    dict_val = BaseTest.get_db_param_dict("QA_DB")
    engine = AlchemyUtil.init_engine(dict_val)
    AlchemyUtil.init_db(engine)  # 创建表（存在则不创建）
    site_rel_db_session = AlchemyUtil.get_session(engine)
    # 先删除自身本地调试的用例记录
    # deleted_debug_case_records_count = AlchemyUtil.delete_for_criteria_commit(
    #     site_rel_db_session, CaseRecordModel, criteria_set={
    #         CaseRecordModel.test_project_name == '',
    #         CaseRecordModel.test_psm == ''
    #     })
    # logger.info(f'Totally delete previous {deleted_debug_case_records_count} debug case records')
    # 先删除自身本地调试的记录
    # deleted_debug_exec_records_count = AlchemyUtil.delete_for_criteria_commit(
    #     site_rel_db_session, ExecutionRecordModel, criteria_set={
    #         ExecutionRecordModel.test_project_name == '',
    #         ExecutionRecordModel.test_psm == ''
    #     })
    # logger.info(f'Totally delete previous {deleted_debug_exec_records_count} debug execution records')
    # 根据PSM和测试项目名，倒序找到最后一次执行的unique tag。
    # records = AlchemyUtil.query_field_list_with_distinct_orderby_limit(
    #     site_rel_db_session, (ExecutionRecordModel.test_unique_tag,),
    #     criteria_set={  # 这是<class 'set'>类型。
    #         ExecutionRecordModel.test_psm == '51JobService',  # 被测PSM
    #         ExecutionRecordModel.test_project_name == '51JobPytest'  # 测试项目名
    #     }, distinct_columns=(ExecutionRecordModel.test_unique_tag,), sequence='DESC',
    #     order_by_columns=(ExecutionRecordModel.gmt_create,), limit_val=1
    # )
    # print(records)
    # 根据PSM和测试项目名，正序找到所有符合的执行unique tag。
    # records = AlchemyUtil.query_field_list_with_distinct(
    #     site_rel_db_session, (ExecutionRecordModel.test_unique_tag,),
    #     criteria_set={  # 这是<class 'set'>类型。
    #         ExecutionRecordModel.test_psm == '51JobService',  # 被测PSM
    #         ExecutionRecordModel.test_project_name == '51JobPytest'  # 测试项目名
    #     }, distinct_columns=(ExecutionRecordModel.test_unique_tag,)
    # )
    # print(records)
    # 验证criteria_set的动态增加条件。
    # criteria_set = {  # 这是<class 'set'>类型。
    #     ExecutionRecordModel.test_psm == '51JobService',  # 被测PSM
    #     ExecutionRecordModel.test_project_name == '51JobPytest'  # 测试项目名
    # }
    # criteria_set.add(ExecutionRecordModel.test_unique_tag == '1692755269')
    # print([x.to_json() for x in AlchemyUtil.query_obj_list(site_rel_db_session, ExecutionRecordModel, criteria_set)])


