#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
线程安全的单例模式元类模块

本模块提供了一个线程安全的单例模式实现，通过元类（metaclass）机制确保
任何使用该元类的类在整个应用程序生命周期内只有一个实例。

核心概念
--------
- **单例模式**: 一种设计模式，确保一个类只有一个实例，并提供全局访问点
- **元类**: Python 中用于创建类的"类"，可以控制类的创建和实例化行为
- **线程安全**: 使用可重入锁（RLock）保证多线程环境下的安全性

使用方式
--------
1. 定义类时指定 metaclass 为 singleton_type
2. 之后每次实例化该类都会返回同一个实例

示例::

    class MyClass(metaclass=singleton_type):
        def __init__(self, value):
            self.value = value

    obj1 = MyClass(1)
    obj2 = MyClass(2)
    print(obj1 is obj2)  # True
    print(obj1.value)    # 1（首次创建时的值）

注意事项
--------
- 单例实例一旦创建，后续的初始化参数将被忽略
- 适用于需要全局唯一实例的场景，如数据库连接池、配置管理器等
"""

from threading import RLock
from typing import Any, Dict, Tuple

__author__ = 'myh '
__date__ = '2023/3/10 '


class singleton_type(type):
    """线程安全的单例模式元类

    通过重写 __call__ 方法，在类实例化时进行拦截，确保每个类只创建一个实例。
    使用可重入锁（RLock）保证在多线程环境下的线程安全性。

    Attributes:
        single_lock: 类级别的可重入锁，用于保护实例创建过程

    Example:
        >>> class DatabaseConnection(metaclass=singleton_type):
        ...     def __init__(self, host: str):
        ...         self.host = host
        ...
        >>> conn1 = DatabaseConnection("localhost")
        >>> conn2 = DatabaseConnection("remotehost")
        >>> conn1 is conn2
        True
    """

    single_lock = RLock()

    def __call__(cls, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> Any:
        """创建或返回类的单例实例

        当使用该元类的类被实例化时，此方法被调用。它会检查该类是否已有实例，
        如果没有则创建新实例，否则返回已存在的实例。

        Args:
            *args: 传递给类构造函数的位置参数
            **kwargs: 传递给类构造函数的关键字参数

        Returns:
            该类的唯一实例

        Note:
            如果实例已存在，传入的参数将被忽略，不会更新实例状态
        """
        with singleton_type.single_lock:
            # 检查类是否已有实例
            if not hasattr(cls, "_instance"):
                # 首次调用时创建实例
                cls._instance = super(singleton_type, cls).__call__(*args, **kwargs)

        return cls._instance
