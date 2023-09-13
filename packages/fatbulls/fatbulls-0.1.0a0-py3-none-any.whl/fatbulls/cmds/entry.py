#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################


"""
File: entry.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/8/14 17:21:27
"""

import click


@click.group()
@click.help_option('-h', '--help')
def cli():
    pass

