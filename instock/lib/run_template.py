#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
批量任务执行模板模块

本模块提供了一个通用的任务执行模板，支持以下三种运行模式：
1. **区间模式**: 指定起止日期，自动遍历区间内的所有交易日执行任务
2. **枚举模式**: 指定多个日期（逗号分隔），依次执行任务
3. **当前模式**: 不指定日期，自动获取最近的有效交易日执行任务

核心概念
--------
- **任务函数**: 接收日期作为第一个参数的可调用对象
- **交易日过滤**: 自动跳过非交易日，只在交易日执行任务
- **并发执行**: 使用线程池并发执行多个日期的任务

使用方式
--------
1. 区间模式（处理一段时间的历史数据）::

    python job.py 2023-03-01 2023-03-21

2. 枚举模式（处理指定的几个日期）::

    python job.py 2023-03-01,2023-03-02,2023-03-03

3. 当前模式（处理最近交易日的数据）::

    python job.py

注意事项
--------
- 区间模式和枚举模式下，任务以 2 秒间隔并发提交，避免对数据源造成压力
- 函数名以 'save_nph' 开头的任务使用实时数据日期
- 函数名以 'save_after_close' 开头的任务使用已收盘数据日期
"""

import logging
import datetime
import concurrent.futures
import sys
import time
from typing import Callable, Any

import instock.lib.trade_time as trd

__author__ = 'myh '
__date__ = '2023/3/10 '


def run_with_args(run_fun: Callable[..., Any], *args: Any) -> None:
    """根据命令行参数执行任务函数

    这是一个通用的任务执行模板，根据命令行参数的数量自动选择执行模式：
    - 2 个参数：区间模式，遍历日期区间内的所有交易日
    - 1 个参数：枚举模式，处理逗号分隔的多个日期
    - 0 个参数：当前模式，处理最近的有效交易日

    Args:
        run_fun: 任务函数，第一个参数必须是日期（datetime.date 类型）
        *args: 传递给任务函数的额外参数

    Raises:
        异常会被捕获并记录到日志，不会向上抛出

    Example:
        定义任务函数并使用模板执行::

            def save_daily_data(date, extra_param):
                print(f"处理 {date} 的数据，参数：{extra_param}")

            if __name__ == '__main__':
                run_with_args(save_daily_data, "额外参数")

    Note:
        - 任务函数的命名约定影响日期选择：
          - 'save_nph' 开头：使用可能包含实时数据的日期
          - 'save_after_close' 开头：使用已收盘的日期
          - 其他：使用可能包含实时数据的日期
    """
    if len(sys.argv) == 3:
        # ============================================================
        # 区间模式：python xxx.py 2023-03-01 2023-03-21
        # ============================================================
        tmp_year, tmp_month, tmp_day = sys.argv[1].split("-")
        start_date = datetime.datetime(int(tmp_year), int(tmp_month), int(tmp_day)).date()
        tmp_year, tmp_month, tmp_day = sys.argv[2].split("-")
        end_date = datetime.datetime(int(tmp_year), int(tmp_month), int(tmp_day)).date()
        run_date = start_date

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                while run_date <= end_date:
                    # 只处理交易日
                    if trd.is_trade_date(run_date):
                        executor.submit(run_fun, run_date, *args)
                        # 间隔 2 秒提交，避免并发过高
                        time.sleep(2)
                    run_date += datetime.timedelta(days=1)
        except Exception as e:
            logging.error(f"run_template.run_with_args处理异常：{run_fun}{sys.argv}{e}")

    elif len(sys.argv) == 2:
        # ============================================================
        # 枚举模式：python xxx.py 2023-03-01,2023-03-02
        # ============================================================
        dates = sys.argv[1].split(',')

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for date in dates:
                    tmp_year, tmp_month, tmp_day = date.split("-")
                    run_date = datetime.datetime(int(tmp_year), int(tmp_month), int(tmp_day)).date()
                    # 只处理交易日
                    if trd.is_trade_date(run_date):
                        executor.submit(run_fun, run_date, *args)
                        time.sleep(2)
        except Exception as e:
            logging.error(f"run_template.run_with_args处理异常：{run_fun}{sys.argv}{e}")

    else:
        # ============================================================
        # 当前模式：python xxx.py
        # ============================================================
        try:
            # 获取最近的有效交易日
            run_date, run_date_nph = trd.get_trade_date_last()

            # 根据函数名选择合适的日期
            if run_fun.__name__.startswith('save_nph'):
                # 实时数据任务，使用可能包含当天数据的日期
                run_fun(run_date_nph, False)
            elif run_fun.__name__.startswith('save_after_close'):
                # 收盘后数据任务，使用已收盘的日期
                run_fun(run_date, *args)
            else:
                # 默认使用实时数据日期
                run_fun(run_date_nph, *args)
        except Exception as e:
            logging.error(f"run_template.run_with_args处理异常：{run_fun}{sys.argv}{e}")
