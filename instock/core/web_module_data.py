#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
Web 模块数据类定义模块

本模块定义了 Web 界面数据模块的数据结构，用于描述一个数据表在 Web 界面中的
展示和查询配置。

核心概念
--------
- **web_module_data**: 描述一个数据模块的完整配置
- **模式**: 支持查询（query）和编辑（editor）两种模式
- **URL 生成**: 自动生成数据访问 URL

使用方式
--------
创建模块配置::

    module = web_module_data(
        mode="query",
        type="股票基本数据",
        ico="fa fa-book",
        name="股票实时行情",
        table_name="cn_stock_spot",
        columns=('code', 'name', 'price'),
        column_names=('代码', '名称', '价格'),
        primary_key=['code'],
        is_realtime=True,
        order_by=" `price` DESC"
    )
    print(module.url)  # /instock/data?table_name=cn_stock_spot
"""

from typing import List, Optional, Tuple

__author__ = 'myh '
__date__ = '2023/5/11 '


class web_module_data:
    """Web 数据模块配置类

    描述一个数据表在 Web 界面中的展示和查询配置。

    Attributes:
        mode: 模式，'query' 查询模式或 'editor' 编辑模式
        type: 分类类型，用于菜单分组显示
        ico: Font Awesome 图标类名
        name: 模块显示名称（中文）
        table_name: 对应的数据库表名
        columns: 表字段列表
        column_names: 字段中文名称列表
        primary_key: 主键字段列表
        is_realtime: 是否为实时数据
        order_by: 默认排序 SQL 片段
        order_columns: 额外的排序列定义（用于子查询）
        url: 自动生成的数据访问 URL
    """

    def __init__(
        self,
        mode: str,
        type: str,
        ico: str,
        name: str,
        table_name: str,
        columns: Tuple[str, ...],
        column_names: Tuple[str, ...],
        primary_key: List[str],
        is_realtime: bool,
        order_columns: Optional[str] = None,
        order_by: Optional[str] = None
    ):
        """初始化模块配置

        Args:
            mode: 模式（query/editor）
            type: 分类类型
            ico: 图标类名
            name: 显示名称
            table_name: 数据库表名
            columns: 字段列表
            column_names: 字段中文名列表
            primary_key: 主键字段列表
            is_realtime: 是否实时数据
            order_columns: 额外排序列定义
            order_by: 排序 SQL 片段
        """
        self.mode = mode
        self.type = type
        self.ico = ico
        self.name = name
        self.table_name = table_name
        self.columns = columns
        self.column_names = column_names
        self.primary_key = primary_key
        self.is_realtime = is_realtime
        self.order_by = order_by
        self.order_columns = order_columns
        # 自动生成数据访问 URL
        self.url = f"/instock/data?table_name={self.table_name}"
