#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
通达信竞价抢筹数据抓取模块

本模块提供从通达信获取集合竞价阶段抢筹数据的功能，用于分析早盘和尾盘
的主力资金抢筹行为。

数据来源
--------
- 通达信抢筹数据接口: http://excalc.icfqs.com:7616/TQLEX?Entry=HQServ.hq_nlp

核心功能
--------
- **stock_chip_race_open**: 获取早盘竞价抢筹数据
- **stock_chip_race_close**: 获取尾盘竞价抢筹数据

竞价抢筹说明
------------
- **早盘抢筹**: 9:15-9:25 集合竞价阶段的委托和成交情况
- **尾盘抢筹**: 14:57-15:00 收盘集合竞价阶段的情况
- **抢筹幅度**: 开盘价相对昨收的涨幅
- **抢筹委托金额**: 集合竞价阶段的委托金额
- **抢筹成交金额**: 集合竞价阶段的成交金额
- **抢筹占比**: 抢筹成交金额占委托金额的比例

使用方式
--------
获取早盘抢筹数据::

    from instock.core.crawling.stock_chip_race import stock_chip_race_open
    df = stock_chip_race_open()  # 获取当日数据
    df = stock_chip_race_open(date="2025-02-26")  # 获取指定日期数据
    print(df.head())

注意事项
--------
- 早盘数据在 9:25 后更新
- 尾盘数据在 15:00 后更新
- 接口可能需要特定的请求头
"""

import pandas as pd
import requests

from instock.core.singleton_proxy import proxys

__author__ = 'myh '
__date__ = '2025/2/26 '

def stock_chip_race_open(date: str = "") -> pd.DataFrame:
    """
    通达信竞价抢筹_早盘抢筹
    http://excalc.icfqs.com:7616/TQLEX?Entry=HQServ.hq_nlp
    :return: 早盘抢筹
    :rtype: pandas.DataFrame
    """
    url = "http://excalc.icfqs.com:7616/TQLEX?Entry=HQServ.hq_nlp"
    #sort:1抢筹委托金额, 2抢筹成交金额, 3开盘金额, 4抢筹幅度, 5抢筹占比
    if date=="":
        params = [{"funcId": 20, "offset": 0, "count": 100, "sort": 1, "period": 0,
                   "Token": "6679f5cadca97d68245a086793fc1bfc0a50b487487c812f", "modname": "JJQC"}]
    else:
        params = [{"funcId": 20, "offset": 0, "count": 100, "sort": 1, "period": 0,
                   "Token": "6679f5cadca97d68245a086793fc1bfc0a50b487487c812f", "modname": "JJQC", "date": date}]
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 TdxW",
    }

    r = requests.post(url, proxies = proxys().get_proxies(), json=params,headers=headers)
    data_json = r.json()
    data = data_json["datas"]
    if not data:
        return pd.DataFrame()
    temp_df = pd.DataFrame(data)
    temp_df.columns = [
        "代码",
        "名称",
        "昨收",
        "今开",
        "开盘金额",
        "抢筹幅度",
        "抢筹委托金额",
        "抢筹成交金额",
        "最新价",
        "_",
        "天",
        "板",
    ]

    temp_df["昨收"] = temp_df["昨收"]/10000
    temp_df["今开"] = temp_df["今开"] / 10000
    temp_df["抢筹幅度"] = round(temp_df["抢筹幅度"] * 100, 2)
    temp_df["最新价"] = round(temp_df["最新价"], 2)
    temp_df["涨跌幅"] = round((temp_df["最新价"] / temp_df["昨收"]-1) * 100, 2)
    temp_df["抢筹占比"] = round((temp_df["抢筹成交金额"] / temp_df["开盘金额"]) * 100, 2)

    temp_df = temp_df[
        [
            "代码",
            "名称",
            "最新价",
            "涨跌幅",
            "昨收",
            "今开",
            "开盘金额",
            "抢筹幅度",
            "抢筹委托金额",
            "抢筹成交金额",
            "抢筹占比",
            "天",
            "板",
        ]
    ]

    return temp_df

def stock_chip_race_end(date: str = "") -> pd.DataFrame:
    """
    通达信竞价抢筹_尾盘抢筹
    http://excalc.icfqs.com:7616/TQLEX?Entry=HQServ.hq_nlp
    :return: 尾盘抢筹
    :rtype: pandas.DataFrame
    """
    url = "http://excalc.icfqs.com:7616/TQLEX?Entry=HQServ.hq_nlp"
    #sort:1抢筹委托金额, 2抢筹成交金额, 3开盘金额, 4抢筹幅度, 5抢筹占比
    if date=="":
        params = [{"funcId": 20, "offset": 0, "count": 100, "sort": 1, "period": 1,
                   "Token": "6679f5cadca97d68245a086793fc1bfc0a50b487487c812f", "modname": "JJQC"}]
    else:
        params = [{"funcId": 20, "offset": 0, "count": 100, "sort": 1, "period": 1,
                   "Token": "6679f5cadca97d68245a086793fc1bfc0a50b487487c812f", "modname": "JJQC", "date": date}]
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "TdxW",
    }

    r = requests.post(url, proxies = proxys().get_proxies(), json=params,headers=headers)
    data_json = r.json()
    data = data_json["datas"]
    if not data:
        return pd.DataFrame()
    temp_df = pd.DataFrame(data)
    temp_df.columns = [
        "代码",
        "名称",
        "昨收",
        "今开",
        "收盘金额",
        "抢筹幅度",
        "抢筹委托金额",
        "抢筹成交金额",
        "最新价",
        "_",
        "天",
        "板",
    ]

    temp_df["昨收"] = temp_df["昨收"]/10000
    temp_df["今开"] = temp_df["今开"] / 10000
    temp_df["抢筹幅度"] = round(temp_df["抢筹幅度"] * 100, 2)
    temp_df["最新价"] = round(temp_df["最新价"], 2)
    temp_df["涨跌幅"] = round((temp_df["最新价"] / temp_df["昨收"]-1) * 100, 2)
    temp_df["抢筹占比"] = round((temp_df["抢筹成交金额"] / temp_df["收盘金额"]) * 100, 2)

    temp_df = temp_df[
        [
            "代码",
            "名称",
            "最新价",
            "涨跌幅",
            "昨收",
            "今开",
            "收盘金额",
            "抢筹幅度",
            "抢筹委托金额",
            "抢筹成交金额",
            "抢筹占比",
            "天",
            "板",
        ]
    ]

    return temp_df

if __name__ == "__main__":
    fund_chip_race_open_df = stock_chip_race_open()
    print(fund_chip_race_open_df)

    fund_chip_race_end_df = stock_chip_race_end()
    print(fund_chip_race_end_df)
