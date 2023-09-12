# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-07-06 09:53:29
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-07-07 13:38:28
from gailbot import Plugin, GBPluginMethods, UttObj
import logging


class SampleOne(Plugin):
    """
    The plugin itself does not fail, but since it depends on test_fail2,
    it also will never be run, and should fail
    """

    def __init__(self) -> None:
        super().__init__()

    def apply(self, dependency_outputs, methods: GBPluginMethods):
        uttObjDict = methods.get_utterance_objects()
        for _, uttObjList in uttObjDict.items():
            for uttObj in uttObjList:
                print(
                    f"{uttObj.start} -- {uttObj.end}, {uttObj.speaker}, {uttObj.text}"
                )

        uttDictDict = methods.utterances
        for _, uttDictList in uttDictDict.items():
            for uttDict in uttDictList:
                print(uttDict)

        self.successful = True
        # Note: this line is required to allow gailbot plugin manager
        # recognize that this plugin is run successfully
        # It is not necessary though, another way is to wrap everything in a try-catch block
        # in gailbot's PluginComponent __call__() function, and get rid of the plugin.successfull == true
        # check.
        return True
