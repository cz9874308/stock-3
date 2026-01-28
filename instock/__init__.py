#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InStock 股票分析系统

InStock 是一个功能完整的 A 股数据采集与分析系统，支持：

核心功能
--------
- **数据采集**: 实时行情、历史K线、资金流向、龙虎榜等
- **技术分析**: 40+ 种技术指标计算
- **形态识别**: 60+ 种K线形态识别
- **策略选股**: 多种经典选股策略
- **回测分析**: 策略收益回测
- **Web 界面**: 数据展示和可视化
- **自动交易**: 基于 easytrader 的自动交易

模块结构
--------
- instock.lib: 基础设施层
- instock.core: 核心业务层
- instock.job: 任务调度层
- instock.web: Web 服务层
- instock.trade: 交易引擎层

快速开始
--------
1. 启动 Web 服务::

    python instock/web/web_service.py

2. 执行数据采集::

    python instock/job/execute_daily_job.py

3. 启动自动交易::

    python instock/trade/trade_service.py
"""

__author__ = 'myh '
__date__ = '2023/4/3 '
