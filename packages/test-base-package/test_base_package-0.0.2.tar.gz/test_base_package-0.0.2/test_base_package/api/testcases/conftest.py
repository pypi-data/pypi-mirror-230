# -*- coding: utf-8 -*-
import allure
import pytest

from testcases import auth
from utils.data import dataRow
from utils.read_data import file_data


@pytest.fixture(scope="session", autouse=True)
def login():
    api = file_data.load_yaml("api/login/login.yml")
    resp = auth.post(path=api.get("url"), json=dataRow.get("web_info"), headers=api.get("headers"))
    auth.assert_equal_resp_code(200).assert_equal("$.code", 200)
    result = resp.json()
    auth.headers = {"Token": result["data"]}
