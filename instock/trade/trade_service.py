#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易服务主入口

本模块是 InStock 自动交易系统的主入口，基于事件驱动架构，
集成 easytrader 库实现券商交易接口对接。

核心架构
--------
- **MainEngine**: 主引擎，协调各子系统
- **EventEngine**: 事件驱动引擎
- **ClockEngine**: 时钟推送引擎
- **Strategy**: 交易策略

支持的券商
----------
- 广发证券客户端 (gf_client)
- 其他 easytrader 支持的券商

配置文件
--------
- config/trade_client.json: 券商账号配置

启动方式
--------
命令行运行::

    python trade_service.py

日志文件
--------
日志保存在 `instock/trade/log/stock_trade.log`

注意事项
--------
- 生产环境建议关闭策略热重载功能 (is_watch_strategy = False)
- 需要安装对应券商的客户端软件
"""

import os.path
import sys

# 在项目运行时，临时将项目路径添加到环境变量
cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)

# 配置文件路径
need_data = os.path.join(cpath_current, 'config', 'trade_client.json')
log_filepath = os.path.join(cpath_current, 'log', 'stock_trade.log')

from instock.trade.robot.engine.main_engine import MainEngine
from instock.trade.robot.infrastructure.default_handler import DefaultLogHandler

__author__ = 'myh '
__date__ = '2023/4/10 '


def main():
    broker = 'gf_client'
    log_handler = DefaultLogHandler(name='交易服务', log_type='file', filepath=log_filepath)
    m = MainEngine(broker, need_data, log_handler)
    m.is_watch_strategy = True  # 策略文件出现改动时,自动重载,不建议在生产环境下使用
    m.load_strategy()
    m.start()


# main函数入口
if __name__ == '__main__':
    main()
