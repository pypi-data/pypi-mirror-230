# -*- coding: utf-8 -*-
# @Time : 2023/07/04
# @Author : chengwenping2

def calc_rate(pass_case, fail_case):
    if pass_case + fail_case != 0:
        rate = round((pass_case / (pass_case + fail_case)) * 100, 2)
        rate = "%.2f" % rate
    else:
        rate = 0
    return rate
