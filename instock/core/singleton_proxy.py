#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理服务器单例管理模块

本模块提供 HTTP 代理服务器的单例管理功能，用于网络请求时使用代理，
避免 IP 被数据源封禁。

核心概念
--------
- **代理池**: 从配置文件加载的代理服务器列表
- **随机选择**: 每次请求随机选择一个代理，分散请求负载
- **单例模式**: 代理列表在应用启动时加载一次

配置文件
--------
代理配置文件位于: instock/config/proxy.txt
每行一个代理地址，格式如: http://ip:port 或 socks5://ip:port

使用方式
--------
获取代理用于 requests::

    from instock.core.singleton_proxy import proxys
    import requests

    proxy = proxys().get_proxies()
    if proxy:
        response = requests.get(url, proxies=proxy)
    else:
        response = requests.get(url)

注意事项
--------
- 如果代理配置文件不存在或为空，get_proxies() 返回 None
- 建议使用可靠的代理服务，避免请求失败
"""

import os.path
import random
import sys
from typing import Dict, List, Optional

from instock.lib.singleton_type import singleton_type

# 设置项目路径
cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)

# 代理配置文件路径
proxy_filename = os.path.join(cpath_current, 'config', 'proxy.txt')

__author__ = 'myh '
__date__ = '2025/1/6 '


class proxys(metaclass=singleton_type):
    """HTTP 代理服务器管理单例

    从配置文件加载代理列表，提供随机代理选择功能。

    Attributes:
        data: List[str]，代理服务器地址列表

    Example:
        >>> proxy = proxys().get_proxies()
        >>> if proxy:
        ...     requests.get(url, proxies=proxy)
    """

    def __init__(self):
        """初始化并从配置文件加载代理列表"""
        self.data = None
        try:
            with open(proxy_filename, "r") as file:
                # 读取非空行并去重
                self.data = list(set(
                    line.strip() for line in file.readlines() if line.strip()
                ))
        except Exception:
            pass

    def get_data(self) -> Optional[List[str]]:
        """获取代理列表

        Returns:
            代理地址列表，如果未配置则为 None
        """
        return self.data

    def get_proxies(self) -> Optional[Dict[str, str]]:
        """随机获取一个代理配置

        从代理池中随机选择一个代理，返回 requests 库可用的代理字典。

        Returns:
            代理配置字典 {'http': proxy, 'https': proxy}，
            如果没有可用代理则返回 None
        """
        if self.data is None or len(self.data) == 0:
            return None

        proxy = random.choice(self.data)
        return {"http": proxy, "https": proxy}

"""
    def get_proxies(self):
        if self.data is None:
            return None

        while len(self.data) > 0:
            proxy = random.choice(self.data)
            if https_validator(proxy):
                return {"http": proxy, "https": proxy}
            self.data.remove(proxy)

        return None


from requests import head
def https_validator(proxy):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
               'Accept': '*/*',
               'Connection': 'keep-alive',
               'Accept-Language': 'zh-CN,zh;q=0.8'}
    proxies = {"http": f"{proxy}", "https": f"{proxy}"}
    try:
        r = head("https://data.eastmoney.com", headers=headers, proxies=proxies, timeout=3, verify=False)
        return True if r.status_code == 200 else False
    except Exception as e:
        return False
"""