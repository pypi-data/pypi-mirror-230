#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: config.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/8/31 15:56:05
"""

import os.path
from typing import List
from datetime import datetime
from fatbulls.core.exception import FactorBackTestException
from fatbulls.factor.constant import UNIV_NAME, RET_TYPE


class BackTestConfig(object):

    def __init__(self, sd: str, ed: str, task_num: str, backtest_name: str):
        self.today = datetime.now().strftime("%Y%m%d")
        self.backtest_day = datetime.now().strftime("%Y%m%d")
        self.sd = sd
        self.ed = ed
        self.task_num = task_num
        self.backtest_name = backtest_name

    @property
    def sd(self):
        return self._sd

    @sd.setter
    def sd(self, value):
        if not isinstance(value, str) or value < '20130000':
            raise FactorBackTestException('invalid sd date inputs')
        self._sd = value

    @property
    def ed(self):
        return self._ed

    @ed.setter
    def ed(self, value):
        if not isinstance(value, str):
            raise FactorBackTestException('invalid ed date inputs')
        self._ed = value


class FactorBackTestConfig(BackTestConfig):

    def __init__(self, sd: str, ed: str, task_num: str = 'WaitForOne', backtest_name: str = 'test_backtest',
                 univ_name: str = 'cnall', fdays: int = 1, rettype: str = 'vwap30', factor_dirs: List = None):
        BackTestConfig.__init__(self, sd, ed, task_num, backtest_name)
        if factor_dirs is None:
            raise FactorBackTestException('factor directory path is empty')
        self.univ_name = univ_name
        self.fdays = fdays
        self.rettype = rettype
        self.factor_dirs = factor_dirs

    @property
    def univ_name(self):
        return self._univ_name

    @univ_name.setter
    def univ_name(self, value):
        if not isinstance(value, str) or value not in UNIV_NAME:
            raise FactorBackTestException("preset univ_name {} not found".format(value))
        self._univ_name = value

    @property
    def rettype(self):
        return self._rettype

    @rettype.setter
    def rettype(self, value):
        if not isinstance(value, str) or value not in RET_TYPE:
            raise FactorBackTestException("preset rettype {} not found".format(value))
        self._rettype = value

    @property
    def fdays(self):
        return self._fdays

    @fdays.setter
    def fdays(self, value):
        if not (isinstance(value, int) and 1 <= value <= 63):
            raise FactorBackTestException("forward looking days should fall into range 1~63 days")
        self._fdays = value

    @property
    def factor_dirs(self):
        return self._factor_dirs

    @factor_dirs.setter
    def factor_dirs(self, value):
        if not (isinstance(value, List) and len(value) >= 1):
            raise FactorBackTestException("must pass at least 1 valid factor path")
        for dirpath in value:
            if not os.path.exists(dirpath):
                raise FactorBackTestException("factor directory path not exists: {}".format(dirpath))
        self._factor_dirs = value


class PortfolioBacktestConfig(object):

    def __init__(self, config: dict):
        self.config = config





