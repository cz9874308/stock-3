#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股交易时间工具模块

本模块提供了与 A 股市场交易时间相关的各种工具函数，包括交易日判断、
交易时段判断、历史日期计算等功能。

核心概念
--------
- **交易日**: A 股市场开市的日期（排除周末和法定节假日）
- **交易时段**: 上午 9:15-11:30，下午 13:00-15:00
- **集合竞价**: 上午 9:15-9:25（开盘集合竞价），下午 14:57-15:00（收盘集合竞价）

交易时间表
----------
| 时段 | 时间范围 | 说明 |
|------|----------|------|
| 盘前集合竞价 | 09:15 - 09:25 | 可挂单，09:20后不可撤单 |
| 早盘连续竞价 | 09:30 - 11:30 | 正常交易时段 |
| 午间休市 | 11:30 - 13:00 | 暂停交易 |
| 午盘连续竞价 | 13:00 - 14:57 | 正常交易时段 |
| 收盘集合竞价 | 14:57 - 15:00 | 收盘价形成时段 |

使用方式
--------
判断当前是否为交易时间::

    from instock.lib.trade_time import is_tradetime, is_trade_date
    import datetime

    now = datetime.datetime.now()
    if is_trade_date(now.date()) and is_tradetime(now):
        print("当前为交易时间")
"""

import datetime
from typing import Optional, Tuple

from instock.core.singleton_trade_date import stock_trade_date

__author__ = 'myh '
__date__ = '2023/4/10 '

# ============================================================
# 交易时段常量定义
# ============================================================

# 交易时间段（包含集合竞价时段）
OPEN_TIME: Tuple[Tuple[datetime.time, datetime.time], ...] = (
    (datetime.time(9, 15, 0), datetime.time(11, 30, 0)),   # 上午时段
    (datetime.time(13, 0, 0), datetime.time(15, 0, 0)),    # 下午时段
)

# 午间休市时段
PAUSE_TIME: Tuple[Tuple[datetime.time, datetime.time], ...] = (
    (datetime.time(11, 30, 0), datetime.time(12, 59, 30)),
)

# 午间休市结束前的准备时段
CONTINUE_TIME: Tuple[Tuple[datetime.time, datetime.time], ...] = (
    (datetime.time(12, 59, 30), datetime.time(13, 0, 0)),
)

# 收盘时间点
CLOSE_TIME: Tuple[datetime.time, ...] = (
    datetime.time(15, 0, 0),
)


# ============================================================
# 交易日判断函数
# ============================================================

def is_trade_date(date: Optional[datetime.date] = None) -> bool:
    """判断指定日期是否为交易日

    通过查询交易日历数据，判断指定日期是否为 A 股市场的交易日。
    交易日排除了周末和法定节假日。

    Args:
        date: 需要判断的日期，默认为 None

    Returns:
        如果是交易日返回 True，否则返回 False

    Example:
        >>> import datetime
        >>> is_trade_date(datetime.date(2024, 1, 2))
        True
        >>> is_trade_date(datetime.date(2024, 1, 1))  # 元旦
        False
    """
    trade_date = stock_trade_date().get_data()
    if trade_date is None:
        return False
    if date in trade_date:
        return True
    else:
        return False


def get_previous_trade_date(date: datetime.date, count: int = 1) -> datetime.date:
    """获取指定日期之前的第 N 个交易日

    从指定日期向前查找，跳过非交易日，返回第 count 个交易日。

    Args:
        date: 起始日期
        count: 向前查找的交易日数量，默认为 1

    Returns:
        第 count 个之前的交易日日期

    Example:
        >>> import datetime
        >>> # 假设 2024-01-03 是交易日
        >>> get_previous_trade_date(datetime.date(2024, 1, 3), 1)
        datetime.date(2024, 1, 2)
    """
    while True:
        date = get_one_previous_trade_date(date)
        count -= 1
        if count == 0:
            break
    return date


def get_one_previous_trade_date(date: datetime.date) -> datetime.date:
    """获取指定日期的前一个交易日

    从指定日期向前查找最近的一个交易日。

    Args:
        date: 起始日期

    Returns:
        前一个交易日的日期
    """
    trade_date = stock_trade_date().get_data()
    if trade_date is None:
        return date
    tmp_date = date
    while True:
        tmp_date += datetime.timedelta(days=-1)
        if tmp_date in trade_date:
            break
    return tmp_date


def get_next_trade_date(date: datetime.date) -> datetime.date:
    """获取指定日期的下一个交易日

    从指定日期向后查找最近的一个交易日。

    Args:
        date: 起始日期

    Returns:
        下一个交易日的日期

    Example:
        >>> import datetime
        >>> # 假设 2024-01-05 是周五，下一个交易日是 2024-01-08（周一）
        >>> get_next_trade_date(datetime.date(2024, 1, 5))
        datetime.date(2024, 1, 8)
    """
    trade_date = stock_trade_date().get_data()
    if trade_date is None:
        return date
    tmp_date = date
    while True:
        tmp_date += datetime.timedelta(days=1)
        if tmp_date in trade_date:
            break
    return tmp_date


# ============================================================
# 交易时段判断函数
# ============================================================

def is_tradetime(now_time: datetime.datetime) -> bool:
    """判断当前时间是否在交易时段内

    交易时段包括：
    - 上午：09:15 - 11:30
    - 下午：13:00 - 15:00

    Args:
        now_time: 需要判断的时间（datetime 对象）

    Returns:
        如果在交易时段内返回 True，否则返回 False
    """
    now = now_time.time()
    for begin, end in OPEN_TIME:
        if begin <= now < end:
            return True
    else:
        return False


def is_pause(now_time: datetime.datetime) -> Optional[bool]:
    """判断当前时间是否在午间休市时段

    午间休市时段：11:30 - 12:59:30

    Args:
        now_time: 需要判断的时间（datetime 对象）

    Returns:
        如果在午间休市时段返回 True，否则返回 None
    """
    now = now_time.time()
    for b, e in PAUSE_TIME:
        if b <= now < e:
            return True


def is_continue(now_time: datetime.datetime) -> bool:
    """判断当前时间是否在午间休市结束前的准备时段

    准备时段：12:59:30 - 13:00:00，此时段可以进行下午开盘的准备工作。

    Args:
        now_time: 需要判断的时间（datetime 对象）

    Returns:
        如果在准备时段返回 True，否则返回 False
    """
    now = now_time.time()
    for b, e in CONTINUE_TIME:
        if b <= now < e:
            return True
    return False


def is_closing(now_time: datetime.datetime, start: datetime.time = datetime.time(14, 54, 30)) -> bool:
    """判断当前时间是否在收盘集合竞价时段

    默认收盘集合竞价时段：14:54:30 - 15:00:00

    Args:
        now_time: 需要判断的时间（datetime 对象）
        start: 收盘集合竞价开始时间，默认为 14:54:30

    Returns:
        如果在收盘集合竞价时段返回 True，否则返回 False
    """
    now = now_time.time()
    for close in CLOSE_TIME:
        if start <= now < close:
            return True
    return False


def is_close(now_time: datetime.datetime) -> bool:
    """判断当前时间是否已收盘

    收盘时间：15:00:00

    Args:
        now_time: 需要判断的时间（datetime 对象）

    Returns:
        如果已收盘返回 True，否则返回 False
    """
    now = now_time.time()
    for close in CLOSE_TIME:
        if now >= close:
            return True
    return False


def is_open(now_time: datetime.datetime) -> bool:
    """判断当前时间是否已开盘

    开盘时间：09:30:00（连续竞价开始）

    Args:
        now_time: 需要判断的时间（datetime 对象）

    Returns:
        如果已开盘返回 True，否则返回 False

    Note:
        此函数判断的是连续竞价开始时间，不包括集合竞价时段
    """
    now = now_time.time()
    if now >= datetime.time(9, 30, 0):
        return True
    return False


# ============================================================
# 日期区间和报告期计算函数
# ============================================================

def get_trade_hist_interval(date: str) -> Tuple[str, bool]:
    """获取历史数据查询的日期区间

    根据指定的结束日期，计算往前推 3 年的起始日期，并判断是否需要使用缓存数据。

    Args:
        date: 结束日期，格式为 "YYYY-MM-DD"

    Returns:
        元组 (起始日期, 是否使用缓存)
        - 起始日期：格式为 "YYYYMMDD"，为结束日期往前推 3 年
        - 是否使用缓存：如果当前时间在交易时段内且是当天，返回 False

    Example:
        >>> get_trade_hist_interval("2024-01-15")
        ('20210115', True)
    """
    tmp_year, tmp_month, tmp_day = date.split("-")
    date_end = datetime.datetime(int(tmp_year), int(tmp_month), int(tmp_day))
    date_start = (date_end + datetime.timedelta(days=-(365 * 3))).strftime("%Y%m%d")

    now_time = datetime.datetime.now()
    now_date = now_time.date()
    is_trade_date_open_close_between = False

    # 如果查询的是今天，且今天是交易日，且当前在交易时段内
    if date_end.date() == now_date:
        if is_trade_date(now_date):
            if is_open(now_time) and not is_close(now_time):
                is_trade_date_open_close_between = True

    return date_start, not is_trade_date_open_close_between


def get_trade_date_last() -> Tuple[datetime.date, datetime.date]:
    """获取最近的有效交易日期

    根据当前时间智能判断应该使用哪个交易日的数据：
    - 如果当前是交易日且已收盘：返回今天
    - 如果当前是交易日但未收盘：返回前一个交易日（用于已收盘数据）
    - 如果当前不是交易日：返回最近的交易日

    Returns:
        元组 (run_date, run_date_nph)
        - run_date: 用于获取已收盘数据的日期
        - run_date_nph: 用于获取实时数据的日期（nph = 牛批行情）

    Example:
        >>> # 假设今天是交易日且已收盘
        >>> run_date, run_date_nph = get_trade_date_last()
        >>> run_date == datetime.date.today()
        True
    """
    now_time = datetime.datetime.now()
    run_date = now_time.date()
    run_date_nph = run_date

    if is_trade_date(run_date):
        if not is_close(now_time):
            # 未收盘，使用前一个交易日的数据
            run_date = get_previous_trade_date(run_date)
            if not is_open(now_time):
                # 未开盘，实时数据也使用前一个交易日
                run_date_nph = run_date
    else:
        # 非交易日，使用前一个交易日
        run_date = get_previous_trade_date(run_date)
        run_date_nph = run_date

    return run_date, run_date_nph


def get_quarterly_report_date() -> str:
    """获取当前应查询的季度报告期

    根据当前日期，计算应该查询哪个季度的财务报告。

    季报披露规则：
    - 1-3月：查询上年年报（12月31日）
    - 4-6月：查询一季报（3月31日）
    - 7-9月：查询半年报（6月30日）
    - 10-12月：查询三季报（9月30日）

    Returns:
        报告期日期字符串，格式为 "YYYYMMDD"

    Example:
        >>> # 假设当前是 2024 年 5 月
        >>> get_quarterly_report_date()
        '20240331'
    """
    now_time = datetime.datetime.now()
    year = now_time.year
    month = now_time.month

    if 1 <= month <= 3:
        month_day = '1231'
    elif 4 <= month <= 6:
        month_day = '0331'
    elif 7 <= month <= 9:
        month_day = '0630'
    else:
        month_day = '0930'

    return f"{year}{month_day}"


def get_bonus_report_date() -> str:
    """获取当前应查询的分红送配报告期

    根据当前日期，计算应该查询哪个报告期的分红送配信息。
    分红送配通常在年报和半年报后披露。

    披露规则：
    - 2-6月：查询上年年报分红（上年12月31日）
    - 8-12月：查询半年报分红（当年6月30日）
    - 1月和7月：根据具体日期判断

    Returns:
        报告期日期字符串，格式为 "YYYYMMDD"

    Example:
        >>> # 假设当前是 2024 年 4 月
        >>> get_bonus_report_date()
        '20231231'
    """
    now_time = datetime.datetime.now()
    year = now_time.year
    month = now_time.month

    if 2 <= month <= 6:
        year -= 1
        month_day = '1231'
    elif 8 <= month <= 12:
        month_day = '0630'
    elif month == 7:
        if now_time.day > 25:
            month_day = '0630'
        else:
            year -= 1
            month_day = '1231'
    else:  # month == 1
        year -= 1
        if now_time.day > 25:
            month_day = '1231'
        else:
            month_day = '0630'

    return f"{year}{month_day}"
