#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
import inspect
import os

import jinja2 as jinja2
import yaml

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_func() -> dict:
    """
    加载debug_talk函数
    :return:
    """
    import importlib

    debug_module = importlib.import_module("debug_talk")
    all_function = inspect.getmembers(debug_module, inspect.isfunction)
    return dict(all_function)


class ReadFileData:
    def load_yaml(self, file_path, encoding='utf-8'):
        try:
            with open(root_path + "\\" + file_path, encoding=encoding) as f:
                data = yaml.safe_load(f)
                return data

        except Exception as err:
            raise err


file_data = ReadFileData()


def render(tpl_path, **kwargs):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or './', encoding="gbk"), ).get_template(
        filename).render(**kwargs)
