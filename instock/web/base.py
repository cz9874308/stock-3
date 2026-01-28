#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
Web 基础模块

本模块提供 Web 服务的基础类和通用功能，包括数据库连接管理和左侧菜单生成。

核心组件
--------
- **BaseHandler**: Tornado 请求处理器基类，提供数据库连接管理
- **LeftMenu**: 左侧导航菜单数据类
- **GetLeftMenu**: 获取左侧菜单的工厂函数

数据库连接
----------
BaseHandler 在每次请求时检查数据库连接状态，自动重连。

使用方式
--------
创建自定义 Handler::

    from instock.web.base import BaseHandler

    class MyHandler(BaseHandler, ABC):
        def get(self):
            data = self.db.query("SELECT * FROM table")
            self.write(data)
"""

from abc import ABC
from typing import List

import tornado.web

import instock.core.singleton_stock_web_module_data as sswmd

__author__ = 'myh '
__date__ = '2023/3/10 '


class BaseHandler(tornado.web.RequestHandler, ABC):
    """Tornado 请求处理器基类

    提供数据库连接管理，每次请求时自动检查并重连数据库。

    Attributes:
        db: 数据库连接对象，通过 property 访问
    """

    @property
    def db(self):
        """获取数据库连接，自动检查并重连

        Returns:
            torndb.Connection 数据库连接对象
        """
        try:
            # 每次请求检查连接状态
            self.application.db.query("SELECT 1 ")
        except Exception as e:
            print(e)
            self.application.db.reconnect()
        return self.application.db


class LeftMenu:
    """左侧导航菜单数据类

    用于模板渲染，提供菜单列表和当前 URL 信息。

    Attributes:
        leftMenuList: 菜单项列表
        current_url: 当前页面 URL，用于高亮当前菜单
    """

    def __init__(self, url: str):
        """初始化左侧菜单

        Args:
            url: 当前请求的 URL
        """
        self.leftMenuList = sswmd.stock_web_module_data().get_data_list()
        self.current_url = url


def GetLeftMenu(url: str) -> LeftMenu:
    """获取左侧菜单对象

    Args:
        url: 当前请求的 URL

    Returns:
        LeftMenu 实例
    """
    return LeftMenu(url)
