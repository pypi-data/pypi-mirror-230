# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-08-22 06:35:17
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-08-22 07:20:07
from gailbot import Plugin, GBPluginMethods, UttObj
import logging


class TestFail2(Plugin):
    """
    The plugin itself does not fail, but since it depends on test_fail2,
    it also will never be run, and should fail
    """

    def __init__(self) -> None:
        super().__init__()

    def apply(self, dependency_outputs, methods: GBPluginMethods):
        print("test fail 2")
        logging.error("this line will never be logged")
        self.successful = True
        return True
