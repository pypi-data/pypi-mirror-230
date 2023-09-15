# -*- coding: utf-8 -*-
# @Time     : 2020-02-07 11:26
# @Author   : binger

name = "logger_app"
version_info = (0, 0, 2, 23091422)
__version__ = ".".join([str(v) for v in version_info])
__description__ = '实现对logging的简单扩展'

from .model import LoggerApp, register_formatter_tag_mapper, FormatterRule
