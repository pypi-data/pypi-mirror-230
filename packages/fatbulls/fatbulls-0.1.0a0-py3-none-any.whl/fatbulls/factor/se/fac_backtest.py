#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################


from .logger import init_logging
import logging
import fire
from . import fac_class as fac
from pathlib import Path
import os


def backtest_main(
        backtest_name: str,
        sd: str,
        ed: str,
        task_num: str,
        univ_name: str = "cnall",
        fdays: int = 1,
        rettype: str = "vwap30 to vwap30",
        directory_list: list = [],
):
    # 实例化
    loader = fac.FactorBTLoader(
        sd=sd,
        ed=ed,
        backtest_name=backtest_name,
        univ_name=univ_name,
        fdays=fdays,
        rettype=rettype,
        directory_list=directory_list,
    )

    # 数据加载与预处理
    logging.info("start factor loading")
    for d in directory_list:
        loader.load(
            directory=d,
        )
        logging.info(f"factor {d.split('/')[-1]} successfully loaded")
    loader.onlyuniv()

    logging.info("start fwdret loading")
    loader.fwdret_load()

    # 整个回测过程
    logging.info("start factor evaluation")
    output_path = "/data/quant/report/factor_backtest"
    evaluator = fac.FactorEvaluator(
        sd=loader.sd,
        ed=loader.ed,
        backtest_name=loader.backtest_name,
        univ_name=loader.univ_name,
        fdays=loader.fdays,
        rettype=loader.rettype,
        directory_list=loader.directory_list,
        raw=loader.container,
        fwdret1=loader.fwdret1,
        fwdret = loader.fwdret,
        output_path=output_path,
        task_num=task_num,
    )
    evaluator.initialize()
    evaluator.nextfactor()
    while evaluator.whole_processing:
        # evaluator.nextfile()
        # while evaluator.fac_processing:
        #     evaluator.evaluate()
        #     evaluator.save_lastfile()
        #     evaluator.nextfile()
        logging.info(f"factor evaluation for factor{evaluator.curfac}")
        evaluator.evaluate()
        evaluator.fac_report()
        evaluator.nextfactor()
        logging.info("--next factor")
    evaluator.output()


def run(
        backtest_name: str,
        sd: str,
        ed: str,
        task_num: str = "b",
        univ_name: str = "cnall",
        fdays: int = 5,
        rettype: str = "vwap30",
        directory_list: list = [],
):
    fac.FQDataLoader()

    output_path = "/data/quant/report/factor_backtest"
    # 建立sql连接
    # sql_path = os.path.join(
    #     Path(__file__).absolute().parent.parent.parent.parent,
    #     "sqlconn",
    #     "connection.txt",
    # )
    # conndict = SQLConnection.read_connfile(path=sql_path)
    # conn = SQLConnection.load_connection(d=conndict)
    # conn.mysql_connection()

    backtest_main(
        backtest_name=backtest_name,
        sd=sd,
        ed=ed,
        task_num=task_num,
        univ_name=univ_name,
        fdays=fdays,
        rettype=rettype,
        directory_list=directory_list,
    )


if __name__ == "__main__":
    DEBUG = True
    init_logging(__file__.split("/")[-1].split(".")[0])
    logging.info("---start factor evaluation---")
    if DEBUG:
        run(
            backtest_name="test_backtest1",
            sd="20170101",
            ed="20201231",
            directory_list=[
                #"/data/quant/factors/DTech/DTech_volume",
                "/data/quant/factors/DTech/DTech_amt",
                "/data/quant/factors/DTech/DTech_high",
                # "/data/quant/factors/DTech/DTech_ret",
                # "/data/quant/factors/DTech/DTech_lret",
                # "/data/quant/factors/DTech/DTech_opn",
                # "/data/quant/factors/DTech/DTech_vwap",
            ],
        )

        ...
    else:
        fire.Fire(run)

    logging.warning(f"All done")
