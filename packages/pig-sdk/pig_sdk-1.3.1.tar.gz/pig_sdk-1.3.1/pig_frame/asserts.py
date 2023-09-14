# -*- coding: utf-8 -*-
# @Time : 2023/07/04
# @Author : chengwenping2
# @File : testcase.py
"""
文件说明：
"""

from pig_frame.common import *
from decimal import Decimal


def contain(exp, actual, result=None, filter_keys=None, limit_keys=None):
    """
    判断实际值是否包含在期望值中
    @param exp: 期望值可以传入字符串、dict、list、及多层嵌套对象
    @param actual: 实际值可以传入字符串、dict、list、及多层嵌套对象
    @param result: 一般不需要传入，初始已有差异时，可传入list
    @param limit_keys: 通过jsonpath条件表达式限制数据范围
    @param filter_keys: 需要跳过比对的keys list传入，写法['response.data.*','response.data','response[*].data'],
         .*结尾表示跳过对象，[*]过滤list对象,[1]指定list对象中的第二个
    @return: 原组形式返回（true，result）
    """
    if result is None:
        result = []
    if filter_keys is None:
        filter_keys = []
    if limit_keys is None:
        limit_keys = []
    if isinstance(exp, dict) or isinstance(exp, list):
        if isinstance(actual, type(exp)):
            exp_key_list = dict_to_simple(exp)
            actual_key_list = dict_to_simple(actual)
            # 获取两个对象所有key的交集
            mix_list = [val for val in exp_key_list if val in actual_key_list]
            # 实际值中存在，期望值中不存在的key
            diff_list_actual = list(set(exp_key_list).difference(set(actual_key_list)))
            # 比较相同key的value值
            for mix_key in mix_list:
                if not limit_check_key(limit_keys, mix_key):
                    continue
                if filter_key(filter_keys, mix_key):
                    continue
                if obj_search(exp, mix_key) != obj_search(actual, mix_key):
                    result = result + compare_number(
                        obj_search(exp, mix_key),
                        obj_search(actual, mix_key),
                        key=mix_key,
                    )
            for diff_actual_key in diff_list_actual:
                if not limit_check_key(limit_keys, diff_actual_key):
                    continue
                if filter_key(filter_keys, diff_actual_key):
                    continue
                result.append(f"{diff_actual_key} => 在实际值中不存在")
        else:
            result.append(f"期望值与实际值类型不匹配")
            return {
                "check_result": False,
                "check_detail": result,
                "check_type": "contain",
                "expect": exp,
                "actual": actual,
                "filter_keys": filter_keys,
                "limit_keys": limit_keys,
            }
    else:
        if str(actual).__contains__(str(exp)):
            return {
                "check_result": True,
                "check_detail": result,
                "check_type": "contain",
                "expect": exp,
                "actual": actual,
                "filter_keys": filter_keys,
                "limit_keys": limit_keys,
            }
        else:
            result.append(f"实际值 {actual} 中不存在 {exp}")
            return {
                "check_result": False,
                "check_detail": result,
                "check_type": "contain",
                "expect": exp,
                "actual": actual,
                "filter_keys": filter_keys,
                "limit_keys": limit_keys,
            }
    if len(result) == 0:
        return {
            "check_result": True,
            "check_detail": result,
            "check_type": "contain",
            "expect": exp,
            "actual": actual,
            "filter_keys": filter_keys,
            "limit_keys": limit_keys,
        }
    else:
        return {
            "check_result": False,
            "check_detail": result,
            "check_type": "contain",
            "expect": exp,
            "actual": actual,
            "filter_keys": filter_keys,
            "limit_keys": limit_keys,
        }


def not_contain(exp, actual, result=None, filter_keys=None, limit_keys=None):
    """
    判断实际值是不包含在期望值中
    @param exp: 期望值可以传入字符串、dict、list、及多层嵌套对象
    @param actual: 实际值可以传入字符串、dict、list、及多层嵌套对象
    @param result: 一般不需要传入，初始已有差异时，可传入list
     @param filter_keys: 需要跳过比对的keys list传入，写法['response.data.*','response.data','response[*].data'],
         .*结尾表示跳过对象，[*]过滤list对象,[1]指定list对象中的第二个
    @return: 原组形式返回（true，result）
    @param limit_keys: 通过jsonpath条件表达式限制数据范围
    """
    if result is None:
        result = []
    if filter_keys is None:
        filter_keys = []
    if limit_keys is None:
        limit_keys = []
    if isinstance(exp, dict) or isinstance(exp, list):
        if isinstance(actual, type(exp)):
            exp_key_list = dict_to_simple(exp)
            actual_key_list = dict_to_simple(actual)
            # 获取两个对象所有key的交集
            mix_list = [val for val in exp_key_list if val in actual_key_list]
            # 实际值中存在，期望值中不存在的key
            diff_list_actual = list(set(exp_key_list).difference(set(actual_key_list)))
            # 比较相同key的value值
            for mix_key in mix_list:
                if not limit_check_key(limit_keys, mix_key):
                    continue
                if filter_key(filter_keys, mix_key):
                    continue
                if obj_search(exp, mix_key) != obj_search(actual, mix_key):
                    result = result + compare_number(
                        obj_search(exp, mix_key),
                        obj_search(actual, mix_key),
                        key=mix_key,
                    )
            for diff_actual_key in diff_list_actual:
                if not limit_check_key(limit_keys, diff_actual_key):
                    continue
                if filter_key(filter_keys, diff_actual_key):
                    continue
                result.append(f"{diff_actual_key} => 在实际值中不存在")
        else:
            result.append(f"期望值与实际值类型不匹配")
            return {
                "check_result": False,
                "check_detail": result,
                "check_type": "not_contain",
                "expect": exp,
                "actual": actual,
                "filter_keys": filter_keys,
                "limit_keys": limit_keys,
            }
    else:
        if str(actual).__contains__(str(exp)):
            return {
                "check_result": False,
                "check_detail": result,
                "check_type": "not_contain",
                "expect": exp,
                "actual": actual,
                "filter_keys": filter_keys,
                "limit_keys": limit_keys,
            }
        else:
            result.append(f"实际值 {actual} 中不存在 {exp}")
            return {
                "check_result": True,
                "check_detail": result,
                "check_type": "not_contain",
                "expect": exp,
                "actual": actual,
                "filter_keys": filter_keys,
                "limit_keys": limit_keys,
            }
    if len(result) == 0:
        return {
            "check_result": False,
            "check_detail": result,
            "check_type": "not_contain",
            "expect": exp,
            "actual": actual,
            "filter_keys": filter_keys,
            "limit_keys": limit_keys,
        }
    else:
        return {
            "check_result": True,
            "check_detail": result,
            "check_type": "not_contain",
            "expect": exp,
            "actual": actual,
            "filter_keys": filter_keys,
            "limit_keys": limit_keys,
        }


def equal_no_order(exp: list or set, actual: list or set):
    """
    两个可迭代对象对比，list 或者 set

    重复元素会自动去重，使用时请保证入参没有重复数据
    @param actual: list or set实际结果
    @param exp: list or set 期望对象
    """
    result = []
    _exp = exp
    _actual = actual
    if isinstance(exp, list):
        _exp = set(exp)
    if isinstance(actual, list):
        _actual = set(actual)

    _diff = list(_exp.difference(_actual))
    if len(_diff) == 0:
        return {
            "check_result": True,
            "check_detail": result,
            "check_type": "equal",
            "expect": exp,
            "actual": actual,
            "filter_keys": [],
            "limit_keys": [],
        }
    else:
        result.append(f"{_diff} => 在实际值中不存在")
        return {
            "check_result": False,
            "check_detail": result,
            "check_type": "equal",
            "expect": exp,
            "actual": actual,
            "filter_keys": [],
            "limit_keys": [],
        }


def equal(exp, actual, result=None, filter_keys=None, limit_keys=None):
    """
    通用比对方法，验证是否相等
    @param result: list
    @param actual: object
    @param exp: object
    @param limit_keys: 通过jsonpath条件表达式限制数据范围
    @param filter_keys: 需要跳过比对的keys list传入，写法['response.data.*','response.data','response[*].data'],
         .*结尾表示跳过对象，[*]过滤list对象,[1]指定list对象中的第二个
    @return (True,result) 元组形式返回结果0是比对结果，1详细差异
    """
    if result is None:
        result = []
    if filter_keys is None:
        filter_keys = []
    if limit_keys is None:
        limit_keys = []
    if isinstance(exp, dict) or isinstance(exp, list):
        if isinstance(actual, type(exp)):
            exp_key_list = dict_to_simple(exp)
            actual_key_list = dict_to_simple(actual)
            # 获取两个对象所有key的交集
            mix_list = [val for val in exp_key_list if val in actual_key_list]
            # 期望值中存在，实际值中不存在的key
            diff_list_exp = list(set(exp_key_list).difference(set(actual_key_list)))
            # 实际值中存在，期望值中不存在的key
            diff_list_actual = list(set(actual_key_list).difference(set(exp_key_list)))
            # 比较相同key的value值
            for mix_key in mix_list:
                if not limit_check_key(limit_keys, mix_key):
                    continue
                if filter_key(filter_keys, mix_key):
                    continue
                if obj_search(exp, mix_key) != obj_search(actual, mix_key):
                    result = result + compare_number(
                        obj_search(exp, mix_key),
                        obj_search(actual, mix_key),
                        key=mix_key,
                    )
            for diff_exp_key in diff_list_exp:
                if not limit_check_key(limit_keys, diff_exp_key):
                    continue
                if filter_key(filter_keys, diff_exp_key):
                    continue
                result.append(f"{diff_exp_key} => 在实际值中不存在")
            for diff_actual_key in diff_list_actual:
                if not limit_check_key(limit_keys, diff_actual_key):
                    continue
                if filter_key(filter_keys, diff_actual_key):
                    continue
                result.append(f"{diff_actual_key} => 在期望值中不存在")
        else:
            result.append(f"期望值与实际值类型不匹配")
            return {
                "check_result": False,
                "check_detail": result,
                "check_type": "equal",
                "expect": exp,
                "actual": actual,
                "filter_keys": filter_keys,
                "limit_keys": limit_keys,
            }
    else:
        result = result + compare_number(exp, actual)
    if len(result) == 0:
        return {
            "check_result": True,
            "check_type": "equal",
            "check_detail": result,
            "expect": exp,
            "actual": actual,
            "filter_keys": filter_keys,
            "limit_keys": limit_keys,
        }
    else:
        return {
            "check_result": False,
            "check_type": "equal",
            "check_detail": result,
            "expect": exp,
            "actual": actual,
            "filter_keys": filter_keys,
            "limit_keys": limit_keys,
        }


def structure(
    exp, actual, result=None, filter_keys=None, limit_keys=None, check_value_type=False
):
    """
    通用比对方法，验证响应结构是否相同
    @param result: list
    @param actual: object
    @param exp: object
    @param limit_keys: 通过jsonpath条件表达式限制数据范围
    @param filter_keys: 需要跳过比对的keys list传入，写法['response.data.*','response.data','response[*].data'],
         .*结尾表示跳过对象，[*]过滤list对象,[1]指定list对象中的第二个
    @return (True,result) 元组形式返回结果0是比对结果，1详细差异
    @param check_value_type:是否需要比对字段类型
    """
    if result is None:
        result = []
    if filter_keys is None:
        filter_keys = []
    if limit_keys is None:
        limit_keys = []
    if type(exp) != type(actual):
        result.append(f"期望值: {exp} 与实际值: {actual} 类型不等")
    if isinstance(exp, dict) or isinstance(exp, list):
        if isinstance(actual, type(exp)):
            exp_key_list = dict_to_simple(exp)
            actual_key_list = dict_to_simple(actual)
            # 获取两个对象所有key的交集
            mix_list = [val for val in exp_key_list if val in actual_key_list]
            # 期望值中存在，实际值中不存在的key
            diff_list_exp = list(set(exp_key_list).difference(set(actual_key_list)))
            # 实际值中存在，期望值中不存在的key
            diff_list_actual = list(set(actual_key_list).difference(set(exp_key_list)))
            # 比较相同key的value值
            for mix_key in mix_list:
                if not limit_check_key(limit_keys, mix_key):
                    continue
                if filter_key(filter_keys, mix_key):
                    continue
                if (
                    type(obj_search(exp, mix_key)) != type(obj_search(actual, mix_key))
                    and check_value_type
                ):
                    result.append(
                        f"{mix_key} => 期望值: {obj_search(exp, mix_key)} 与实际值: "
                        f"{obj_search(actual, mix_key)} 类型不同"
                    )
            for diff_exp_key in diff_list_exp:
                if not limit_check_key(limit_keys, diff_exp_key):
                    continue
                if filter_key(filter_keys, diff_exp_key):
                    continue
                result.append(f"{diff_exp_key} => 在实际值中不存在")
            for diff_actual_key in diff_list_actual:
                if not limit_check_key(limit_keys, diff_actual_key):
                    continue
                if filter_key(filter_keys, diff_actual_key):
                    continue
                result.append(f"{diff_actual_key} => 在期望值中不存在")
        else:
            result.append(f"期望值与实际值类型不匹配")
            return {
                "check_result": False,
                "check_detail": result,
                "check_type": "structure",
                "expect": exp,
                "actual": actual,
                "filter_keys": filter_keys,
                "limit_keys": limit_keys,
            }
    else:
        if type(exp) != type(actual) and check_value_type:
            result.append(f"期望值: {exp} 与实际值: {actual} 类型不等")
    if len(result) == 0:
        return {
            "check_result": True,
            "check_type": "structure",
            "check_detail": result,
            "expect": exp,
            "actual": actual,
            "filter_keys": filter_keys,
            "limit_keys": limit_keys,
        }
    else:
        return {
            "check_result": False,
            "check_type": "structure",
            "check_detail": result,
            "expect": exp,
            "actual": actual,
            "filter_keys": filter_keys,
            "limit_keys": limit_keys,
        }


def not_equal(exp, actual, result=None, filter_keys=None, limit_keys=None):
    """
    通用比对方法，验证是否不等
    @param result: list
    @param actual: object
    @param exp: object
    @param limit_keys: 通过jsonpath条件表达式限制数据范围
    @param filter_keys: 需要跳过比对的keys list传入，写法['response.data.*','response.data','response[*].data'],
         .*结尾表示跳过对象，[*]过滤list对象,[1]指定list对象中的第二个
    @return (True,result) 元组形式返回结果0是比对结果，1详细差异
    """
    if result is None:
        result = []
    if filter_keys is None:
        filter_keys = []
    if limit_keys is None:
        limit_keys = []
    if isinstance(exp, dict) or isinstance(exp, list):
        if isinstance(actual, type(exp)):
            exp_key_list = dict_to_simple(exp)
            actual_key_list = dict_to_simple(actual)
            # 获取两个对象所有key的交集
            mix_list = [val for val in exp_key_list if val in actual_key_list]
            # 期望值中存在，实际值中不存在的key
            diff_list_exp = list(set(exp_key_list).difference(set(actual_key_list)))
            # 实际值中存在，期望值中不存在的key
            diff_list_actual = list(set(actual_key_list).difference(set(exp_key_list)))
            # 比较相同key的value值
            for mix_key in mix_list:
                if not limit_check_key(limit_keys, mix_key):
                    continue
                if filter_key(filter_keys, mix_key):
                    continue
                if obj_search(exp, mix_key) != obj_search(actual, mix_key):
                    result = result + compare_number(
                        obj_search(exp, mix_key),
                        obj_search(actual, mix_key),
                        key=mix_key,
                    )
            for diff_exp_key in diff_list_exp:
                if not limit_check_key(limit_keys, diff_exp_key):
                    continue
                if filter_key(filter_keys, diff_exp_key):
                    continue
                result.append(f"{diff_exp_key} => 在实际值中不存在")
            for diff_actual_key in diff_list_actual:
                if not limit_check_key(limit_keys, diff_actual_key):
                    continue
                if filter_key(filter_keys, diff_actual_key):
                    continue
                result.append(f"{diff_actual_key} => 在期望值中不存在")
        else:
            result.append(f"期望值与实际值类型不匹配")
            return {
                "check_result": True,
                "check_detail": result,
                "check_type": "not_equal",
                "expect": exp,
                "actual": actual,
                "filter_keys": filter_keys,
                "limit_keys": limit_keys,
            }
    else:
        result = result + compare_number(exp, actual)
    if len(result) == 0:
        return {
            "check_result": False,
            "check_type": "not_equal",
            "check_detail": result,
            "expect": exp,
            "actual": actual,
            "filter_keys": filter_keys,
            "limit_keys": limit_keys,
        }
    else:
        return {
            "check_result": True,
            "check_type": "not_equal",
            "check_detail": result,
            "expect": exp,
            "actual": actual,
            "filter_keys": filter_keys,
            "limit_keys": limit_keys,
        }


def expression(expression, expect="", actual=""):
    """
    自定义表达式断言
    :param expression:
    :return:
    """
    return {
        "check_result": bool(expression),
        "check_type": "expression",
        "check_detail": [],
        "expect": expect,
        "actual": actual,
        "filter_keys": [],
        "limit_keys": [],
    }


def compare_number(exp, actual, key=""):
    result = []
    try:
        if isinstance(exp, int) or isinstance(exp, float):
            if isinstance(actual, int) or isinstance(actual, float):
                if Decimal(str(exp)) != Decimal(str(actual)):
                    result.append(f"期望值:{key} {str(exp)} 与实际值: {str(actual)} 不等")
            else:
                if exp != actual:
                    result.append(
                        f"期望值:{key} {exp} {type(exp)}与实际值: {actual} {type(actual)}不等"
                    )
        else:
            if exp != actual:
                result.append(
                    f"期望值:{key} {exp} {type(exp)}与实际值: {actual} {type(actual)}不等"
                )
    except:
        if exp != actual:
            result.append(f"期望值:{key} {exp} {type(exp)}与实际值: {actual} {type(actual)}不等")
    return result


if __name__ == "__main__":
    data = {
        "responseI18nParam": None,
        "pageNum": 1,
        "pageSize": 10,
        "totalCount": 17,
        "dataList": [
            {
                "success": True,
                "statusCodeEnum": "SUCCESS",
                "statusCode": "0000",
                "messageCode": None,
                "message": None,
                "exception": None,
                "requestI18nParam": None,
            }
        ],
        "pageCount": 2,
    }
    data1 = {
        "responseI18nParam": None,
        "pageNum": 1,
        "pageSize": 10,
        "totalCount": 45,
        "dataList": [
            {
                "success": True,
                "statusCodeEnum": "SUCCESS",
                "statusCode": "00500",
                "messageCode": None,
                "message": None,
                "exception": None,
                "requestI18nParam": None,
            },
            {
                "success": True,
                "statusCodeEnum": "SUCCESS",
                "statusCode": "0000",
                "messageCode": None,
                "message": None,
                "exception": None,
                "requestI18nParam": None,
            },
        ],
        "pageCount": 2,
    }
    result = equal(exp=data, actual=data1, limit_keys=["dataList[0]"])
    print(result)
