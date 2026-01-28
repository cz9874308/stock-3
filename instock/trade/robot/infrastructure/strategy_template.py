#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略模板模块

本模块提供交易策略的基类模板，所有自定义策略都应继承此类。

核心组件
--------
- **StrategyTemplate**: 策略基类，定义策略的生命周期方法

生命周期方法
------------
1. __init__: 构造函数，由引擎自动调用
2. init: 初始化钩子，策略自定义初始化逻辑
3. clock: 时钟事件处理，每个时钟事件触发时调用
4. strategy: 策略核心逻辑
5. shutdown: 关闭钩子，进程退出前调用

可用属性
--------
- user: easytrader 交易接口
- main_engine: 主引擎实例
- clock_engine: 时钟引擎实例
- log: 日志处理器

使用方式
--------
创建自定义策略::

    from instock.trade.robot.infrastructure.strategy_template import StrategyTemplate

    class Strategy(StrategyTemplate):
        name = 'MyStrategy'

        def init(self):
            self.log.info('策略初始化')

        def clock(self, event):
            if event.data.clock_event == 'open':
                self.log.info('开盘了')

        def shutdown(self):
            self.log.info('策略关闭')
"""

from typing import Any, Optional

__author__ = 'myh '
__date__ = '2023/4/10 '


class StrategyTemplate:
    """策略基类模板

    所有交易策略都应继承此类，并实现相应的钩子方法。

    Attributes:
        name: 策略名称，用于标识和日志
        user: easytrader 交易接口
        main_engine: 主引擎实例
        clock_engine: 时钟引擎实例
        log: 日志处理器
    """

    name = 'DefaultStrategyTemplate'

    def __init__(self, user: Any, log_handler: Any, main_engine: Any):
        """初始化策略

        Args:
            user: easytrader 交易接口
            log_handler: 日志处理器
            main_engine: 主引擎实例
        """
        self.user = user
        self.main_engine = main_engine
        self.clock_engine = main_engine.clock_engine
        # 优先使用自定义 log 句柄，否则使用主引擎日志句柄
        self.log = self.log_handler() or log_handler
        self.init()

    def init(self) -> None:
        """初始化钩子

        子类可重写此方法进行自定义初始化。
        """
        pass

    def strategy(self) -> None:
        """策略核心逻辑

        子类应重写此方法实现交易策略。
        """
        pass

    def clock(self, event: Any) -> None:
        """时钟事件处理

        每个时钟事件触发时调用。

        Args:
            event: 时钟事件对象
        """
        pass

    def log_handler(self) -> Optional[Any]:
        """自定义日志处理器

        子类可重写此方法返回自定义的日志处理器。

        Returns:
            日志处理器实例，或 None 使用默认处理器
        """
        return None

    def shutdown(self) -> None:
        """关闭钩子

        进程退出前调用，用于清理资源。
        """
        pass
