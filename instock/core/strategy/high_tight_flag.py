#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
高而窄的旗形策略模块

本模块实现了"高而窄的旗形"（High Tight Flag）形态识别，这是威廉·欧奈尔
（William O'Neil）在《笑傲股市》中描述的经典强势形态。

策略原理
--------
高而窄的旗形是最强势的技术形态之一，特征如下：
1. 股价在短期内大幅上涨（如 1-2 周内上涨 90% 以上）
2. 随后在高位横盘整理，回调幅度很小（通常 10-25%）
3. 整理期间成交量萎缩
4. 通常出现在强势股的启动初期

入场条件
--------
1. 至少上市交易 60 日
2. 当日收盘价 / 之前 24~10 日的最低价 >= 1.9（涨幅 90%+）
3. 之前 24~10 日内必须有连续两天涨幅 >= 9.5%（涨停或接近涨停）
4. 需要龙虎榜有机构买入（istop=True）

使用方式
--------
检查是否满足高而窄旗形条件::

    from instock.core.strategy.high_tight_flag import check_high_tight

    is_signal = check_high_tight(
        code_name=("2024-01-15", "000001", "平安银行"),
        data=hist_data,
        istop=True  # 需要龙虎榜有机构
    )

注意事项
--------
- 该形态较为罕见，筛选结果通常较少
- 需要配合龙虎榜数据使用
"""

from typing import Optional, Tuple

import pandas as pd

__author__ = 'myh '
__date__ = '2023/3/10 '


def check_high_tight(
    code_name: Tuple[str, str, str],
    data: pd.DataFrame,
    date: Optional[object] = None,
    threshold: int = 60,
    istop: bool = False
) -> bool:
    """检查是否满足高而窄旗形条件

    识别股价短期内大幅上涨后形成的强势整理形态。

    Args:
        code_name: 股票标识元组 (日期, 代码, 名称)
        data: 历史 K 线数据 DataFrame
        date: 可选的指定日期
        threshold: 最少交易天数要求，默认 60 日
        istop: 是否龙虎榜有机构买入，必须为 True 才会触发

    Returns:
        如果满足高而窄旗形条件返回 True，否则返回 False
    """
    # 龙虎榜上必须有机构
    if not istop:
        return False
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

    data = data.tail(n=24)
    data = data.head(n=14)
    low = data['low'].values.min()
    ratio_increase = data.iloc[-1]['high'] / low
    if ratio_increase < 1.9:
        return False

    # 连续两天涨幅大于等于10%
    previous_p_change = 0.0
    for _p_change in data['p_change'].values:
        # 单日跌幅超7%；高开低走7%；两日累计跌幅10%；两日高开低走累计10%
        if _p_change >= 9.5:
            if previous_p_change >= 9.5:
                return True
            else:
                previous_p_change = _p_change
        else:
            previous_p_change = 0.0

    return False
