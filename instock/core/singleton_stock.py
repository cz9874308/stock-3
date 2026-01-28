#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据单例缓存模块

本模块提供股票数据的单例缓存管理，确保相同数据在整个应用生命周期内
只获取和存储一次，避免重复请求数据源，提高系统效率。

核心概念
--------
- **单例模式**: 使用 singleton_type 元类确保每个数据类只有一个实例
- **延迟加载**: 数据在首次访问时获取，之后直接返回缓存
- **并发获取**: 历史数据使用线程池并发获取多只股票数据

核心类
------
- **stock_data**: 当日全市场股票行情的单例缓存
- **stock_hist_data**: 全市场股票历史 K 线数据的单例缓存

使用方式
--------
获取当日行情数据::

    from instock.core.singleton_stock import stock_data
    import datetime

    date = datetime.date.today()
    df = stock_data(date).get_data()
    print(f"缓存了 {len(df)} 只股票的行情")

    # 再次调用返回同一实例（不会重新获取数据）
    df2 = stock_data(date).get_data()
    print(df is df2)  # True

获取历史数据::

    from instock.core.singleton_stock import stock_hist_data

    hist_dict = stock_hist_data(date).get_data()
    for stock_key, df in hist_dict.items():
        date_str, code, name = stock_key
        print(f"{code} {name}: {len(df)} 条历史数据")

注意事项
--------
- 单例实例会持续占用内存，适合需要多次访问的场景
- 历史数据获取使用 16 个线程并发，可通过 workers 参数调整
"""

import concurrent.futures
import logging
from typing import Dict, List, Optional, Tuple

import pandas as pd

import instock.core.stockfetch as stf
import instock.core.tablestructure as tbs
import instock.lib.trade_time as trd
from instock.lib.singleton_type import singleton_type

__author__ = 'myh '
__date__ = '2023/3/10 '


class stock_data(metaclass=singleton_type):
    """当日股票行情数据单例

    使用单例模式缓存当日全市场股票行情数据，避免重复获取。

    Attributes:
        data: DataFrame，包含全市场股票的实时/收盘行情数据

    Example:
        >>> df = stock_data(datetime.date.today()).get_data()
        >>> print(len(df))
    """

    def __init__(self, date):
        """初始化并获取指定日期的股票行情数据

        Args:
            date: 日期对象，用于获取该日的行情数据
        """
        try:
            self.data = stf.fetch_stocks(date)
        except Exception as e:
            logging.error(f"singleton.stock_data处理异常：{e}")

    def get_data(self) -> Optional[pd.DataFrame]:
        """获取缓存的行情数据

        Returns:
            包含股票行情的 DataFrame，获取失败时为 None
        """
        return self.data


class stock_hist_data(metaclass=singleton_type):
    """全市场股票历史数据单例

    使用单例模式缓存全市场股票的历史 K 线数据。
    通过线程池并发获取多只股票的历史数据，提高获取效率。

    Attributes:
        data: Dict，键为 (date, code, name) 元组，值为历史 K 线 DataFrame

    Example:
        >>> hist = stock_hist_data(date).get_data()
        >>> for stock_key, df in hist.items():
        ...     print(stock_key[1], len(df))  # 打印股票代码和数据条数
    """

    def __init__(self, date=None, stocks: Optional[List[Tuple]] = None, workers: int = 16):
        """初始化并获取历史数据

        Args:
            date: 日期对象，用于确定股票列表和历史数据区间
            stocks: 可选的股票列表，每个元素为 (date, code, name) 元组
                    如果为 None，则从 stock_data 获取全市场股票列表
            workers: 线程池工作线程数，默认 16
        """
        if stocks is None:
            _subset = stock_data(date).get_data()[list(tbs.TABLE_CN_STOCK_FOREIGN_KEY['columns'])]
            stocks = [tuple(x) for x in _subset.values]

        if stocks is None:
            self.data = None
            return

        # 计算历史数据区间（提高效率，只计算一次）
        date_start, is_cache = trd.get_trade_hist_interval(stocks[0][0])
        _data = {}

        try:
            # 使用线程池并发获取历史数据
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_stock = {
                    executor.submit(stf.fetch_stock_hist, stock, date_start, is_cache): stock
                    for stock in stocks
                }
                for future in concurrent.futures.as_completed(future_to_stock):
                    stock = future_to_stock[future]
                    try:
                        __data = future.result()
                        if __data is not None:
                            _data[stock] = __data
                    except Exception as e:
                        logging.error(f"singleton.stock_hist_data处理异常：{stock[1]}代码{e}")
        except Exception as e:
            logging.error(f"singleton.stock_hist_data处理异常：{e}")

        if not _data:
            self.data = None
        else:
            self.data = _data

    def get_data(self) -> Optional[Dict[Tuple, pd.DataFrame]]:
        """获取缓存的历史数据

        Returns:
            字典，键为 (date, code, name) 元组，值为该股票的历史 K 线 DataFrame
            获取失败时为 None
        """
        return self.data
