#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
回踩年线策略模块

本模块实现了回踩年线（250 日均线）的形态识别，这是经典的趋势回调买入策略。

策略原理
--------
回踩年线策略的核心逻辑：
1. 股价从年线下方向上突破，确认长期趋势转牛
2. 突破后股价回调至年线附近，但不跌破年线
3. 回调过程中成交量萎缩，表明抛压减轻
4. 回调完成后再次上涨，形成二次买点

入场条件
--------
1. 前段（最高价之前）：股价从年线下方向上突破年线
2. 后段（最高价之后）：股价始终在年线之上运行
3. 后段最低价日与最高价日相差 10-50 日（适当的回调时间）
4. 回踩伴随缩量：最高价日成交量 / 最低价日成交量 > 2
5. 回调幅度适中：最低价 / 最高价 < 0.8（回调 20%+）

使用方式
--------
检查是否满足回踩年线条件::

    from instock.core.strategy.backtrace_ma250 import check

    is_signal = check(
        code_name=("2024-01-15", "000001", "平安银行"),
        data=hist_data,
        threshold=60
    )

注意事项
--------
- 需要至少 250 日的历史数据计算年线
- 适合中长期趋势投资
"""

from datetime import datetime, timedelta
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
    """检查是否满足回踩年线条件

    识别股价突破年线后回调不破年线的买入机会。

    Args:
        code_name: 股票标识元组 (日期, 代码, 名称)
        data: 历史 K 线数据 DataFrame
        date: 可选的指定日期
        threshold: 计算周期，默认 60 日

    Returns:
        如果满足回踩年线条件返回 True，否则返回 False
    """
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")

    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()
    if len(data.index) < 250:
        return False

    data.loc[:, 'ma250'] = tl.MA(data['close'].values, timeperiod=250)
    data['ma250'].values[np.isnan(data['ma250'].values)] = 0.0

    data = data.tail(n=threshold)

    # 区间最低点
    lowest_row = [1000000, 0, '']
    # 区间最高点
    highest_row = [0, 0, '']
    # 近期低点
    recent_lowest_row = [1000000, 0, '']

    # 计算区间最高、最低价格
    for _close, _volume, _date in zip(data['close'].values, data['volume'].values, data['date'].values):
        if _close > highest_row[0]:
            highest_row[0] = _close
            highest_row[1] = _volume
            highest_row[2] = _date
        elif _close < lowest_row[0]:
            lowest_row[0] = _close
            lowest_row[1] = _volume
            lowest_row[2] = _date

    if lowest_row[1] == 0 or highest_row[1] == 0:
        return False

    data_front = data.loc[(data['date'] < highest_row[2])]
    data_end = data.loc[(data['date'] >= highest_row[2])]

    if data_front.empty:
        return False
    # 前半段由年线以下向上突破
    if not (data_front.iloc[0]['close'] < data_front.iloc[0]['ma250'] and
            data_front.iloc[-1]['close'] > data_front.iloc[-1]['ma250']):
        return False

    if not data_end.empty:
        # 后半段必须在年线以上运行（回踩年线）
        for _close, _volume, _date, _ma250 in zip(data_end['close'].values, data_end['volume'].values, data_end['date'].values, data_end['ma250'].values):
            if _close < _ma250:
                return False
            if _close < recent_lowest_row[0]:
                recent_lowest_row[0] = _close
                recent_lowest_row[1] = _volume
                recent_lowest_row[2] = _date

    date_diff = datetime.date(datetime.strptime(recent_lowest_row[2], '%Y-%m-%d')) - \
                datetime.date(datetime.strptime(highest_row[2], '%Y-%m-%d'))

    if not (timedelta(days=10) <= date_diff <= timedelta(days=50)):
        return False
    # 回踩伴随缩量
    vol_ratio = highest_row[1] / recent_lowest_row[1]
    back_ratio = recent_lowest_row[0] / highest_row[0]

    if not (vol_ratio > 2 and back_ratio < 0.8):
        return False

    return True
