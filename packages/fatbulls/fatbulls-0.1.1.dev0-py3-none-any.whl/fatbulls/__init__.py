#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################


"""
File: __init__.py.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/8/14 16:09:11
"""
import time
import logging
import os
from functools import wraps

__all__ = [
    '__version__', 'run_backtest', 'time_cost'
]


def time_cost(func):

    @wraps(func)
    def wrap(*args, **kwargs):
        begin_time = time.perf_counter()
        result = func(*args, **kwargs)
        start_time = time.perf_counter()
        tips = '函数: %r 耗时: %2.4f 秒' % (func.__name__, start_time - begin_time)
        logging.info(tips)
        print(tips)
        return result
    return wrap


@time_cost
def run_backtest(**kwargs):
    """
    传入约定函数和因子配置运行回测。约定函数详见 API 手册约定函数部分，可用的配置项详见参数配置部分。

    :Keyword Arguments:
        * **config** (dict) -- 策略配置字典

    :return: dict

    """
    from fatbulls.utils.const import BACKTEST_TYPE
    from fatbulls import main
    backtest_type = kwargs.get('backtest_type', None)
    if backtest_type is None:
        raise ValueError("missing parameter: backtest_type")
    backtest_config = kwargs.get('backtest_config', {})
    if backtest_type == BACKTEST_TYPE.FACTOR_BACKTEST:
        """
        因子回测方法调用
        """
        return main.run_factor_backtest_se(backtest_config)
    elif backtest_type == BACKTEST_TYPE.PORTFOLIO_BACKTEST:
        """ 组合回测的逻辑 """
        from rqalpha.utils.functools import clear_all_cached_functions
        from rqalpha.utils.config import load_yaml
        from rqalpha.utils.dict_func import deep_update
        from fatbulls.utils.request import PortfolioRequest

        fatbulls_config_path = kwargs.get('config_path', None)
        if fatbulls_config_path is None:
            fatbulls_config_path = os.path.join(os.path.dirname(__file__), 'resource/fatbulls_config.yml')
        config = load_yaml(fatbulls_config_path)
        pr = PortfolioRequest(**backtest_config)
        backtest_config = pr.get_config()
        deep_update(backtest_config, config)
        clear_all_cached_functions()
        return main.run_portfolio_backtest(config=config)
    else:
        raise ValueError("invalid parameter: backtest_type, It could be FACTORS or PORTFOLIOS")


__version__ = '0.1.1-dev'


