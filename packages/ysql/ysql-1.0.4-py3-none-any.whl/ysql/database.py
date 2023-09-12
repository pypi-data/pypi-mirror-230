# -*- coding: utf-8 -*-
"""
@Project ：ysql
@File    ：database.py
@IDE     ：PyCharm 
@Author  ：大风起兮呼呼呼
@Email   ：dfqxhhh@163.com
@Date    ：2023/9/10 
"""

import os
import sqlite3

# 传递路数据库路径参数的装饰器
from abc import ABC, abstractmethod
from collections import namedtuple


def Path(path: str):
    def wrapper(cls):
        # 确保目录存在
        db_folder = os.path.dirname(path)
        os.makedirs(db_folder, exist_ok=True)
        # 新增数据库路径属性
        setattr(cls, "db_path", path)
        return cls

    return wrapper


class ABCDatabase(ABC):
    """数据库类的抽象类，定义需要实现的方法"""

    @abstractmethod
    def connect(self):
        """连接数据库"""
        pass

    @abstractmethod
    def disconnect(self):
        """断开数据库连接"""
        pass

    @abstractmethod
    def create_tables(self):
        """创建全部表"""
        pass

    @abstractmethod
    def commit(self):
        """提交事务"""
        pass

    @abstractmethod
    def rollback(self):
        """回滚事务"""
        pass


class MetaDatabase(ABCDatabase):

    def __new__(cls, *args, **kwargs):
        # 获取子类的所有属性
        subclass_attrs = dir(cls)

        # 初步筛选静态变量（不包括方法和特殊属性）
        static_attrs = [attr for attr in subclass_attrs
                        if not callable(getattr(cls, attr)) and not attr.startswith("__")]
        # 根据是否具有entity属性筛选出最终dao属性
        dao_list = [getattr(cls, attr) for attr in static_attrs
                    if hasattr(getattr(cls, attr), "entity")
                    and hasattr(getattr(cls, attr), "update_cursor")]

        # 赋值dao_list为类属性，以便在类内部可见
        cls.__dao_list = dao_list

        # 暂不支持单例模式
        return super().__new__(cls, *args, **kwargs)

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self, if_allow_multithreading=True):
        # 设置多线程连接
        self.connection = sqlite3.connect(self.db_path, check_same_thread=not if_allow_multithreading)
        # 修改row_factory，使得返回结果为具名元组
        self.connection.row_factory = self.dict_factory
        self.cursor = self.connection.cursor()
        self.__update_cursor()

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def create_tables(self):
        for dao in self.__dao_list:
            sql_command = dao.get_sql_create_table()
            self.__execute(sql_command)
        self.commit()

    # ================================================================================================================
    # 类内使用的方法
    def __update_cursor(self):
        for dao in self.__dao_list:
            dao.update_cursor(cursor=self.cursor)

    def __execute(self, query, params=None):
        cursor = self.connection.cursor()
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)

        return cursor

    @staticmethod
    def dict_factory(cursor, row: tuple):
        """转换查询结果格式为具名元组"""
        # 获取列描述信息
        column_names = [description[0] for description in cursor.description]
        # 使用列名创建具名元组
        FieldTuple = namedtuple("Result", column_names)
        return FieldTuple(*row)
