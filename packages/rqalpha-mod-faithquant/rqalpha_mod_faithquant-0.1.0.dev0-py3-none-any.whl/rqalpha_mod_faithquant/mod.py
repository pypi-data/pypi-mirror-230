#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2023 datavita.com.cn, Inc. All Rights Reserved
#
########################################################################


"""
File: mod.py.py
Author: wangjiangfeng(wangjiangfeng@hcyjs.com)
Date: 2023/9/12 16:11:47
"""
import os
from typing import Any
from rqalpha.interface import AbstractMod
from rqalpha.environment import Environment
from rqalpha.utils.logger import user_log, user_system_log
from logbook.handlers import RotatingFileHandler


class FaithquantMod(AbstractMod):

    def __init__(self):
        self._env = None
        self._mod_config = None

    def start_up(self, env, mod_config):
        # type: (Environment, Any) -> None
        self._env = env
        self._mod_config = mod_config
        save_backtest_log = getattr(mod_config, 'save_backtest_log', False)
        if save_backtest_log:
            self._save_backtest_log()

    def _save_backtest_log(self):
        filename = None
        try:
            base_report_path = self._env.config.faithquant.portfolio.base_report_path
            task_num = self._env.config.faithquant.portfolio.task_num
            log_path = "{}/{}/logs".format(str(base_report_path).rstrip("/"), task_num)
            if not os.path.exists(log_path):
                os.makedirs(log_path, exist_ok=True)
            filename = '{}/rqalpha_backtest.log'.format(log_path)
            user_log.handlers.append(RotatingFileHandler(filename, max_size=1024*1024, bubble=True))
            user_system_log.handlers.append(RotatingFileHandler(filename, max_size=1024*1024, bubble=True))
        except Exception as e:
            user_system_log.warn("initialize RotatingFileHandler failed ! filename: {}, msg: {}", filename, str(e))

    def tear_down(self, code, exception=None):
        pass
