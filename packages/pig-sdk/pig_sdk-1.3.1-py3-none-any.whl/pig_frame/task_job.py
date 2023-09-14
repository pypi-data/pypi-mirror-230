# -*- coding: utf-8 -*-
# @Time : 2023/7/4
# @Author : chengwenping2
# @File : task.py
"""
文件说明：调度任务
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger


class Task:
    def __init__(self):
        self.scheduler = BlockingScheduler()

    def add_task(self, function, cron: str, args=()):
        """
        添加调度任务
        :param function: 需要执行的方法
        :param cron: cron 标准表达式
        :param args: 执行方法依赖参数
        :return:
        """
        self.scheduler.add_job(function, CronTrigger.from_crontab(cron), args=args)

    def start_tasks(self):
        self.scheduler.start()


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(lambda x:print(x), CronTrigger.from_crontab("13 0/1 * * *"), args=("1"))
    scheduler.start()
