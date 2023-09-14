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


def init(context):
    logger.info("Fatbulls组合回测框架初始化")


def before_trading(context):
    pass


def handle_bar(context, bar_dict):
    """你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新"""
    bar_date = context.now
    day = bar_date.strftime('%Y%m%d')
    logger.info("handle_bar开始处理")
    if hasattr(context.config.faithquant.portfolio.stock_positions, day):
        df_stocks = getattr(context.config.faithquant.portfolio.stock_positions, day)
        if df_stocks is None or df_stocks.empty:
            logger.info("组合数据为空，执行清仓操作")
            logger.info("开始执行清仓操作")
            positions = get_positions()
            for position in positions:
                order_book_id = position.order_book_id
                quantity = position.quantity
                order_shares(order_book_id, quantity * -1)
        else:
            target_portfolio = {k: w for k, w in zip(df_stocks['K'], df_stocks['W'])}
            price_or_styles = {k: p for k, p in zip(df_stocks['K'], df_stocks['vwap'])}
            # 调用目标函数按目标下单
            order_target_portfolio(target_portfolio, price_or_styles)
    else:
        logger.info("持仓数据不存在，日期：{}", day)
    logger.info("交易完毕")
