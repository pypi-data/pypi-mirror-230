# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-07-31 16:21:27
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-08-01 05:38:38
from pydantic import BaseModel
from typing import Dict


class EngineSettingInterface(BaseModel):
    engine: str

    def get_init_kwargs(self) -> Dict[str, str]:
        """
        get the setting kwargs for initializing the engine
        """
        d = self.dict()["init"]
        return d

    def get_transcribe_kwargs(self) -> Dict[str, str]:
        """
        get the settings kwargs for transcribe function
        """
        d = self.dict()["transcribe"]
        return d
