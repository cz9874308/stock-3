#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
持续上涨（均线多头）策略模块

本模块实现了均线多头排列的趋势判断，用于识别处于稳定上升趋势中的股票。

策略原理
--------
均线多头排列是经典的趋势判断方法：
- 短期均线位于长期均线之上
- 各周期均线呈现向上发散态势
- 表明短期、中期、长期投资者都处于盈利状态

入场条件
--------
1. 30日前的30日均线 < 20日前的30日均线 < 10日前的30日均线 < 当日的30日均线
2. 当日的30日均线 / 30日前的30日均线 > 1.2（均线上涨 20%+）

使用方式
--------
检查是否满足均线多头条件::

    from instock.core.strategy.keep_increasing import check

    is_signal = check(
        code_name=("2024-01-15", "000001", "平安银行"),
        data=hist_data,
        threshold=30
    )

注意事项
--------
- 趋势策略适合右侧交易
- 在均线粘合期可能产生虚假信号
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
    threshold: int = 30
) -> bool:
    """检查是否满足均线多头排列条件

    判断 30 日均线是否呈现持续上涨态势。

    Args:
        code_name: 股票标识元组 (日期, 代码, 名称)
        data: 历史 K 线数据 DataFrame
        date: 可选的指定日期
        threshold: 计算周期，默认 30 日

    Returns:
        如果满足均线多头条件返回 True，否则返回 False
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

    data.loc[:, 'ma30'] = tl.MA(data['close'].values, timeperiod=30)
    data['ma30'].values[np.isnan(data['ma30'].values)] = 0.0

    data = data.tail(n=threshold)

    step1 = round(threshold / 3)
    step2 = round(threshold * 2 / 3)

    if data.iloc[0]['ma30'] < data.iloc[step1]['ma30'] < \
            data.iloc[step2]['ma30'] < data.iloc[-1]['ma30'] and data.iloc[-1]['ma30'] > 1.2 * data.iloc[0]['ma30']:
        return True
    else:
        return False
