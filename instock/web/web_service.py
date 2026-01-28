#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
Web 服务主入口

本模块是 InStock 股票分析系统的 Web 服务入口，基于 Tornado 框架构建，
提供股票数据展示、技术指标可视化、股票关注等功能。

技术栈
------
- **Tornado**: 高性能异步 Web 框架
- **Bootstrap**: 前端 UI 框架
- **Bokeh**: 数据可视化库（用于 K 线图）
- **SpreadJS**: 表格控件（用于数据表格展示）

路由配置
--------
- /: 首页
- /instock/data: 数据表格页面
- /instock/api_data: 数据 API 接口
- /instock/data/indicators: 技术指标可视化页面
- /instock/control/attention: 股票关注操作接口

启动方式
--------
命令行运行::

    python web_service.py

Docker 运行::

    docker-compose up -d

访问地址
--------
默认端口 9988，访问 http://localhost:9988/

日志文件
--------
日志保存在 `instock/web/log/stock_web.log`
"""

import logging
import os.path
import sys
from abc import ABC

import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado import gen

# 在项目运行时，临时将项目路径添加到环境变量
cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)

# 配置日志
log_path = os.path.join(cpath_current, 'log')
if not os.path.exists(log_path):
    os.makedirs(log_path)
logging.basicConfig(
    format='%(asctime)s %(message)s',
    filename=os.path.join(log_path, 'stock_web.log')
)
logging.getLogger().setLevel(logging.ERROR)

import instock.lib.database as mdb
import instock.lib.torndb as torndb
import instock.lib.version as version
import instock.web.base as webBase
import instock.web.dataIndicatorsHandler as dataIndicatorsHandler
import instock.web.dataTableHandler as dataTableHandler

__author__ = 'myh '
__date__ = '2023/3/10 '


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            # 设置路由
            (r"/", HomeHandler),
            (r"/instock/", HomeHandler),
            # 使用datatable 展示报表数据模块。
            (r"/instock/api_data", dataTableHandler.GetStockDataHandler),
            (r"/instock/data", dataTableHandler.GetStockHtmlHandler),
            # 获得股票指标数据。
            (r"/instock/data/indicators", dataIndicatorsHandler.GetDataIndicatorsHandler),
            # 加入关注
            (r"/instock/control/attention", dataIndicatorsHandler.SaveCollectHandler),
        ]
        settings = dict(  # 配置
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,  # True,
            # cookie加密
            cookie_secret="027bb1b670eddf0392cdda8709268a17b58b7",
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)
        # Have one global connection to the blog DB across all handlers
        self.db = torndb.Connection(**mdb.MYSQL_CONN_TORNDB)


# 首页handler。
class HomeHandler(webBase.BaseHandler, ABC):
    @gen.coroutine
    def get(self):
        self.render("index.html",
                    stockVersion=version.__version__,
                    leftMenu=webBase.GetLeftMenu(self.request.uri))


def main():
    # tornado.options.parse_command_line()
    tornado.options.options.logging = None

    http_server = tornado.httpserver.HTTPServer(Application())
    port = 9988
    http_server.listen(port)

    print(f"服务已启动，web地址 : http://localhost:{port}/")
    logging.error(f"服务已启动，web地址 : http://localhost:{port}/")

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
