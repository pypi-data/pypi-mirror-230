# -*- coding: utf-8 -*-
# @Time : 2023/7/7
# @Author : chengwenping2


from pig_frame.http_request import *
from pig_frame.asserts import *
from pig_frame.decorators import pig_frame_case


@pig_frame_case(report_name="test_demo", creator="程文平")
def tset(test_case, **kwargs):
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
        case_assert=[
            (
                "返回码200",
                equal(
                    200,
                    jmespath.search("status_code", result),
                    filter_keys=None,
                    limit_keys=None,
                ),
            ),
            (
                "返回码不是200",
                not_equal(
                    200,
                    jmespath.search("status_code", result),
                    filter_keys=None,
                    limit_keys=None,
                ),
            ),
        ],
    )

    test_case.check(
        result,
        case_name="Http 返回码为 200",
        case_assert=[
            equal(
                200,
                jmespath.search("status_code", result),
                filter_keys=None,
                limit_keys=None,
            ),
            not_equal(
                200,
                jmespath.search("status_code", result),
                filter_keys=None,
                limit_keys=None,
            ),
        ],
    )
    test_case.check(
        result,
        case_name="Http 返回码为 200",
        case_assert=equal(
            200,
            jmespath.search("status_code", result),
            filter_keys=None,
            limit_keys=None,
        ),
    )


if __name__ == "__main__":
    kwargs = {}
    # env_config_file:环境配置文件相对路径（相对于conf/），例如/conf/uat.json就写uat.json，/conf/product/test.json就写product/test.json
    tset(env_config_file="test.json", **kwargs)
