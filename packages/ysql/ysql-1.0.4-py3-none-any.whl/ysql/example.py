# -*- coding: utf-8 -*-
"""
@Project ：ysql
@File    ：example.py
@IDE     ：PyCharm 
@Author  ：大风起兮呼呼呼
@Email   ：dfqxhhh@163.com
@Date    ：2023/9/10 
"""
import os
import shutil

from ysql.dao import Dao, Sql
from ysql.database import Path, MetaDatabase
from ysql.entity import Entity, Constraint


# ====================================================================================================================
# 项目gitee地址：https://gitee.com/darlingxyz/ysql（请于此查看项目详细信息，如README文件）
# 如果直接下载源码使用，请将ysql文件夹放置在根目录中，与venv目录同级，否则需要重新导入其中各文件的依赖项
# 通过pip安装时，可以随时使用以下代码来获取此示例文件
# from ysql.example import get_example
# get_example()
# ====================================================================================================================
# 结构说明：
# Entity定义数据表
# Dao定义数据操作接口，提供表级控制
# Database集成Dao便于统一对外，提供库级控制


# ====================================================================================================================
# 数据表类的定义形式
@Entity  # 对python原生的dataclass类使用Entity装饰器即可，但与该框架是完全解耦的，仍然可以当作一个普通的dataclass来使用
class Student:  # 类名即表名
    name: str  # 必须同时定义属性名和数据类型，其中属性名即表的字段名
    number: int
    address: str
    student_id: int = Constraint(Constraint.AutoPrimaryKey)  # 特殊字段如自增主键，不仅需指定数据类型，还需添加约束条件，且必须位于类定义的最后
    # 约束类Constraint目前提供了主要的5种约束
    # PrimaryKey 主键约束
    # AutoPrimaryKey 自增主键约束
    # Not_NULL 字段非空约束
    # Unique 字段唯一性约束
    # foreign_key 外键约束


@Entity
class Score:
    score: float
    student_id: int = Constraint(foreign_key=Student.student_id)  # 外键约束需要与另一张表建立关联，即传递另一个数据类的属性


# ====================================================================================================================
# Dao类的定义形式
@Dao(entity=Student)  # 使用Dao装饰器，并传递对应的entity类
class DaoStudent:

    # 无需定义insert方法，使用Dao装饰器之后，已经自动实现了该方法，可直接调用
    # 缺点是在IDE的自动补全中无法提示该方法的存在
    # @Insert  # 如需重新定义插入方法，可使用sql装饰器并传递相应的sql语句，或者直接使用Insert装饰器，也可自动实现。
    # def insert(self, entity):
    #   pass
    # 凡是采取@Insert插入记录的，被装饰方法会自动返回插入记录的主键

    @Sql("select * from student where student_id=?;")  # 对方法使用Sql装饰器，并传入sql语句即可
    def get_student(self, student_id):  # 参数名可任意，但顺序需要与sql语句中?的传值顺序一致
        pass  # 方法本身无需实现

    @Sql("select address from student where student_id=?;")
    def get_student_address(self, student_id):
        pass  # 方法本身无需实现
        # 需要返回值的时候会以列表形式自动返回结果，且会根据查询字段将查询到的单条记录自动解析为具名元组。


@Dao(Score)  # 也可直接传入对应的entity
class DaoScore:

    # 涉及使用对应entity的表名时，可以使用__代替符，相应的不允许sql语句在其他位置使用__字符。
    @Sql(f"select * from __ where {Student.student_id.name}=?;")  # 可不写死字段，采取Entity.field.name格式也可访问该字段的字符名称
    def get_score(self, student_id):
        pass  # 方法本身无需实现


# ====================================================================================================================
# 数据库类的定义形式
db_path = "db_folder/test.db"  # 此处是需要每次运行均删除数据库，故额外定义路径变量


@Path(db_path)  # 使用Path装饰器传递数据库的路径，可直接传路径字符串
class MyDatabase(MetaDatabase):  # 还需额外继承MetaDatabase类，原因是若采用装饰器实现，则无法获得自动补全的方法提示
    # 查看ABCDatabase类或MetaDatabase类了解可调用方法

    # 需要将全部Dao类分别定义为类中静态变量
    dao_student = DaoStudent()
    dao_score = DaoScore()


def get_example():
    """复制本文件的工具函数"""
    # 获取当前文件的路径
    src = __file__
    dst = "ysql_example.py"
    shutil.copy(src, dst)
    print('已生成示例文件：ysql_example.py')


if __name__ == '__main__':
    # 删除已存在的数据库文件
    if os.path.exists(db_path):
        os.remove(db_path)

    db = MyDatabase()  # 创建数据库类的实例
    db.connect()  # 连接数据库
    db.create_tables()  # 创建表

    db.dao_student.insert(Student(name="好家伙", number=123456789, address="HIT A01"))  # 插入一条student记录
    db.dao_score.insert(Score(score=59.5, student_id=1))  # 插入一条score记录
    db.commit()  # 提交改动

    result1 = db.dao_student.get_student(student_id=1)  # 获取一条student记录
    result2 = db.dao_score.get_score(student_id=1)

    # 查询结果以列表形式返回
    print(f"查询结果1：{result1}\n查询结果2：{result2}")

    # 查询结果的单条记录为具名元组
    for result in result1:
        print(f"结果1中的姓名：{result.name}；电话：{result.number}地址：{result.address}")

    db.disconnect()  # 关闭数据库连接
