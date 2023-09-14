# -*- coding: utf-8 -*-
# @Time : 2023/7/7
# @Author : chengwenping2

from pig_frame.asserts import *
from pig_frame.decorators import pig_frame_case
from pig_frame.common import *
from pig_frame.http_request import request
from pig_frame.test_case import TestCase


@pig_frame_case(report_name="接口返回值是否正确", creator="负责人")
def case_template(test_case: TestCase, **kwargs):

    result = request(
        method="get",
        url="https://postman-echo.com/get",
        description="Postman Echo",
        json=None,
        data=None,
        params={"foo1": "bar1", "foo2": "bar2"},
        headers=None,
    )

    test_case.check(
        result,
        case_name="入参原样返回",
        case_assert=equal(
            {"foo1": "bar1", "foo2": "bar2"}, jmespath.search("response.args", result)
        ),
    )
    test_case.stop("用户主动结束用例")

    test_case.check(
        result,
        case_name="入参bar1原样返回",
        case_assert=equal("bar1", jmespath.search("response.args.foo1", result)),
    )


if __name__ == "__main__":
    kwargs = {}
    # env_config_file:环境配置文件相对路径（相对于conf/），例如/conf/uat.json就写uat.json，/conf/product/test.json就写product/test.json
    case_template(env_config_file="uat.json", **kwargs)
