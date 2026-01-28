#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志处理模块

本模块提供交易系统的日志处理功能，基于 logbook 库实现。

核心组件
--------
- **DefaultLogHandler**: 默认日志处理器，支持控制台和文件输出

日志级别
--------
从高到低：CRITICAL > ERROR > WARNING > NOTICE > INFO > DEBUG > TRACE > NOTSET

使用方式
--------
::

    from instock.trade.robot.infrastructure.default_handler import DefaultLogHandler

    # 输出到控制台
    log = DefaultLogHandler(name='MyLog', log_type='stdout')
    log.info('Hello, World!')

    # 输出到文件
    log = DefaultLogHandler(name='MyLog', log_type='file', filepath='app.log')
    log.error('Something went wrong!')

注意事项
--------
- 日志时间使用本地时区
- 文件日志会自动创建目录
"""

import os
import sys

import logbook
from logbook import FileHandler, Logger, StreamHandler

__author__ = 'myh '
__date__ = '2023/4/10 '

# 使用本地时区格式化日志时间
logbook.set_datetime_format('local')


class DefaultLogHandler(object):
    """默认的 Log 类"""

    def __init__(self, name='default', log_type='stdout', filepath='default.log', loglevel='DEBUG'):
        """Log对象
        :param name: log 名字
        :param :logtype: 'stdout' 输出到屏幕, 'file' 输出到指定文件
        :param :filename: log 文件名
        :param :loglevel: 设定log等级 ['CRITICAL', 'ERROR', 'WARNING', 'NOTICE', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
        :return log handler object
        """
        self.log = Logger(name)
        if log_type == 'stdout':
            StreamHandler(sys.stdout, level=loglevel).push_application()
        if log_type == 'file':
            if os.path.isdir(filepath) and not os.path.exists(filepath):
                os.makedirs(os.path.dirname(filepath))
            file_handler = FileHandler(filepath, level=loglevel)
            self.log.handlers.append(file_handler)

    def __getattr__(self, item, *args, **kwargs):
        return self.log.__getattribute__(item, *args, **kwargs)
