# -*- coding: utf-8 -*-
# @Time : 2023/07/04
# @Author : chengwenping2
# @File : my_thread.py
"""
文件说明：多线程执行任务，并获取返回
"""
import threading


class MyThread(threading.Thread):
    def __init__(self, func, args=(), kwargs=None, func_name=""):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None
        self.func_name = func_name

    def run(self):
        if self.kwargs is not None:
            self.result = self.func(*self.args, **self.kwargs)
        else:
            self.result = self.func(*self.args)

    def get_result(self):
        threading.Thread.join(self)  # 等待线程执行完毕
        try:
            return self.result, self.func_name
        except Exception:
            return None
