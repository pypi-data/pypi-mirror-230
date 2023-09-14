#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################




"""
File: __init__.py.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/8/14 16:36:59
"""

import os
import re

FQDATAC_DEFAULT_ADDRESS = "fqdatac://ak:sk@219.143.244.230:8390"


def init_fqdatac_env(uri):
    if uri is None:
        return

    if '@' not in uri:
        uri = "tcp://{}@{}".format(uri, FQDATAC_DEFAULT_ADDRESS)

    if not re.match(r"\w*://.+:.+@.+:\d+", uri):
        raise ValueError('invalid fqdatac uri. use user:password or tcp://user:password@ip:port')

    os.environ['FQDATAC_CONF'] = uri
