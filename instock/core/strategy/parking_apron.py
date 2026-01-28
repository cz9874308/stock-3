#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
停机坪策略模块

本模块实现了"停机坪"形态识别，这是涨停后高位横盘整理的经典形态。

策略原理
--------
停机坪形态的核心特征：
1. 股价出现涨停（涨幅 > 9.5%）且满足海龟入场条件
2. 涨停后连续 3 日在涨停价上方横盘整理
3. 整理期间振幅较小（开盘价与收盘价相差 < 3%）
4. 整理期间涨跌幅控制在 ±5% 以内

这种形态表明：
- 涨停后抛压较小，股价能稳定在高位
- 主力资金锁仓良好，筹码稳定
- 可能是下一波上涨前的蓄势阶段

入场条件
--------
1. 最近 15 日有涨幅 > 9.5% 的涨停日
2. 涨停日满足海龟交易法则入场条件
3. 涨停后 3 日在涨停价上方横盘（振幅 < 3%，涨跌幅 < 5%）

使用方式
--------
检查是否满足停机坪条件::

    from instock.core.strategy.parking_apron import check

    is_signal = check(
        code_name=("2024-01-15", "000001", "平安银行"),
        data=hist_data,
        threshold=15
    )

注意事项
--------
- 涨停后追涨有风险，需控制仓位
- 建议配合龙虎榜数据分析主力意图
"""

from datetime import datetime
from typing import Optional, Tuple

import pandas as pd

from instock.core.strategy import turtle_trade

__author__ = 'myh '
__date__ = '2023/3/10 '


def check(
    code_name: Tuple[str, str, str],
    data: pd.DataFrame,
    date: Optional[object] = None,
    threshold: int = 15
) -> bool:
    """检查是否满足停机坪条件

    识别涨停后高位横盘整理的形态。

    Args:
        code_name: 股票标识元组 (日期, 代码, 名称)
        data: 历史 K 线数据 DataFrame
        date: 可选的指定日期
        threshold: 计算周期，默认 15 日

    Returns:
        如果满足停机坪条件返回 True，否则返回 False
    """
    origin_data = data
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

    limitup_row = [1000000, '']
    # 找出涨停日
    for _close, _p_change, _date in zip(data['close'].values, data['p_change'].values, data['date'].values):
        if _p_change > 9.5:
            if turtle_trade.check_enter(code_name, origin_data, date=datetime.date(datetime.strptime(_date, '%Y-%m-%d')), threshold=threshold):
                limitup_row[0] = _close
                limitup_row[1] = _date
                if check_internal(data, limitup_row):
                    return True
    return False

def check_internal(data, limitup_row):
    limitup_price = limitup_row[0]
    limitup_end = data.loc[(data['date'] > limitup_row[1])]
    limitup_end = limitup_end.head(n=3)
    if len(limitup_end.index) < 3:
        return False

    consolidation_day1 = limitup_end.iloc[0]
    consolidation_day23 = limitup_end.tail(n=2)

    if not (consolidation_day1['close'] > limitup_price and consolidation_day1['open'] > limitup_price and
            0.97 < consolidation_day1['close'] / consolidation_day1['open'] < 1.03):
        return False

    for _close, _p_change, _open in zip(consolidation_day23['close'].values, consolidation_day23['p_change'].values, consolidation_day23['open'].values):
        if not (0.97 < (_close / _open) < 1.03 and -5 < _p_change < 5
                and _close > limitup_price and _open > limitup_price):
            return False

    return True
