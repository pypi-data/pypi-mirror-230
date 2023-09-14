# -*- coding: utf-8 -*-
# @Time : 2023/07/04
# @Author : chengwenping2
# @File : http_request.py
"""
文件说明：http请求执行器，
"""
import re
import traceback

import pyjson5
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from datetime import datetime
from requests.adapters import HTTPAdapter
from pig_frame import log
from pig_frame.exceptions import PigFrameCaseException
from pig_frame.ddt import process_mock_data


def request(method, url, description="", retry_times=1, **kwargs):
    """
    http请求统一处理，请求参数、响应、状态码等统一返回，请求网络异常时，间隔5S重试三次
    :param url:
    :param method:支持get、post、等常用请求方式
    :param description:接口描述
    :param retry_times:重试次数
    :param kwargs:扩展参数支持"headers", "cookies", "params", "data", "json"
    :param files 标准写法
    {
    "field1" : ("filename1", open("filePath1", "rb")),
    "field2" : ("filename2", open("filePath2", "rb"), "image/jpeg"),
    "field3" : ("filename3", open("filePath3", "rb"), "image/jpeg", {"refer" :"localhost"})
    }
    :return:
    """
    for key in kwargs:
        if key not in [
            "headers",
            "cookies",
            "params",
            "data",
            "json",
            "files",
            "auth",
            "timeout",
            "allow_redirects",
            "proxies",
            "hooks",
            "stream",
            "verify",
            "cert",
        ]:
            raise Exception(f"传入参数 {key} 不支持")
    for key in ["params", "data", "json"]:
        if kwargs.get(key) is not None:
            kwargs[key] = process_mock_data(kwargs[key])
    start_time = datetime.now()

    try:
        result = _request(method, url, description, retry_times, **kwargs)
    except Exception as e:
        raise PigFrameCaseException(
            description=description,
            case_name=str(e),
            check_detail=traceback.format_exc(limit=-1, chain=False),
            use_time=(datetime.now() - start_time).microseconds / 1000,
        )

    if result is None:
        raise PigFrameCaseException(
            description=description,
            case_name="接口返回结果为空",
            check_detail="接口返回结果为空",
            use_time=(datetime.now() - start_time).microseconds / 1000,
        )
    return result


def _request(method, url, description="", retry_times=1, **kwargs):
    s = requests.Session()
    s.mount("http://", HTTPAdapter(max_retries=retry_times))
    s.mount("https://", HTTPAdapter(max_retries=retry_times))

    start_time = datetime.now()
    r = s.request(
        method=str(method).lower(),
        # 调用方需要将完整 url 拆分为 host+path传递，且 host 包含协议部分
        url=url,
        # allow_redirects=kwargs.pop("allow_redirects", False),
        # timeout=kwargs.pop("timeout", 15),
        # verify=kwargs.pop("verify", False),
        # 扩展参数直接对外提供，调用方传递需要了解 requests 库的文档，将其组装为 json 格式通过入参 json 传递进来
        **kwargs,
    )
    use_time = (datetime.now() - start_time).microseconds / 1000
    result = None
    if r is not None:
        html_etree = None
        jsonp = None
        try:
            response = r.json()
            try:
                jsonp = pyjson5.loads(re.findall("\(.*\)", r.text)[0][1:-1])
            except:
                pass
        except:
            response = r.text
            try:
                html_etree = BeautifulSoup(r.text, 'html.parser')
            except:
                pass

        result = {
            "params": {
                "params": kwargs.get("params"),
                "data": kwargs.get("data"),
                "json": kwargs.get("json"),
            },
            "response": response,
            "jsonp": jsonp,
            "html_tree": html_etree,
            "status_code": r.status_code,
            "url": r.url,
            "path": r.request.path_url,
            # 请求耗时，单位 ms
            "use_time": use_time,
            "description": description,
            "headers": r.request.headers,
            "response_headers": r.headers,
            "method": str(method).upper(),
            "response_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        log.info(f"请求地址：{url}，请求入参：{result.get('params')}")
        log.info(f"请求响应：{response}")
        log.info(f"请求response_headers：{r.headers}")

    return result
