#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################


"""
File: backtest.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/9/6 14:00:37
"""

import os
from fatbulls.core.engine import AbstractBackTestEngine
from fatbulls.core.exception import FactorBackTestException
from fatbulls.model.portfolio import Portfolios
from fatbulls.apis.api_fqdatac import get_daysrange
from rqalpha import run_file


class PortfolioBacktestEngine(AbstractBackTestEngine):

    def __init__(self, backtest_config: dict, strategy_file_path: str = None):
        self.backtest_config = backtest_config
        self.matching_type = backtest_config['mod']['sys_simulation']['matching_type']
        self.run_type = backtest_config['base']['run_type']
        self.start_date = self.backtest_config['base']['start_date']
        self.end_date = self.backtest_config['base']['end_date']
        self.strategy_file_path = strategy_file_path
        self.report_path = None
        self.trade_days = None
        self.portfolios = None

    def run(self):
        self.init_report_path()
        self.trade_days = get_daysrange(self.start_date, self.end_date)
        portfolio_dirpath = self.backtest_config['portfolio']['portfolio_dirpath']
        protfolio_name = portfolio_dirpath.rstrip("/").split("/")[-2]
        self.portfolios = Portfolios(protfolio_name, portfolio_dirpath)
        self.portfolios.check_portfolio(self.trade_days)
        self.backtest_config['portfolio']['portfolios'] = self.portfolios.get_portfolio_data(self.start_date, self.end_date)
        run_file(self.strategy_file_path, config=self.backtest_config)

    def save_report(self):
        """保存report"""
        # 写入_SUCCESS
        if self.report_path is None:
            self.init_report_path()
        filename = self.report_path.rstrip("/") + "_SUCCESS"
        if os.path.isfile(filename):
            os.remove(filename)
        with open(filename, 'rw') as fp:
            fp.write("1")

    def init_report_path(self):
        try:
            base_report_path = self.backtest_config['portfolio']['base_report_path']
            task_num = self.backtest_config['portfolio']['task_num']
            self.report_path = os.path.join(base_report_path, task_num, 'data')
            self.backtest_config['mod']['sys_analyser']['record'] = True
            self.backtest_config['mod']['sys_analyser']['output_file'] = "{}/{}.pkl".format(self.report_path, task_num)
            self.backtest_config['mod']['sys_analyser']['report_save_path'] = self.report_path
            self.backtest_config['mod']['sys_analyser']['enabled'] = True
            self.backtest_config['mod']['sys_analyser']['plot'] = True
            self.backtest_config['mod']['sys_analyser']['plot_save_file'] = self.report_path
            os.makedirs(self.report_path, exist_ok=True)
        except Exception as e:
            raise FactorBackTestException("get_report_path error: {}".format(str(e)))
