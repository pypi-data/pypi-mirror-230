#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################


"""
File: exception.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/8/31 15:36:50
"""


class FactorBackTestException(Exception):
    """
    因子回测通用异常类
    """
    def __init__(self, msg):
        self.msg = msg


class FqDatacException(Exception):
    """
    SDK调用异常
    """
    def __init__(self, msg):
        self.msg = msg
