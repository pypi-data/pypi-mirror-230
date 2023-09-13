# -*- coding: utf-8 -*-
import allure
import pytest

from setting import page
from testcases import auth
from utils.read_data import file_data
from test_base_package.common.plugin import allure_plugin


@allure.feature("组织类别")
class TestOrgCategory:
    api = file_data.load_yaml("api/org_category/org_category.yml")
    add_org_category_data = file_data.load_yaml("data/org_category/add_org_category.yml", "gbk")

    @allure.title("查询组织类别")
    def test_search_org_category(self):
        auth.post(self.api.get("get"), json=page)
        auth.assert_equal_resp_code(200)

    @allure_plugin
    @pytest.mark.parametrize("data", add_org_category_data)
    def test_add_org_category(self, data):
        auth.post(path=self.api.get("post"), json=data.get("json"))
        auth.validate(data.get("validate"))
        auth.assert_in(rule="$.msg", member="名称", msg="查询产参数")

    # def test_put_org_category(self):
    #     auth.post(path=self.api.get("get"), json=page)
    #     auth.validate(data.get("validate"))
