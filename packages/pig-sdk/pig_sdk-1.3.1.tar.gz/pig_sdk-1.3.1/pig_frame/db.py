# -*- coding: utf-8 -*-
# @Time : 2023/07/04
# @Author : chengwenping2
# @File : db.py
"""
文件说明：封装常用公共方法
"""

import pymysql
from sshtunnel import SSHTunnelForwarder
from pymysql import converters, FIELD_TYPE
import redis


conv = converters.conversions
conv[FIELD_TYPE.NEWDECIMAL] = float  # convert decimals to float
conv[FIELD_TYPE.DATE] = str  # convert dates to strings
conv[FIELD_TYPE.TIMESTAMP] = str  # convert dates to strings
conv[FIELD_TYPE.DATETIME] = str  # convert dates to strings
conv[FIELD_TYPE.TIME] = str  # convert dates to strings


def mysql_execute(**kwargs):
    """
    mysql 查询工具
    :param kwargs:
    :return:
    """
    ssh_host = kwargs.get("ssh_host")
    ssh_prot = kwargs.get("ssh_prot")
    ssh_user = kwargs.get("ssh_user")
    ssh_password = kwargs.get("ssh_password")

    host = kwargs.get("host")
    port = kwargs.get("port")
    db = kwargs.get("db")
    user = kwargs.get("user")
    password = kwargs.get("password")
    limit = kwargs.get("limit")
    sql = kwargs.get("sql")
    if limit is None:
        limit = 200

    server = SSHTunnelForwarder(
        ssh_address_or_host=(ssh_host, ssh_prot),
        ssh_username=ssh_user,
        ssh_password=ssh_password,
        remote_bind_address=(host, port))
    server.start()

    conn = pymysql.connect(host="localhost",
                         port=server.local_bind_port,
                         user=user,
                         password=password,
                         database=db,
                         charset='utf8',
                         connect_timeout=100,
                         cursorclass=pymysql.cursors.DictCursor,
                         conv=conv)

    cursor = conn.cursor()
    try:
        cursor.execute(sql)
    finally:
        cursor.close()
        conn.close()
    return cursor.fetchmany(limit)
def redis_execute(**kwargs):
    """
    redis查询工具
    :param kwargs:
    :return:
    """
    host = kwargs.get("host")
    port = kwargs.get("port")
    pw = kwargs.get("password")
    key = kwargs.get("key")
    conn = redis.Redis(
            host=host,
            port=port,
            password=pw,
            db=0
        )

    try:
        val = conn.get(key)
    finally:
        conn.close()
    return val

