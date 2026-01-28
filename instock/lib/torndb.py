#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
TornDB 数据库封装模块

本模块是 PyMySQL 的轻量级封装，最初是 Tornado 框架的一部分（tornado.database），
在 Tornado 3.0 中被移除后作为独立模块 torndb 发布。本项目对其进行了适配修改，
使用 PyMySQL 替代 MySQLdb。

核心概念
--------
- **Connection**: 数据库连接的封装类，提供查询和执行方法
- **Row**: 字典的子类，支持通过属性访问列值
- **自动重连**: 连接空闲超时后自动重连

主要特性
--------
1. **简化的 API**: 隐藏游标操作，提供直接的查询/执行方法
2. **Row 对象**: 查询结果可通过属性访问（如 row.column_name）
3. **自动超时重连**: 防止 MySQL 8 小时空闲断开问题
4. **时区设置**: 默认设置为 UTC 时区

使用方式
--------
基本查询::

    from instock.lib.torndb import Connection

    db = Connection("localhost:3306", "database", "user", "password")

    # 查询多行
    for article in db.query("SELECT * FROM articles"):
        print(article.title)

    # 查询单行
    user = db.get("SELECT * FROM users WHERE id = %s", user_id)

    # 执行更新
    db.execute("UPDATE users SET name = %s WHERE id = %s", name, user_id)

注意事项
--------
- 默认 SQL 模式为 TRADITIONAL，会将警告转为错误
- 默认字符集为 utf8，建议生产环境使用 utf8mb4
"""

from __future__ import absolute_import, division, with_statement

import copy
import itertools
import logging
import os
import time
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

import pymysql

__author__ = 'myh '
__date__ = '2023/3/10 '

try:
    # PyMySQL 模块导入
    import pymysql.connections
    import pymysql.converters
    import pymysql.cursors
    import pymysql.constants.FLAG

except ImportError:
    # 为了在 readthedocs.org 上能够导入模块
    if 'READTHEDOCS' in os.environ:
        pymysql = None
    else:
        raise

# 模块版本信息
version = "0.3"
version_info = (0, 3, 0, 0)


class Connection(object):
    """MySQL 数据库连接封装类

    对 PyMySQL DB-API 连接的轻量级封装，主要价值在于：
    1. 将查询结果行封装为 Row 对象，支持通过列名属性访问
    2. 隐藏游标操作，简化数据库操作 API
    3. 自动处理连接超时重连

    Attributes:
        host: 数据库主机地址
        database: 数据库名称
        max_idle_time: 最大空闲时间（秒），超时后自动重连

    Example:
        基本使用::

            db = Connection("localhost:3306", "mydatabase", "user", "password")

            # 查询多行
            for article in db.query("SELECT * FROM articles"):
                print(article.title)  # 通过属性访问列值

            # 查询单行
            user = db.get("SELECT * FROM users WHERE id = %s", user_id)
            if user:
                print(user.name)

            # 执行更新
            rows_affected = db.execute("UPDATE users SET name = %s WHERE id = %s", name, user_id)

    Note:
        - 默认时区设置为 UTC (+0:00)
        - 默认字符集为 utf8
        - 默认 SQL 模式为 TRADITIONAL（警告转错误）
    """

    def __init__(
        self,
        host: str,
        database: str,
        user: Optional[str] = None,
        password: Optional[str] = None,
        max_idle_time: int = 7 * 3600,
        connect_timeout: int = 10,
        time_zone: str = "+0:00",
        charset: str = "utf8",
        sql_mode: Optional[str] = "TRADITIONAL"
    ):
        """初始化数据库连接

        Args:
            host: 数据库主机，格式为 "host" 或 "host:port"，也支持 Unix socket 路径
            database: 数据库名称
            user: 数据库用户名
            password: 数据库密码
            max_idle_time: 最大空闲时间（秒），默认 7 小时，超时后自动重连
            connect_timeout: 连接超时时间（秒），默认 10 秒
            time_zone: 时区设置，默认 UTC (+0:00)
            charset: 字符集，默认 utf8
            sql_mode: SQL 模式，默认 TRADITIONAL，设为 None 可清除

        Raises:
            连接失败时会记录错误日志，但不会抛出异常
        """
        self.host = host
        self.database = database
        self.max_idle_time = float(max_idle_time)

        #  自定义
        args = dict(conv=CONVERSIONS, charset=charset,
                    db=database, init_command=('SET time_zone = "%s"' % time_zone),
                    connect_timeout=connect_timeout, sql_mode=sql_mode)
        # args = dict(conv=CONVERSIONS, use_unicode=True, charset=charset,
        #             db=database, init_command=('SET time_zone = "%s"' % time_zone),
        #             connect_timeout=connect_timeout, sql_mode=sql_mode)
        #

        if user is not None:
            args["user"] = user
        if password is not None:
            args["passwd"] = password

        # We accept a path to a MySQL socket file or a host(:port) string
        if "/" in host:
            args["unix_socket"] = host
        else:
            self.socket = None
            pair = host.split(":")
            if len(pair) == 2:
                args["host"] = pair[0]
                args["port"] = int(pair[1])
            else:
                args["host"] = host
                args["port"] = 3306

        self._db = None
        self._db_args = args
        self._last_use_time = time.time()
        try:
            self.reconnect()
        except Exception:
            logging.error(f"Cannot connect to MySQL on {self.host}", exc_info=True)

    def __del__(self):
        """析构函数，确保连接被关闭"""
        self.close()

    def close(self) -> None:
        """关闭数据库连接

        安全地关闭当前数据库连接。如果连接不存在或已关闭，不会抛出异常。
        """
        if getattr(self, "_db", None) is not None:
            self._db.close()
            self._db = None

    def reconnect(self) -> None:
        """重新建立数据库连接

        关闭现有连接（如果存在）并创建新连接。
        新连接会自动启用 autocommit 模式。
        """
        self.close()
        self._db = pymysql.connect(**self._db_args)
        self._db.autocommit(True)

    def iter(
        self,
        query: str,
        *parameters: Any,
        **kwparameters: Any
    ) -> Iterator['Row']:
        """流式查询，返回结果迭代器

        使用服务端游标（SSCursor）进行流式查询，适合处理大量数据，
        避免一次性加载全部结果到内存。

        Args:
            query: SQL 查询语句
            *parameters: 位置参数，用于替换 SQL 中的 %s 占位符
            **kwparameters: 关键字参数，用于替换 SQL 中的 %(name)s 占位符

        Yields:
            Row 对象，每次迭代返回一行数据

        Example:
            >>> for row in db.iter("SELECT * FROM large_table"):
            ...     process(row)
        """
        self._ensure_connected()
        cursor = pymysql.cursors.SSCursor(self._db)
        try:
            self._execute(cursor, query, parameters, kwparameters)
            column_names = [d[0] for d in cursor.description]
            for row in cursor:
                yield Row(zip(column_names, row))
        finally:
            cursor.close()

    def query(
        self,
        query: str,
        *parameters: Any,
        **kwparameters: Any
    ) -> List['Row']:
        """执行查询并返回结果列表

        执行 SELECT 查询并返回所有结果行。每行数据封装为 Row 对象，
        支持通过属性访问列值。

        Args:
            query: SQL 查询语句
            *parameters: 位置参数
            **kwparameters: 关键字参数

        Returns:
            Row 对象列表

        Example:
            >>> users = db.query("SELECT * FROM users WHERE age > %s", 18)
            >>> for user in users:
            ...     print(user.name, user.email)
        """
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters, kwparameters)
            column_names = [d[0] for d in cursor.description]
            return [Row(itertools.zip_longest(column_names, row)) for row in cursor]
        finally:
            cursor.close()

    def get(
        self,
        query: str,
        *parameters: Any,
        **kwparameters: Any
    ) -> Optional['Row']:
        """执行查询并返回单行结果

        用于期望返回单行结果的查询（如通过主键查询）。

        Args:
            query: SQL 查询语句
            *parameters: 位置参数
            **kwparameters: 关键字参数

        Returns:
            如果有结果返回 Row 对象，无结果返回 None

        Raises:
            Exception: 如果查询返回多于一行结果

        Example:
            >>> user = db.get("SELECT * FROM users WHERE id = %s", 1)
            >>> if user:
            ...     print(user.name)
        """
        rows = self.query(query, *parameters, **kwparameters)
        if not rows:
            return None
        elif len(rows) > 1:
            raise Exception("Multiple rows returned for Database.get() query")
        else:
            return rows[0]

    def execute(
        self,
        query: str,
        *parameters: Any,
        **kwparameters: Any
    ) -> int:
        """执行 SQL 语句并返回最后插入的行 ID

        用于执行 INSERT、UPDATE、DELETE 等语句。
        为保持历史兼容性，返回 lastrowid（对 INSERT 有意义）。

        Args:
            query: SQL 语句
            *parameters: 位置参数
            **kwparameters: 关键字参数

        Returns:
            最后插入行的 ID（lastrowid）
        """
        return self.execute_lastrowid(query, *parameters, **kwparameters)

    def execute_lastrowid(
        self,
        query: str,
        *parameters: Any,
        **kwparameters: Any
    ) -> int:
        """执行 SQL 语句并返回最后插入的行 ID

        Args:
            query: SQL 语句
            *parameters: 位置参数
            **kwparameters: 关键字参数

        Returns:
            最后插入行的 ID
        """
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters, kwparameters)
            return cursor.lastrowid
        finally:
            cursor.close()

    def execute_rowcount(
        self,
        query: str,
        *parameters: Any,
        **kwparameters: Any
    ) -> int:
        """执行 SQL 语句并返回影响的行数

        Args:
            query: SQL 语句
            *parameters: 位置参数
            **kwparameters: 关键字参数

        Returns:
            受影响的行数
        """
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters, kwparameters)
            return cursor.rowcount
        finally:
            cursor.close()

    def executemany(
        self,
        query: str,
        parameters: List[Tuple]
    ) -> int:
        """批量执行 SQL 语句

        使用相同的 SQL 语句和不同的参数批量执行。

        Args:
            query: SQL 语句模板
            parameters: 参数列表，每个元素是一组参数

        Returns:
            最后插入行的 ID
        """
        return self.executemany_lastrowid(query, parameters)

    def executemany_lastrowid(
        self,
        query: str,
        parameters: List[Tuple]
    ) -> int:
        """批量执行 SQL 语句并返回最后插入的行 ID

        Args:
            query: SQL 语句模板
            parameters: 参数列表

        Returns:
            最后插入行的 ID
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()

    def executemany_rowcount(
        self,
        query: str,
        parameters: List[Tuple]
    ) -> int:
        """批量执行 SQL 语句并返回影响的行数

        Args:
            query: SQL 语句模板
            parameters: 参数列表

        Returns:
            受影响的总行数
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.rowcount
        finally:
            cursor.close()

    # 方法别名，提供更语义化的接口
    update = execute_rowcount       # UPDATE 操作关心影响行数
    updatemany = executemany_rowcount
    insert = execute_lastrowid      # INSERT 操作关心新行 ID
    insertmany = executemany_lastrowid

    def _ensure_connected(self) -> None:
        """确保数据库连接有效

        MySQL 默认在连接空闲 8 小时后关闭，但客户端不会主动检测，
        直到执行查询时才会失败。此方法通过预防性重连解决此问题：
        如果连接空闲超过 max_idle_time（默认 7 小时），则主动重连。
        """
        if (self._db is None or
                (time.time() - self._last_use_time > self.max_idle_time)):
            self.reconnect()
        self._last_use_time = time.time()

    def _cursor(self):
        """获取数据库游标"""
        self._ensure_connected()
        return self._db.cursor()

    def _execute(self, cursor, query, parameters, kwparameters):
        """执行 SQL 语句的内部方法"""
        try:
            return cursor.execute(query, kwparameters or parameters)
        except OperationalError:
            logging.error(f"Error connecting to MySQL on {self.host}")
            self.close()
            raise


class Row(dict):
    """支持属性访问语法的字典类

    继承自 dict，允许通过属性方式访问字典键值。
    用于封装数据库查询结果行，使代码更简洁易读。

    Example:
        >>> row = Row({'name': 'Alice', 'age': 25})
        >>> print(row.name)   # 属性访问
        'Alice'
        >>> print(row['age']) # 字典访问
        25
    """

    def __getattr__(self, name: str) -> Any:
        """通过属性名获取字典值

        Args:
            name: 属性名（对应字典键）

        Returns:
            字典中对应键的值

        Raises:
            AttributeError: 如果键不存在
        """
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


if pymysql is not None:
    # Fix the access conversions to properly recognize unicode/binary
    FIELD_TYPE = pymysql.constants.FIELD_TYPE
    FLAG = pymysql.constants.FLAG
    CONVERSIONS = copy.copy(pymysql.converters.conversions)

    field_types = [FIELD_TYPE.BLOB, FIELD_TYPE.STRING, FIELD_TYPE.VAR_STRING]
    if 'VARCHAR' in vars(FIELD_TYPE):
        field_types.append(FIELD_TYPE.VARCHAR)

    for field_type in field_types:
        # CONVERSIONS[field_type] = [(FLAG.BINARY, str)] + CONVERSIONS[field_type]
        CONVERSIONS[field_type] = [(FLAG.BINARY, str)].append(CONVERSIONS[field_type])

    # Alias some common MySQL exceptions
    IntegrityError = pymysql.IntegrityError
    OperationalError = pymysql.OperationalError
