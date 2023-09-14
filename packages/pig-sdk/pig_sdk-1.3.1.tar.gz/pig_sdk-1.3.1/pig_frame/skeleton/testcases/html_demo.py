# -*- coding: utf-8 -*-
# @Time : 2023/7/7
# @Author : chengwenping2

from pig_frame.asserts import *
from pig_frame.decorators import pig_frame_case
from pig_frame.common import *
from pig_frame.http_request import request


@pig_frame_case(report_name="HTML请求DEMO", creator="负责人", unique_report=True)
def case_template(test_case, **kwargs):
    result = request(
        method="get",
        url="http://127.0.0.1:5001/html",
        description="本地Mock Server返回html"
    )

    log.info(f'html:{result["html_tree"]}')

    test_case.check(
        result,
        case_name="返回html验证",
        case_assert=equal('<meta charset="utf-8"/>', str(result["html_tree"].contents[1]))
    )
    test_case.check(
        result,
        case_name="返回的content-type为json",
        case_assert=contain("text/html", result["response_headers"]["Content-Type"])
    )


if __name__ == "__main__":
    kwargs = {}
    # env_config_file:环境配置文件相对路径（相对于conf/），例如/conf/uat.json就写uat.json，/conf/product/test.json就写product/test.json
    case_template(env_config_file="test.json", **kwargs)
