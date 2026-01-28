# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
东方财富选股器数据抓取模块

本模块提供从东方财富网选股器获取股票多维度数据的功能，可获取股票的
基本面、技术面、资金面等综合指标数据。

数据来源
--------
- 东方财富网选股器: https://data.eastmoney.com/xuangu/
- API 接口: https://data.eastmoney.com/dataapi/xuangu/list

核心功能
--------
- **stock_selection**: 获取选股器全量股票数据（包含 100+ 个指标字段）
- **stock_selection_params**: 获取选股器可用的指标参数列表

数据字段
--------
包含但不限于：股票代码、名称、最新价、涨跌幅、市盈率、市净率、
ROE、营收增长率、净利润增长率、概念板块、风格板块等。

使用方式
--------
获取选股器数据::

    from instock.core.crawling.stock_selection import stock_selection
    df = stock_selection()
    print(df.columns.tolist())  # 查看所有可用字段

注意事项
--------
- 选股器数据量较大，首次获取可能需要较长时间
- 数据字段定义来自 tablestructure.TABLE_CN_STOCK_SELECTION
"""

import math
import random
import time

import pandas as pd

import instock.core.tablestructure as tbs
from instock.core.eastmoney_fetcher import eastmoney_fetcher

__author__ = 'myh '
__date__ = '2025/12/31 '

# 创建全局 HTTP 请求实例
fetcher = eastmoney_fetcher()

def stock_selection() -> pd.DataFrame:
    """
    东方财富网-个股-选股器
    https://data.eastmoney.com/xuangu/
    :return: 选股器
    :rtype: pandas.DataFrame
    """
    cols = tbs.TABLE_CN_STOCK_SELECTION['columns']
    page_size = 50
    page_current = 1
    sty = ""  # 初始值 "SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,CHANGE_RATE"
    for k in cols:
        sty = f"{sty},{cols[k]['map']}"
    url = "https://data.eastmoney.com/dataapi/xuangu/list"
    params = {
        "sty": sty[1:],
        "filter": "(MARKET+in+(\"上交所主板\",\"深交所主板\",\"深交所创业板\"))(NEW_PRICE>0)",
        "p": page_current,
        "ps": page_size,
        "source": "SELECT_SECURITIES",
        "client": "WEB"
    }

    r = fetcher.make_request(url, params=params)
    data_json = r.json()
    data = data_json["result"]["data"]
    if not data:
        return pd.DataFrame()

    data_count = data_json["result"]["count"]
    page_count = math.ceil(data_count/page_size)
    while page_count > 1:
        # 添加随机延迟，避免爬取过快
        time.sleep(random.uniform(1, 1.5))
        page_current = page_current + 1
        params["p"] = page_current
        r = fetcher.make_request(url, params=params)
        data_json = r.json()
        _data = data_json["result"]["data"]
        data.extend(_data)
        page_count =page_count - 1

    temp_df = pd.DataFrame(data)

    mask = ~temp_df['CONCEPT'].isna()
    temp_df.loc[mask, 'CONCEPT'] = temp_df.loc[mask, 'CONCEPT'].apply(lambda x: ', '.join(x))
    mask = ~temp_df['STYLE'].isna()
    temp_df.loc[mask, 'STYLE'] = temp_df.loc[mask, 'STYLE'].apply(lambda x: ', '.join(x))

    for k in cols:
        t = tbs.get_field_type_name(cols[k]["type"])
        if t == 'numeric':
            temp_df[cols[k]["map"]] = pd.to_numeric(temp_df[cols[k]["map"]], errors="coerce")
        elif t == 'datetime':
            temp_df[cols[k]["map"]] = pd.to_datetime(temp_df[cols[k]["map"]], errors="coerce").dt.date

    return temp_df


def stock_selection_params():
    """
    东方财富网-个股-选股器-选股指标
    https://data.eastmoney.com/xuangu/
    :return: 选股器-选股指标
    :rtype: pandas.DataFrame
    """
    url = "https://datacenter-web.eastmoney.com/wstock/selection/api/data/get"
    params = {
        "type": "RPTA_PCNEW_WHOLE",
        "sty": "ALL",
        "p": 1,
        "ps": 1000,
        "source": "SELECT_SECURITIES",
        "client": "WEB"
    }

    r = fetcher.make_request(url, params=params)
    data_json = r.json()
    zxzb = data_json["result"]["data"]  # 指标
    print(zxzb)


if __name__ == "__main__":
    stock_selection_df = stock_selection()
    print(stock_selection)
    # stock_selection_params()