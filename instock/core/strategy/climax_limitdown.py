#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
放量跌停策略模块

本模块实现了放量跌停形态的识别，用于发现可能的恐慌性抛售和超跌反弹机会。

策略原理
--------
放量跌停是极端的市场行为，可能代表：
- 利空消息导致的恐慌性抛售
- 主力出货的尾声（放量见底）
- 短线超跌后的反弹机会

注意：这是高风险策略，需要配合基本面分析判断是否为"利空出尽"。

识别条件
--------
1. 当日跌幅 > 9.5%（跌停或接近跌停）
2. 当日成交额 >= 2 亿元（有大量资金参与）
3. 当日成交量 / 5 日平均成交量 >= 4（成交量显著放大）

使用方式
--------
检查是否满足放量跌停条件::

    from instock.core.strategy.climax_limitdown import check

    is_signal = check(
        code_name=("2024-01-15", "000001", "平安银行"),
        data=hist_data,
        threshold=60
    )

注意事项
--------
- 放量跌停不一定是买入信号，可能是下跌开始
- 需要结合基本面分析判断是利空出尽还是趋势反转
- 高风险策略，建议小仓位参与
"""

from typing import Optional, Tuple

import numpy as np
import pandas as pd
import talib as tl

__author__ = 'myh '
__date__ = '2023/3/10 '


def check(
    code_name: Tuple[str, str, str],
    data: pd.DataFrame,
    date: Optional[object] = None,
    threshold: int = 60
) -> bool:
    """检查是否满足放量跌停条件

    识别成交量显著放大的跌停形态。

    Args:
        code_name: 股票标识元组 (日期, 代码, 名称)
        data: 历史 K 线数据 DataFrame
        date: 可选的指定日期
        threshold: 计算周期，默认 60 日

    Returns:
        如果满足放量跌停条件返回 True，否则返回 False
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
    if p_change > -9.5:
        return False

    data.loc[:, 'vol_ma5'] = tl.MA(data['volume'].values, timeperiod=5)
    data['vol_ma5'].values[np.isnan(data['vol_ma5'].values)] = 0.0

    data = data.tail(n=threshold + 1)
    if len(data.index) < threshold + 1:
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
    if vol_ratio >= 4:
        return True
    else:
        return False
