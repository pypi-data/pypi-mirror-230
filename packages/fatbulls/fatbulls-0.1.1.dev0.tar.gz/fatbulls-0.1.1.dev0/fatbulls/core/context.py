#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################


"""
File: context.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/8/14 16:33:27
"""
import logging
from rqalpha.core.global_var import GlobalVars
from fatbulls.model.config import FactorBackTestConfig


class FatbullsFactorContext(object):
    _fbctx = None  # type: FatbullsFactorContext

    def __init__(self, config):
        FatbullsFactorContext._fbctx = self
        self.config = config
        self.global_vars = GlobalVars()
        self.backtest_config = None

    @classmethod
    def get_instance(cls):
        """
        返回已经创建的 Context 对象
        """
        if FatbullsFactorContext._fbctx is None:
            raise RuntimeError(
                "FatbullsFactorContext has not been created."
                " Please Use `FatbullsFactorContext.get_instance()` after FatBulls init")
        return FatbullsFactorContext._fbctx

    def set_config(self, config):
        self.config = config

    def get_config(self):
        return self.config

    def get_factor_config(self) -> FactorBackTestConfig:
        try:
            if self.backtest_config is not None:
                return self.backtest_config
            self.backtest_config = FactorBackTestConfig(
                sd=self.config.factor.sd,
                ed=self.config.factor.ed,
                task_num=self.config.factor.task_num,
                backtest_name=self.config.factor.backtest_name,
                univ_name=self.config.factor.univ_name,
                fdays=self.config.factor.fdays,
                rettype=self.config.factor.rettype,
                factor_dirs=self.config.factor.factor_dirs
            )
        except Exception as e:
            raise EnvironmentError('valid factor backtest config!, msg: {}'.format(str(e)))
        return self.backtest_config

    def get_base_logpath(self):
        try:
            return self.config.factor.base_log_path
        except Exception as e:
            logging.warning("factor.base_log_path not exists")
            return None

    def get_base_report_dirpath(self):
        try:
            return self.config.factor.base_report_dirpath
        except Exception as e:
            raise FileNotFoundError("factor.base_report_dirpath not exists")


class FatbullsPortfolioContext(object):
    _fbctx = None  # type: FatbullsPortfolioContext

    def __init__(self, config):
        FatbullsPortfolioContext._fbctx = self
        self.config = config
        self.global_vars = GlobalVars()
        self.backtest_config = None

    @classmethod
    def get_instance(cls):
        """
        返回已经创建的 Context 对象
        """
        if FatbullsPortfolioContext._fbctx is None:
            raise RuntimeError(
                "FatbullsPortfolioContext has not been created."
                " Please Use `FatbullsPortfolioContext.get_instance()` after FatBulls init")
        return FatbullsPortfolioContext._fbctx

