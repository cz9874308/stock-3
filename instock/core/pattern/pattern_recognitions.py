#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K 线形态识别模块

本模块提供基于 TA-Lib 的 K 线形态识别功能，可识别 60+ 种经典 K 线形态，
用于技术分析和交易信号生成。

依赖库
------
- **TA-Lib**: 技术分析库，提供 K 线形态识别函数

支持的形态分类
--------------
反转形态：
- 锤子线 (Hammer)
- 吊颈线 (Hanging Man)
- 吞没形态 (Engulfing)
- 刺透形态 (Piercing)
- 乌云盖顶 (Dark Cloud Cover)
- 晨星/暮星 (Morning/Evening Star)

持续形态：
- 上升/下降三法 (Rising/Falling Three Methods)
- 三只乌鸦 (Three Black Crows)
- 三个白兵 (Three White Soldiers)

中性形态：
- 十字星 (Doji)
- 纺锤线 (Spinning Top)

使用方式
--------
识别所有形态::

    from instock.core.pattern.pattern_recognitions import get_pattern_recognitions
    df_with_patterns = get_pattern_recognitions(
        data=stock_data,
        stock_column=pattern_columns
    )

识别单只股票的形态::

    from instock.core.pattern.pattern_recognitions import get_pattern_recognition
    pattern_row = get_pattern_recognition(
        code_name=("2024-01-15", "000001", "平安银行"),
        data=hist_data,
        stock_column=pattern_columns
    )

返回值说明
----------
形态识别函数返回值：
- 100: 看涨形态
- -100: 看跌形态
- 0: 无形态

注意事项
--------
- 形态识别需要至少若干天的历史数据（取决于形态复杂度）
- 形态信号仅供参考，需结合其他分析方法使用
"""

import logging
from typing import Dict, Optional

import pandas as pd

__author__ = 'myh '
__date__ = '2023/3/24 '


def get_pattern_recognitions(data, stock_column, end_date=None, threshold=120, calc_threshold=None):
    isCopy = False
    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask]
        isCopy = True
    if calc_threshold is not None:
        data = data.tail(n=calc_threshold)
        isCopy = True
    if isCopy:
        data = data.copy()

    for k in stock_column:
        try:
            data.loc[:, k] = stock_column[k]['func'](data['open'].values, data['high'].values, data['low'].values, data['close'].values)
        except Exception as e:
            pass

    if data is None or len(data.index) == 0:
        return None

    if threshold is not None:
        data = data.tail(n=threshold).copy()

    return data


def get_pattern_recognition(code_name, data, stock_column, date=None, calc_threshold=12):
    try:
        # 增加空判断，如果是空返回 0 数据。
        if date is None:
            end_date = code_name[0]
        else:
            end_date = date.strftime("%Y-%m-%d")

        code = code_name[1]
        # 设置返回数组。
        # 增加空判断，如果是空返回 0 数据。
        if len(data.index) <= 1:
            return None

        stockStat = get_pattern_recognitions(data, stock_column, end_date=end_date, threshold=1,
                                             calc_threshold=calc_threshold)

        if stockStat is None:
            return None

        isHas = False
        for k in stock_column:
            if stockStat.iloc[0][k] != 0:
                isHas = True
                break

        if isHas:
            stockStat.loc[:, 'code'] = code
            return stockStat.iloc[0, -(len(stock_column) + 1):]

    except Exception as e:
        logging.error(f"pattern_recognitions.get_pattern_recognition处理异常：{code}代码{e}")

    return None
