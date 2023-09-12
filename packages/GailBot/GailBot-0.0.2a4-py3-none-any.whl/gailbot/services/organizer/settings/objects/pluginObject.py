# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-07-31 16:21:27
# @Last Modified by:   Hannah Shader
# @Last Modified time: 2023-08-11 16:10:48
from typing import List


class PluginSuiteSetObj:
    def __init__(self, plugins) -> None:
        self.data = plugins

    def get_data(self) -> List[str]:
        return self.data
