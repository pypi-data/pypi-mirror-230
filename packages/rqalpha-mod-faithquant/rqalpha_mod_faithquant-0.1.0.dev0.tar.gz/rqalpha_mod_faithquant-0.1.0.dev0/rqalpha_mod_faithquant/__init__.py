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
Date: 2023/9/12 16:10:34
"""

"""
    模块自定义参数
"""
__config__ = {
    "mod_name": "rqalpha_mod_extend_faithquant",
    "save_backtest_log": True
}


def load_mod():
    """
    供rqalpha框架回测启动加载
    """
    from .mod import FaithquantMod
    return FaithquantMod()
