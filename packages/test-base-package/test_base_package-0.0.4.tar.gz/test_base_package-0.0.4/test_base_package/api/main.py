#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
import os


if __name__ == '__main__':
    # 更新测试报告
    os.system("allure generate ./tmp/allure_results -o ./report --clean")
