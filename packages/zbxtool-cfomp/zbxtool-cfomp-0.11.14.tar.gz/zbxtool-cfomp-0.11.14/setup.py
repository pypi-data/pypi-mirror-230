#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Gary
# Datetime: 2022/12/2 16:07
# IDE: PyCharm
"""
    Package construction: 'zbxtool-cfomp'
"""
import os
from setuptools import setup, find_packages

if os.path.exists("requirements.txt"):
    with open(file="requirements.txt", mode="r", encoding="utf-8") as reqs_file:
        reqs = [req.strip() for req in reqs_file.readlines()]

setup(
    # 包名称
    name="zbxtool-cfomp",
    # 程序的简单描述
    description="A Zabbix Manager Tool",
    # 需要处理的包目录（通常为包含 __init__ 的文件夹）
    packages=find_packages(),
    package_data={"": ["configs.ini"]},
    # 自动包含所有受版本控制的数据文件
    include_package_data=True,
    # 不压缩包，而是以目录的形式安装
    zip_safe=True,
    # 程序适用的软件平台
    platforms=["Linux", "Windows"],
    # 当前模块依赖包
    install_requires=reqs,
    # 使用 setuptools_scm 插件自动管理包版本
    use_scm_version={
        "relative_to": __file__,
        "local_scheme": "no-local-version",
    },
    # setup.py 本身的依赖包，不会自动安装
    setup_requires=["setuptools_scm==5.0.2"],
    # 安装后自动生成 /usr/bin/zbxtool 可执行文件
    # 该文件入口指向 lib/cli.py 的 main 函数
    entry_points={
        "console_scripts": [
            "zbxtool = lib.cli:main"
        ],
    }
)
