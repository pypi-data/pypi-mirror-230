# -*- coding: utf-8 -*-
import pymysql

from utils.logger import logger


class MySqlDB:
    __conn = None

    def __init__(self, host, user, password, database, charset="utf8mb4", cursor_class=pymysql.cursors.DictCursor):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.cursor_class = cursor_class

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()

    def connect(self):
        """
        连接mysql
        :return:
        """
        try:
            self.__conn = pymysql.connect(host=self.host,
                                          user=self.user,
                                          password=self.password,
                                          database=self.database,
                                          charset=self.charset,
                                          cursorclass=self.cursor_class)
        except Exception as err:
            logger.error(err)
            raise err

        return self.__conn

    def close(self):
        """
        关闭连接
        :return:
        """
        if self.__conn:
            self.__conn.close()
