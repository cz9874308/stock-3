#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
东方财富网数据获取器模块

本模块提供与东方财富网 API 交互的 HTTP 客户端，封装了 Cookie 管理、
会话管理、代理支持和请求重试功能。

核心概念
--------
- **会话管理**: 使用 requests.Session 保持连接和 Cookie
- **Cookie 来源**: 优先级为 环境变量 > 配置文件 > 默认值
- **代理支持**: 自动使用 singleton_proxy 提供的代理
- **重试机制**: 请求失败时自动重试

Cookie 配置方式
---------------
1. 环境变量::

    export EAST_MONEY_COOKIE="your_cookie_here"

2. 配置文件::

    # 创建 instock/config/eastmoney_cookie.txt
    # 写入 Cookie 内容

使用方式
--------
发送请求::

    from instock.core.eastmoney_fetcher import eastmoney_fetcher

    fetcher = eastmoney_fetcher()
    response = fetcher.make_request(
        url="http://push2.eastmoney.com/api/qt/clist/get",
        params={"pn": 1, "pz": 50}
    )
    data = response.json()

更新 Cookie::

    fetcher.update_cookie("new_cookie_value")

注意事项
--------
- Cookie 可能会过期，建议定期从浏览器获取新的 Cookie
- 请求频率过高可能导致 IP 被封，建议配合代理使用
"""

import os
import random
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from instock.core.singleton_proxy import proxys

__author__ = 'myh '
__date__ = '2025/12/31 '


class eastmoney_fetcher:
    """东方财富网数据获取器

    封装了与东方财富网 API 交互的 HTTP 客户端功能，包括：
    - Cookie 管理（支持多种来源）
    - 会话保持（使用 requests.Session）
    - 代理支持（自动使用配置的代理）
    - 请求重试（网络错误时自动重试）

    Attributes:
        base_dir: 项目基础目录
        session: requests.Session 对象

    Example:
        >>> fetcher = eastmoney_fetcher()
        >>> response = fetcher.make_request(url, params)
        >>> data = response.json()
    """

    def __init__(self):
        """初始化获取器，创建会话并配置 Cookie"""
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.session = self._create_session()

    def _get_cookie(self) -> str:
        """获取东方财富网的 Cookie

        按以下优先级获取 Cookie：
        1. 环境变量 EAST_MONEY_COOKIE
        2. 配置文件 config/eastmoney_cookie.txt
        3. 默认 Cookie（可能已过期）

        Returns:
            Cookie 字符串
        """
        # 1. 尝试从环境变量获取
        cookie = os.environ.get('EAST_MONEY_COOKIE')
        if cookie:
            return cookie

        # 2. 尝试从配置文件获取
        cookie_file = Path(os.path.join(self.base_dir, 'config', 'eastmoney_cookie.txt'))
        if cookie_file.exists():
            with open(cookie_file, 'r') as f:
                cookie = f.read().strip()
            if cookie:
                return cookie

        # 3. 默认 Cookie（仅作为备选，可能已过期）
        return 'fullscreengg=1; fullscreengg2=1; qgqp_b_id=76670de7aee4283d73f88b9c543a53f0; st_si=52987000764549; st_sn=1; st_psi=20251231162316664-113200301321-0046286479; st_asi=delete; st_pvi=43436093393372; st_sp=2025-12-31%2016%3A23%3A16; st_inirUrl='

    def _create_session(self) -> requests.Session:
        """创建并配置 HTTP 会话

        设置通用请求头和 Cookie，模拟浏览器行为。

        Returns:
            配置好的 requests.Session 对象
        """
        session = requests.Session()

        # 设置请求头，模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://quote.eastmoney.com/',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        session.headers.update(headers)

        # 设置 Cookie
        session.cookies.update({'Cookie': self._get_cookie()})
        return session

    def make_request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        retry: int = 1,
        timeout: int = 10
    ) -> requests.Response:
        """发送 HTTP GET 请求

        支持自动重试、代理和超时配置。

        Args:
            url: 请求 URL
            params: URL 查询参数字典
            retry: 失败时的重试次数，默认 1 次
            timeout: 请求超时时间（秒），默认 10 秒

        Returns:
            requests.Response 对象

        Raises:
            requests.exceptions.RequestException: 所有重试都失败时抛出

        Example:
            >>> response = fetcher.make_request(
            ...     "http://api.example.com/data",
            ...     params={"page": 1},
            ...     retry=3
            ... )
        """
        for i in range(retry):
            try:
                response = self.session.get(
                    url,
                    proxies=proxys().get_proxies(),
                    params=params,
                    timeout=timeout
                )
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                print(f"请求错误: {e}, 第 {i + 1}/{retry} 次重试")
                if i < retry - 1:
                    # 随机延迟后重试，避免立即重试
                    time.sleep(random.uniform(1, 3))
                else:
                    raise

    def update_cookie(self, new_cookie: str) -> None:
        """更新会话的 Cookie

        用于在运行时更新 Cookie，例如 Cookie 过期后手动更新。

        Args:
            new_cookie: 新的 Cookie 字符串
        """
        self.session.cookies.update({'Cookie': new_cookie})