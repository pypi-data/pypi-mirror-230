#!/usr/bin/env python
# -*- coding:utf-8 -*-
from contextlib import contextmanager
from multiprocessing import RLock as PLock
from multiprocessing import Manager
from threading import RLock as TLock
from typing import Set, TypeVar, List

from gevent.lock import Semaphore

from ..utils.objects import ObjectsUtils

T = TypeVar("T", TLock, PLock, Semaphore)
C = TypeVar("C", Set, List)


class Sentry(object):
    """
    lock by variable.
    Theoretically, objects can be locked in this way.
    For example, file locking.
    """

    def __init__(self, lock, free, using):
        self.__lock: T = lock
        self.__free: C = free
        self.__using: C = using

    def __free_add(self, *obj):
        if isinstance(self.__free, Set):
            self.__free.update(set(obj))
        else:
            self.__free.extend(obj)

    def __using_add(self, *obj):
        if isinstance(self.__using, Set):
            self.__using.update(set(obj))
        else:
            self.__using.extend(obj)

    def release(self, obj):
        ObjectsUtils.check_non_none(obj, RuntimeError("can't be 'None'"))
        self.__lock.acquire()
        self.__using.remove(obj)
        self.__free_add(obj)
        self.__lock.release()
        return obj

    def add(self, *obj):
        """
        add element(s)
        """
        ObjectsUtils.check_non_none(obj, RuntimeError("can't be 'None'"))
        self.__lock.acquire()
        self.__free_add(*obj)
        self.__lock.release()

    def addd_item(self, item):
        """
        batch call add()
        """
        self.add(*item)

    def remove(self, obj):
        ObjectsUtils.check_non_none(obj, RuntimeError("can't be 'None'"))
        self.__lock.acquire()
        self.__using.remove(obj)
        self.__lock.release()

    @contextmanager
    def acquire(self, value=None):
        """
        Try to get an object.
        if not found value from cache, will get last object

        files = ["file1", "file2"]

        lock = Coffers.process()
        lock.add_item(files)

        case1:
            for f in files:
                with lock.acquire(f) as obj:
                    # get excepted file
                    if obj == f:
                        # do something
                    else:
                        # do something
        case2:
            for f in files:
                with lock.acquire() as obj:
                    # I don't know which file I need, so I start looking for the last one
                    if obj == f:
                        # do something
                    else:
                        # do something
        """
        obj = None
        self.__lock.acquire()
        size = len(self.__free)
        if size > 0:
            # noinspection PyBroadException
            try:
                index = self.__free.index(value)
            except BaseException:
                index = -1
            obj = self.__free.pop(index)
            self.__using_add(obj)
        yield obj
        self.__lock.release()


class _Singleton(type):
    """
    singletons
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Coffers(metaclass=_Singleton):
    """
    Built-in lock type
    """

    @staticmethod
    def process() -> Sentry:
        """
        multi processing lock
        """
        manager = Manager()
        free: Set = manager.list()
        using: Set = manager.list()
        lock: T = PLock()
        return Sentry(lock, free, using)

    @staticmethod
    def thread() -> Sentry:
        """
        multi thread lock

        """
        return Sentry(TLock(), set(), set())

    @staticmethod
    def coroutine() -> Sentry:
        """
        coroutine lock
        """
        return Sentry(Semaphore(1), set(), set())


__all__ = [Coffers, Sentry]
