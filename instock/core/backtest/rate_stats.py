#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
收益率统计模块

本模块提供股票买入后的收益率计算功能，用于回测分析和策略评估。

核心概念
--------
- **累计涨跌幅**: 相对于买入日收盘价的累计涨跌百分比
- **持仓天数**: 从买入日开始计算的持有天数
- **区间收益**: 指定持仓期间的收益统计

核心功能
--------
- **get_rates**: 计算从买入日开始的后续 N 日累计收益率

使用方式
--------
计算买入后 100 个交易日的累计收益::

    from instock.core.backtest.rate_stats import get_rates

    rates = get_rates(
        code_name=("2024-01-15", "000001", "平安银行"),
        data=hist_data,
        stock_column=rate_columns,
        threshold=101  # 计算 100 天收益（+1 是因为包含买入日）
    )
    print(rates)

返回数据说明
------------
返回的 Series 包含：
- date: 买入日期
- code: 股票代码
- day_1 ~ day_N: 第 1~N 日的累计涨跌幅（百分比）

注意事项
--------
- 收益率为相对于买入日收盘价的百分比
- 如果历史数据不足，后续日期的收益率为 None
"""

import logging
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

__author__ = 'myh '
__date__ = '2023/3/10 '


def get_rates(code_name, data, stock_column, threshold=101):
    try:
        # 增加空判断，如果是空返回 0 数据。
        if data is None:
            return None

        start_date = code_name[0]
        code = code_name[1]
        # 设置返回数组。
        stock_data_list = [start_date, code]

        mask = (data['date'] >= start_date)
        data = data.loc[mask].copy()
        data = data.head(n=threshold)

        if len(data.index) <= 1:
            return None

        close1 = data.iloc[0]['close']
        # data.loc[:, 'sum_pct_change'] = data['close'].apply(lambda x: round(100 * (x - close1) / close1, 2))
        data.loc[:, 'sum_pct_change'] = np.around(100 * (data['close'].values - close1) / close1, decimals=2)
        # 计算区间最高、最低价格

        first = True
        col_len = len(data.columns)
        for row in data.values:
            if first:
                first = False
            else:
                stock_data_list.append(row[col_len-1])

        _l = len(stock_column) - len(stock_data_list)
        for i in range(0, _l):
            stock_data_list.append(None)

    except Exception as e:
        logging.error(f"rate_stats.get_rates处理异常：{code}代码{e}")

    return pd.Series(stock_data_list, index=stock_column)
