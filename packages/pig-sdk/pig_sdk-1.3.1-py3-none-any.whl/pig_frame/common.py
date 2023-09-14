# -*- coding: utf-8 -*-
# @Time : 2023/07/04
# @Author : chengwenping2
# @File : common.py
"""
文件说明：封装常用公共方法
"""
import copy
import datetime
import hashlib
import json
import os
import platform
import random
import re
import socket
import string as string_char
import traceback
import uuid
import getpass

import psutil
from faker import Faker

import jmespath
import jsonpath
import pyjson5 as json5

from pig_frame import log
from pig_frame.template import get_mail_html
from pig_frame.xmind_util import XmindUtil
import sys

jsonpath = jsonpath
random = random
traceback = traceback
logging = log
jmespath = jmespath
faker = Faker(locale="zh_CN")


def get_project_home():
    """
    获取符合 pig_frame 标准框架项目的项目根目录
    :return: str
    """
    # 进程当前运行目录
    cwd = os.getcwd()
    index = cwd.rfind(f"{os.sep}testcases")
    if index == -1:
        return cwd

    project_home = cwd[:index]
    return project_home


def get_case_home():
    """
    获取项目用例根目录
    @return:
    """
    return f"{get_project_home()}{os.sep}/testcases"


def add_traceback(param):
    pass


def get_conf_home():
    """
    获取配置根目录
    @return:
    """
    return f"{get_project_home()}{os.sep}/conf"


def process_str_pystr(string):
    """
    字符串变量处理
    :param string:
    :return:
    """
    try:
        if isinstance(string, str):
            match = re.findall("\$\{\{.*\}\}", string)
            if len(match) != 0:
                for match_item in match:
                    string = string.replace(match_item, match_item[3:-2])
                return string
            match = re.findall("\$\{.*\}", string)
            if len(match) != 0:
                string = string.replace("${", "{")
                return f'f"{string}"'
            return f'"{string}"'
        else:
            return string
    except:
        return string


def process_obj_variable(obj, result=None):
    keys = dict_to_simple(obj)
    replace_value = {}
    for key in keys:
        try:
            value = jmespath.search(key, obj)
            if not isinstance(value, str):
                continue
            match = re.findall("\${{\w+}}", value)
            if len(match) != 0:
                replace_value[f"'{value}'"] = process_str_pystr(value)
            else:
                match = re.findall("\${\w+}", value)
                if len(match) != 0:
                    replace_value[f"'{value}'"] = process_str_pystr(value)
        except:
            continue
    obj_str = str(obj)
    for key in replace_value:
        obj_str = obj_str.replace(key, replace_value[key])
    return obj_str


def process_variable(obj):
    """
    带参数的json字符串转换为python对象字符串
    :param string:json字符串
    :return:str
    """
    try:
        if isinstance(obj, str):
            return process_str_pystr(obj)
        elif isinstance(obj, dict) or isinstance(obj, list):
            return process_obj_variable(obj)
        else:
            return obj
    except:
        return obj
#
# def merge_dict(test_case, pig_frame_env):
#     """
#     老版本脚本兼容
#     """
#     return merge_dict_with_self_variables(test_case, pig_frame_env, **{})


def _exclude(file: str, exclude: list[str]):
    if exclude is None or len(exclude) == 0:
        return False
    for item in exclude:
        if item in file:
            return True
    return False


def get_cases_by_folder(folder_path, exclude: list[str] = None, result=None):
    """
    查找所有测试用例
    @param folder_path:
    @param result:
    @param exclude:需要排除的文件
    @return:
    """
    if result is None:
        result = []
    files = os.listdir(folder_path)
    for file in files:
        try:
            if _exclude(file, exclude):
                log.debug(f"{file} 已被过滤.")
                continue
            new_path = folder_path + os.sep + file
            if os.path.isdir(new_path):
                get_cases_by_folder(new_path, exclude, result)
            else:
                if file.endswith(".py") or file.endswith(".PY"):
                    if new_path.__contains__("testcases"):
                        result.append(new_path)
        except:
            continue
    return result


def merge_dict_with_self_variables(test_case, pig_frame_env, **config):
    """
    变量优先级处理：用例变量>环境变量>全局变量
    :param test_case: 用例执行脚本__file__
    :param pig_frame_env: 环境变量文件，相对于conf/目录
    :return: 按照优先级合并后的变量[]
    """
    global_variables = {}
    test_case_variables = {}
    env_variables = {}
    project_home = get_project_home()
    if not os.path.exists(f"{project_home}{os.sep}conf"):
        log.error("配置目录不存在，跳过变量优先级处理动作")
        return config

    try:
        file_name = str(test_case).split(f"testcases{os.sep}")[1].split(".")[0]
        case_file = f"{os.sep}conf{os.sep}{file_name}.json"
        if not os.path.exists(project_home + case_file):
            log.warn("用例变量[%s]不存在", case_file)
        else:
            try:
                f = open(project_home + case_file, "r", encoding="utf-8")
                test_case_variables = json5.load(f)
                log.debug("用例变量：%s", test_case_variables)
            except json5.Json5EOF:
                test_case_variables = {}
                log.error("读取用例变量[%s]发生错误", case_file)
    except:
        case_file = ""

    env_file = f"{os.sep}conf{os.sep}{pig_frame_env}"
    if os.path.exists(project_home + env_file):
        try:
            env_variables = json5.load(
                open(project_home + env_file, "r", encoding="utf-8")
            )
            log.debug("环境变量:%s", env_variables)
        except json5.Json5EOF:
            env_variables = {}
            log.error("读取环境变量[%s]发生错误", env_file)
    else:
        log.error("环境变量[%s]不存在", env_file)

    global_file = f"{os.sep}conf{os.sep}global.json"
    if os.path.exists(project_home + global_file):
        try:
            global_variables = json5.load(
                open(project_home + global_file, "r", encoding="utf-8")
            )
            log.debug("系统变量:%s", global_variables)
        except json5.Json5EOF:
            global_variables = {}
            log.error("读取系统变量[%s]发生错误", global_file)
    else:
        log.error("系统变量[%s]不存在", global_file)

    log.debug(
        "变量优先级：外部传递变量%s>用例变量%s>环境变量%s>全局环境%s", config, case_file, env_file, global_file
    )
    variables = {**global_variables, **env_variables, **test_case_variables, **config}
    log.info("变量合并结果(最终生效内容)：%s", variables)
    return variables


def remove_log(test_case):
    """
    删除用例的执行日志
    :param test_case: 用例执行脚本
    """
    project_home = get_project_home()
    try:
        file_name = os.path.basename(test_case).split(".")[0] if os.path.basename(test_case).split(".")[0] else test_case
        log_file = f"{project_home}{os.sep}logs{os.sep}{file_name}.log"
        if os.path.exists(log_file):
            os.remove(log_file)
    except FileNotFoundError:
        log.error(traceback.format_exc())


def compatible_jsonpath(key):
    """
    兼容jsonpath 表达式
    :param key:
    :return:
    """
    if str(key).startswith("$"):
        key = str(key).replace("$.", "").replace("$", "")
        match = re.findall("\.\d+", key)
        for item in match:
            key = str(key).replace(item, f'."{item[1::]}"')
    return key


def obj_search(obj, key):
    key = compatible_jsonpath(key)
    return jmespath.search(key, obj)


def filter_key(keys, key):
    """
    判断key是否在keys中存在，支持data.*、data[*]特殊可以值判断
    @param keys: jsonpath 查询语句写法key_list ['data.data.conde']
    @param key: key 字符串 data.data
    @return:
    """
    for i in range(len(keys)):
        keys[i] = compatible_jsonpath(keys[i])
    for item in keys:
        if str(key).startswith(f"{item}."):
            return True
        elif str(key).startswith(f"{item}["):
            return True
    if key in keys:
        return True
    else:
        for item in keys:
            if str(item).__contains__("[*]") and str(item).endswith(".*"):
                temp_index = [m.start() for m in re.finditer("\*", str(item)[0:-1])]
                for char_index in temp_index:
                    key = replace_char(key, "*", char_index)
                if str(key).startswith(str(item)[0:-1]):
                    return True
            elif str(item).endswith(".*"):
                if str(key).startswith(str(item)[0:-1]):
                    return True
            elif str(item).__contains__("[*]"):
                temp_index = [m.start() for m in re.finditer("\*", str(item))]
                for char_index in temp_index:
                    key = replace_char(key, "*", char_index)
                if str(item) == str(key):
                    return True
        return False


def limit_check_key(keys, key):
    """
    判断key是否在keys中存在，支持data.*、data[*]特殊可以值判断
    @param keys: jsonpath 查询语句写法key_list ['data.data.conde']
    @param key: key 字符串 data.data
    @return:
    """
    for i in range(len(keys)):
        keys[i] = compatible_jsonpath(keys[i])
    if len(keys) == 0:
        return True
    if key in keys:
        return True
    else:
        for item in keys:
            if str(item).__contains__("[*]") and str(item).endswith(".*"):
                temp_index = [m.start() for m in re.finditer("\*", str(item)[0:-1])]
                for char_index in temp_index:
                    key = replace_char(key, "*", char_index)
                if str(key).startswith(str(item)[0:-1]):
                    return True
            elif str(item).endswith(".*"):
                if str(key).startswith(str(item)[0:-1]):
                    return True
            elif str(item).__contains__("[*]"):
                temp_index = [m.start() for m in re.finditer("\*", str(item))]
                for char_index in temp_index:
                    key = replace_char(key, "*", char_index)
                if str(item) == str(key):
                    return True
            elif str(item).startswith("*"):
                return True
            elif (
                    str(key).startswith(item + ".")
                    or str(key).startswith(item + "[")
                    or str(key).startswith(f'"{item}"')
            ):
                return True
        return False


def replace_char(string, char, index):
    """
    替换字符串指定位置字符
    @param string:
    @param char:
    @param index:
    @return:
    """
    try:
        string = list(string)
        string[index] = char
        return "".join(string)
    except:
        return string


def check_str_ascii_letters(sting):
    for c in str(sting):
        if c not in string_char.ascii_letters:
            return True
    return False


def dict_to_simple(dict_data):
    if isinstance(dict_data, dict):
        return dict_to_simple_process(dict_data, temp="")
    else:
        return dict_to_simple_process(dict_data, temp="")


def dict_to_simple_process(dict_data, temp="", result=None):
    """
    将复杂对象扁平化处理，返回jsonpath查询语句
    :data 待处理对象
    :temp 中间临时变量，不需要传值
    :result 返回链式key [],调用方法时，避免数据污染，可以传入初始值[]
    """
    if result is None:
        result = []
    data = copy.deepcopy(dict_data)
    if isinstance(data, dict):
        for key in data:
            temp_key = key
            try:
                if not check_str_ascii_letters(temp_key):
                    dict_to_simple_process(data[key], f"{temp}{temp_key}.", result)
                else:
                    dict_to_simple_process(data[key], f'{temp}"{temp_key}".', result)
            except:
                dict_to_simple_process(data[key], f"{temp}{temp_key}.", result)

    if isinstance(data, list):
        for i in range(len(data)):
            if temp.endswith("."):
                temp = temp[0:-1]
            dict_to_simple_process(data[i], f"{temp}[{i}].", result)
    else:
        if isinstance(data, dict) or isinstance(data, list):
            pass
        else:
            if temp.endswith("."):
                temp = temp[0:-1]
            result.append(temp)
    return result


def case_to_xmind(report, report_name, creator, path, all_in_one=False):
    try:
        if all_in_one:
            pass
        else:
            api_details = []
            apis = []
            step_details = []
            step_detail = {}
            url = ""
            number = 0
            for step in report:
                try:
                    curl_url = step.get("url")
                    if curl_url == "":
                        continue
                    if (
                            url != curl_url
                            or f"{number}、" + step.get("description") not in step_detail
                    ):
                        step_details.append(copy.deepcopy(step_detail))
                        step_detail = {}
                        number += 1
                        step_detail[f"{number}、" + step.get("description")] = [
                            step.get("name")
                        ]
                    else:
                        step_detail[f"{number}、" + step.get("description")].append(
                            step.get("name")
                        )
                    url = curl_url
                    if curl_url not in apis:
                        api_details.append(
                            {
                                step.get("description"): [
                                    {"url": curl_url},
                                    {"params": step.get("params").get("params")},
                                    {"data": step.get("params").get("data")},
                                    {"json": step.get("params").get("json")},
                                ]
                            }
                        )
                        apis.append(curl_url)
                except:
                    continue
            xmind_detail = {
                report_name: [
                    {"测试步骤": step_details},
                    {"接口详情": api_details},
                    {"负责人": creator},
                ]
            }
            XmindUtil().create_xmind_file(
                data=xmind_detail, path=path, file_name=report_name
            )

            log.info(f"用例知识已沉淀至:{path}/{report_name}.xmind")
    except:
        log.info(f"用例知识已沉淀xmind文件生成失败")


def report_overview(results, upload=False):
    """
    批量执行测试用例时返回统计报告
    @param upload: 是否需要上传测试报告到oss
    @param results: 测试用例集执行结果
    @return:
    """
    detail, report_path = [], {}
    for report in results:
        try:
            if report is not None:
                # if upload:
                #     out_link = upload_report(report.report_path)
                #     report.report_path = out_link
                # else:
                #     out_link = report.report_path
                report_path[report.report_name] = report.report_path
                detail.append(
                    {
                        "case_name": report.report_name,
                        "report_path": report.report_path,
                        "creator": report.creator,
                        "pass_case": report.pass_case,
                        "fail_case": report.fail_case,
                        "use_time": round((report.end_time - report.start_time).total_seconds(), 2),
                        "start_time": report.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": report.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "result": report.report
                    }
                )
        except:
            log.info(f"生成汇总报告：{traceback.format_exc()}")
            continue

    return get_mail_html(
        **{
            "total_scene": len(detail),
            "fail_scene": len([item for item in detail if item["fail_case"] > 0]),
            "pass_case": sum(jmespath.search("[*].pass_case", detail)),
            "fail_case": sum(jmespath.search("[*].fail_case", detail)),
            "use_time": round(sum(jmespath.search("[*].use_time", detail)), 2),
            "detail": detail,
        }
    ), report_path


def create_overview_report(project_home, report_name, results, upload=False):
    """
    批量执行生成汇总测试报告
    @param report_name:
    @param results:
    @param upload:
    @return:
    """
    try:
        report_path = f"{project_home}{os.sep}test_report{os.sep}{report_name}.html"
        html = report_overview(results, upload)[0]
        with open(report_path, "w", encoding="utf-8") as file:
            file.write(html)
        results_new = []
        for item in results:
            if not isinstance(item, dict):
                results_new.append(
                    {
                        "created": item.created,
                        "creator": item.creator,
                        "pass_case": item.pass_case,
                        "report": item.report,
                        "report_name": item.report_name,
                        "report_path": item.report_path,
                    }
                )
        with open(report_path.replace(".html", ".json"), "w", encoding="utf-8") as file:
            file.write(
                json.dumps(
                    obj=results_new,
                    default=lambda x: x.__dict__,
                    sort_keys=False,
                    indent=2,
                    ensure_ascii=False,
                )
            )
        log.info(f"汇总测试报告已生成至:{report_path}")
        return f"{report_path}"
    except:
        log.info(f"生成汇总报告错误:{traceback.format_exc()}")
        return None


def process_file_name(file_name):
    """
    处理文件名称特殊字符，避免文件生成失败
    @param file_name:
    @return:
    """
    for item in '<>/\|:"*?:：《》"*？ ,、、，,！@#￥%……&*（）!@#$%^&*()~`~`':
        file_name = str(file_name).replace(item, "")
    return file_name


def check_case_path(case_path):
    """
    校验测试用例是否在testcases 目录下
    @param case_path:
    @return:
    """
    path = os.path.dirname(case_path)
    while True:
        if os.path.basename(path) == "testcases":
            if os.path.dirname(path) in sys.path:
                break
            sys.path.append(os.path.dirname(path))
            break
        elif os.path.basename(path) == "":
            print("请将用例放入testcases目录下执行:\n不在testcases目录下执行的用例、测试报告、日志等可能混乱")
            break
        else:
            path = os.path.dirname(path)

    print("")


def get_call_link(step=1):
    """
    获取脚本调用链路 并返回调用路径的指定上级
    @param step:相对于当前调用链路的前面几步
    @return:
    """
    try:
        path = os.path.abspath(__file__)
        traceback_extract_stack = traceback.extract_stack()
        for index, value in enumerate(traceback_extract_stack):
            if value.filename == path:
                return traceback_extract_stack[index - step - 1].filename
        return ""
    except:
        return ""


def get_log_conf(project_home):
    try:
        # 标准工作目录，读取 global.json里面的配置，用于服务器部署
        with open(f"{project_home}/conf/global.json", "r", encoding="utf-8") as f:
            global_conf = json5.load(f)
            return global_conf["log_path"]
    except:
        pass
    return project_home


def get_md5(string):
    """
    获取字符串的MD5 值
    @param string:
    @return:
    """
    m = hashlib.md5()
    m.update(string.encode("utf-8"))
    return m.hexdigest().upper()


def get_system_ip():
    """
    获取本机ip地址
    @return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def get_mac_address():
    """
    获取本机mac地址
    @return:
    """
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e: e + 2] for e in range(0, 11, 2)])


def get_system_info():
    """
    获取电脑主机关键信息
    @return:
    """
    platform_info = {
        "machine": platform.machine(),
        "node": platform.node(),
        "system": platform.system(),
        "platform": platform.platform(),
        "ip": get_system_ip(),
        "host_name": socket.gethostname(),
        "cpu_count": psutil.cpu_count(),
        "total_memory": f"{round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 2)} G",
        "free_memory": f"{round(psutil.virtual_memory().free / 1024 / 1024 / 1024, 2)} G",
        "local_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mac": get_mac_address(),
        "user": getpass.getuser()
    }
    return platform_info


def get_project_name():
    """
    获取项目名称，如果 conf/global.json中配置了"project_name"，则直接返回它，否则获取项目目录作为项目名称
    :return:
    """
    project_home = get_project_home()
    if os.path.exists(f"{project_home}/conf/global.json"):
        with open(f"{project_home}/conf/global.json", "r", encoding="utf-8") as f:
            global_conf = json5.load(f)
            return global_conf["project_name"]

    return os.path.basename(project_home)
