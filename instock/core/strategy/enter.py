#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
放量上涨策略模块

本模块实现了放量上涨的入场信号判断，用于识别成交量显著放大且价格上涨的股票，
这通常表示有主力资金入场。

策略原理
--------
放量上涨是技术分析中的经典形态，其核心逻辑是：
- 成交量突然放大表明有大量资金介入
- 配合价格上涨表明资金是买入而非卖出
- 量价配合良好的上涨更具持续性

入场条件
--------
1. 当日涨幅 >= 2%（阳线上涨）
2. 收盘价 >= 开盘价（收阳线）
3. 当日成交额 >= 2 亿元（流动性保障）
4. 当日成交量 / 5 日平均成交量 >= 2（量比放大）

使用方式
--------
检查是否满足放量上涨条件::

    from instock.core.strategy.enter import check_volume

    is_signal = check_volume(
        code_name=("2024-01-15", "000001", "平安银行"),
        data=hist_data,
        threshold=60
    )

注意事项
--------
- 需要包含成交量数据的历史 K 线
- 成交额阈值 2 亿适用于 A 股主板，小盘股可能需要调整
"""

from typing import Optional, Tuple

import numpy as np
import pandas as pd
import talib as tl

__author__ = 'myh '
__date__ = '2023/3/10 '


def check_volume(
    code_name: Tuple[str, str, str],
    data: pd.DataFrame,
    date: Optional[object] = None,
    threshold: int = 60
) -> bool:
    """检查是否满足放量上涨条件

    判断股票是否出现成交量显著放大且价格上涨的形态。

    Args:
        code_name: 股票标识元组 (日期, 代码, 名称)
        data: 历史 K 线数据 DataFrame
        date: 可选的指定日期
        threshold: 计算周期，默认 60 日

    Returns:
        如果满足放量上涨条件返回 True，否则返回 False
    """
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()
    if len(data.index) < threshold:
        return False

    p_change = data.iloc[-1]['p_change']
    if p_change < 2 or data.iloc[-1]['close'] < data.iloc[-1]['open']:
        return False

    data.loc[:, 'vol_ma5'] = tl.MA(data['volume'].values, timeperiod=5)
    data['vol_ma5'].values[np.isnan(data['vol_ma5'].values)] = 0.0

    data = data.tail(n=threshold + 1)
    if len(data) < threshold + 1:
        return False

    # 最后一天收盘价
    last_close = data.iloc[-1]['close']
    # 最后一天成交量
    last_vol = data.iloc[-1]['volume']

    amount = last_close * last_vol

    # 成交额不低于2亿
    if amount < 200000000:
        return False

    data = data.head(n=threshold)

    mean_vol = data.iloc[-1]['vol_ma5']

    vol_ratio = last_vol / mean_vol
    if vol_ratio >= 2:
        return True
    else:
        return False
