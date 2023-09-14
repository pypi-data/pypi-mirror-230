# -*- coding: utf-8 -*-
# @Time : 2023/7/4
# @Author : chengwenping2
# @File : test_suite.py
"""
文件说明：可管理多个测试用例，批量执行测试用例
"""
import traceback
import os
from pig_frame import log
from pig_frame.runner import run_testcase_script
from pig_frame.my_thread import MyThread
from pig_frame.common import create_overview_report, get_cases_by_folder
from pig_frame.se_common import get_case_type

class TestSuite:
    def __init__(self, task_name="巡检集", suite_name="测试集", author="System", case_home=None):
        self.test_cases = []
        self.parallel = False
        self.suite_name = suite_name
        self.case_home = case_home
        self.author = author
        self.suite = f"{self.case_home}{os.sep}{self.suite_name}.py"
        self.task_name = task_name
        self.task = f"{self.case_home}{os.sep}{self.task_name}.py"

    def add_cases_by_folder(self, folder_path, env_config_file=None, exclude: list[str] = None, kwargs=None):
        """
        通过文件夹维度批量添加测试用例
        @param folder_path:用例目录绝对路径
        @param env_config_file:
        @param exclude: 排除条目，传递字符串数组
        @param kwargs:
        """
        if self.case_home is not None:
            folder_path = f"{self.case_home}{os.sep}{folder_path}"
        folder_path = os.path.abspath(folder_path)
        suite = f"{self.case_home}{os.sep}{self.suite_name}.py"
        cases = get_cases_by_folder(folder_path=folder_path, exclude=exclude)
        for item in cases:
            if get_case_type(item) in ["用例集", "未知"]:
                continue
            if kwargs is None:
                kwargs = {}
            self.add_case(item, env_config_file, **kwargs)

    def add_case(self, file, env_config_file=None, **kwargs):
        """
        添加测试用例
        :param file: 测试用例绝对路径
        :param env_config_file: 环境变量文件，相对于conf/目录
        :kwargs :用户自定义变量可通过此参数添加
        :return:
        """
        env_config_file = env_config_file or kwargs.pop('suite_env_config_file', 'test.json')
        if self.case_home is not None:
            if str(os.path.abspath(file)).startswith(os.path.abspath(self.case_home)):
                folder_path = file
            else:
                folder_path = f"{self.case_home}{os.sep}{file}"
        else:
            folder_path = file
        folder_path = os.path.abspath(folder_path)

        if str(env_config_file).__contains__("testcases"):
            env_config_file = str(env_config_file).split("testcases")[1]
        self.test_cases.append(
            {"case_file": folder_path, "case_args": env_config_file, "task":self.task, "suite":self.suite, "kwargs": kwargs}
        )

    def get_cases(self):
        return self.test_cases

    def run_cases(self):
        results = self._run_cases()
        return results

    def _run_cases(self):
        """
        批量执行测试用例
        :return: 返回测试用例结果[]
        """
        results = []

        log.info("开始执行任务")
        if self.parallel:
            threads = []
            for case in self.test_cases:
                t = MyThread(
                    func=run_testcase_script,
                    args=(case["case_file"], case["case_args"]),
                    kwargs=case["kwargs"],
                    func_name=case,
                )
                threads.append(t)
                t.start()
            for t in threads:
                data = t.get_result()
                result = data[0]
                case_info = data[1]

                results.append(t.get_result()[0])
                log.info(f"测试报告：{t.get_result()}")

        else:
            for case in self.test_cases:
                try:
                    result = run_testcase_script(
                        case["case_file"], case["task"], case["suite"], case["case_args"], **case["kwargs"]
                    )
                    if result is not None:
                        results.append(result)
                        log.info(f"{case['case_file']} 测试报告：{result.report_path}")
                except:
                    log.info(f"{case['case_file']} 执行失败：{traceback.format_exc()}")

        try:
            report_path = create_overview_report(
                project_home=self.case_home.split("testcases")[0],
                report_name=self.suite_name,
                results=results,
            )
        except:
            report_path = ""
        total_case = 0
        pass_case = 0
        fail_case = 0
        for item in results:
            total_case += item.pass_case + item.fail_case
            pass_case += item.pass_case
            fail_case += item.fail_case
        return {
            "results": results,
            "suite_name": self.suite_name,
            "author": self.author,
            "total_case": total_case,
            "pass_case": pass_case,
            "fail_case": fail_case,
            "report_path": report_path,
        }
