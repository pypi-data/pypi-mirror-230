# -*- coding: utf-8 -*-
add_org_category = [
    {
        "json": {
            "createdAt": None,
            "allowDel": False,
            "name": "",
            "code": "",
            "remark": "",
            "orgLan": {
                "supervisedOrg": "看守所",
                "orgShort": "所",
                "supervisedArea": "监管区域",
                "supervisedShortArea": "监",
                "supervised": "在押人员",
                "supervisedShort": "犯",
                "user": "管教",
                "userManager": "管教管理员",
                "detain": "收押",
                "supervisionTime": "收押期限",
                "supervisionTimeShort": "期",
                "remainingSupervisionTime": "余期",
                "releaseSupervision": "出所",
                "supervising": "在押"
            },
            "creator": ""
        },
        "validate": {
            "assert_equal": {
                "key": "$.code",
                "value": 201
            }
        }
    },
]
