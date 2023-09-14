#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################


"""
File: logger.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/9/13 11:08:34
"""

import datetime as dt
import logging
from pathlib import Path
import os

APP_DIR = Path(__file__).absolute().parent.parent


def init_logging(app_name, console_level=logging.WARNING):
    logdir = APP_DIR / "log"
    os.makedirs(logdir, exist_ok=True)
    today_date: str = dt.datetime.now().strftime("%Y%m%d")

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    fmt = logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s]: %(message)s")

    fn: str = logdir / f"{app_name}_{today_date}.log"
    file_handler = logging.FileHandler(fn, mode="a", encoding="utf8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    warn_fn: str = logdir / f"{app_name}_{today_date}_warn.log"
    warnfile_handler = logging.FileHandler(warn_fn, mode="a", encoding="utf8")
    warnfile_handler.setLevel(logging.WARNING)
    warnfile_handler.setFormatter(fmt)
    logger.addHandler(warnfile_handler)

    console = logging.StreamHandler()
    console.setLevel(console_level)
    console.setFormatter(fmt)
    logger.addHandler(console)


def check_exist_and_makedir(path,file_name):
    files = os.listdir(path)
    current_file = [x for x in files ]
    folder_path = os.path.join(path, file_name)
    if file_name in current_file:
        pass
    else:
        os.mkdir(folder_path)
    return folder_path


if __name__ == "__main__":
    init_logging("test")

