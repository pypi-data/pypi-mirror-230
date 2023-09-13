#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################

import os
# from datetime import datetime

"""
File: request.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/9/5 16:45:25
"""


class PortfolioRequest(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_config(self):
        config = dict()
        config['base'] = self.get_base_config()
        config['mod'] = {}
        config['mod']['sys_analyser'] = self.get_analyser_config()
        config['mod']['sys_simulation'] = self.get_simulation_config()
        config['mod']['sys_transaction_cost'] = self.get_transaction_cos_config()
        config['portfolio'] = self.get_portfolio_config()
        return config

    def get_start_date(self):
        if hasattr(self, 'sd'):
            sd = getattr(self, 'sd')
        else:
            raise ValueError('paramter sd not found, It could be a start date, eg: 20230331')
        # return datetime.strptime(sd, "%Y%m%d").strftime("%Y-%m-%d")
        return sd

    def get_end_date(self):
        if hasattr(self, 'ed'):
            ed = getattr(self, 'ed')
        else:
            raise ValueError('paramter ed not found, It could be a end date, eg: 20230331')
        # return datetime.strptime(ed, "%Y%m%d").strftime("%Y-%m-%d")
        return ed

    def get_stock_accounts(self):
        if hasattr(self, 'stock_accounts'):
            stock_accounts = getattr(self, 'stock_accounts')
        else:
            raise ValueError('paramter stock_accounts not found, It could be a integer, eg: 10000000000')
        return stock_accounts

    def get_benchmark(self):
        if hasattr(self, 'benchmark'):
            benchmark = getattr(self, 'benchmark')
        else:
            raise ValueError('paramter benchmark not found, It could be a instrument code, eg: 000300.XSHG')
        return benchmark

    def get_matching_type(self):
        if hasattr(self, 'matching_type'):
            matching_type = getattr(self, 'matching_type')
        else:
            raise ValueError('paramter matching_type not found, It could be a enum value, eg: vwap, current_bar')
        return matching_type

    def get_slippage(self):
        if hasattr(self, 'slippage'):
            slippage = getattr(self, 'slippage')
        else:
            raise ValueError('paramter slippage not found, It could be a integer, eg: 1')
        return slippage

    def get_stock_commission_multiplier(self):
        if hasattr(self, 'stock_commission_multiplier'):
            stock_commission_multiplier = getattr(self, 'stock_commission_multiplier')
        else:
            raise ValueError('paramter stock_commission_multiplier not found, It could be a integer, eg: 1')
        return stock_commission_multiplier

    def get_tax_multiplier(self):
        if hasattr(self, 'tax_multiplier'):
            tax_multiplier = getattr(self, 'tax_multiplier')
        else:
            raise ValueError('paramter tax_multiplier not found, It could be a integer, eg: 1')
        return tax_multiplier

    def get_management_fee(self):
        if hasattr(self, 'management_fee'):
            management_fee = getattr(self, 'management_fee')
        else:
            raise ValueError('paramter management_fee not found, It could be a integer, eg: 1')
        management_fee = [("STOCK", management_fee), ("FUTURE", 0.0000)]
        return management_fee

    def get_base_config(self):
        base_config = dict()
        base_config['start_date'] = self.get_start_date()
        base_config['end_date'] = self.get_end_date()
        base_config['accounts'] = {}
        base_config['accounts']['stock'] = self.get_stock_accounts()
        base_config['run_type'] = self.get_run_type()
        return base_config

    def get_analyser_config(self):
        """
        'sys_analyser': {
                    'benchmark': '',
                    'output_file': '',
                    'report_save_path': '',
                    'plot_save_file': '',
                    'plot_config': {
                        'open_close_points': True,
                        'weekly_indicators': True
                    },
                },
                 "record": True,
            "output_file": "/Users/wangjiangfeng/Downloads/demo.pkl",
            "report_save_path": "/Users/wangjiangfeng/Downloads",
            "enabled": True,
            "plot": True,
            "plot_save_file": "/Users/wangjiangfeng/Downloads",
        """
        analyser_config = dict()
        analyser_config['record'] = True
        analyser_config['benchmark'] = self.get_benchmark()
        analyser_config['output_file'] = ''
        analyser_config['report_save_path'] = ''
        analyser_config['plot_save_file'] = ''
        analyser_config['plot_config'] = {
            'open_close_points': True,
            'weekly_indicators': True
        }
        return analyser_config

    def get_simulation_config(self):
        """
        'sys_simulation': {
                    'matching_type': '',
                    'slippage': '',
                    'anagement_fee': []
                },
        """
        simulation_config = dict()
        simulation_config['matching_type'] = self.get_matching_type()
        simulation_config['slippage'] = self.get_slippage()
        simulation_config['management_fee'] = self.get_management_fee()
        return simulation_config

    def get_transaction_cos_config(self):
        """
        'sys_transaction_cost': {
                    'commission_multiplier': '',
                    'stock_commission_multiplier': '',
                    'tax_multiplier': '',
                }
        """
        transaction_cost = dict()
        transaction_cost['stock_commission_multiplier'] = self.get_stock_commission_multiplier()
        transaction_cost['tax_multiplier'] = self.get_tax_multiplier()
        return transaction_cost

    def get_portfolio_config(self):
        portfolio_config = dict()
        portfolio_config['portfolio_dirpath'] = self.get_portfolos_dirpath()
        portfolio_config['base_report_path'] = self.get_base_report_path()
        portfolio_config['task_num'] = self.get_task_num()
        portfolio_config['backtest_name'] = self.get_backtest_name()
        return portfolio_config

    def get_portfolos_dirpath(self):
        if hasattr(self, 'portfolos_dirpath'):
            portfolos_dirpath = getattr(self, 'portfolos_dirpath')
        else:
            raise ValueError('paramter portfolos_dirpath not found, It could be a filepath,'
                             ' eg: /data/quant/portfolios/wuyiyang/baseline_1001/portfolios')
        if not os.path.exists(portfolos_dirpath):
            raise NotADirectoryError('portfolos_dirpath not exists')
        return portfolos_dirpath

    def get_base_report_path(self):
        base_report_path = ''
        if hasattr(self, 'base_report_path'):
            base_report_path = getattr(self, 'base_report_path', None)
            if (base_report_path is not None) and (not os.path.exists(base_report_path)):
                raise NotADirectoryError('base_report_path not exists')
        return base_report_path

    def get_backtest_name(self):
        if hasattr(self, 'backtest_name'):
            backtest_name = getattr(self, 'backtest_name', None)
        else:
            raise ValueError('paramter backtest_name not found, It could be a string, eg: 房地产回测')
        return backtest_name

    def get_task_num(self):
        if hasattr(self, 'task_num'):
            task_num = getattr(self, 'task_num', None)
        else:
            raise ValueError('paramter task_num not found, It could be a unique string, eg: 1123333')
        return task_num

    def get_run_type(self):
        if hasattr(self, 'run_type'):
            run_type = getattr(self, 'run_type')
        else:
            run_type = 'b'
        return run_type
