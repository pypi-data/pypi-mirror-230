# -*- coding: utf-8 -*-
from datetime import datetime


def current_date() -> str:
    """
    获取当前时间
    :return:
    """
    return datetime.now().strftime("%Y%m%d")


