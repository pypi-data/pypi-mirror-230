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

from six import with_metaclass
from abc import ABCMeta, abstractmethod


class AbstractBackTestEngine(with_metaclass(ABCMeta)):

    @abstractmethod
    def run(self):
        raise NotImplementedError

    @abstractmethod
    def save_report(self):
        raise NotImplementedError

