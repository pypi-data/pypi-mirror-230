# -*- coding: utf-8 -*-
# @Time : 2023/07/04
# @Author : chengwenping2
import os
import sys
import logging
import time
import traceback
from datetime import datetime

from pig_frame import log
from pig_frame.common import (
    case_to_xmind,
    remove_log,
    merge_dict_with_self_variables,
    get_call_link,
)
from pig_frame.exceptions import PigFrameCaseException, PigFrameCaseStopException
from pig_frame.test_case import TestCase
from pig_frame.test_suite import TestSuite


def execute_time(func):
    """
    打印方法执行时间
    @param func:
    @return:
    """

    def wrapper(*args, **kwargs):
        start = time.time()
        logging.info(f"{args} {kwargs}")
        func_return = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 执行耗时 {end - start} 秒")
        logging.info(f"{func.__name__} 执行耗时 {end - start} 秒")
        return func_return

    return wrapper


def check_position(func):
    """
    检测当前路径是否在pig_frame标准项目下
    @param func:
    @return:
    """

    def check_path(*args, **kwargs):
        if check_pig_frame_path():
            return func(*args, **kwargs)
        else:
            print(
                "请在符合pig_frame框架标准目录结构的路径中执行此命令\n\n"
                "提示：包含idl/、testcases/的目录\n"
            )
            sys.exit(1)

    return check_path


def check_pig_frame_path():
    """
    检测是是否在testcases下执行
    @return:
    """
    path = os.getcwd()
    if os.path.exists(path):
        files = os.listdir(path)
        if "testcases" in files:
            return True

    return False


def pig_frame_case(
    report_name, creator, unique_report=False, create_xmind=False, output_json_file=True
):
    """
    pig_frame case 入口
    @param report_name:报告名称
    @param creator:创建人
    @param unique_report: True 多次执行报告覆盖、Fasle 多次执行报告不覆盖
    @param create_xmind:True 生成xmind 文件
    @param output_json_file:True 生成json数据报告
    @return:
    """

    def decorator_name(func):
        def decorated(**kwargs):
            start_time = datetime.now()
            path = kwargs.get("file_abs_path_especially", get_call_link(step=1))
            remove_log(path)
            kwargs["file_abs_path_especially"] = path
            suite = kwargs.get("suite")
            task = kwargs.get("task")

            test_case = TestCase(
                report_name=report_name,
                creator=creator,
                output_json_file=output_json_file,
            )
            try:
                kwargs = merge_dict_with_self_variables(path, kwargs.get("env_config_file", "test.json"), **kwargs)
                func(test_case, **kwargs)
            except PigFrameCaseException as e:
                log.error(f"{report_name} 执行失败：" + traceback.format_exc())
                test_case.check_without_request(
                    description=e.description,
                    case_name=e.case_name,
                    case_assert={
                        "check_result": False,
                        "check_detail": e.check_detail,
                    },
                    use_time=e.use_time,
                )
            except PigFrameCaseStopException as e:
                log.info(f"{report_name} 执行结束：" + e.stop_reason)
            except Exception as e:
                log.error(f"{report_name} 执行失败：" + traceback.format_exc())
                test_case.check_without_request(
                    description=f"{report_name}",
                    case_name=str(e),
                    case_assert={
                        "check_result": False,
                        "check_detail": traceback.format_exc(),
                    },
                    use_time=(datetime.now() - start_time).microseconds / 1000,
                )
            finally:
                test_case.output_report(path, unique=unique_report, suite=suite, task=task)
                if create_xmind:
                    case_to_xmind(
                        report=test_case.report,
                        report_name=test_case.report_name,
                        creator=test_case.creator,
                        path=os.path.dirname(test_case.report_path),
                    )
                log.info(f"测试用例 {report_name} 已执行完毕.")
                return test_case

        return decorated

    return decorator_name


def pig_frame_suite(suite_name, creator):
    """
    测试集入口
    @param suite_name:测试集名称
    @param creator:创建人
    @return:
    """

    def decorator_name(func):
        def decorated(**kwargs):
            if kwargs.get("file_abs_path_especially") is not None:
                path = kwargs.pop("file_abs_path_especially")
            else:
                path = get_call_link(step=1)

            remove_log(path)
            task_name = kwargs.get("task_name")
            if task_name:
                remove_log(task_name)

            if 'env_config_file' in kwargs.keys():
                env_config_file = kwargs.pop('env_config_file')
                kwargs = merge_dict_with_self_variables(path, env_config_file, **kwargs)
                kwargs["suite_env_config_file"] = env_config_file

            test_suite = TestSuite(
                task_name=kwargs.get("task_name"),
                suite_name=kwargs.pop("suite_name", suite_name),
                case_home=os.path.dirname(path),
                author=creator,
            )
            try:
                func(test_suite, **kwargs)
                return test_suite.run_cases()
            except:
                log.error(f"测试集执行失败{suite_name}：" + traceback.format_exc())
                return None

        return decorated

    return decorator_name


