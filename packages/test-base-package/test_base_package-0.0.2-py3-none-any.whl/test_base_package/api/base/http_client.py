# -*- coding: utf-8 -*-
import requests
import json as _json

from requests import Response, Session

from jsonpath import jsonpath

from setting import base_url
from utils.logger import logger as api_logger
from unittest.case import TestCase

test_case = TestCase()


class HttpClient:
    # 接口做post一般都是采用json格式进行提交
    headers = {
        "content-type": "application/json;charset=UTF-8",
    }

    resp = Response()
    resp_json = None

    def __init__(self):
        self.__session = requests.session()

    def get(self, path, **kwargs):
        return self.__request(path, 'GET', **kwargs)

    def post(self, path, data=None, json=None, **kwargs):
        return self.__request(path, 'POST', data, json, **kwargs)

    def head(self, url, **kwargs):
        return self.__request(url, "HEAD", **kwargs)

    def put(self, url, **kwargs):
        return self.__request(url, "PUT", **kwargs)

    def delete(self, url, **kwargs):
        return self.__request(url, "DELETE", **kwargs)

    def options(self, url, **kwargs):
        return self.__request(url, "OPTIONS", **kwargs)

    def __request(self, url, method: str, data=None, json=None, **kwargs):
        headers = kwargs.get("headers")
        params = kwargs.get("params")
        url = base_url + url
        # 如果传入header不为空，那么更新header
        if headers:
            self.headers.update(headers)
        else:
            kwargs["headers"] = self.headers
        self.__request_log(url, method, data, json, params, self.headers)

        match method:
            case "GET":
                resp = self.__session.get(url, **kwargs)
            case "POST":
                resp = self.__session.post(url, data, json, **kwargs)
            case "HEAD":
                resp = self.__session.head(url, **kwargs)
            case "PUT":
                resp = self.__session.put(url, data, **kwargs)
            case "DELETE":
                resp = self.__session.delete(url, **kwargs)
            case "OPTIONS":
                resp = self.__session.options(url, **kwargs)
            case _:
                raise KeyError("validate not method {}".format(method))

        self.resp = resp

        if resp:
            self.resp_json = resp.json()
        self.__response_log(resp)
        return resp

    @staticmethod
    def __request_log(url, method, data=None, json=None, params=None, headers=None):
        api_logger.info(
            "请求地址:{url},请求方式:{method},请求头:{data},请求params参数: {json},请求体params参数:{params},请求体headers参数:{headers}".format(
                url=url, method=method, data=_json.dumps(data), json=_json.dumps(json), params=_json.dumps(params),
                headers=_json.dumps(headers)))

    @staticmethod
    def __response_log(resp):
        try:
            if resp.encoding != "utf-8":
                api_logger.info("返回信息 : {}".format(resp.text.encode(resp.encoding).decode('utf-8'), ensure_ascii=False))
            else:
                api_logger.info("返回信息 : {}".format(resp.text, ensure_ascii=False))
        except Exception as e:
            api_logger.error('系统错误：{}'.format(e))

    def check_response(self):
        """
        返回参数检查
        :return:
        """
        if self.resp_json is None:
            api_logger.error("Response is None")
            raise "Response is None"

    def assert_equal_resp_code(self, code: int, msg=None) -> "HttpClient":
        self.check_response()
        test_case.assertEqual(self.resp.status_code, code, msg=msg)
        return self

    def assert_true(self, rule, msg=None):
        self.check_response()
        expr = jsonpath(self.resp_json, rule)
        test_case.assertTrue(expr=expr, msg=msg)
        return self

    def assert_false(self, rule, msg=None):
        self.check_response()
        expr = jsonpath(self.resp_json, rule)
        test_case.assertFalse(expr=expr, msg=msg)
        return self

    def assert_equal(self, rule, second, msg=None) -> "HttpClient":
        self.check_response()
        first = self.get_value(self.resp_json, rule)
        test_case.assertEqual(first=first, second=second, msg=msg)

        return self

    def assert_not_equal(self, rule, second, msg=None) -> "HttpClient":
        self.check_response()
        first = self.get_value(self.resp_json, rule)
        test_case.assertNotEqual(first=first, second=second, msg=msg)

        return self

    def assert_in(self, rule, member, msg=None) -> "HttpClient":
        self.check_response()
        container = self.get_value(self.resp_json, rule)
        test_case.assertIn(member=member, container=container, msg=msg)

        return self

    def assert_not_in(self, rule, member, msg=None) -> "HttpClient":
        self.check_response()
        container = jsonpath(self.resp_json, rule)
        test_case.assertNotIn(member=member, container=container, msg=msg)
        return self

    def assert_is(self, rule, second, msg=None) -> "HttpClient":
        self.check_response()
        expr = jsonpath(self.resp_json, rule)
        test_case.assertIs(expr1=expr, expr2=second, msg=msg)
        return self

    def assert_is_not(self, rule, member, msg=None) -> "HttpClient":
        self.check_response()
        container = jsonpath(self.resp_json, rule)
        test_case.assertIsNot(member=member, container=container, msg=msg)
        return self

    def assert_is_none(self, rule, msg=None) -> "HttpClient":
        self.check_response()
        expr = jsonpath(self.resp_json, rule)
        test_case.assertIsNone(expr, msg=msg)
        return self

    def assert_is_not_none(self, rule, msg=None) -> "HttpClient":
        self.check_response()
        expr = jsonpath(self.resp_json, rule)
        test_case.assertIsNotNone(expr, msg=msg)
        return self

    def assert_regex(self, rule, expected_regex, msg=None) -> "HttpClient":
        self.check_response()
        text = jsonpath(self.resp_json, rule)
        test_case.assertRegex(text, expected_regex, msg=msg)
        return self

    def assert_not_regex(self, rule, expected_regex, msg=None) -> "HttpClient":
        self.check_response()
        text = jsonpath(self.resp_json, rule)
        test_case.assertNotRegex(text, expected_regex, msg=msg)
        return self

    def assert_match(self, eq: dict, key: str):
        """
        断言key
        :param eq:断言字典
        :param key:断言方式
        :return:
        """
        match key:
            case "assert_equal_resp_code":
                self.assert_equal_resp_code(eq.get("value"))
            case "assert_equal":
                self.assert_equal(eq.get("key"), eq.get("value"))
            case "assert_not_equal":
                self.assert_not_equal(eq.get("key"), eq.get("value"))
            case "assert_true":
                self.assert_in(eq.get("key"), eq.get("value"))
            case "assert_false":
                self.assert_false(eq.get("key"), eq.get("value"))
            case "assert_in":
                self.assert_in(eq.get("key"), eq.get("value"))
            case "assert_not_in":
                self.assert_not_in(eq.get("key"), eq.get("value"))
            case "assert_is":
                self.assert_is(eq.get("key"), eq.get("value"))
            case "assert_is_not":
                self.assert_is_not(eq.get("key"), eq.get("value"))
            case "assert_is_none":
                self.assert_is_none(eq.get("key"), eq.get("value"))
            case "assert_is_not_none":
                self.assert_is_not_none(eq.get("key"), eq.get("value"))
            case "assert_regex":
                self.assert_regex(eq.get("key"), eq.get("value"))
            case "assert_not_regex":
                self.assert_not_regex(eq.get("key"), eq.get("value"))
            case _:
                api_logger.error('系统错误：validate not key {}'.format(key))
                raise KeyError("validate not key {}".format(key))

        return

    @staticmethod
    def get_value(resp_json, rule) -> "HttpClient":
        """
        获取返回数据字符串
        :param resp_json:
        :param rule:
        :return: value
        """
        value = jsonpath(resp_json, rule)
        if len(value) == 1:
            value = jsonpath(resp_json, rule)[0]
        return value

    def validate(self, first) -> "HttpClient":
        """
        结果验证
        :param first:断言序列
        :return:
        """
        if isinstance(first, dict):
            for key in first.keys():
                eq = first.get(key)
                # 进行断言
                self.assert_match(eq=eq, key=key)
        elif isinstance(first, list):
            for item in first:
                if isinstance(item, dict):
                    for key in item.keys():
                        eq = item.get(key)
                        # 进行断言
                        self.assert_match(eq=eq, key=key)
                else:
                    api_logger.error("参数错误:{}", item)
        else:
            api_logger.error("暂不支持该参数类型:{}", first)

        return self
