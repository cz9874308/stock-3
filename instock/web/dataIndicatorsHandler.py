#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
技术指标可视化处理模块

本模块提供股票技术指标的可视化页面和股票关注功能。

核心组件
--------
- **GetDataIndicatorsHandler**: 渲染技术指标可视化页面（K 线图 + 指标）
- **SaveCollectHandler**: 处理股票关注/取消关注操作

可视化内容
----------
- K 线图
- 成交量图
- MACD、KDJ、RSI 等技术指标

路由
----
- GET /instock/data/indicators?code=xxx&date=xxx: 技术指标页面
- GET /instock/control/attention?code=xxx&otype=xxx: 关注操作

使用方式
--------
查看股票技术指标::

    http://localhost:9988/instock/data/indicators?code=000001&date=2024-01-15

关注/取消关注::

    # 关注
    http://localhost:9988/instock/control/attention?code=000001&otype=0
    # 取消关注
    http://localhost:9988/instock/control/attention?code=000001&otype=1
"""

import logging
from abc import ABC

from tornado import gen

import instock.core.kline.visualization as vis
import instock.core.stockfetch as stf
import instock.web.base as webBase

__author__ = 'myh '
__date__ = '2023/3/10 '


# 获得页面数据。
class GetDataIndicatorsHandler(webBase.BaseHandler, ABC):
    @gen.coroutine
    def get(self):
        code = self.get_argument("code", default=None, strip=False)
        date = self.get_argument("date", default=None, strip=False)
        name = self.get_argument("name", default=None, strip=False)
        comp_list = []
        try:
            if code.startswith(('1', '5')):
                stock = stf.fetch_etf_hist((date, code))
            else:
                stock = stf.fetch_stock_hist((date, code))
            if stock is None:
                return

            pk = vis.get_plot_kline(code, stock, date, name)
            if pk is None:
                return

            comp_list.append(pk)
        except Exception as e:
            logging.error(f"dataIndicatorsHandler.GetDataIndicatorsHandler处理异常：{e}")

        self.render("stock_indicators.html", comp_list=comp_list,
                    leftMenu=webBase.GetLeftMenu(self.request.uri))


# 关注股票。
class SaveCollectHandler(webBase.BaseHandler, ABC):
    @gen.coroutine
    def get(self):
        import datetime
        import instock.core.tablestructure as tbs
        code = self.get_argument("code", default=None, strip=False)
        otype = self.get_argument("otype", default=None, strip=False)
        try:
            table_name = tbs.TABLE_CN_STOCK_ATTENTION['name']
            if otype == '1':
                # sql = f"DELETE FROM `{table_name}` WHERE `code` = '{code}'"
                sql = f"DELETE FROM `{table_name}` WHERE `code` = %s"
                self.db.query(sql,code)
            else:
                # sql = f"INSERT INTO `{table_name}`(`datetime`, `code`) VALUE('{datetime.datetime.now()}','{code}')"
                sql = f"INSERT INTO `{table_name}`(`datetime`, `code`) VALUE(%s, %s)"
                self.db.query(sql,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),code)
        except Exception as e:
            err = {"error": str(e)}
            # logging.info(err)
            # self.write(err)
            # return
        self.write("{\"data\":[{}]}")