#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################


"""
File: run.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/8/14 17:22:48
"""


import os

import click
from rqalpha.utils.click_helper import Date
from rqalpha.utils.config import parse_config

from .entry import cli


@cli.command(help="Run a strategy")
@click.help_option('-h', '--help')
# -- Base Configuration
@click.option('-d', '--data-bundle-path', 'base__data_bundle_path', type=click.Path(exists=True))
@click.option('-f', '--strategy-file', 'base__strategy_file', type=click.Path(exists=True))
@click.option('-s', '--start-date', 'base__start_date', type=Date())
@click.option('-e', '--end-date', 'base__end_date', type=Date())
@click.option('-l', '--log-level', 'extra__log_level', type=click.Choice(['verbose', 'debug', 'info', 'error', 'none']))
def run(**kwargs):
    config_path = kwargs.get('config_path', None)
    if config_path is not None:
        config_path = os.path.abspath(config_path)
        kwargs.pop('config_path')
    if not kwargs.get('base__securities', None):
        kwargs.pop('base__securities', None)

    from fatbulls import main
    source_code = kwargs.get("base__source_code")
    cfg = parse_config(kwargs, config_path=config_path, click_type=True, source_code=source_code)
    source_code = cfg.base.source_code
    results = main.run(cfg, source_code=source_code)

    if results is None:
        return 1


def inject_run_param(param: click.Parameter):
    cli.commands["run"].params.append(param)

