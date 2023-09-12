# -*- coding: utf-8 -*-
# @Author: Muhammad Umair
# @Date:   2023-01-10 13:29:08
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-08-01 05:32:56
from typing import Dict, List, Any
from gailbot.core.engines import Engine, Watson, Google, WhisperEngine, WhisperX

_ENGINES = {"watson": Watson, "google": Google, "whisper": WhisperEngine, "whisperX": WhisperX}


class EngineManager:
    """
    provides wrapper function to run available speech detect engines
    """

    @staticmethod
    def available_engines() -> List[str]:
        """
        Returns:
            List[str]: return a list of available engine
        """
        return list(_ENGINES.keys())

    @staticmethod
    def is_engine(name: str) -> bool:
        return name in EngineManager.available_engines()

    @staticmethod
    def init_engine(name: str, **kwargs) -> Engine:
        if not EngineManager.is_engine(name):
            raise Exception(f"Engine not supported: {name}")
        engine = _ENGINES[name](**kwargs)
        return engine
