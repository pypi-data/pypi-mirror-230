# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-07-06 10:35:27
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-07-07 13:41:06

from gailbot import Plugin, GBPluginMethods, UttObj
import logging


class TestSucc1(Plugin):
    """
    The plugin itself does not fail, but since it depends on test_fail2,
    it also will never be run, and should fail
    """

    def __init__(self) -> None:
        super().__init__()

    def apply(self, dependency_outputs, methods: GBPluginMethods):
        print("Test succ1")
        logging.info("running test_succ1")
        self.successful = True
        # Note: this line is required to allow gailbot plugin manager
        # recognize that this plugin is run successfully
        # It is not necessary though, another way is to wrap everything in a try-catch block
        # in gailbot's PluginComponent __call__() function, and get rid of the plugin.successfull == true
        # check.
        return True
