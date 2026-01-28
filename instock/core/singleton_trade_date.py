#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易日历单例缓存模块

本模块提供 A 股交易日历数据的单例缓存管理，用于判断某一天是否为交易日。

核心概念
--------
- **交易日历**: A 股市场的历史交易日列表
- **单例缓存**: 交易日历在应用生命周期内只获取一次

使用方式
--------
判断是否为交易日::

    from instock.core.singleton_trade_date import stock_trade_date
    import datetime

    trade_dates = stock_trade_date().get_data()
    if datetime.date(2024, 1, 2) in trade_dates:
        print("是交易日")

注意事项
--------
- 交易日历数据来自新浪财经，首次获取需要网络请求
- 返回的是 set 类型，查询效率为 O(1)
"""

import logging
from typing import Optional, Set
import datetime

import instock.core.stockfetch as stf
from instock.lib.singleton_type import singleton_type

__author__ = 'myh '
__date__ = '2023/3/10 '


class stock_trade_date(metaclass=singleton_type):
    """A 股交易日历单例

    使用单例模式缓存交易日历数据，避免重复获取。
    交易日历用于判断某一天是否为 A 股市场的交易日。

    Attributes:
        data: Set[datetime.date]，包含所有历史交易日的集合

    Example:
        >>> trade_dates = stock_trade_date().get_data()
        >>> import datetime
        >>> datetime.date(2024, 1, 2) in trade_dates
        True
    """

    def __init__(self):
        """初始化并获取交易日历数据"""
        try:
            self.data = stf.fetch_stocks_trade_date()
        except Exception as e:
            logging.error(f"singleton.stock_trade_date处理异常：{e}")

    def get_data(self) -> Optional[Set[datetime.date]]:
        """获取交易日历数据

        Returns:
            交易日期的集合，获取失败时为 None
        """
        return self.data
