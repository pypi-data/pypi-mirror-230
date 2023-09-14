#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
import allure
import pytest

from testcases import auth
from utils.read_data import file_data
from test_base_package.common.plugin import allure_plugin


@pytest.fixture(scope="function")
def execute_database_sql():
    yield


@allure.feature("系统登录")
class TestLogin:
    login_data = file_data.load_yaml("data/login/login.yml")

    @allure_plugin
    @pytest.mark.parametrize("login", login_data)
    def test_login(self, login):
        api = file_data.load_yaml("api/login/login.yml")
        auth.post(path=api.get("url"), json=login.get("json"), headers=api.get("headers"))
        auth.validate(login.get("validate"))
