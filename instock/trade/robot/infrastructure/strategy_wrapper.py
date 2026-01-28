#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略进程包装器模块

本模块提供将策略运行在独立进程中的包装器，用于隔离策略运行环境。

核心组件
--------
- **ProcessWrapper**: 进程包装器，将策略包装在独立进程中运行

设计目的
--------
1. 隔离策略运行环境，避免策略崩溃影响主引擎
2. 支持策略的独立重启
3. 通过队列进行跨进程通信

使用方式
--------
::

    from instock.trade.robot.infrastructure.strategy_wrapper import ProcessWrapper

    wrapper = ProcessWrapper(strategy)
    wrapper.on_clock(event)  # 推送时钟事件
    wrapper.stop()  # 停止策略进程

注意事项
--------
- 跨进程通信使用 multiprocessing.Queue
- 策略进程接收退出信号后会优雅关闭
"""

import multiprocessing as mp
from threading import Thread

__author__ = 'myh '
__date__ = '2023/4/10 '


class ProcessWrapper(object):
    def __init__(self, strategy):
        self.__strategy = strategy
        # 时钟队列
        self.__clock_queue = mp.Queue(10000)
        # 包装进程
        self.__proc = mp.Process(target=self._process)
        self.__proc.start()

    def stop(self):
        self.__clock_queue.put(0)
        self.__proc.join()

    def on_clock(self, event):
        self.__clock_queue.put(event)

    def _process_clock(self):
        while True:

            try:
                event = self.__clock_queue.get(block=True)
                # 退出
                if event == 0:
                    break
                self.__strategy.clock(event)
            except:
                pass

    def _process(self):
        clock_thread = Thread(target=self._process_clock, name="ProcessWrapper._process_clock")
        clock_thread.start()

        clock_thread.join()
