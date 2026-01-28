#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接与操作模块

本模块提供了 MySQL/MariaDB 数据库的连接管理和常用操作函数，是整个 InStock
系统的数据持久化核心模块。

核心概念
--------
- **SQLAlchemy Engine**: 用于 Pandas DataFrame 的批量数据插入
- **PyMySQL Connection**: 用于原生 SQL 的执行（增删改查）
- **环境变量配置**: 支持通过环境变量覆盖默认数据库配置（适用于 Docker 部署）

配置方式
--------
1. 默认配置（开发环境）::

    db_host = "localhost"
    db_user = "root"
    db_password = "root"
    db_database = "instockdb"

2. 环境变量配置（生产环境/Docker）::

    export db_host=192.168.1.100
    export db_user=instock
    export db_password=your_password
    export db_database=instockdb
    export db_port=3306

使用方式
--------
插入 DataFrame 数据::

    from instock.lib.database import insert_db_from_df
    insert_db_from_df(df, 'table_name', None, False, '`code`,`date`')

执行 SQL 查询::

    from instock.lib.database import executeSqlFetch
    result = executeSqlFetch("SELECT * FROM table WHERE code = %s", ('000001',))

注意事项
--------
- 生产环境请务必通过环境变量设置数据库密码，避免硬编码
- 批量插入大数据时建议分批处理，避免内存溢出
"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import pymysql
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.types import NVARCHAR

__author__ = 'myh '
__date__ = '2023/3/10 '

# ============================================================
# 数据库连接配置
# ============================================================

# 默认配置（可通过环境变量覆盖）
db_host: str = "localhost"      # 数据库服务主机
db_user: str = "root"           # 数据库访问用户
db_password: str = "root"       # 数据库访问密码
db_database: str = "instockdb"  # 数据库名称
db_port: int = 3306             # 数据库服务端口
db_charset: str = "utf8mb4"     # 数据库字符集

# 从环境变量读取配置（Docker 部署时通过 -e 参数传递）
_db_host = os.environ.get('db_host')
if _db_host is not None:
    db_host = _db_host
_db_user = os.environ.get('db_user')
if _db_user is not None:
    db_user = _db_user
_db_password = os.environ.get('db_password')
if _db_password is not None:
    db_password = _db_password
_db_database = os.environ.get('db_database')
if _db_database is not None:
    db_database = _db_database
_db_port = os.environ.get('db_port')
if _db_port is not None:
    db_port = int(_db_port)

# SQLAlchemy 连接 URL
MYSQL_CONN_URL: str = "mysql+pymysql://%s:%s@%s:%s/%s?charset=%s" % (
    db_user, db_password, db_host, db_port, db_database, db_charset)
logging.info(f"数据库链接信息：{MYSQL_CONN_URL}")

# PyMySQL DB-API 连接参数
MYSQL_CONN_DBAPI: Dict[str, Any] = {
    'host': db_host,
    'user': db_user,
    'password': db_password,
    'database': db_database,
    'charset': db_charset,
    'port': db_port,
    'autocommit': True
}

# TornDB 连接参数
MYSQL_CONN_TORNDB: Dict[str, Any] = {
    'host': f'{db_host}:{str(db_port)}',
    'user': db_user,
    'password': db_password,
    'database': db_database,
    'charset': db_charset,
    'max_idle_time': 3600,
    'connect_timeout': 1000
}


# ============================================================
# 数据库连接函数
# ============================================================

def engine() -> Engine:
    """创建默认数据库的 SQLAlchemy 引擎

    返回连接到默认数据库（instockdb）的 SQLAlchemy Engine 对象，
    主要用于 Pandas DataFrame 的 to_sql 操作。

    Returns:
        SQLAlchemy Engine 对象

    Example:
        >>> eng = engine()
        >>> df.to_sql('table_name', con=eng, if_exists='append')
    """
    return create_engine(MYSQL_CONN_URL)


def engine_to_db(to_db: str) -> Engine:
    """创建指定数据库的 SQLAlchemy 引擎

    用于连接到非默认数据库，支持跨数据库的数据操作。

    Args:
        to_db: 目标数据库名称

    Returns:
        连接到指定数据库的 SQLAlchemy Engine 对象
    """
    _engine = create_engine(MYSQL_CONN_URL.replace(f'/{db_database}?', f'/{to_db}?'))
    return _engine


def get_connection() -> Optional[pymysql.connections.Connection]:
    """获取 PyMySQL 数据库连接

    创建并返回一个 PyMySQL 连接对象，用于执行原生 SQL 语句。
    连接配置来自 MYSQL_CONN_DBAPI 字典。

    Returns:
        PyMySQL 连接对象，如果连接失败返回 None

    Example:
        >>> with get_connection() as conn:
        ...     with conn.cursor() as cursor:
        ...         cursor.execute("SELECT * FROM table")
        ...         result = cursor.fetchall()
    """
    try:
        return pymysql.connect(**MYSQL_CONN_DBAPI)
    except Exception as e:
        logging.error(f"database.conn_not_cursor处理异常：{MYSQL_CONN_DBAPI}{e}")
    return None


# ============================================================
# DataFrame 数据插入函数
# ============================================================

def insert_db_from_df(
    data: pd.DataFrame,
    table_name: str,
    cols_type: Optional[Dict[str, Any]],
    write_index: bool,
    primary_keys: str,
    indexs: Optional[Dict[str, str]] = None
) -> None:
    """将 DataFrame 数据插入到默认数据库

    这是一个便捷函数，内部调用 insert_other_db_from_df 实现。
    如果表不存在会自动创建，并设置主键和索引。

    Args:
        data: 要插入的 Pandas DataFrame 数据
        table_name: 目标表名
        cols_type: 列类型映射字典，格式为 {列名: SQLAlchemy类型}
                   - None: 使用 Pandas 自动推断的类型
                   - 空字典 {}: 所有列使用 NVARCHAR(255)
                   - 具体映射: 使用指定的类型
        write_index: 是否将 DataFrame 索引写入数据库
        primary_keys: 主键定义，格式如 '`code`,`date`'
        indexs: 索引定义字典，格式为 {索引后缀: 索引列}

    Example:
        >>> df = pd.DataFrame({'code': ['000001'], 'name': ['平安银行']})
        >>> insert_db_from_df(df, 'stock_info', None, False, '`code`')
    """
    insert_other_db_from_df(None, data, table_name, cols_type, write_index, primary_keys, indexs)


def insert_other_db_from_df(
    to_db: Optional[str],
    data: pd.DataFrame,
    table_name: str,
    cols_type: Optional[Dict[str, Any]],
    write_index: bool,
    primary_keys: str,
    indexs: Optional[Dict[str, str]] = None
) -> None:
    """将 DataFrame 数据插入到指定数据库

    完整的数据插入函数，支持：
    1. 自动创建表结构
    2. 自动添加主键（如果表尚无主键）
    3. 自动添加索引

    Args:
        to_db: 目标数据库名称，None 表示使用默认数据库
        data: 要插入的 Pandas DataFrame 数据
        table_name: 目标表名
        cols_type: 列类型映射字典
        write_index: 是否将 DataFrame 索引写入数据库
        primary_keys: 主键定义
        indexs: 索引定义字典

    Note:
        - 使用 if_exists='append' 模式，数据会追加到现有表
        - 主键和索引只在表首次创建时添加
    """
    # 选择合适的数据库引擎
    if to_db is None:
        engine_mysql = engine()
    else:
        engine_mysql = engine_to_db(to_db)

    # 使用 SQLAlchemy 检查器检查表结构
    ipt = inspect(engine_mysql)
    col_name_list = data.columns.tolist()

    # 如果需要写入索引，将索引名添加到列列表
    if write_index:
        col_name_list.insert(0, data.index.name)

    # 执行数据插入
    try:
        if cols_type is None:
            # 使用 Pandas 自动推断的类型
            data.to_sql(name=table_name, con=engine_mysql, schema=to_db,
                        if_exists='append', index=write_index)
        elif not cols_type:
            # 所有列使用 NVARCHAR(255)
            data.to_sql(name=table_name, con=engine_mysql, schema=to_db,
                        if_exists='append',
                        dtype={col_name: NVARCHAR(255) for col_name in col_name_list},
                        index=write_index)
        else:
            # 使用指定的列类型
            data.to_sql(name=table_name, con=engine_mysql, schema=to_db,
                        if_exists='append', dtype=cols_type, index=write_index)
    except Exception as e:
        logging.error(f"database.insert_other_db_from_df处理异常：{table_name}表{e}")

    # 检查并添加主键（如果表尚无主键）
    if not ipt.get_pk_constraint(table_name)['constrained_columns']:
        try:
            with get_connection() as conn:
                with conn.cursor() as db:
                    # 添加主键
                    db.execute(f'ALTER TABLE `{table_name}` ADD PRIMARY KEY ({primary_keys});')
                    # 添加索引
                    if indexs is not None:
                        for k in indexs:
                            db.execute(f'ALTER TABLE `{table_name}` ADD INDEX IN{k}({indexs[k]});')
        except Exception as e:
            logging.error(f"database.insert_other_db_from_df处理异常：{table_name}表{e}")


# ============================================================
# 数据更新函数
# ============================================================

def update_db_from_df(
    data: pd.DataFrame,
    table_name: str,
    where: List[str]
) -> None:
    """根据 DataFrame 数据批量更新数据库记录

    遍历 DataFrame 的每一行，生成并执行 UPDATE SQL 语句。
    where 参数指定的列用于构建 WHERE 条件，其余列用于 SET 子句。

    Args:
        data: 包含更新数据的 Pandas DataFrame
        table_name: 目标表名
        where: 用于 WHERE 条件的列名列表

    Example:
        >>> df = pd.DataFrame({
        ...     'code': ['000001'],
        ...     'date': ['2024-01-15'],
        ...     'close': [12.5]
        ... })
        >>> update_db_from_df(df, 'stock_daily', ['code', 'date'])
        # 生成: UPDATE stock_daily SET close = 12.5 WHERE code = '000001' AND date = '2024-01-15'

    Note:
        - NaN 值会被转换为 NULL
        - 字符串值会自动加引号
    """
    # 将 NaN 转换为 None（对应 SQL 的 NULL）
    data = data.where(data.notnull(), None)
    update_string = f'UPDATE `{table_name}` set '
    where_string = ' where '
    cols = tuple(data.columns)

    with get_connection() as conn:
        with conn.cursor() as db:
            try:
                for row in data.values:
                    sql = update_string
                    sql_where = where_string

                    for index, col in enumerate(cols):
                        if col in where:
                            # 该列用于 WHERE 条件
                            if len(sql_where) == len(where_string):
                                # 第一个条件
                                if type(row[index]) == str:
                                    sql_where = f'''{sql_where}`{col}` = '{row[index]}' '''
                                else:
                                    sql_where = f'''{sql_where}`{col}` = {row[index]} '''
                            else:
                                # 后续条件用 AND 连接
                                if type(row[index]) == str:
                                    sql_where = f'''{sql_where} and `{col}` = '{row[index]}' '''
                                else:
                                    sql_where = f'''{sql_where} and `{col}` = {row[index]} '''
                        else:
                            # 该列用于 SET 子句
                            if type(row[index]) == str:
                                # 检查 None 或 NaN（NaN != NaN）
                                if row[index] is None or row[index] != row[index]:
                                    sql = f'''{sql}`{col}` = NULL, '''
                                else:
                                    sql = f'''{sql}`{col}` = '{row[index]}', '''
                            else:
                                if row[index] is None or row[index] != row[index]:
                                    sql = f'''{sql}`{col}` = NULL, '''
                                else:
                                    sql = f'''{sql}`{col}` = {row[index]}, '''

                    # 拼接完整 SQL（移除最后的逗号和空格）
                    sql = f'{sql[:-2]}{sql_where}'
                    db.execute(sql)
            except Exception as e:
                logging.error(f"database.update_db_from_df处理异常：{sql}{e}")


# ============================================================
# 通用 SQL 执行函数
# ============================================================

def checkTableIsExist(tableName: str) -> bool:
    """检查数据库表是否存在

    通过查询 information_schema.tables 判断指定表是否存在于数据库中。

    Args:
        tableName: 要检查的表名

    Returns:
        如果表存在返回 True，否则返回 False

    Example:
        >>> if checkTableIsExist('stock_daily'):
        ...     print("表已存在")
    """
    with get_connection() as conn:
        with conn.cursor() as db:
            db.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_name = '{0}'
                """.format(tableName.replace('\'', '\'\'')))
            if db.fetchone()[0] == 1:
                return True
    return False


def executeSql(sql: str, params: Tuple = ()) -> None:
    """执行增删改 SQL 语句

    执行不返回结果集的 SQL 语句，如 INSERT、UPDATE、DELETE、DDL 等。

    Args:
        sql: SQL 语句，可包含 %s 占位符
        params: SQL 参数元组，用于替换占位符

    Example:
        >>> executeSql("DELETE FROM stock_daily WHERE date < %s", ('2020-01-01',))
    """
    with get_connection() as conn:
        with conn.cursor() as db:
            try:
                db.execute(sql, params)
            except Exception as e:
                logging.error(f"database.executeSql处理异常：{sql}{e}")


def executeSqlFetch(sql: str, params: Tuple = ()) -> Optional[Tuple]:
    """执行查询 SQL 并返回所有结果

    执行 SELECT 语句并返回完整的结果集。

    Args:
        sql: SELECT SQL 语句
        params: SQL 参数元组

    Returns:
        查询结果的元组，每个元素是一行数据；如果出错返回 None

    Example:
        >>> result = executeSqlFetch(
        ...     "SELECT code, name FROM stock_info WHERE code = %s",
        ...     ('000001',)
        ... )
        >>> for row in result:
        ...     print(row)
    """
    with get_connection() as conn:
        with conn.cursor() as db:
            try:
                db.execute(sql, params)
                return db.fetchall()
            except Exception as e:
                logging.error(f"database.executeSqlFetch处理异常：{sql}{e}")
    return None


def executeSqlCount(sql: str, params: Tuple = ()) -> int:
    """执行计数查询并返回数量

    专门用于执行 COUNT 等聚合查询，返回单个整数结果。

    Args:
        sql: 包含 COUNT 的 SQL 语句
        params: SQL 参数元组

    Returns:
        计数结果，如果查询失败或无结果返回 0

    Example:
        >>> count = executeSqlCount(
        ...     "SELECT COUNT(*) FROM stock_daily WHERE date = %s",
        ...     ('2024-01-15',)
        ... )
        >>> print(f"共有 {count} 条记录")
    """
    with get_connection() as conn:
        with conn.cursor() as db:
            try:
                db.execute(sql, params)
                result = db.fetchall()
                if len(result) == 1:
                    return int(result[0][0])
                else:
                    return 0
            except Exception as e:
                logging.error(f"database.select_count计算数量处理异常：{e}")
    return 0
