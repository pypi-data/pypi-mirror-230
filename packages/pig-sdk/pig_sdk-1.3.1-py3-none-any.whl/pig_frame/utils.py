# -*- coding: utf-8 -*-
# @Time : 2023/7/4
# @Author : chengwenping2
import io
import json
import time

import json5

from pig_frame.common import get_project_home


def tail_f(file_name, callback, interval=0.1):
    """
    Unix tail follow implementation in Python.can be used to monitor changes to a file.
    :param file_name: 文件名称
    :param callback: If a callback function is registered it is called with every new line
    :param interval: Number of seconds to wait between each iteration; Defaults to 0.1.
    """
    with open(file_name) as file_:
        # Go to the end of file
        file_.seek(0, io.SEEK_END)
        while True:
            curr_position = file_.tell()
            line = file_.readline()
            if not line:
                file_.seek(curr_position)
            else:
                callback(line)
            time.sleep(interval)


def tail(file_name, line_count=10, encoding="utf-8"):
    """
    读取某文本文件最后 N 行
    :param file_name: 文件名称
    :param line_count: 读多少行
    :param encoding: 文件编码
    :return: 数组格式的行列表
    """
    f = open(file_name, mode="rb")
    f.seek(0, io.SEEK_END)
    file_size = f.tell()
    if file_size == 0 or line_count <= 0:
        return []

    lines = []
    prev_char = None
    curr_line = bytearray()
    chars_read = 0
    f.seek(-1, io.SEEK_END)
    while True:
        curr_char = f.read(1)
        chars_read += 1
        # 以下三个步骤：增加字符、增加行、跳出循环，如果文件已经读完，则都要做
        if curr_char not in (b"\n", b"\r") or chars_read == file_size:
            curr_line.extend(curr_char)
        if (
            curr_char == b"\n"
            or (curr_char == b"\r" and not prev_char == b"\n")
            or chars_read == file_size
        ):
            curr_line.reverse()
            lines.append(bytes(curr_line).decode(encoding))
            curr_line.clear()
        if len(lines) == line_count or chars_read == file_size:
            break
        # 往前退一个字节
        f.seek(-2, io.SEEK_CUR)
        prev_char = curr_char
    lines.reverse()

    f.close()
    return lines


def save_config_by_json(file_name, key, value):
    """
    保存配置到Json格式的配置文件，有就更新，没有就新增

    :param file_name:文件名称，环境配置文件相对路径（相对于conf/），例如/conf/pre.json就写pre.json，/conf/product/test.json就写product/test.json
    :param key: 配置项名称
    :param value: 配置值
    :return True/False
    """
    return save_configs_by_json(file_name,  key, value)


def save_configs_by_json(file_name, key, value):
    """
    保存配置到Json格式的配置文件，有就更新，没有就新增
    :param file_name:文件名称，环境配置文件相对路径（相对于conf/），例如/conf/pre.json就写pre.json，/conf/product/test.json就写product/test.json
    :param key_values: key：value 格式的字典
    :return True/False
    """
    try:
        file_name = get_project_home() + "/conf/" + file_name
        f = open(file_name, "r", encoding="utf-8")
        old = json5.load(f)
        f.close()

        list = key.split(".")
        old[list[0]][list[1]] = value

        f = open(file_name, "w", encoding="utf-8")
        # rs = {**old, **key_values}
        f.write(json.dumps({**old}, indent=2, ensure_ascii=False))
        f.close()
        return True
    except:
        return False

