# -*- coding: utf-8 -*-
# @Time : 2023/07/05
# @Author : chengwenping2
# @File    : common
# @Description :初始化数据~
import copy
import hashlib
import logging
import os.path
import traceback
import time
import jmespath
import pyjson5

from pig_frame.common import dict_to_simple, get_log_conf
from pig_frame.utils import tail_f, tail


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

def get_user_path():
    """
    获取全局文件路径
    @return:
    """
    if not os.path.exists(f"{os.path.expanduser('~')}{os.sep}pig_frame"):
        os.mkdir(f"{os.path.expanduser('~')}{os.sep}pig_frame")
    return f"{os.path.expanduser('~')}{os.sep}pig_frame"


def md5(string):
    m = hashlib.md5()
    m.update(string.encode("utf-8"))
    return m.hexdigest()


def str_hash(string):
    return md5(string)


def batch_str_hash(stings):
    result = []
    for item in stings:
        result.append(str_hash(item))
    return result


def get_file_name(file_path):
    """
    获取文件文件名称
    @param file_path:
    @return:
    """
    return os.path.basename(file_path)


def get_python_files(file_path, result=[]):
    """
    获取指定目录下所有Python脚本绝对路径
    @param file_path:
    @param result:
    @return:
    """
    files = os.listdir(file_path)
    for file in files:
        new_path = file_path + os.sep + file
        if os.path.isdir(new_path):
            get_python_files(new_path, result)
        else:
            if file.endswith(".py") or file.endswith(".PY"):
                if new_path.__contains__("testcases"):
                    result.append(os.path.abspath(new_path))
    return result


def get_directory_tree(file_path, exclude_system_check=False):
    result = []
    files = os.listdir(file_path)
    files.sort()
    for file in files:
        new_path = file_path + os.sep + file
        if exclude_system_check:
            if (
                str(new_path).__contains__("系统检测")
                or str(new_path).__contains__("测试场景")
                or str(new_path).__contains__("测试物料")
            ):
                continue
        if os.path.isdir(new_path) and file != "__pycache__":
            result.append(
                {
                    "label": file,
                    "path": os.path.abspath(new_path),
                    "children": get_directory_tree(
                        new_path, exclude_system_check=exclude_system_check
                    ),
                }
            )
    return result

def read_conf(conf_path):
    try:
        with open(conf_path, "r", encoding="utf-8") as file:
            conf = pyjson5.loads(file.read())
            return conf
    except:
        return {}


def get_case_type(case_path):
    """
    获取测试用例类型
    @param case_path:
    @return:
    """
    try:
        with open(case_path, "r", encoding="utf-8") as file:
            lines = file.read()
            if lines.__contains__("TestSuite") or lines.__contains__("@pig_frame_suite"):
                return "用例集"
            elif lines.__contains__("TestCase") or lines.__contains__("@pig_frame_case"):
                if str(case_path).__contains__("测试场景"):
                    return "测试场景"
                elif str(case_path).__contains__("测试物料"):
                    return "测试物料"
                elif str(case_path).__contains__("服务点名"):
                    return "服务点名"
                elif str(case_path).__contains__("系统检测"):
                    return "系统检测"
                return "用例"
            else:
                return "未知"
    except:
        return "未知"


def count_case_check(case_path):
    total_case = 0
    try:
        with open(case_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                if str(line).__contains__("test_case.check"):
                    total_case += 1
    finally:
        return total_case


def count_models_status(directory_tree_child, status):
    """
    统计目录状态数据
    @param directory_tree_child:
    @param status:
    @return:
    """
    keys = dict_to_simple(directory_tree_child)
    count = 0
    for key in keys:
        if not str(key).endswith(".model_status"):
            continue
        if jmespath.search(key, directory_tree_child) == status:
            count += 1
    return count


def sorted_children(data):
    result = []
    data_bak = copy.deepcopy(data)
    try:
        for item in data:
            if len(item.get("children")) == 0:
                result.append(item)
        for item in data:
            if len(item.get("children")) != 0:
                result.append(item)
        return result
    except:
        logging.info(f"排序异常：{traceback.format_exc()}")
        return data_bak


# 数据统计效率优化


def filter_cases_by_directory_path(cases, directory_path):
    """查找给定目录的子项"""
    case_result = []
    for case in cases:
        if str(case["case_path"]).__contains__(directory_path):
            case_result.append(case)
    return case_result


def filter_key_by_end(keys, end):
    """
    找出给定list 以 end 结束的数据
    @param keys:
    @param end:
    @return:
    """
    result = []
    for key in keys:
        if str(key).endswith(end):
            result.append(key)
    return result


def filter_case_info_by_key(case_info, key, value):
    """
    通过给定key 和value 过滤数据
    @param case_info:
    @param key:
    @param value:
    @return:
    """
    result = []
    for case in case_info:
        if case[key] == value:
            result.append(case)
    return result


def sum_case_info(case_info, key):
    """
    通过给定key 汇总计算
    @param case_info:
    @param key:
    @return:
    """
    result = 0
    for case in case_info:
        if case["status"] == "" and key == "total_case":
            result += case["static_total_case"]
        else:
            if case[key] is not None:
                result += int(case[key])
    return result


def count_model(case_info):
    """
    统计根节点目录个数
    @param case_info:
    @return:
    """
    result = []
    for case in case_info:
        try:
            result.append(os.path.dirname(case["case_path"]))
        except:
            continue
    result = list(set(result))
    return result


def count_model_by_status(case_info):
    """
    统计各个根目录状态
    @param case_info:
    @return:
    """
    models = {}
    for case in case_info:
        try:
            model_path = os.path.dirname(case["case_path"])
            if model_path in models:
                models[model_path].append(case["case_result"])
            else:
                models[model_path] = [case["case_result"]]
        except:
            continue
    pass_model = 0
    fail_model = 0
    unexecuted = 0
    for key in models:
        all_status = list(set(models[key]))
        if "失败" in all_status or "部分通过" in all_status:
            fail_model += 1
        elif len(all_status) == 1 and all_status[0] == "通过":
            pass_model += 1
        else:
            unexecuted += 1

    return pass_model, fail_model, unexecuted


# 废弃，严重影响接口响应时间
def update_directory_tree_model_info(directory_tree):
    """
    更新models状态相关信息到目录树，同时对目录结构排序，子级节点的放前面
    @param directory_tree:
    @return:
    """
    if isinstance(directory_tree, dict):
        directory_tree["children"] = sorted_children(directory_tree["children"])
        directory_tree["models_unexecuted"] = count_models_status(
            directory_tree["children"], "未执行"
        )
        directory_tree["models_pass"] = count_models_status(
            directory_tree["children"], "通过"
        )
        directory_tree["models_part_pass"] = count_models_status(
            directory_tree["children"], "部分通过"
        )
        directory_tree["models_fail"] = count_models_status(
            directory_tree["children"], "失败"
        )

    if (
        directory_tree.get("children") is not None
        and len(directory_tree.get("children")) > 0
    ):
        for i in range(len(directory_tree.get("children"))):
            update_directory_tree_model_info(directory_tree.get("children")[i])
    return directory_tree


def update_directory_tree_cass_info(directory_tree, cases, show_all=True):
    """
    更新case相关信息到目录树
    @param directory_tree:
    @param cases:
    @return:
    """
    if isinstance(directory_tree, dict):
        if len(directory_tree["children"]) == 0:
            directory_tree["label"] = "" + directory_tree["label"]
        case_info = filter_cases_by_directory_path(cases, directory_tree["path"])
        directory_tree["script_total"] = len(case_info)
        models_count = len(count_model(case_info))
        directory_tree["models_count"] = models_count
        model_status = count_model_by_status(case_info)
        directory_tree["models_pass"] = model_status[0]
        directory_tree["models_fail"] = model_status[1]
        directory_tree["models_unexecuted"] = model_status[2]
        if model_status[0] == models_count:
            directory_tree["model_status"] = "通过"
        elif model_status[0] != 0 and model_status[1] != 0:
            directory_tree["model_status"] = "部分通过"
        elif model_status[0] == 0 and model_status[1] != 0:
            directory_tree["model_status"] = "失败"
        elif model_status[2] == models_count:
            directory_tree["model_status"] = "未执行"
            if not show_all:
                directory_tree.pop("children")
        else:
            directory_tree["model_status"] = "失败"
        directory_tree["script_finish"] = len(
            filter_case_info_by_key(case_info, "status", "完成")
        )
        directory_tree["script_pass"] = len(
            filter_case_info_by_key(case_info, "case_result", "通过")
        )
        directory_tree["script_fail"] = (
            directory_tree["script_finish"] - directory_tree["script_pass"]
        )
        directory_tree["script_running"] = len(
            filter_case_info_by_key(case_info, "status", "执行中")
        )
        directory_tree["script_unexecuted"] = len(
            filter_case_info_by_key(case_info, "status", "")
        )
        directory_tree["total_case"] = sum_case_info(case_info, "total_case")
        directory_tree["pass_case"] = sum_case_info(case_info, "pass_case")
        directory_tree["fail_case"] = sum_case_info(case_info, "fail_case")
        directory_tree["cases"] = case_info
    if (
        directory_tree.get("children") is not None
        and len(directory_tree.get("children")) > 0
    ):
        children_len = len(directory_tree.get("children"))
        for i in range(children_len):
            update_directory_tree_cass_info(
                directory_tree.get("children")[children_len - i - 1], cases, show_all
            )
            if (
                directory_tree.get("children")[children_len - i - 1].get("model_status")
                == "未执行"
                or directory_tree.get("children")[children_len - i - 1].get(
                    "models_count"
                )
                == 0
            ) and not show_all:
                directory_tree.get("children").pop(children_len - i - 1)
    return directory_tree


def tail_f_all_log(project_home, callback, interval=0.01):
    """
    读取 all.log最后一行，调用 callback 方法
    :param project_home: 项目根目录
    :param callback: 每读到一行新的日志，执行的方法
    :param interval: 读取时间间隔，默认 100ms
    :return:
    """
    log_path = project_home + "/logs/all.log"
    if not os.path.exists(log_path):
        project_home = get_log_conf(project_home)

    log_path = project_home + "/logs/all.log"
    tail_f(log_path, callback, interval)


def tail_all_log(project_home, callback, n=10):
    """
    读取 all.log最后n行，调用 callback 方法
    :param n: 读取的行数
    :param project_home: 项目跟目录
    :param callback: 每读到一行新的日志，执行的方法
    :return:
    """
    log_path = project_home + "/logs/all.log"
    if not os.path.exists(log_path):
        project_home = get_log_conf(project_home)

    log_path = project_home + "/logs/all.log"
    lines = tail(log_path, n)
    for line in lines:
        callback(line)


def get_case_log(case_path):
    """
    读取执行日志
    :return: 日志内容
    :param case_path 调用方脚本名称
    """
    try:
        file_name = os.path.basename(case_path).split(".")[0]
        project_home = case_path.split("/testcases/")[0]
        log_file = f"{project_home}/logs/{file_name}.log"
        if not os.path.exists(log_file):
            project_home = get_log_conf(project_home)

        log_file = f"{project_home}/logs/{file_name}.log"
        if not os.path.exists(log_file):
            return "日志文件不存在"

        with open(log_file, "r", encoding="utf-8") as f:
            return f.read()
    except:
        logging.error(f"获取日志异常：{traceback.format_exc()}")
        return traceback.format_exc()


if __name__ == "__main__":
    print(
        get_directory_tree(
            "/Users/tianmaocheng/ypsh/python_project/sgc_autotest/testcases/B2P"
        )
    )
