# -*- coding: utf-8 -*-
"""
@Project ：ysql
@File    ：entity.py
@IDE     ：PyCharm 
@Author  ：大风起兮呼呼呼
@Email   ：dfqxhhh@163.com
@Date    ：2023/9/10 
"""

from dataclasses import dataclass


def Entity(entity_class):
    # 将数据类中的每个属性都赋值为Constraint类
    def wrapper(cls):
        # 获取数据类中的字段名称和类型的字典
        fields = cls.__annotations__

        for field_name, field_type in fields.items():
            # 获取字段的约束条件对象
            constraint_obj = getattr(cls, field_name, None)
            if isinstance(constraint_obj, Constraint):
                continue
            else:
                # 如果不是，就创建一个空的Constraint对象，并赋值给数据类中的字段
                setattr(cls, field_name, Constraint(name=field_name))
        # 调用dataclass装饰器，并返回数据类
        return dataclass(cls)

    return wrapper(entity_class)


class Constraint:
    # 具体的约束值
    PrimaryKey = "PRIMARY KEY"
    AutoPrimaryKey = "PRIMARY KEY AUTOINCREMENT"
    Not_NULL = "NOT NULL"
    Unique = "UNIQUE"

    # default和check约束需要传值，暂不实现

    def __init__(self, *args, foreign_key=None, name=None):
        self.constraints = [*args]
        self.foreign_key = foreign_key
        self.name = name  # 存储描述符所属的属性名称
        self.owner = None  # 存储描述符所属的类名称

    def __get__(self, instance, owner):
        # 在类上访问属性，返回描述符对象本身
        if instance is None:
            return self
        # 在实例上访问属性，返回属性自身的值
        else:
            return instance.__dict__[self.name]

    def __set__(self, instance, value):
        # 在实例上设置属性值
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        # 在类上设置描述符所属的类和属性名称
        self.owner = owner.__name__
        self.name = name
