#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : cache
# @Time         : 2023/8/24 09:22
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 通用缓存

from meutils.pipe import *
from cachetools import cached, cachedmethod, LRUCache, RRCache, TTLCache
from joblib import hashing  # hashing.hash

key_fn = lambda *args, **kwargs: hashing.hash((args, kwargs))


def ttlcache(maxsize=128, ttl=np.inf):
    cache = cached(TTLCache(maxsize, ttl), key=key_fn)

    @wrapt.decorator
    def inner(wrapped, instance, args, kwargs):
        wrapped = cache(wrapped)
        return wrapped(*args, **kwargs)

    return inner


if __name__ == '__main__':
    @ttlcache()
    def f(x):
        time.sleep(1)
        return x


    with timer(1):
        print(f([1, 2]))
    with timer(2):
        print(f(range(10)))
