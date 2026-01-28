#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
海龟交易法则策略模块

本模块实现了经典的海龟交易法则（Turtle Trading Rules）中的入场信号判断，
这是由理查德·丹尼斯（Richard Dennis）和威廉·埃克哈特（William Eckhardt）
在 1980 年代开发的著名趋势跟踪策略。

策略原理
--------
海龟交易法则基于唐奇安通道（Donchian Channel）突破理论：
- 当价格突破 N 日最高价时，认为上升趋势确立，产生买入信号
- 当价格跌破 N 日最低价时，认为下降趋势确立，产生卖出信号

入场条件
--------
- 当日收盘价 >= 最近 N 日（默认 60 日）的最高收盘价

使用方式
--------
检查是否满足入场条件::

    from instock.core.strategy.turtle_trade import check_enter

    is_signal = check_enter(
        code_name=("2024-01-15", "000001", "平安银行"),
        data=hist_data,
        threshold=60  # 60日突破
    )

注意事项
--------
- 需要足够的历史数据（至少 threshold 天）
- 海龟法则还包括仓位管理和止损规则，本模块仅实现入场信号
"""

from typing import Optional, Tuple

import pandas as pd

__author__ = 'myh '
__date__ = '2023/3/10 '

# 默认账户资金（用于仓位计算）
BALANCE = 200000


def check_enter(
    code_name: Tuple[str, str, str],
    data: pd.DataFrame,
    date: Optional[object] = None,
    threshold: int = 60
) -> bool:
    """检查是否满足海龟交易法则的入场条件

    判断当日收盘价是否创出指定区间内的最高价，即价格向上突破。

    Args:
        code_name: 股票标识元组 (日期, 代码, 名称)
        data: 历史 K 线数据 DataFrame，需包含 'date' 和 'close' 列
        date: 可选的指定日期，默认使用 code_name 中的日期
        threshold: 突破周期，默认 60 日

    Returns:
        如果满足入场条件返回 True，否则返回 False
    """
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask]
    if len(data.index) < threshold:
        return False

    data = data.tail(n=threshold)

    max_price = 0
    for _close in data['close'].values:
        if _close > max_price:
            max_price = _close

    last_close = data.iloc[-1]['close']

    if last_close >= max_price:
        return True

    return False
