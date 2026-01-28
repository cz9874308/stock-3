#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日数据任务调度器

本模块是整个数据采集系统的主调度入口，负责按顺序执行各类数据采集和处理任务。
通常由 cron 定时任务在每个交易日收盘后触发执行。

执行流程
--------
1. **init_job**: 检查并初始化数据库
2. **basic_data_daily_job**: 采集股票/ETF 实时行情数据
3. **selection_data_daily_job**: 采集综合股票数据
4. **basic_data_other_daily_job**: 采集其他基础数据（并发执行）
5. **indicators_data_daily_job**: 计算技术指标数据（可选）
6. **klinepattern_data_daily_job**: 识别 K 线形态（可选）
7. **strategy_data_daily_job**: 执行策略选股（可选）
8. **backtest_data_daily_job**: 执行回测分析（可选）
9. **basic_data_after_close_daily_job**: 采集收盘后数据（如龙虎榜）

使用方式
--------
命令行直接运行::

    python execute_daily_job.py

定时任务配置示例（cron）::

    # 每个交易日 15:30 执行
    30 15 * * 1-5 cd /path/to/instock/job && python execute_daily_job.py

日志文件
--------
日志保存在 `instock/job/log/stock_execute_job.log`

注意事项
--------
- 建议在交易日收盘后执行，确保数据完整
- 首次运行会自动创建数据库和表结构
- 部分任务被注释掉，可根据需要启用
"""

import concurrent.futures
import datetime
import logging
import os.path
import sys
import time

# 在项目运行时，临时将项目路径添加到环境变量
cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)

# 配置日志
log_path = os.path.join(cpath_current, 'log')
if not os.path.exists(log_path):
    os.makedirs(log_path)
logging.basicConfig(
    format='%(asctime)s %(message)s',
    filename=os.path.join(log_path, 'stock_execute_job.log')
)
logging.getLogger().setLevel(logging.INFO)

# 导入各任务模块
import init_job as bj
import basic_data_daily_job as hdj
import basic_data_other_daily_job as hdtj
import basic_data_after_close_daily_job as acdj
import indicators_data_daily_job as gdj
import strategy_data_daily_job as sdj
import backtest_data_daily_job as bdj
import klinepattern_data_daily_job as kdj
import selection_data_daily_job as sddj

__author__ = 'myh '
__date__ = '2023/3/10 '


def main():
    start = time.time()
    _start = datetime.datetime.now()
    logging.info("######## 任务执行时间: %s #######" % _start.strftime("%Y-%m-%d %H:%M:%S.%f"))
    # 第1步创建数据库
    bj.main()
    # 第2.1步创建股票基础数据表
    hdj.main()
    # 第2.2步创建综合股票数据表
    sddj.main()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # # 第3.1步创建股票其它基础数据表
        executor.submit(hdtj.main)
        # # 第3.2步创建股票指标数据表
        # executor.submit(gdj.main)
        # # # # 第4步创建股票k线形态表
        # executor.submit(kdj.main)
        # # # # 第5步创建股票策略数据表
        # executor.submit(sdj.main)

    # # # # 第6步创建股票回测
    # bdj.main()

    # # # # 第7步创建股票闭盘后才有的数据
    acdj.main()

    logging.info("######## 完成任务, 使用时间: %s 秒 #######" % (time.time() - start))


# main函数入口
if __name__ == '__main__':
    main()
