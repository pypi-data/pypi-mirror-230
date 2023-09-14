#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/1/26 12:06 下午
# @Author  : zhengyu.0985
# @FileName: setup.py
# @Software: PyCharm

import setuptools

# 项目运行需要的依赖
REQUIRES = [
    # 'attrs<20.0.0,>=19.3.0',
    'requests>=2.24.0,<3.0.0',
    # 'requests-toolbelt>=0.9.1,<1.0.0',
    # 'thriftpy2>=0.4.12,<0.5.0',
    # 'cython>=0.29.21,<0.40.0',
    'pytest>=4.0.0,<=6.2.2',
    # 'selenium>=3.141.0,<4.0.0',
    # 'iniconfig>=1.1.1,<2.0.0',
    # 'pexpect>=4.8.0,<5.0.0',
    # 'retry>=0.9.2,<1.0.0',
    # 'selenium-wire>=3.0.0,<10.0.0',
    # 'pytest-xdist>=2.0.0, <10.0.0',
    # 'jsonpath>=0.8.2, <3.0.0',
    # 'deepdiff>=5.0.2, <10.0.0',
    # 'Flask>=2.0.1, <10.0.0',
    # "allure-pytest>=2.9.42, <10.0.0",
    # "pytest-rerunfailures>=9.1.1, <20.0.0",
    # "numpy>=1.21.4,<1.22.0"
]

# 开发、测试过程中需要的依赖
DEV_REQUIRES = [
    # 'flake8>=3.5.0,<4.0.0',
    # 'mypy>=0.620; python_version>="3.4"',
    # 'tox>=3.0.0,<4.0.0',
    # 'isort>=4.0.0,<5.0.0',
    'pytest>=4.0.0,<5.0.0',
]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="51job-autotest-framework",
    version="0.3.5",
    author="Jason.RollingKing",
    author_email="386773780@qq.com",
    description="Python Project For QA Test",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/jason024/python_project",
    project_urls={
        "Bug Tracker": "https://gitee.com/jason024/python_project/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
