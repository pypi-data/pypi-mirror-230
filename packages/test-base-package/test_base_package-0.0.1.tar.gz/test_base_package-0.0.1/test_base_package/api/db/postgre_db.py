# -*- coding: utf-8 -*-
import psycopg2

from utils.logger import logger


class PostGreDB:
    __conn = None

    def __init__(self, user, password, host, port, database, connection_factory=None, cursor_factory=None):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.connection_factory = connection_factory
        self.cursor_factory = cursor_factory

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()

    def connect(self):
        """
        连接PostGre数据库
        :return:
        """
        try:
            self.__conn = psycopg2.connect(database=self.database,
                                           user=self.user,
                                           password=self.password,
                                           host=self.host,
                                           port=self.port,
                                           connection_factory=self.connection_factory,
                                           cursor_factory=self.cursor_factory)

            return self.__conn
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
