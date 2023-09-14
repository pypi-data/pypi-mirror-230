# -*- coding: utf-8 -*-
# @Time : 2023/7/7
# @Author : chengwenping2
"""
文件说明：批量执行测试用例demo，执行脚本必须位于testcases目录下，可按需包装
"""
from pig_frame.decorators import pig_frame_suite


@pig_frame_suite(suite_name="测试集", creator="负责人")
def run_suite(test_suite, **kwargs):
    # 改成 True 可以并行执行用例
    test_suite.parallel = False
    test_suite.add_case("idl_demo.py", **kwargs)
    # test_suite.add_cases_by_folder(folder_path=f"", exclude=['系统'], kwargs=kwargs)
    # test_suite.add_cases_by_folder(folder_path=f"", kwargs=kwargs)


if __name__ == "__main__":
    # env_config_file:环境配置文件相对路径（相对于conf/），例如/conf/uat.json就写uat.json，/conf/product/test.json就写product/test.json
    run_suite(env_config_file='dev.json')
