# -*- coding: utf-8 -*-
# @Time : 2023/7/4
# @Author : chengwenping2
import importlib
import os.path
import traceback
from pig_frame import log
from termcolor import colored
from pig_frame.common import check_case_path


def run_testcase_script(file, task, suite, env_config_file: str = None, **kwargs):
    """run specified testcase
    :param file 脚本路径
    :param env_config_file conf 目录下面对应的文件名称
    1.变量优先级处理
    3.运行脚本

    """
    try:
        check_case_path(file)

        module_path = os.path.abspath(file).replace(
            os.path.abspath(file).split("testcases")[0], ""
        )[0:-3]
        mod = importlib.import_module(f"{module_path.replace(os.sep,'.')}")
        # 执行用例
        mod_dict = mod.__dict__
        for key in mod_dict:
            if str(mod_dict[key]).__contains__(
                "pig_frame_case.<locals>.decorator_name.<locals>.decorated"
            ):
                kwargs["file_abs_path_especially"] = os.path.abspath(file)
                kwargs["suite"] = suite
                kwargs["task"] = task
                return getattr(mod, key)(env_config_file=env_config_file, **kwargs)
        if env_config_file is None:
            return getattr(mod, "idl_run_case")(**kwargs)
        else:
            return getattr(mod, "run_case")(env_config_file=env_config_file, **kwargs)
    except:

        log.info(colored(f"执行{file}发生错误  \n{traceback.format_exc()}", "red"))


def run_testcase_suite(file, task_name, env_config_file: str = None, **kwargs):
    """run specified testcase
    :param file 脚本路径
    :param env_config_file conf 目录下面对应的文件名称
    1.变量优先级处理
    3.运行脚本

    """
    try:
        check_case_path(file)

        module_path = os.path.abspath(file).replace(
            os.path.abspath(file).split("testcases")[0], ""
        )[0:-3]
        mod = importlib.import_module(f"{module_path.replace(os.sep,'.')}")
        importlib.reload(mod)
        mod_dict = mod.__dict__
        for key in mod_dict:
            if str(mod_dict[key]).__contains__(
                "pig_frame_suite.<locals>.decorator_name.<locals>.decorated"
            ):
                kwargs["file_abs_path_especially"] = os.path.abspath(file)
                kwargs["task_name"] = task_name
                return getattr(mod, key)(suite_env_config_file=env_config_file, **kwargs)
        # 执行用例
        if env_config_file is None:
            return getattr(mod, "run_suite")(kwargs)
        else:
            return getattr(mod, "run_suite")(suite_env_config_file=env_config_file, **kwargs)
    except Exception as e:
        log.info(colored(f"执行{file}发生错误{e}  \n{traceback.format_exc()}", "red"))
        return {
            "report_path": "执行异常",
            "pass_case": 0,
            "author": "未知",
            "total_case": 0,
            "fail_case": 0,
        }

if __name__ == "__main__":
    run_testcase_suite(
        ""
    )
