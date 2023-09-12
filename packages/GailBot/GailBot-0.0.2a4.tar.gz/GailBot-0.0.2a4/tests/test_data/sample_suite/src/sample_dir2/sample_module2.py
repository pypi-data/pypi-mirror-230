# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-07-06 09:53:29
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-07-07 13:38:50
from gailbot import Plugin, GBPluginMethods, UttObj
import logging


class SampleTwo(Plugin):
    """
    The plugin itself does not fail, but since it depends on test_fail2,
    it also will never be run, and should fail
    """

    def __init__(self) -> None:
        super().__init__()

    def apply(self, dependency_outputs, methods: GBPluginMethods):
        print(f"path to merged media file {methods.merged_media}")
        print(f"path to the audio paths {methods.get_audio_path()}")
        print(f"plugin suite work path to save temporary file {methods.work_path}")
        print(f"plugin suite result output path {methods.out_path}")
        self.successful = True
        return True
