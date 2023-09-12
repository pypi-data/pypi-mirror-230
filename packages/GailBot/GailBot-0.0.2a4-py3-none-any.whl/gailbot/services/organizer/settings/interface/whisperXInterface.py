# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-07-17 19:21:51
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-08-01 05:39:08
from pydantic import BaseModel, ValidationError
from typing import Dict, Union
from .engineSettingInterface import EngineSettingInterface
from gailbot.core.utils.logger import makelogger

logger = makelogger("whisperXInterface")


class ValidateWhisperX(BaseModel):
    engine: str
    language: str = None


class Init(BaseModel):
    pass


class TranscribeSetting(BaseModel):
    language: str = None


class WhisperXInterface(EngineSettingInterface):
    """
    Interface for the Whisper speech to text engine
    """
    transcribe: TranscribeSetting
    init: Init = None
    engine: str


def load_whisperX_setting(
        setting: Dict[str, str]
) -> Union[bool, EngineSettingInterface]:
    """given a dictionary, load the dictionary as a whisper setting

    Args:
        setting (Dict[str, str]): the dictionary that contains the setting data

    Returns:
        Union[bool , SettingInterface]: if the setting dictionary is validated
                                        by the whisper setting interface,
                                        return the Google setting interface
                                        as an instance of SettingInterface,
                                        else return false
    """
    logger.info("initialize whisper engine")
    if "engine" not in setting.keys() or setting["engine"].lower() != "whisperx":
        return False
    try:
        logger.info(setting)
        setting = setting.copy()
        ValidateWhisperX(**setting)
        whisper_set = dict()
        whisper_set["engine"] = setting.pop("engine")
        whisper_set["init"] = dict()
        whisper_set["transcribe"] = dict()
        whisper_set["transcribe"].update(setting)
        whisper_set = WhisperXInterface(**whisper_set)
        return whisper_set
    except ValidationError as e:
        logger.error(e, exc_info=e)
        logger.error(f"error in validating whisper interface {e}")
        return False
