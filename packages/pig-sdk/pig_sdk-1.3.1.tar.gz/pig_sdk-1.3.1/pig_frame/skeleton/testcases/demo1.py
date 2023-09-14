# -*- coding: utf-8 -*-
# @Time : 2023/7/7
# @Author : chengwenping2

from pig_frame.asserts import *
from pig_frame.decorators import pig_frame_case
from pig_frame.common import *
from pig_frame.http_request import request


@pig_frame_case(report_name="用例名称", creator="负责人", unique_report=True)
def case_template(test_case, **kwargs):
    bar2 = kwargs.get("bar2")
    bar1 = kwargs.get("bar1")

    result = request(
        method="get",
        url="https://postman-echo.com/get",
        description="Postman Echo",
        json=None,
        data=None,
        params={"foo1": bar1, "foo2": bar2},
        headers=None,
    )

    test_case.check(
        result,
        case_name="Http 返回码为 200",
        case_assert=equal(200, jmespath.search("status_code", result)),
    )

    variable_name = jmespath.search("response.code", result)


if __name__ == "__main__":
    kwargs = {}
    # env_config_file:环境配置文件相对路径（相对于conf/），例如/conf/uat.json就写uat.json，/conf/product/test.json就写product/test.json
    case_template(env_config_file="test.json", **kwargs)
