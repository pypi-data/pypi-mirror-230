#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : common
# @Time         : 2020/11/12 11:42 上午
# @Author       : yuanjie
# @Email        : meutils@qq.com
# @Software     : PyCharm
# @Description  : 单向引用，避免循环引用

import io
import os
import gc
import re
import sys
import time
import types
import typing
import uuid
import zipfile
import datetime
import operator
import inspect
import textwrap
import socket
import logging
import warnings

warnings.filterwarnings("ignore")

import functools
import argparse
import traceback
import threading
import multiprocessing
import base64
import shutil
import random
import asyncio
import importlib
import itertools
import pickle
import textwrap
import subprocess
import wget
import yaml
import typer
import json
import joblib
from joblib.hashing import hash
import requests
import wrapt
import sklearn
import numpy as np
import pandas as pd

from typing import *
from pathlib import Path
from queue import Queue
from pprint import pprint
from abc import abstractmethod
from dataclasses import dataclass
from functools import reduce, lru_cache, partial

from collections import Counter, OrderedDict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

plt.rcParams['axes.unicode_minus'] = False

from loguru import logger
# logger.remove()
# logger.add(sys.stderr,
#            format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <4}</level> - <level>{message}</level>')


from tqdm.auto import tqdm

tqdm.pandas()

from pydantic import BaseModel, Field
from faker import Faker  # https://www.cnblogs.com/aichixigua12/p/13236092.html

fake_zh = Faker(locale='zh_CN')

# from PIL import Image, ImageGrab
# image
# im = ImageGrab.grabclipboard() 获取剪切板的图片

# 第三方
from meutils.other.crontab import CronTab
from meutils.other.besttable import Besttable

# ME
from meutils._utils import *
from meutils.init.evn import *
from meutils.init.oo import __O000OO0O0000OO00O
from meutils.hash_utils import murmurhash
from meutils.cache_utils import ttl_cache, disk_cache, diskcache
from meutils.decorators import decorator, args, singleton, timer, background, background_task
from meutils.path_utils import get_module_path, get_resolve_path, sys_path_append, path2list, get_config

lock = threading.Lock()
__O000OO0O0000OO00O()

from dotenv import load_dotenv

load_dotenvs = lambda dotenv_paths: [load_dotenv(p, verbose=True) for p in dotenv_paths]

load_dotenv(
    os.getenv('EVN', "/Users/betterme/PycharmProjects/AI/.env"),  # EVN=传入绝对路径 todo: 自定义 .env.secret
    verbose=True
)

cli = typer.Typer(name="MeUtils CLI")

# 常量
CPU_NUM = os.cpu_count()
FONT = FontProperties(fname=get_resolve_path('./data/SimHei.ttf', __file__))

HOST_NAME = DOMAIN_NAME = LOCAL_HOST = LOCAL = HOST = PORT = ''

HOME_CACHE = Path.home() / ".cache"

try:
    if not hasattr(typing, 'Literal'):
        import typing
        import typing_extensions

        Literal = typing_extensions.Literal
        typing.Literal = Literal

    if not hasattr(functools, 'cached_property'):
        from cached_property import cached_property
    else:
        from functools import cached_property

    from IPython.core.interactiveshell import InteractiveShell

    InteractiveShell.ast_node_interactivity = "all"  # 多行输出

    from rich import print as rprint

    HOST_NAME = socket.gethostname()
    DOMAIN_NAME = socket.getfqdn(HOST_NAME)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as _st:
        _st.connect(('10.255.255.255', 1))
        HOST, PORT = _st.getsockname()

    # import orjson as json  # dumps 结果是字节型
    # json.dumps = partial(json.dumps, option=json.OPT_NON_STR_KEYS)

    from icecream import ic

    ic.configureOutput(includeContext=True)

except ImportError:
    pass


def _bar(current, total, width=100):
    """https://www.jb51.net/article/232232.htm"""

    i = int(current / total * 100)
    s = f"""\r{i}%|{"█" * (i // 5)}|"""
    print(s, end="", flush=True)
    # sys.stdout.flush()


wget.download = partial(wget.download, bar=_bar)


class BaseConfig(BaseModel):
    """基础配置"""
    _path: str = None

    @classmethod
    def init(cls):
        """init from path[zk/yaml]"""
        assert cls._path is not None, "请指定 _path"
        return cls.parse_path(cls._path)

    @classmethod
    def parse_path(cls, path):
        if Path(path).is_file():
            return cls.parse_yaml(cls._path)
        else:
            return cls.parse_zk(cls._path)

    @classmethod
    def parse_yaml(cls, path):
        json = yaml.safe_load(Path(path).read_bytes())
        return cls.parse_obj(json)

    @classmethod
    def parse_zk(cls, path):
        from meutils.zk_utils import get_zk_config
        json = get_zk_config(path)
        return cls.parse_obj(json)

    @classmethod
    def parse_env(cls):
        return cls.parse_obj(os.environ)


# limit memory
def limit_memory(memory=16):
    """
    :param memory: 默认限制内存为 16G
    :return:
    """
    import resource

    rsrc = resource.RLIMIT_AS
    # res_mem=os.environ["RESOURCE_MEM"]
    memlimit = memory * 1024 ** 3
    resource.setrlimit(rsrc, (memlimit, memlimit))
    # soft, hard = resource.getrlimit(rsrc)
    logger.info("memory limit as: %s G" % memory)


def magic_cmd(cmd='ls', parse_fn=lambda s: s, print_output=False):
    """

    :param cmd:
    :param parse_fn: lambda s: s.split('\n')
    :param print_output:
    :return:
    """
    cmd = ' '.join(cmd.split())
    status, output = subprocess.getstatusoutput(cmd)
    output = output.strip()

    logger.info(f"CMD: {cmd}")
    logger.info(f"CMD Status: {status}")

    if print_output:
        logger.info(f"CMD Output: {output}")

    return status, parse_fn(output)


def run_command(command='ls'):
    """
    运行Shell命令并输出其输出
    """
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, shell=True, universal_newlines=True
    )
    while True:
        # 读取Shell命令的输出
        key = str(time.time())
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            # 实时显示输出
            print(output.strip())

    return process.poll()


def is_open(ip='88.01.012.01'[::-1], port=7000, timeout=0.5):
    """
        互联网 is_open('baidu.com:80')

    @param ip:
    @param port:
    @param timeout:
    @return:
    """
    if ':' in ip:
        ip, port = ip.split(':')

    socket.setdefaulttimeout(timeout)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((ip, int(port)))
            s.shutdown(socket.SHUT_RDWR)
            return True
        except:
            return False


def get_var_name(var):
    """获取变量字符串名
        a=1
        b=1
        c=1
        只会取 a, 因是通过 id 确定 key
    """
    _locals = sys._getframe(1).f_locals
    for k, v in _locals.items():
        if id(var) == id(v):  # 相同值可能有误判
            return k


def get_current_fn():
    """获取执行函数的函数名
        def f(): # f
            print(get_current_fn())
    @return:
    """
    # inspect.currentframe().f_back === sys._getframe().f_back
    # f_name = inspect.getframeinfo(inspect.currentframe().f_back)[2]  # 最外层

    f_name = sys._getframe(1).f_code.co_name  # sys._getframe(1) 外层 sys._getframe(0) 内层
    return f_name


def clear(ignore=('TYPE_CHECKING', 'logger', 'START_TIME', 'CPU_NUM', 'HOST_NAME', 'LOCAL_HOST', 'LOCAL')):
    """销毁全局变量
    TODO：可添加过滤规则
    """
    keys = []
    ignore = set(ignore)
    for key, value in globals().items():
        if key.startswith('_') or key in ignore:
            continue
        if callable(value) or value.__class__.__name__ == "module":
            continue
        keys.append(key)

    logger.debug("销毁全局变量: " + list4log(keys))
    for key in keys:
        del globals()[key]
    return keys


def show_code(func):
    sourcelines, _ = inspect.getsourcelines(func)
    _ = textwrap.dedent("".join(sourcelines))
    print(_)
    return _


def file_replace(file, old, new):
    p = Path(file)
    _ = (
        p.read_text()
        .replace(old, new)
    )
    p.write_text(_)


def exec_callback(source, **namespace):
    """

    @param source:
    @param namespace: source 入参
    @return: 出参
    """
    namespace = namespace or {}
    exec(source, namespace)
    namespace.pop('__builtins__')
    return namespace  # output


def pkl_dump(obj, file):
    with lock:
        try:
            with open(file, 'wb') as f:
                return pickle.dump(obj, f)
        except IOError:
            return False


def pkl_load(file):
    try:
        with open(file, 'rb') as f:
            return pickle.load(f)
    except IOError:
        return False


class MeBackgroundTasks(object):
    """
    def func(x):
        print(f'Sleeping: {x}')
        time.sleep(x)
        print(f'DONE: {x}')

    bk = BackgroundTasks()
    bk.add_task(func, x=1)
    bk.add_task(func, x=2)
    bk.add_task(func, x=3)
    """

    def __init__(self, max_workers=None, thread_name_prefix='🐶BackgroundTasks'):
        self.pool = ThreadPoolExecutor(max_workers, thread_name_prefix)

    def add_task(self, func, *args, **kwargs):
        future = self.pool.submit(func, *args, **kwargs)  # pool.map(fn, *iterables, timeout=None, chunksize=1)
        future.add_done_callback(lambda x: logger.error(future.exception()) if future.exception() else None)


background_tasks = MeBackgroundTasks()


# import uuid
# uuid.uuid4().hex
# attrs = [attr for attr in dir(i) if not callable(getattr(i, attr)) and not attr.startswith("__")]


def try_import(
        module_name: str, *, pip_name: Optional[str] = None, package: Optional[str] = None
) -> Any:
    """Dynamically imports a module and raises a helpful exception if the module is not
    installed."""
    module = None
    try:
        module = importlib.import_module(module_name, package)
    except ImportError:
        raise ImportError(
            f"Could not import {module_name} python package. "
            f"Please install it with `pip install {pip_name or module_name}`."
        )
    return module


if __name__ == '__main__':
    s = "import pandas as pd; output = pd.__version__"
    s = "import os; output = os.popen(cmd).read().split()"
    print(exec_callback(s, cmd='ls'))
    # with timer() as t:
    #     time.sleep(3)
    #
    # status, output = magic_cmd('ls')
    # print(status, output)
    #
    # d = {'a': 1, 'b': 2}
    # print(bjson(d))
    # print(BaseConfig.parse_obj(d))

    print(show_code(show_code))
    print(get_var_name(s))
