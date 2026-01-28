#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
无大幅回撤策略模块

本模块实现了无大幅回撤的上涨形态识别，用于筛选稳健上涨且回调幅度较小的股票。

策略原理
--------
无大幅回撤策略的核心逻辑：
- 股价持续上涨且涨幅可观（60 日涨幅 > 60%）
- 期间没有出现大幅回调，说明持仓者惜售
- 这类股票通常处于主升浪阶段，上涨趋势稳固

入场条件
--------
1. 当日收盘价比 60 日前收盘价涨幅 > 60%
2. 最近 60 日内，无以下任何一种大幅回撤：
   - 单日跌幅超过 7%
   - 单日高开低走超过 7%
   - 连续两日累计跌幅超过 10%
   - 连续两日高开低走累计超过 10%

使用方式
--------
检查是否满足无大幅回撤条件::

    from instock.core.strategy.low_backtrace_increase import check

    is_signal = check(
        code_name=("2024-01-15", "000001", "平安银行"),
        data=hist_data,
        threshold=60
    )

注意事项
--------
- 追涨策略，需要控制仓位
- 建议配合止损策略使用
"""

from typing import Optional, Tuple

import pandas as pd

__author__ = 'myh '
__date__ = '2023/3/10 '


def check(
    code_name: Tuple[str, str, str],
    data: pd.DataFrame,
    date: Optional[object] = None,
    threshold: int = 60
) -> bool:
    """检查是否满足无大幅回撤条件

    识别稳健上涨且回调幅度较小的股票。

    Args:
        code_name: 股票标识元组 (日期, 代码, 名称)
        data: 历史 K 线数据 DataFrame
        date: 可选的指定日期
        threshold: 计算周期，默认 60 日

    Returns:
        如果满足无大幅回撤条件返回 True，否则返回 False
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

    ratio_increase = (data.iloc[-1]['close'] - data.iloc[0]['close']) / data.iloc[0]['close']
    if ratio_increase < 0.6:
        return False

    # 允许有一次“洗盘”
    previous_p_change = 100.0
    previous_open = -1000000.0
    for _p_change, _close, _open in zip(data['p_change'].values, data['close'].values, data['open'].values):
        # 单日跌幅超7%；高开低走7%；两日累计跌幅10%；两日高开低走累计10%
        if _p_change < -7 or (_close - _open) / _open * 100 < -7 \
                or previous_p_change + _p_change < -10 \
                or (_close - previous_open)/previous_open * 100 < -10:
            return False
        previous_p_change = _p_change
        previous_open = _open
    return True
