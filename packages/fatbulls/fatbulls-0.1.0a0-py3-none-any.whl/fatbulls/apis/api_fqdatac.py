#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################


"""
File: api_fqdatac.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/8/31 15:26:25
"""

import datetime
import pandas as pd
from dateutil.parser import parse
from rqalpha.api import export_as_api
from rqalpha.utils.arg_checker import apply_rules, verify_that
from ..core.exception import FqDatacException

try:
    import fqdatac
except ImportError:
    class DummyFqDatac:
        __name__ = "fqdatac"

        def __getattr__(self, item):
            return self

        def __call__(self, *args, **kwargs):
            raise FqDatacException('fqdatac is not available, extension apis will not function properly')
    fqdatac = DummyFqDatac()


def to_date(date):
    if isinstance(date, datetime.datetime):
        return date.date()
    if isinstance(date, datetime.date):
        return date

    if isinstance(date, str):
        return parse(date).date()

    raise FqDatacException('unknown date value: {}'.format(date))


def to_date_str(date):
    if isinstance(date, datetime.datetime):
        return date.strftime('%Y%m%d')
    elif isinstance(date, datetime.date):
        return date.strftime('%Y%m%d')
    elif isinstance(date, str):
        return date.replace("-", "")
    return date


@export_as_api
@apply_rules(verify_that('start_date').is_valid_date())
@apply_rules(verify_that('end_date').is_valid_date())
def get_daysrange(start_date, end_date) -> list:
    """
    从fqdatac取数据
    :param start_date:
    :param end_date:
    :return:
    """
    start_date = to_date_str(start_date)
    end_date = to_date_str(end_date)
    #df_days = pd.read_csv('/Users/wangjiangfeng/.faithquant/fakedata/all_days.csv', header=0)
    #trade_days = df_days['day'].tolist()
    #return [str(day) for day in trade_days if start_date <= str(day) <= end_date]
    return fqdatac.get_daysrange(start_date, end_date, days_type='trading', output_format='str')


@export_as_api
@apply_rules(verify_that('start_date').is_valid_date())
@apply_rules(verify_that('end_date').is_valid_date())
def get_universe(start_date, end_date, univ_name) -> pd.DataFrame:
    """
    从fqdatac取数据
    :param start_date: yyyyMMdd
    :param end_date: yyyyMMdd
    :param univ_name: universe name
    :return: pd.DataFrame
    """
    return fqdatac.get_universe(start_date, end_date, univ_name)

