#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################


"""
File: engine.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/9/1 09:44:49
"""

"""portfolio文件列名"""
PORTFOLIO_COLUMNS = ['K', 'D', 'T', 'V', 'W', 'entry_dt', 'entry_time', 'init_W', 'yest_W']
PORTFOLIO_MAX_WEIGHT = 0.95
PORTFOLIO_WEIGHT_FIELD = 'W'

"""回测模式：日回测"""
MATCHING_TYPE_DAY_MODE = [
    'current_bar',  # 对应c2c, 以当前bar为收盘价。
    'vwap',         # 成交量加权平均价撮合。
]

"""回测模式：分钟回测"""
MATCHING_TYPE_MIN_MODE = [
    'current_bar',  # 对应c2c, 以当前bar为收盘价。
    'vwap',         # 成交量加权平均价撮合。
    'next_bar',     # 对应o2o, 下一个 bar 的开盘价
]

"""回测模式：TICK回测"""
MATCHING_TYPE_TICK_MODE = [
    'last',                 # 以最新价
    'best_own',             # 己方最优价
    'best_counterparty',    # 对手方最优价撮合
    'counterparty_offer',   # 逐档撮合
]