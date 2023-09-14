#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################


"""
File: portfolio.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/9/6 15:08:53
"""

import os
import pandas as pd
from rqalpha.utils.repr import property_repr
from fatbulls.core.exception import FactorBackTestException
from fatbulls.portfolio.constant import PORTFOLIO_COLUMNS, PORTFOLIO_MAX_WEIGHT, PORTFOLIO_WEIGHT_FIELD
from rqalpha.utils.functools import lru_cache


class Portfolios(object):

    __repr__ = property_repr

    def __init__(self, portfolio_name, portfolio_dirpath):
        self._portfolio_name = portfolio_name
        self._portfolio_dirpath = portfolio_dirpath

    def check_portfolio(self, trade_days):
        days = self.get_portfolio_days()
        if set(trade_days).issubset(days):
            return True
        else:
            missing_days = [str(day) for day in trade_days if str(day) not in days]
            raise FactorBackTestException("missing trade day csv file in portfolio path, days: {}"
                                          .format(",".join(missing_days)))

    @property
    def portfolio_name(self):
        return self._portfolio_name

    @property
    def portfolio_dirpath(self):
        return self._portfolio_dirpath

    @lru_cache(128)
    def get_portfolio_days(self):
        return [file.split(".")[0] for file in os.listdir(self._portfolio_dirpath)]

    @lru_cache(128)
    def get_portfolio_data(self, start_date=None, end_date=None) -> dict:
        if not os.path.exists(self._portfolio_dirpath):
            raise FactorBackTestException("portfolio dirpath not exists")
        portfolio_data = {}
        portfolio_days = self.get_portfolio_days()
        max_day = max(portfolio_days)
        min_day = min(portfolio_days)
        start_date = min_day if start_date is None else start_date
        end_date = max_day if end_date is None else end_date
        for trade_day in portfolio_days:
            if trade_day < start_date or trade_day > end_date:
                continue
            file = "{}.csv".format(trade_day)
            filename = os.path.join(self._portfolio_dirpath, file)
            df_portfolio_day = pd.read_csv(filename, header=0)
            if not df_portfolio_day.empty:
                sum_weight = df_portfolio_day[PORTFOLIO_WEIGHT_FIELD].sum()
                if sum_weight > PORTFOLIO_MAX_WEIGHT:
                    """总权重压缩到0到0.95区间"""
                    df_portfolio_day[PORTFOLIO_WEIGHT_FIELD] = df_portfolio_day[PORTFOLIO_WEIGHT_FIELD] / sum_weight
                    df_portfolio_day[PORTFOLIO_WEIGHT_FIELD] = (df_portfolio_day[PORTFOLIO_WEIGHT_FIELD]
                                                                * (PORTFOLIO_MAX_WEIGHT - 0.0) + 0.0)
                df_portfolio_day['K'] = df_portfolio_day['K'].apply(lambda x: str(x)
                                                                    .replace(".SH", ".XSHG")
                                                                    .replace(".SZ", ".XSHE"))
                # 保留4为小数
                df_portfolio_day['W'] = df_portfolio_day['W'].round(4)
                df_portfolio_day['vwap'] = df_portfolio_day['vwap'].round(4)
                portfolio_data[trade_day] = df_portfolio_day[['K', 'D', 'T', 'W', 'vwap']]
            else:
                portfolio_data[trade_day] = {}
        return portfolio_data


# if __name__ == "__main__":
#     p = Portfolios('baseline001', '/Users/wangjiangfeng/.faithquant/portfolios')
#     p.get_portfolio_data()
