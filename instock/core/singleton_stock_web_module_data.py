#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
Web 模块数据配置单例模块

本模块提供 Web 界面所需的模块配置数据的单例管理，定义了系统中所有可查询的
数据表模块及其展示配置。

核心概念
--------
- **模块配置**: 每个数据表在 Web 界面中的展示配置（名称、图标、列定义等）
- **单例模式**: 模块配置在系统启动时初始化一次
- **分类组织**: 模块按功能分类（综合选股、基本数据、指标数据、策略数据等）

配置项说明
----------
每个模块配置包含：
- mode: 模式（query 查询 / editor 编辑）
- type: 分类类型（用于菜单分组）
- ico: Font Awesome 图标类名
- name: 显示名称（中文）
- table_name: 数据库表名
- columns: 列字段列表
- column_names: 列中文名称列表
- is_realtime: 是否实时数据
- order_by: 默认排序

使用方式
--------
获取模块配置::

    from instock.core.singleton_stock_web_module_data import stock_web_module_data

    # 获取所有模块列表
    modules = stock_web_module_data().get_data_list()

    # 获取指定表的模块配置
    config = stock_web_module_data().get_data('cn_stock_spot')
"""

import instock.core.tablestructure as tbs
import instock.core.web_module_data as wmd
from instock.lib.singleton_type import singleton_type

__author__ = 'myh '
__date__ = '2023/3/10 '


class stock_web_module_data(metaclass=singleton_type):
    def __init__(self):
        _data = {}
        self.data_list = [wmd.web_module_data(
            mode="query",
            type="综合选股",
            ico="fa fa-desktop",
            name=tbs.TABLE_CN_STOCK_SELECTION['cn'],
            table_name=tbs.TABLE_CN_STOCK_SELECTION['name'],
            columns=tuple(tbs.TABLE_CN_STOCK_SELECTION['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_STOCK_SELECTION['columns']),
            primary_key=[],
            is_realtime=False,
            order_columns=f"(SELECT `datetime` FROM `{tbs.TABLE_CN_STOCK_ATTENTION['name']}` WHERE `code`=`{tbs.TABLE_CN_STOCK_SELECTION['name']}`.`code`) AS `cdatetime`",
            order_by=" `cdatetime` DESC"
        ), wmd.web_module_data(
            mode="query",
            type="股票基本数据",
            ico="fa fa-book",
            name=tbs.TABLE_CN_STOCK_SPOT['cn'],
            table_name=tbs.TABLE_CN_STOCK_SPOT['name'],
            columns=tuple(tbs.TABLE_CN_STOCK_SPOT['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_STOCK_SPOT['columns']),
            primary_key=[],
            is_realtime=True,
            order_columns=f"(SELECT `datetime` FROM `{tbs.TABLE_CN_STOCK_ATTENTION['name']}` WHERE `code`=`{tbs.TABLE_CN_STOCK_SPOT['name']}`.`code`) AS `cdatetime`",
            order_by=" `cdatetime` DESC"
        ), wmd.web_module_data(
            mode="query",
            type="股票基本数据",
            ico="fa fa-book",
            name=tbs.TABLE_CN_STOCK_CHIP_RACE_OPEN['cn'],
            table_name=tbs.TABLE_CN_STOCK_CHIP_RACE_OPEN['name'],
            columns=tuple(tbs.TABLE_CN_STOCK_CHIP_RACE_OPEN['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_STOCK_CHIP_RACE_OPEN['columns']),
            primary_key=[],
            is_realtime=True,
            order_columns=f"(SELECT `datetime` FROM `{tbs.TABLE_CN_STOCK_ATTENTION['name']}` WHERE `code`=`{tbs.TABLE_CN_STOCK_CHIP_RACE_OPEN['name']}`.`code`) AS `cdatetime`",
            order_by=" `bid_trust_amount` DESC"
        ), wmd.web_module_data(
            mode="query",
            type="股票基本数据",
            ico="fa fa-book",
            name=tbs.TABLE_CN_STOCK_CHIP_RACE_END['cn'],
            table_name=tbs.TABLE_CN_STOCK_CHIP_RACE_END['name'],
            columns=tuple(tbs.TABLE_CN_STOCK_CHIP_RACE_END['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_STOCK_CHIP_RACE_END['columns']),
            primary_key=[],
            is_realtime=False,
            order_columns=f"(SELECT `datetime` FROM `{tbs.TABLE_CN_STOCK_ATTENTION['name']}` WHERE `code`=`{tbs.TABLE_CN_STOCK_CHIP_RACE_END['name']}`.`code`) AS `cdatetime`",
            order_by=" `bid_trust_amount` DESC"
        ), wmd.web_module_data(
            mode="query",
            type="股票基本数据",
            ico="fa fa-book",
            name=tbs.TABLE_CN_STOCK_LIMITUP_REASON['cn'],
            table_name=tbs.TABLE_CN_STOCK_LIMITUP_REASON['name'],
            columns=tuple(tbs.TABLE_CN_STOCK_LIMITUP_REASON['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_STOCK_LIMITUP_REASON['columns']),
            primary_key=[],
            is_realtime=True,
            order_columns=f"(SELECT `datetime` FROM `{tbs.TABLE_CN_STOCK_ATTENTION['name']}` WHERE `code`=`{tbs.TABLE_CN_STOCK_LIMITUP_REASON['name']}`.`code`) AS `cdatetime`",
            order_by=" `cdatetime` DESC"
        ), wmd.web_module_data(
            mode="query",
            type="股票基本数据",
            ico="fa fa-book",
            name=tbs.TABLE_CN_STOCK_FUND_FLOW['cn'],
            table_name=tbs.TABLE_CN_STOCK_FUND_FLOW['name'],
            columns=tuple(tbs.TABLE_CN_STOCK_FUND_FLOW['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_STOCK_FUND_FLOW['columns']),
            primary_key=[],
            is_realtime=True,
            order_columns=f"(SELECT `datetime` FROM `{tbs.TABLE_CN_STOCK_ATTENTION['name']}` WHERE `code`=`{tbs.TABLE_CN_STOCK_FUND_FLOW['name']}`.`code`) AS `cdatetime`",
            order_by=" `cdatetime` DESC"
        ), wmd.web_module_data(
            mode="query",
            type="股票基本数据",
            ico="fa fa-book",
            name=tbs.TABLE_CN_STOCK_BONUS['cn'],
            table_name=tbs.TABLE_CN_STOCK_BONUS['name'],
            columns=tuple(tbs.TABLE_CN_STOCK_BONUS['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_STOCK_BONUS['columns']),
            primary_key=[],
            is_realtime=True,
            order_columns=f"(SELECT `datetime` FROM `{tbs.TABLE_CN_STOCK_ATTENTION['name']}` WHERE `code`=`{tbs.TABLE_CN_STOCK_BONUS['name']}`.`code`) AS `cdatetime`",
            order_by=" `cdatetime` DESC"
        ), wmd.web_module_data(
            mode="query",
            type="股票基本数据",
            ico="fa fa-book",
            name=tbs.TABLE_CN_STOCK_lHB['cn'],
            table_name=tbs.TABLE_CN_STOCK_lHB['name'],
            columns=tuple(tbs.TABLE_CN_STOCK_lHB['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_STOCK_lHB['columns']),
            primary_key=[],
            is_realtime=True,
            order_columns=f"(SELECT `datetime` FROM `{tbs.TABLE_CN_STOCK_ATTENTION['name']}` WHERE `code`=`{tbs.TABLE_CN_STOCK_lHB['name']}`.`code`) AS `cdatetime`",
            order_by=" `cdatetime`,`ranking_times` DESC"
        ), wmd.web_module_data(
            mode="query",
            type="股票基本数据",
            ico="fa fa-book",
            name=tbs.TABLE_CN_STOCK_BLOCKTRADE['cn'],
            table_name=tbs.TABLE_CN_STOCK_BLOCKTRADE['name'],
            columns=tuple(tbs.TABLE_CN_STOCK_BLOCKTRADE['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_STOCK_BLOCKTRADE['columns']),
            primary_key=[],
            is_realtime=False,
            order_columns=f"(SELECT `datetime` FROM `{tbs.TABLE_CN_STOCK_ATTENTION['name']}` WHERE `code`=`{tbs.TABLE_CN_STOCK_BLOCKTRADE['name']}`.`code`) AS `cdatetime`",
            order_by=" `cdatetime` DESC"
        ), wmd.web_module_data(
            mode="query",
            type="股票基本数据",
            ico="fa fa-book",
            name=tbs.TABLE_CN_STOCK_FUND_FLOW_INDUSTRY['cn'],
            table_name=tbs.TABLE_CN_STOCK_FUND_FLOW_INDUSTRY['name'],
            columns=tuple(tbs.TABLE_CN_STOCK_FUND_FLOW_INDUSTRY['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_STOCK_FUND_FLOW_INDUSTRY['columns']),
            primary_key=[],
            is_realtime=True,
            order_by=" `fund_amount` DESC"
        ), wmd.web_module_data(
            mode="query",
            type="股票基本数据",
            ico="fa fa-book",
            name=tbs.TABLE_CN_STOCK_FUND_FLOW_CONCEPT['cn'],
            table_name=tbs.TABLE_CN_STOCK_FUND_FLOW_CONCEPT['name'],
            columns=tuple(tbs.TABLE_CN_STOCK_FUND_FLOW_CONCEPT['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_STOCK_FUND_FLOW_CONCEPT['columns']),
            primary_key=[],
            is_realtime=True,
            order_by=" `fund_amount` DESC"
        ), wmd.web_module_data(
            mode="query",
            type="股票基本数据",
            ico="fa fa-book",
            name=tbs.TABLE_CN_ETF_SPOT['cn'],
            table_name=tbs.TABLE_CN_ETF_SPOT['name'],
            columns=tuple(tbs.TABLE_CN_ETF_SPOT['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_ETF_SPOT['columns']),
            primary_key=[],
            is_realtime=True
        ), wmd.web_module_data(
            mode="query",
            type="股票指标数据",
            ico="fa fa-indent",
            name=tbs.TABLE_CN_STOCK_INDICATORS['cn'],
            table_name=tbs.TABLE_CN_STOCK_INDICATORS['name'],
            columns=tuple(tbs.TABLE_CN_STOCK_INDICATORS['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_STOCK_INDICATORS['columns']),
            primary_key=[],
            is_realtime=False,
            order_columns=f"(SELECT `datetime` FROM `{tbs.TABLE_CN_STOCK_ATTENTION['name']}` WHERE `code`=`{tbs.TABLE_CN_STOCK_INDICATORS['name']}`.`code`) AS `cdatetime`",
            order_by=" `cdatetime` DESC"
        ), wmd.web_module_data(
            mode="query",
            type="股票指标数据",
            ico="fa fa-indent",
            name=tbs.TABLE_CN_STOCK_INDICATORS_BUY['cn'],
            table_name=tbs.TABLE_CN_STOCK_INDICATORS_BUY['name'],
            columns=tuple(tbs.TABLE_CN_STOCK_INDICATORS_BUY['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_STOCK_INDICATORS_BUY['columns']),
            primary_key=[],
            is_realtime=False,
            order_columns=f"(SELECT `datetime` FROM `{tbs.TABLE_CN_STOCK_ATTENTION['name']}` WHERE `code`=`{tbs.TABLE_CN_STOCK_INDICATORS_BUY['name']}`.`code`) AS `cdatetime`",
            order_by=" `cdatetime` DESC"
        ), wmd.web_module_data(
            mode="query",
            type="股票指标数据",
            ico="fa fa-indent",
            name=tbs.TABLE_CN_STOCK_INDICATORS_SELL['cn'],
            table_name=tbs.TABLE_CN_STOCK_INDICATORS_SELL['name'],
            columns=tuple(tbs.TABLE_CN_STOCK_INDICATORS_SELL['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_STOCK_INDICATORS_SELL['columns']),
            primary_key=[],
            is_realtime=False,
            order_columns=f"(SELECT `datetime` FROM `{tbs.TABLE_CN_STOCK_ATTENTION['name']}` WHERE `code`=`{tbs.TABLE_CN_STOCK_INDICATORS_SELL['name']}`.`code`) AS `cdatetime`",
            order_by=" `cdatetime` DESC"
        ), wmd.web_module_data(
            mode="query",
            type="股票K线形态",
            ico="fa fa-tag",
            name=tbs.TABLE_CN_STOCK_KLINE_PATTERN['cn'],
            table_name=tbs.TABLE_CN_STOCK_KLINE_PATTERN['name'],
            columns=tuple(tbs.TABLE_CN_STOCK_KLINE_PATTERN['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_STOCK_KLINE_PATTERN['columns']),
            primary_key=[],
            is_realtime=False,
            order_columns=f"(SELECT `datetime` FROM `{tbs.TABLE_CN_STOCK_ATTENTION['name']}` WHERE `code`=`{tbs.TABLE_CN_STOCK_KLINE_PATTERN['name']}`.`code`) AS `cdatetime`",
            order_by=" `cdatetime` DESC"
        ), wmd.web_module_data(
            mode="query",
            type="股票策略数据",
            ico="fa fa-check-square-o",
            name=tbs.TABLE_CN_STOCK_SPOT_BUY['cn'],
            table_name=tbs.TABLE_CN_STOCK_SPOT_BUY['name'],
            columns=tuple(tbs.TABLE_CN_STOCK_SPOT_BUY['columns']),
            column_names=tbs.get_field_cns(tbs.TABLE_CN_STOCK_SPOT_BUY['columns']),
            primary_key=[],
            is_realtime=False,
            order_columns=f"(SELECT `datetime` FROM `{tbs.TABLE_CN_STOCK_ATTENTION['name']}` WHERE `code`=`{tbs.TABLE_CN_STOCK_SPOT_BUY['name']}`.`code`) AS `cdatetime`",
            order_by=" `cdatetime` DESC"
        )]

        for table in tbs.TABLE_CN_STOCK_STRATEGIES:
            self.data_list.append(
                wmd.web_module_data(
                    mode="query",
                    type="股票策略数据",
                    ico="fa fa-check-square-o",
                    name=table['cn'],
                    table_name=table['name'],
                    columns=tuple(table['columns']),
                    column_names=tbs.get_field_cns(table['columns']),
                    primary_key=[],
                    is_realtime=False,
                    order_columns=f"(SELECT `datetime` FROM `{tbs.TABLE_CN_STOCK_ATTENTION['name']}` WHERE `code`=`{table['name']}`.`code`) AS `cdatetime`",
                    order_by=" `cdatetime` DESC"
                )
            )
        for tmp in self.data_list:
            _data[tmp.table_name] = tmp
        self.data = _data

    def get_data_list(self):
        return self.data_list

    def get_data(self, name):
        return self.data[name]
