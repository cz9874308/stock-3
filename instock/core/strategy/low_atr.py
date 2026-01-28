#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
低 ATR 成长策略模块

本模块实现了低波动率成长股的识别，寻找波动较小但有明显上涨趋势的股票。

策略原理
--------
低 ATR 策略的核心理念：
- ATR（平均真实波幅）较低表明股价波动温和
- 在低波动的基础上有明显涨幅，说明是稳健的上涨
- 这类股票风险较低，适合稳健型投资者

入场条件
--------
1. 至少上市交易 250 日（有足够历史数据）
2. 最近 10 个交易日的平均日波动率 < 10%（低波动）
3. 最近 10 个交易日的最高收盘价 / 最低收盘价 > 1.1（有涨幅）

使用方式
--------
检查是否满足低 ATR 成长条件::

    from instock.core.strategy.low_atr import check_low_increase

    is_signal = check_low_increase(
        code_name=("2024-01-15", "000001", "平安银行"),
        data=hist_data,
        threshold=10
    )

注意事项
--------
- 适合寻找稳健上涨的股票
- 可能会错过快速拉升的机会
"""

from typing import Optional, Tuple

import pandas as pd

__author__ = 'myh '
__date__ = '2023/3/10 '


def check_low_increase(
    code_name: Tuple[str, str, str],
    data: pd.DataFrame,
    date: Optional[object] = None,
    ma_short: int = 30,
    ma_long: int = 250,
    threshold: int = 10
) -> bool:
    """检查是否满足低 ATR 成长条件

    识别低波动但有明显涨幅的股票。

    Args:
        code_name: 股票标识元组 (日期, 代码, 名称)
        data: 历史 K 线数据 DataFrame
        date: 可选的指定日期
        ma_short: 短期均线周期，默认 30
        ma_long: 长期均线周期，默认 250
        threshold: 计算周期，默认 10 日

    Returns:
        如果满足低 ATR 成长条件返回 True，否则返回 False
    """
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask]
    if len(data.index) < ma_long:
        return False

    # data.loc[:, 'ma_short'] = tl.MA(data['close'].values, timeperiod=ma_short)
    # data['ma_short'].values[np.isnan(data['ma_short'].values)] = 0.0
    # data.loc[:, 'ma_long'] = tl.MA(data['close'].values, timeperiod=ma_long)
    # data['ma_long'].values[np.isnan(data['ma_long'].values)] = 0.0

    data = data.tail(n=threshold)
    inc_days = 0
    dec_days = 0
    days_count = len(data.index)
    if days_count < threshold:
        return False

    # 区间最低点
    lowest_row = 1000000
    # 区间最高点
    highest_row = 0

    total_change = 0.0
    for _close, _p_change in zip(data['close'].values, data['p_change'].values):
        if _p_change > 0:
            total_change += abs(_p_change)
            inc_days = inc_days + 1
        elif _p_change < 0:
            total_change += abs(_p_change)
            dec_days = dec_days + 1

        if _close > highest_row:
            highest_row = _close
        elif _close < lowest_row:
            lowest_row = _close

    atr = total_change / days_count
    if atr > 10:
        return False

    ratio = (highest_row - lowest_row) / lowest_row

    if ratio > 1.1:
        return True

    return False
