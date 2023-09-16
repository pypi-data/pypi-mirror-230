# -*-coding:utf-8 -*-
"""
:创建时间: 2023/9/9 14:46
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division

if False:
    from typing import *

import sys

import setuptools

lib_name = 'aidevkit'

author = 'cpcgskill'
author_email = 'cpcgskill@outlook.com'

version = '0.3.3'

description = '一些ai开发过程中使用到的工具模块'

project_homepage = 'https://github.com/cpcgskill/aidevkit'

project_urls = {
    'Bug Tracker': 'https://github.com/cpcgskill/aidevkit/issues',
}

license_ = 'Apache Software License (Apache 2.0)'

python_requires = '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*'

console_scripts = []

with open("./requirements.txt", "rb") as f:
    install_requires_content = f.read().decode(encoding='utf-8')
    install_requires = install_requires_content.splitlines()
    install_requires = [i for i in install_requires if i and not i.startswith('#')]
    install_requires = [i for i in install_requires if set(i) != {' '}]

with open("README.md", "rb") as f:
    long_description = f.read().decode(encoding='utf-8')

setuptools.setup(
    name=lib_name,
    version=version,
    author=author,
    author_email=author_email,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=project_homepage,
    project_urls=project_urls,
    license=license_,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    package_dir={"": "src"},
    # # 使用自动搜索
    packages=setuptools.find_packages(where="src"),
    python_requires=python_requires,
    # 指定依赖
    install_requires=install_requires,
    # 指定启用包数据如log.ico这样的文件
    include_package_data=True,
    entry_points={
        # 控制台脚本
        "console_scripts": console_scripts,
    },
)
