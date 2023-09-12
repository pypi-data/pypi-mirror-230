# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-07-06 10:35:27
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-07-07 14:04:38
from gailbot import Plugin, GBPluginMethods, UttObj
import logging
import time


class TestSucc3(Plugin):
    """
    The plugin itself does not fail, but since it depends on test_fail2,
    it also will never be run, and should fail
    """

    def __init__(self) -> None:
        super().__init__()

    def apply(self, dependency_outputs, methods: GBPluginMethods):
        print("long running test3 ")
        logging.info("long running test4")
        time.sleep(10)
        self.successful = True
        return True
