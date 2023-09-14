# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

__version__ = '0.0.3'  # 版本号
requirements = open('requirements.txt').readlines()  # 依赖文件

setup(
    name='test_base_package',
    version=__version__,
    author='自动化测试基础包',
    author_email='tianjincn@163.com',
    packages=find_packages(),
    python_requires='>=3.5.0',
    install_requires=requirements,  # 安装依赖
    description='python 自动化测试基础包'

)
