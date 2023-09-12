# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-07-06 10:35:27
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-07-06 10:35:58
import logging
from gailbot import Plugin, GBPluginMethods, UttObj


class TestFail1(Plugin):
    """
    The plugin is supposed to fail with an exception
    """

    def __init__(self) -> None:
        super().__init__()

    def apply(self, dependency_outputs, methods: GBPluginMethods):
        print("test fail 1")
        logging.error("this test will throw error")
        raise Exception("test one fails")
