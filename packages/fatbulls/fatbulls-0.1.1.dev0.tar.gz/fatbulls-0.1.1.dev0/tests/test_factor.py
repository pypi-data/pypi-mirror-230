#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################


"""
File: test_factor.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/8/31 16:14:03
"""
import os


def test_portfolio_file():
    for file in os.listdir("/Users/wangjiangfeng/.faithquant/portfolios"):
        print(file)
