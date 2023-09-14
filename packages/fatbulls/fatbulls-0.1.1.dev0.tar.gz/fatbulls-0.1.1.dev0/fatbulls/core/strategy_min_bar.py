#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################


"""
File: strategy_day_bar.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/9/7 15:33:26
"""

from rqalpha.apis import *


# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    logger.info("Fatbulls组合回测框架初始化")
    # 是否已发送了order
    context.fired = False


def before_trading(context):
    pass


def handle_bar(context, bar_dict):
    """你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新"""
    #
    if not context.fired:
        # order_percent并且传入1代表买入该股票并且使其占有投资组合的100%
        order_percent(context.s1, 1)
        context.fired = True
