#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################


"""
File: main.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/8/14 17:30:51
"""

import os
import logging
import pandas as pd

from deprecated import deprecated
from fatbulls.utils import init_fqdatac_env
from fatbulls.utils.logger import init_logging
from fatbulls.factor.se import fac_backtest
from fatbulls.core.context import FatbullsFactorContext
from fatbulls.portfolio.backtest import PortfolioBacktestEngine
from fatbulls.core.exception import FactorBackTestException


def set_pandas_options():
    pd.set_option("display.max_columns", 100)
    pd.set_option("display.width", 1000)
    pd.set_option("display.max_colwidth", 100)
    pd.set_option("display.float_format", lambda x: "%.4f" % x)


def init_fqdatac(fqdatac_uri):
    if fqdatac_uri in ["disabled", "DISABLED"]:
        return
    try:
        import fqdatac
    except ImportError:
        return
    if isinstance(fqdatac.client.get_client(), fqdatac.client.DummyClient):
        init_fqdatac_env(fqdatac_uri)
        try:
            fqdatac.init()
        except Exception as e:
            logging.error('fqdatac init failed, some apis will not function properly: {}'.format(str(e)))


def run_factor_backtest_se(config, app_name='fatbulls_factor_backtest', set_pandas=True):
    try:
        """
        config = {
            backtest_name: str,
            sd: str,
            ed: str,
            task_num: str = "b",
            univ_name: str = "cnall",
            fdays: int = 5,
            rettype: str = "vwap30",
            directory_list: list = [],
        }
        """
        logging.info("app_name: {}", app_name)
        logging.info("set_pandas: {}", set_pandas)
        # 不做任何处理直接调用
        fac_backtest.run(**config)
    except Exception as e:
        raise e


@deprecated
def run_factor_backtest(config, app_name='fatbulls_factor_backtest', set_pandas=True):
    try:
        if set_pandas:
            """pandas 设置"""
            set_pandas_options()
        init_fqdatac(config['base']['fqdatac_uri'])
        if config.factor.base_log_path:
            app_dir = config.factor.base_log_path
        else:
            app_dir = None
        init_logging(app_name, app_dir)
        fat_ctx = FatbullsFactorContext(config)
        factor_conf = fat_ctx.get_factor_config()
        fat_ctx.get_base_report_dirpath()
        logging.info(factor_conf)
        logging.info("---start factor evaluation---")
        logging.info("mock execute")
        logging.info("All done")
    except Exception as e:
        raise e


def run_portfolio_backtest(config, set_pandas=True):
    try:
        if set_pandas:
            """pandas 设置"""
            set_pandas_options()
        init_fqdatac(config['base']['fqdatac_uri'])
        run_type = config['base']['run_type']
        frequency = config['base']['frequency']
        if run_type == 'b' and frequency == '1d':
            # 目前只支持日度回测
            base_path = os.path.dirname(os.path.abspath(__file__))
            strategy_file_path = os.path.join(base_path, "core/strategy_day_bar.py")
            engine = PortfolioBacktestEngine(backtest_config=config, strategy_file_path=strategy_file_path)
            engine.run()
        else:
            raise FactorBackTestException("only support run type of stock history backtest and daily frequency")
        logging.info("All done")
    except Exception as e:
        raise e
