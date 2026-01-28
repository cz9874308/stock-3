#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心业务层

本包包含 InStock 系统的核心业务逻辑。

子模块
------
- crawling: 数据抓取模块
- indicator: 技术指标计算
- pattern: K线形态识别
- strategy: 选股策略
- backtest: 回测分析
- kline: K线可视化

核心类
------
- stockfetch: 统一数据获取入口
- singleton_stock: 股票数据缓存
- tablestructure: 数据表结构定义
"""

__author__ = 'myh '
__date__ = '2023/4/3 '
