# -*- coding: utf-8 -*-
# @Time : 2023/7/4
# @Author : chengwenping2
# @File : test_case.py
"""
文件说明：添加测试用例，输出测试报告
"""
import html
import os
import sys
import copy
import json
import pyjson5
import traceback
from datetime import datetime

from pig_frame import log
from pig_frame.asserts import equal, not_equal, contain, not_contain
from pig_frame.common import get_project_home, jmespath
from pig_frame.http_request import request
from pig_frame.template import get_report_template
from pig_frame.num_util import calc_rate
from pig_frame.exceptions import PigFrameCaseStopException

traceback = traceback


def read_log(file):
    """
    读取执行日志
    :return: 日志内容
    :param file 调用方脚本名称
    """
    try:
        project_home = get_project_home()
        file_name = os.path.basename(file).split(".")[0]
        log_file = f"{project_home}{os.sep}logs{os.sep}{file_name}.log"
        if not os.path.exists(log_file):
            # 标准工作目录，读取 global.json里面的配置，主要用于服务器部署
            with open(f"{project_home}/conf/global.json", "r", encoding="utf-8") as f:
                global_conf = pyjson5.load(f)
                project_home = global_conf["log_path"]
        log_file = f"{project_home}{os.sep}logs{os.sep}{file_name}.log"

        with open(log_file, "r", encoding="utf-8") as f:
            return f.read()
    except:
        log.warn("获取执行日志发生异常，测试报告中将无法查看执行日志！")
        return "未获取到执行过程中的日志文件"

def check_report_name(report_name):
    try:
        if report_name is None or report_name == "":
            return "测试报告"
        else:
            for item in '<>/\|:"*?:：《》"*？ ,、、，,！@#￥%……&*（）!@#$%^&*()~`~`':
                report_name = str(report_name).replace(item, "")
            return report_name
    except:
        return "测试报告"

def check_python_ver():
    ver = sys.version_info
    if ver.major < 3:
        log.error("You should Upgrade to Python3.9+")
        exit(1)
    if ver.major == 3 and ver.minor < 9:
        log.error("You should Upgrade to Python3.9+")
        exit(1)

class TestCase:
    def __init__(self, report_name, creator="system", output_json_file=True):
        check_python_ver()
        # 测试报告名称
        self.report_name = check_report_name(report_name)
        # 验证点集合
        self.report = []
        # 测试报告路径
        self.report_path = ""
        self.pass_case = 0
        self.fail_case = 0
        self.start_time = datetime.now()
        # 脚本编写负责人
        self.creator = creator
        self.created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.output_json_file = output_json_file
        self.end_time = None
        self.stop_reason = None

    def stop(self, stop_reason: str):
        self.stop_reason = stop_reason
        raise PigFrameCaseStopException(stop_reason)

    def check(self, response=None, **kwargs):
        """
        添加测试用例验证点
        :param response:调用http_request.request请求返回的数据对象
        :param kwargs:
        case_name:测试用例名
        check:期望值
        case_assert:断言结果对象、支持传入多个如[("case_name",check1)、("case_name",check2)] or equal() or [equal(),not_equal()]
        :return:
        """
        try:
            if response is None:
                response = {
                    "url": "",
                    "params": "",
                    "response": "",
                    "use_time": "",
                    "description": "",
                    "headers": {},
                    "status_code": "",
                    "method": "",
                    "response_time": "",
                    "retry_times": "",
                }
            if response:
                if isinstance(kwargs.get("case_assert"), list):
                    for sub_case_assert in kwargs.get("case_assert"):
                        if isinstance(sub_case_assert, tuple):
                            if len(sub_case_assert) == 2:
                                case_name = sub_case_assert[0]
                                case_check = sub_case_assert[1]
                            else:
                                case_name = ""
                                case_check = {
                                    "check_result": False,
                                    "check_detail": ["未填写断言方式"],
                                    "check_type": "contain",
                                    "expect": "",
                                    "actual": "",
                                    "filter_keys": [],
                                    "limit_keys": [],
                                }
                        else:
                            if len(kwargs.get("case_assert")) > 1:
                                case_name = (
                                    kwargs.get("case_name")
                                    + f"_{sub_case_assert.get('check_type')}"
                                )
                            else:
                                case_name = kwargs.get("case_name")
                            case_check = sub_case_assert
                        temp_check = {
                            "name": case_name,
                            "expect": case_check.get("expect"),
                            "actual": case_check.get("actual"),
                            "check_result": case_check.get("check_result"),
                            "check_type": case_check.get("check_type"),
                            "check_detail": case_check.get("check_detail"),
                            "filter_keys": case_check.get("filter_keys"),
                            "limit_keys": case_check.get("limit_keys"),
                            "url": response.get("url"),
                            "params": response.get("params"),
                            "response": response.get("response"),
                            "use_time": response.get("use_time"),
                            "description": response.get("description"),
                            "headers": eval(str(response.get("headers"))),
                            "status_code": response.get("status_code"),
                            "method": response.get("method"),
                            "response_time": response.get("response_time"),
                            "retry_times": response.get("retry_times"),
                        }
                        self.report.append(copy.deepcopy(temp_check))
                        log.debug(f"{case_name} 验证结果：")
                        log.debug(f'  断言结果:{case_check.get("check_result")}')

                        if not case_check.get("check_result"):
                            log.debug(f'  差异明细:{case_check.get("check_detail")}')
                else:
                    result = {
                        "handle": kwargs.get("case_handle"),
                        "name": kwargs.get("case_name"),
                        "expect": kwargs.get("case_assert").get("expect"),
                        "actual": kwargs.get("case_assert").get("actual"),
                        "check_result": kwargs.get("case_assert").get("check_result"),
                        "check_type": kwargs.get("case_assert").get("check_type"),
                        "check_detail": kwargs.get("case_assert").get("check_detail"),
                        "filter_keys": kwargs.get("case_assert").get("filter_keys"),
                        "limit_keys": kwargs.get("case_assert").get("limit_keys"),
                        "url": response.get("url"),
                        "params": response.get("params"),
                        "response": response.get("response"),
                        "use_time": response.get("use_time"),
                        "description": response.get("description"),
                        "headers": eval(str(response.get("headers"))),
                        "status_code": response.get("status_code"),
                        "method": response.get("method"),
                        "response_time": response.get("response_time"),
                        "retry_times": response.get("retry_times"),
                    }
                    self.report.append(copy.deepcopy(result))
                    log.debug(f'{kwargs.get("case_name")} 验证结果：')
                    log.debug(f'  断言结果:{kwargs.get("case_assert").get("check_result")}')

                    if not kwargs.get("case_assert").get("check_result"):
                        log.debug(
                            f'  差异明细:{kwargs.get("case_assert").get("check_detail")}'
                        )

            else:
                if isinstance(kwargs.get("case_assert"), list):
                    for sub_case_assert in kwargs.get("case_assert"):
                        if isinstance(sub_case_assert, tuple):
                            if len(sub_case_assert) == 2:
                                case_name = sub_case_assert[0]
                                case_check = sub_case_assert[1]
                            else:
                                case_name = ""
                                case_check = {
                                    "check_result": False,
                                    "check_detail": ["未填写断言方式"],
                                    "check_type": "contain",
                                    "expect": "",
                                    "actual": "",
                                    "filter_keys": [],
                                    "limit_keys": [],
                                }
                        else:
                            if len(kwargs.get("case_assert")) > 1:
                                case_name = (
                                    kwargs.get("case_name")
                                    + f"_{sub_case_assert.get('check_type')}"
                                )
                            else:
                                case_name = kwargs.get("case_name")
                            case_check = sub_case_assert
                        temp_check = {
                            "name": case_name,
                            "expect": case_check.get("expect"),
                            "actual": case_check.get("actual"),
                            "check_result": case_check.get("check_result"),
                            "check_type": case_check.get("check_type"),
                            "check_detail": case_check.get("check_detail"),
                            "filter_keys": case_check.get("filter_keys"),
                            "limit_keys": case_check.get("limit_keys"),
                            "url": response.get("url"),
                            "params": response.get("params"),
                            "response": response.get("response"),
                            "use_time": response.get("use_time"),
                            "description": response.get("description"),
                            "headers": "",
                            "status_code": "",
                            "method": "",
                            "response_time": response.get("response_time"),
                            "retry_times": response.get("retry_times"),
                        }
                        self.report.append(copy.deepcopy(temp_check))
                        log.debug(f"{case_name} 验证结果：")
                        log.debug(f'  断言结果:{case_check.get("check_result")}')

                        if not case_check.get("check_result"):
                            log.debug(f'  差异明细:{case_check.get("check_detail")}')
                    else:
                        result = {
                            "name": kwargs.get("case_name"),
                            "expect": kwargs.get("case_assert").get("expect"),
                            "actual": kwargs.get("case_assert").get("actual"),
                            "check_type": kwargs.get("case_assert").get("check_type"),
                            "check_result": kwargs.get("case_assert").get(
                                "check_result"
                            ),
                            "check_detail": kwargs.get("case_assert").get(
                                "check_detail"
                            ),
                            "filter_keys": kwargs.get("case_assert").get("filter_keys"),
                            "limit_keys": kwargs.get("case_assert").get("limit_keys"),
                            "url": response.get("url"),
                            "params": response.get("params"),
                            "response": response.get("response"),
                            "use_time": response.get("use_time"),
                            "description": response.get("description"),
                            "headers": "",
                            "status_code": "",
                            "method": "",
                            "response_time": response.get("response_time"),
                            "retry_times": response.get("retry_times"),
                        }
                        self.report.append(result)

                        log.debug(f'{kwargs.get("case_name")} 验证结果：')
                        log.debug(
                            f'  断言结果:{kwargs.get("case_assert").get("check_result")}'
                        )
                        if not kwargs.get("case_assert").get("check_result"):
                            log.debug(
                                f'  差异明细:{kwargs.get("case_assert").get("check_detail")}'
                            )
        except Exception as e:
            log.error(f"添加测试用例失败:{traceback.format_exc()}\n{e}")

    def run_ddt(self, host, kwargs):
        """
        执行外置Excel 测试用例
        @param host:
        @param kwargs:
        @return:
        """
        headers = kwargs.get("headers")
        excel_case = kwargs.get("pig_frame_ddt_http_case_list")
        if headers is None:
            headers = {}
        for case in excel_case:
            result = request(
                method=case.get("method"),
                url=f'{host}{case.get("path")}',
                json=case.get("body"),
                params=case.get("params"),
                data=case.get("data"),
                headers=headers,
                description=case.get("desc"),
            )
            if case.get("assert_type") == "相等":
                self.check(
                    result,
                    case_name=case.get("case_name"),
                    case_assert=equal(
                        case.get("exp"), jmespath.search("response", result)
                    ),
                )
            elif case.get("assert_type") == "不‍相等":
                self.check(
                    result,
                    case_name=case.get("case_name"),
                    case_assert=not_equal(
                        case.get("exp"), jmespath.search("response", result)
                    ),
                )
            elif case.get("assert_type") == "包含":
                self.check(
                    result,
                    case_name=case.get("case_name"),
                    case_assert=contain(
                        case.get("exp"), jmespath.search("response", result)
                    ),
                )
            elif case.get("assert_type") == "不包含":
                self.check(
                    result,
                    case_name=case.get("case_name"),
                    case_assert=not_contain(
                        case.get("exp"), jmespath.search("response", result)
                    ),
                )

    def check_without_request(
        self, description, case_name, case_assert: dict, use_time
    ):
        """
        添加测试用例验证点，用于无请求的验证点
        :param description 请求名称
        :param case_name 验证点名称
        :param case_assert 验证结果
        :param use_time 花费时间
        """
        try:
            response = {
                "url": "",
                "params": "",
                "response": "",
                "use_time": use_time,
                "description": description,
                "headers": {},
                "status_code": "",
                "method": "",
                "response_time": "",
                "retry_times": "",
            }
            result = {
                "name": case_name,
                "expect": case_assert.get("expect"),
                "actual": case_assert.get("actual"),
                "check_type": case_assert.get("check_type"),
                "check_result": case_assert.get("check_result"),
                "check_detail": case_assert.get("check_detail"),
                "filter_keys": case_assert.get("filter_keys"),
                "limit_keys": case_assert.get("limit_keys"),
                "url": response.get("url"),
                "params": response.get("params"),
                "response": response.get("response"),
                "use_time": response.get("use_time"),
                "description": response.get("description"),
                "headers": "",
                "status_code": "200",
                "method": "",
                "response_time": response.get("response_time"),
                "retry_times": response.get("retry_times"),
            }
            self.report.append(result)

            log.debug(f"{case_name} 验证结果：")
            log.debug(f'  断言结果:{case_assert.get("check_result")}')
        except Exception as e:
            log.error(f"添加测试用例失败:{traceback.format_exc()}\n{e}")

    def output_report(self, file=None, unique=True, suite=None, task=None):
        """
        基线数据比对、测试报告生成、测试报告数据写入DB
        :return:
        :param file 调用方脚本名称
        :param unique 多次执行是否只生成一份报告
        """
        project_home = get_project_home()

        try:
            pass_case = 0
            fail_case = 0
            create_time = self.created
            if file is not None:
                report_home = os.path.dirname(file).replace("testcases", "test_report")
            else:
                report_home = f"{project_home}{os.sep}test_report"

            os.makedirs(report_home, exist_ok=True)
            if unique is True:
                self.report_path = f"{report_home}{os.sep}{self.report_name}.html"
            else:
                self.report_path = f'{report_home}{os.sep}{self.report_name}_{datetime.now().strftime("%Y-%m-%d_%H%M%S_%f")[:-3]}.html'
            for i in range(len(self.report)):
                self.report[i]["id"] = i
                if self.report[i]["check_result"]:
                    pass_case += 1
                    self.report[i]["check_result"] = "通过"
                else:
                    fail_case += 1
                    self.report[i]["check_result"] = "失败"
            use_time = datetime.now() - self.start_time
            self.end_time = datetime.now()

            logs = ""
            if file is not None:
                logs = html.escape(read_log(file))
            if logs == "未获取到执行过程中的日志文件":
                if suite is not None:
                    logs = html.escape(read_log(suite))
            if logs == "未获取到执行过程中的日志文件":
                if task is not None:
                    logs = html.escape(read_log(task))

            # 生成报告前，转义报告数据
            for index, value in enumerate(self.report):
                if isinstance(value["response"], str):
                    self.report[index]["response"] = html.escape(value['response'])

                    self.report[index]["check_result"] = html.escape(value['check_result'])
                    self.report[index]["check_detail"] = [html.escape(i) for i in value['check_detail']] if isinstance(value['check_detail'], list) else value['check_detail']

                    self.report[index]["actual"] = html.escape(value['actual']) if isinstance(value['actual'], str) else value['actual']
                    self.report[index]["expect"] = html.escape(value['expect']) if isinstance(value['expect'], str) else value['expect']
            allData = {
                "createTime": create_time,
                "tableData": self.report,
                "title": self.report_name,
                "totalTime": round(use_time.total_seconds(), 2),
                "pass": pass_case,
                "fail": fail_case,
                "passrate": calc_rate(pass_case, fail_case),
                "total": fail_case + pass_case,
                "logs": logs,
                "stop_reason": self.stop_reason
            }
            report_lines = get_report_template(
                case_detail=json.dumps(
                    obj=allData,
                    default=lambda x: x.__dict__,
                    sort_keys=False,
                    indent=2,
                    ensure_ascii=False,
                ),
                case_pass=pass_case,
                case_fail=fail_case
            )
            with open(self.report_path, "w", encoding="utf-8") as f:
                f.write(report_lines)
            if self.output_json_file:
                with open(
                    self.report_path.replace(".html", ".json"), "w", encoding="utf-8"
                ) as f:
                    f.write(
                        json.dumps(
                            obj=allData,
                            default=lambda x: x.__dict__,
                            sort_keys=False,
                            indent=2,
                            ensure_ascii=False,
                        )
                    )
            self.pass_case = pass_case
            self.fail_case = fail_case
            log.info(f"{self.report_name} 执行结果：")
            log.info(f"  用例共计: {self.pass_case+self.fail_case} 条")
            log.info(f"  通过: {self.pass_case} 条")
            if self.fail_case > 0:
                log.error(f"  失败: {self.fail_case} 条")
            log.info(f"  测试报告已生成至：{self.report_path}")
            return self.report_path
        except Exception as e:
            log.error(f"生成报告错误：%s{str(e)}", traceback.format_exc())


if __name__ == "__main__":
    print(check_report_name("测试/、、\\yosh"))
