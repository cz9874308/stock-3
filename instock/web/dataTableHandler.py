#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
数据表格处理模块

本模块提供股票数据表格的页面渲染和数据 API 接口。

核心组件
--------
- **GetStockHtmlHandler**: 渲染数据表格页面
- **GetStockDataHandler**: 提供数据表格的 JSON API
- **MyEncoder**: 自定义 JSON 编码器，处理日期和字节类型

数据格式
--------
日期类型转换为 OA Date 格式，用于 SpreadJS 表格控件显示。

路由
----
- GET /instock/data?table_name=xxx: 数据表格页面
- GET /instock/api_data?name=xxx&date=xxx: 数据 API

使用方式
--------
访问数据表格页面::

    http://localhost:9988/instock/data?table_name=cn_stock_spot

获取 JSON 数据::

    http://localhost:9988/instock/api_data?name=cn_stock_spot&date=2024-01-15
"""

import datetime
import json
from abc import ABC

from tornado import gen

import instock.core.singleton_stock_web_module_data as sswmd
import instock.lib.trade_time as trd
import instock.web.base as webBase

__author__ = 'myh '
__date__ = '2023/3/10 '


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, bytes):
            return "是" if ord(obj) == 1 else "否"
        elif isinstance(obj, datetime.date):
            delta = datetime.datetime.combine(obj, datetime.time.min) - datetime.datetime(1899, 12, 30)
            return f'/OADate({float(delta.days) + (float(delta.seconds) / 86400)})/'  # 86,400 seconds in day
            # return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)


# 获得页面数据。
class GetStockHtmlHandler(webBase.BaseHandler, ABC):
    @gen.coroutine
    def get(self):
        name = self.get_argument("table_name", default=None, strip=False)
        web_module_data = sswmd.stock_web_module_data().get_data(name)
        run_date, run_date_nph = trd.get_trade_date_last()
        if web_module_data.is_realtime:
            date_now_str = run_date_nph.strftime("%Y-%m-%d")
        else:
            date_now_str = run_date.strftime("%Y-%m-%d")
        self.render("stock_web.html", web_module_data=web_module_data, date_now=date_now_str,
                    leftMenu=webBase.GetLeftMenu(self.request.uri))


# 获得股票数据内容。
class GetStockDataHandler(webBase.BaseHandler, ABC):
    def get(self):
        name = self.get_argument("name", default=None, strip=False)
        date = self.get_argument("date", default=None, strip=False)
        web_module_data = sswmd.stock_web_module_data().get_data(name)
        self.set_header('Content-Type', 'application/json;charset=UTF-8')

        if date is None:
            where = ""
        else:
            # where = f" WHERE `date` = '{date}'"
            where = f" WHERE `date` = %s"

        order_by = ""
        if web_module_data.order_by is not None:
            order_by = f" ORDER BY {web_module_data.order_by}"

        order_columns = ""
        if web_module_data.order_columns is not None:
            order_columns = f",{web_module_data.order_columns}"

        sql = f" SELECT *{order_columns} FROM `{web_module_data.table_name}`{where}{order_by}"
        data = self.db.query(sql,date)

        self.write(json.dumps(data, cls=MyEncoder))
