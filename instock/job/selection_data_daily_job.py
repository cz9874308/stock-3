#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
综合股票数据每日采集任务

本模块负责采集东方财富选股器的综合股票数据，包含多维度的基本面和技术面信息。

核心功能
--------
- **save_nph_stock_selection_data**: 采集并存储综合股票数据

数据内容
--------
从东方财富选股器获取的数据包括：
- 基本面指标：市盈率、市净率、ROE 等
- 技术面指标：涨跌幅、成交量、换手率等
- 资金面指标：主力资金流向等

数据表
------
- cn_stock_selection: 综合股票数据表

使用方式
--------
命令行运行::

    python selection_data_daily_job.py

注意事项
--------
- 在交易日收盘后执行
- 数据来源为东方财富选股器
"""

import logging
import os.path
import sys

import pandas as pd

cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)

import instock.core.stockfetch as stf
import instock.core.tablestructure as tbs
import instock.lib.database as mdb
import instock.lib.run_template as runt

__author__ = 'myh '
__date__ = '2023/5/5 '


def save_nph_stock_selection_data(date, before=True):
    if before:
        return

    try:
        data = stf.fetch_stock_selection()
        if data is None:
            return

        table_name = tbs.TABLE_CN_STOCK_SELECTION['name']
        # 删除老数据。
        if mdb.checkTableIsExist(table_name):
            _date = data.iloc[0]['date']
            del_sql = f"DELETE FROM `{table_name}` where `date` = '{_date}'"
            mdb.executeSql(del_sql)
            cols_type = None
        else:
            cols_type = tbs.get_field_types(tbs.TABLE_CN_STOCK_SELECTION['columns'])

        mdb.insert_db_from_df(data, table_name, cols_type, False, "`date`,`code`")
    except Exception as e:
        logging.error(f"selection_data_daily_job.save_nph_stock_selection_data处理异常：{e}")


def main():
    runt.run_with_args(save_nph_stock_selection_data)


# main函数入口
if __name__ == '__main__':
    main()
