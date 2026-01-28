#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务调度模块

本包提供数据采集和分析的定时任务。

主要模块
--------
- execute_daily_job: 每日任务调度入口
- init_job: 数据库初始化
- basic_data_daily_job: 基础行情采集
- indicators_data_daily_job: 技术指标计算
- strategy_data_daily_job: 策略选股执行
- backtest_data_daily_job: 回测分析

执行方式
--------
通过 cron 定时任务在每个交易日收盘后执行。
"""

__author__ = 'myh '
__date__ = '2023/4/3 '
