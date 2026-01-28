#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
平台突破策略模块

本模块实现了平台突破的入场信号判断，用于识别股票在横盘整理后向上突破的形态。

策略原理
--------
平台突破是经典的技术分析形态，表示股票在经历一段时间的横盘整理后，
由于某种催化剂导致价格向上突破：

1. **平台期**: 股价在 60 日均线附近窄幅震荡，偏离度控制在 -5% ~ 20%
2. **突破日**: 开盘价低于 60 日均线，收盘价高于 60 日均线（向上穿越）
3. **量能配合**: 突破当日需要放量上涨确认

入场条件
--------
1. 60 日内某日收盘价 >= 60 日均线 > 开盘价（向上突破均线）
2. 突破日满足放量上涨条件
3. 突破前股价与 60 日均线偏离控制在 -5% ~ 20%（确认平台形态）

使用方式
--------
检查是否满足平台突破条件::

    from instock.core.strategy.breakthrough_platform import check

    is_signal = check(
        code_name=("2024-01-15", "000001", "平安银行"),
        data=hist_data,
        threshold=60
    )

注意事项
--------
- 需要足够的历史数据计算 60 日均线
- 依赖 enter.check_volume 函数判断放量
"""

from datetime import datetime
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import talib as tl

from instock.core.strategy import enter

__author__ = 'myh '
__date__ = '2023/3/10 '


def check(
    code_name: Tuple[str, str, str],
    data: pd.DataFrame,
    date: Optional[object] = None,
    threshold: int = 60
) -> bool:
    """检查是否满足平台突破条件

    判断股票是否形成平台整理后向上突破的形态。

    Args:
        code_name: 股票标识元组 (日期, 代码, 名称)
        data: 历史 K 线数据 DataFrame
        date: 可选的指定日期
        threshold: 计算周期，默认 60 日

    Returns:
        如果满足平台突破条件返回 True，否则返回 False
    """
    origin_data = data
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()
    if len(data.index) < threshold:
        return False

    data.loc[:, 'ma60'] = tl.MA(data['close'].values, timeperiod=60)
    data['ma60'].values[np.isnan(data['ma60'].values)] = 0.0

    data = data.tail(n=threshold)

    breakthrough_row = None
    for _close, _open, _date, _ma60 in zip(data['close'].values, data['open'].values, data['date'].values, data['ma60'].values):
        if _open < _ma60 <= _close:
            if enter.check_volume(code_name, origin_data, date=datetime.date(datetime.strptime(_date, '%Y-%m-%d')), threshold=threshold):
                breakthrough_row = _date
                break

    if breakthrough_row is None:
        return False

    data_front = data.loc[(data['date'] < breakthrough_row) & (data['ma60'] > 0)]
    for _close, _ma60 in zip(data_front['close'].values, data_front['ma60'].values):
        if not (-0.05 < ((_ma60 - _close) / _ma60) < 0.2):
            return False

    return True
