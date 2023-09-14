#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################


"""
File: const.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/9/12 11:13:31
"""

from rqalpha.const import CustomEnum


# noinspection PyPep8Naming
class BACKTEST_TYPE(CustomEnum):

    FACTOR_BACKTEST = 'FACTORS'

    PORTFOLIO_BACKTEST = 'PORTFOLIOS'
