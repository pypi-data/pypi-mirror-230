# -*- coding: UTF-8 -*-
# @Time : 2023/9/5
# @Author : chengwenping2

from setuptools import setup
import pig_frame


def readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()


setup(
    name="pig_sdk",
    version=pig_frame.__version__[0],
    description="接口自动化框架",
    long_description=readme(),
    keywords="自动化",
    packages=[
        "pig_frame",
        "pig_frame/log",
    ],
    package_data={
        "pig_frame": [
            "templates/*.*",
            "skeleton/*",
            "skeleton/*.*",
            "skeleton/**/*.*",
            "skeleton/**/**/*.*",
            "skeleton/**/**/**/*.*",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Topic :: Utilities",
        # # 许可证信息
        # "License :: MIT License",
    ],
    url="https://git.oak.net.cn/test_group/pigs_sdk/-/tree/master/pig_frame",
    license="MIT",
    author="chengwenping2",
    author_email="chengwenping2@newhope.cn",
    maintainer="chengwenping2",
    maintainer_email="chengwenping2@newhope.cn",
    install_requires=[
        "jsonpath~=0.82",
        "PyMySQL~=1.0.3",
        "jmespath~=0.10.0",
        "Requests~=2.31.0",
        "setuptools~=56.0.0",
        "psutil~=5.9.5",
        "XMind~=1.2.0",
        "APScheduler~=3.10.1",
        "pyjson5~=1.6.2",
        "json5~=0.9.14",
        "Faker~=18.10.1",
        "Jinja2~=3.1.2",
        "termcolor~=2.3.0",
        "openpyxl~=3.1.2",
        "urllib3~=1.26.16",
        "beautifulsoup4~=4.12.2",
        "sshtunnel~=0.4.0",
        "redis~=5.0.0"
    ],
    extras_require={
      'GUI': ["PyQt6~=6.2.0"]
    },
    zip_safe=False,
)
