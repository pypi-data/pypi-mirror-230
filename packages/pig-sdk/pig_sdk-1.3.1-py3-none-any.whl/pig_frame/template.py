# -*- coding: utf-8 -*-
# @Time : 2023/7/4
# @Author : chengwenping2

from jinja2 import Environment, PackageLoader
from pig_frame.num_util import calc_rate

jinja2_env = Environment(loader=PackageLoader('pig_frame', 'templates'))


def get_report_template(case_detail, case_pass, case_fail):
    template = jinja2_env.get_template('test_case_report.html')
    kwargs = {
        "echart_pass": case_pass,
        "echart_fail": case_fail,
        "alldataInstert": case_detail
    }
    return template.render(**kwargs)


def get_mail_html(total_scene, pass_case, fail_case, detail, fail_scene, use_time):
    for item in detail:
        item["rate"] = calc_rate(item["pass_case"], item["fail_case"])

    template = jinja2_env.get_template('test_suite_report.html')
    kwargs = {
        "total_scene": total_scene,
        "fail_scene": fail_scene,
        "use_time": use_time,
        "pass_case": pass_case,
        "fail_case": fail_case,
        "total_case": pass_case + fail_case,
        "rate": calc_rate(pass_case, fail_case),
        "cases": detail,
        "start_time": detail[0]["start_time"],
        "end_time": detail[-1]["end_time"],
    }
    return template.render(**kwargs)

def generate_json_template(**kwargs):
    template = jinja2_env.get_template('idl.json')
    return template.render(**kwargs)
