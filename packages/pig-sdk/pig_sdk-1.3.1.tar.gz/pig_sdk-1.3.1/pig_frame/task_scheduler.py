# -*- coding: utf-8 -*-
# @Time : 2023/7/4
# @Author : chengwenping2
# @File : scheduler.py
"""
文件说明：定时批量执行测试用例并发送测试报告
"""

import os
import sys
from datetime import datetime

from pig_frame.runner import run_testcase_suite
from pig_frame.se_common import get_case_type

from pig_frame import log
from pig_frame.common import get_project_home, report_overview
import pyjson5 as json5
import traceback
from pig_frame.mail import sent_mail
from pig_frame.task_job import Task
from pig_frame.test_suite import TestSuite


def write_report(report_name, content):
    report_path = ""
    try:
        project_home = get_project_home()
        if not os.path.exists(f"{project_home}{os.sep}test_report"):
            os.mkdir(f"{project_home}{os.sep}test_report")
        report_path = f'{project_home}{os.sep}test_report{os.sep}{report_name}.html'
        # report_path = f'{project_home}{os.sep}test_report{os.sep}{report_name}_{datetime.now().strftime("%Y-%m-%d_%H%M%S_%f")[:-3]}.html'
        log.info(f"{report_name}测试报告生成路径：{report_path}")
        f = open(report_path, "w", encoding="utf-8")
        f.write(content)
        f.close()
        return report_path
    except:
        return report_path


def run_cases(cases, task_detail):
    results = _run_cases(cases, task_detail)
    return results


def _run_cases(cases, task_detail):
    """
    通过定时任务执行用例，并收集用例执行结果发送报告
    :param cases: 用例列表
    :param task_detail: 配置的task详情
    :return:
    """
    begin_time = datetime.now()
    schedule_result = {}
    testcase = []
    testsuites = []
    for item in cases:
        if get_case_type(item.get("case_file")) == "用例集":
            testsuites.append(item)
        else:
            testcase.append(item)
    # 执行测试集
    suite_results = []
    task_name = task_detail.get("task_name")
    for suite in testsuites:
        try:
            kwargs = suite.get("kwargs")
            if kwargs is None:
                kwargs = {}
            suite_results = suite_results + run_testcase_suite(
                suite["case_file"], task_name, env_config_file=suite.get("case_args"), **kwargs
            ).get("results")

        except:
            continue
    # 执行测试用例
    test_suite = TestSuite()
    test_suite.test_cases = testcase
    results = test_suite.run_cases()

    # 汇总执行结果发送报告
    sum_results = results.get("results") + suite_results
    report_content = report_overview(sum_results, upload=False)
    report_name = task_detail.get("subject", "自动化用例执行报告")
    report_subject = task_detail.get("subject", "自动化用例执行报告") + datetime.now().strftime(
        "%Y-%m-%d_%H%M%S_%f")[:-3]

    # 更新执行记录
    suite_report_path = write_report(report_name, report_content[0])
    sum_pass = 0
    sum_fail = 0

    for sub_result in sum_results:
        sum_pass += sub_result.pass_case
        sum_fail += sub_result.fail_case

    if sum_fail > 0:
        report_subject = "[异常]" + report_subject
    else:
        report_subject = "[正常]" + report_subject

    sender = task_detail.get("sender")

    if sender is None:
        log.warn("用户未配置发件人邮箱，测试报告将生成至本地")
    else:
        try:
            sent_mail(
                sender=sender,
                sender_alias=task_detail.get("senderAlias"),
                cc=task_detail.get("cc", []),
                to=task_detail.get("to"),
                subject=report_subject,
                body=report_content[0],
                att=report_content[1]
            )
        except:
            log.info(f"发送测试报告失败{traceback.format_exc()}")

    schedule_result["sender"] = sender
    schedule_result["sender_alias"] = task_detail.get("senderAlias", "pig_frame")
    schedule_result["to"] = task_detail.get("to")
    schedule_result["cc"] = task_detail.get("cc")
    schedule_result["subject"] = report_subject
    schedule_result["pass_case"] = sum_pass
    schedule_result["fail_case"] = sum_fail
    schedule_result["report_content"] = report_content
    schedule_result["begin_time"] = begin_time
    schedule_result["end_time"] = datetime.now()
    schedule_result["case_results"] = sum_results
    return schedule_result


def run_task_once(schedule_config="conf/scheduler.json", task_name=None, project_home=None):
    """
    读取任务配置启动定时任务
    @project_home 可自己指定项目根目录
    :return:
    """
    try:
        if project_home is None:
            project_home = get_project_home()
        task_json = f"{project_home}{os.sep}{schedule_config}"
        if not os.path.exists(task_json):
            log.error(f"{schedule_config}文件不存在，请先配置任务执行脚本")

        with open(task_json, "r", encoding="utf-8") as file:
            task_list = json5.loads(file.read())
            for task in task_list:
                task["task_name"] = task_name
                cases = []
                for case in task.get("testcases"):
                    cases.append(
                        {
                            "case_file": os.path.abspath(
                                project_home
                                + f"{os.sep}testcases{os.sep}"
                                + case.get("file_path")
                            ),
                            "case_args": case.get("env_config_file"),
                            "kwargs": case.get("kwargs")
                            if case.get("kwargs") is not None
                            else {},
                        }
                    )

                run_cases(cases, task)
    except:
        log.error("解析task任务失败")
        log.error(traceback.format_exc())


def run_task(schedule_config="conf/scheduler.json"):
    """
    读取任务配置启动定时任务
    :return:
    """
    try:
        sys.path.append(os.getcwd())
        project_home = get_project_home()
        task_json = f"{project_home}{os.sep}{schedule_config}"
        if os.path.exists(task_json):
            with open(task_json, "r", encoding="utf-8") as file:
                task_obj = json5.loads(file.read())
            task_detail = task_obj
            t = Task()
            if task_detail is not None:
                for task in task_detail:
                    cases = []
                    for case in task.get("testcases"):
                        cases.append(
                            {
                                "case_file": os.path.abspath(
                                    project_home
                                    + f"{os.sep}testcases{os.sep}"
                                    + case.get("file_path")
                                ),
                                "case_args": case.get("env_config_file"),
                                "kwargs": case.get("kwargs")
                                if case.get("kwargs") is not None
                                else {},
                            }
                        )
                    t.add_task(
                        run_cases,
                        str(task.get("cron")).replace("?", "*"),
                        args=(cases, task),
                    )

                    if task.get("run_on_start"):
                        # 立即执行
                        run_cases(cases, task)
            log.info("定时任务已启动")
            t.start_tasks()
        else:
            log.info(f"{schedule_config}文件不存在，请先配置任务执行脚本")
    except:
        log.error("解析task任务失败")
        log.error(traceback.format_exc())


if __name__ == "__main__":
    run_task("templates/conf/scheduler.json")
