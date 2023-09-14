# -*- coding: utf-8 -*-
import requests

baseUrl = "http://192.168.1.166:7010/"
resp = requests.post(url=baseUrl + "api/v1/public/public/login",
                     json={"account": "00003", "loginPw": "e10adc3949ba59abbe56e057f20f883e"})

if resp.status_code == 200 and resp.json().get("code") == 200:
    token = resp.json().get("data")

    resp = requests.post(url=baseUrl + "api/v1/money/supervised-money-settle/search",
                         json={
                             "page": 1,
                             "pageSize": 200,
                             "status": 6
                         },
                         headers={"Token": token})

    if resp.status_code != 200 or resp.json().get("code") != 200:
        print("查询异常")

    rows = resp.json().get("data")["rows"]

    for row in rows:
        resp = requests.post(url=baseUrl + "api/v1/money/supervised-money-settle/revoke/{}".format(row["id"]),
                             json={"opinion": "撤销"},
                             headers={"Token": token})

        if resp.status_code != 200 or resp.json().get("code") != 200:
            print(resp.text)

    #     resp = requests.post(url=baseUrl + "api/v1/money/supervised-money-settle/abandon/{}".format(row["id"]),
    #                          json={"abandonRemark": "不同意"},
    #                          headers={"Token": token})
    #
    #     if resp.status_code != 200 or resp.json().get("code") != 200:
    #         print(resp.text)

    # resp = requests.post(url=baseUrl + "api/v1/supervised/org-supervised-prisoner/search",
    #                      json={
    #                          "page": 1,
    #                          "pageSize": 1000,
    #                          "status": 1,
    #                          "supervisedAreaId": "288972232963788800",
    #                      },
    #                      headers={"Token": token})
    #
    # if resp.status_code != 200 or resp.json().get("code") != 200:
    #     print("查询异常")
    #
    # rows = resp.json().get("data")["rows"]
    # data = {
    #     "bankMoneyTypeId": "268027659152396289",
    #     "remark": "",
    #     "bankMoneyTypeName": "出所取款",
    #     "sum": 1,
    #     "settleParam": [
    #
    #     ]
    # }
    #
    # for row in rows:
    #     data["settleParam"].append({"supervisedId": row["supervisedId"], "releasedDate": "2022-12-15"})
    #
    # resp = requests.post(baseUrl + "api/v1/money/supervised-money-settle/batch", json=data, headers={"Token": token})
    #
    # if resp.status_code != 200 or resp.json().get("code") != 200:
    #     print(resp.text)
else:
    print("登录异常")
