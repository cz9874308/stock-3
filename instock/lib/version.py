#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InStock 版本信息模块

本模块定义了 InStock 系统的版本号，用于版本追踪和兼容性检查。

使用方式
--------
导入版本号::

    from instock.lib.version import __version__
    print(f"当前版本: {__version__}")

版本号规则
----------
采用语义化版本号（Semantic Versioning）格式：主版本号.次版本号.修订号

- **主版本号**: 不兼容的 API 修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正
"""

__author__ = 'myh '
__date__ = '2023/3/11 '

# InStock 系统版本号，每次发布时更新
__version__ = "4.0.0"
