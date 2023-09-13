# -*- coding: utf-8 -*-
from functools import wraps
from jsonpath import jsonpath

import allure

allure_list = [
    "title",
    "description",
    "description_html",
    "label",
    "severity",
    "feature",
    "story",
    "tag",
    "link",
    "issue",
    "testcase",
    "suite",
    "parent_suite",
    "sub_suite"
]


def allure_plugin(func):
    """
    allure定制测试报告插件
    :return:
    """

    @wraps(func)
    def plugin(*args, **kwargs):
        if not len(kwargs.keys()):
            return func(*args, **kwargs)

        for key in allure_list:
            rule = "$..{}".format(key)

            result = jsonpath(kwargs, rule)

            if getattr(allure.dynamic, key) and result and len(result):
                value = result[0]
                # 利用反射获取allure属性
                allure_func = getattr(allure.dynamic, key)

                # 执行allure方法
                allure_func(value)
            return func(*args, **kwargs)

    return plugin
